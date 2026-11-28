
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP


DATABASE_PATH = None


def get_connection():
    if DATABASE_PATH is not None:
        path = DATABASE_PATH
    else:
        from app.database.passenger_request_db import DATABASE_PATH as path

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def create_payment_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS payment_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL UNIQUE,
            listing_id INTEGER NOT NULL,
            driver_id INTEGER NOT NULL,
            passenger_id INTEGER NOT NULL,
            total_fare REAL NOT NULL CHECK(total_fare >= 0),
            accepted_passengers INTEGER NOT NULL CHECK(accepted_passengers > 0),
            amount REAL NOT NULL CHECK(amount >= 0),
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK(status IN ('pending', 'paid', 'failed')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(request_id) REFERENCES ride_requests(id)
        )
    """)
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_payment_passenger_history
        ON payment_records(passenger_id, created_at DESC)
    """)


def initialize_payment_table():
    with get_connection() as connection:
        create_payment_table(connection)
        connection.commit()


def recalculate_payment_records(connection, listing_id):
    create_payment_table(connection)

    listing = connection.execute(
        "SELECT fare FROM ride_listings WHERE id = ?",
        (listing_id,)
    ).fetchone()

    if listing is None:
        return

    accepted = connection.execute("""
        SELECT id, listing_id, driver_id, passenger_id
        FROM ride_requests
        WHERE listing_id = ? AND status = 'accepted'
        ORDER BY id
    """, (listing_id,)).fetchall()

    if not accepted:
        return

    now = datetime.now(timezone.utc).isoformat()
    total_fare = Decimal(str(listing["fare"]))
    total_cents = int(
        (total_fare * 100).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )
    accepted_count = len(accepted)

    for request in accepted:
        connection.execute("""
            INSERT OR IGNORE INTO payment_records (
                request_id, listing_id, driver_id, passenger_id,
                total_fare, accepted_passengers, amount, status,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, 'pending', ?, ?)
        """, (
            request["id"],
            request["listing_id"],
            request["driver_id"],
            request["passenger_id"],
            float(total_fare),
            accepted_count,
            now,
            now
        ))

    records = connection.execute("""
        SELECT request_id, amount, status
        FROM payment_records
        WHERE listing_id = ?
        ORDER BY request_id
    """, (listing_id,)).fetchall()

    paid_cents = 0
    unpaid_ids = []

    for record in records:
        if record["status"] == "paid":
            paid_cents += int(
                (Decimal(str(record["amount"])) * 100).quantize(
                    Decimal("1")
                )
            )
        else:
            unpaid_ids.append(record["request_id"])

    remaining_cents = max(0, total_cents - paid_cents)

    if unpaid_ids:
        base, remainder = divmod(
            remaining_cents, len(unpaid_ids)
        )

        for index, request_id in enumerate(unpaid_ids):
            amount_cents = base + (1 if index < remainder else 0)

            connection.execute("""
                UPDATE payment_records
                SET total_fare = ?,
                    accepted_passengers = ?,
                    amount = ?,
                    updated_at = ?
                WHERE request_id = ? AND status != 'paid'
            """, (
                float(total_fare),
                accepted_count,
                amount_cents / 100,
                now,
                request_id
            ))

    connection.execute("""
        UPDATE payment_records
        SET total_fare = ?,
            accepted_passengers = ?,
            updated_at = ?
        WHERE listing_id = ? AND status = 'paid'
    """, (
        float(total_fare),
        accepted_count,
        now,
        listing_id
    ))


def get_passenger_payment_history(passenger_id):
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT p.*, l.start_area, l.destination_area,
                   l.departure_time
            FROM payment_records p
            JOIN ride_listings l ON l.id = p.listing_id
            WHERE p.passenger_id = ?
            ORDER BY p.created_at DESC, p.id DESC
        """, (passenger_id,)).fetchall()

        return [dict(row) for row in rows]


def get_passenger_payment(request_id, passenger_id):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT p.*, l.start_area, l.destination_area,
                   l.departure_time
            FROM payment_records p
            JOIN ride_listings l ON l.id = p.listing_id
            WHERE p.request_id = ? AND p.passenger_id = ?
        """, (request_id, passenger_id)).fetchone()

        return dict(row) if row else None

def update_payment_status(request_id, driver_id, status):
    if status not in ("pending", "paid", "failed"):
        return None

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE payment_records
            SET status = ?, updated_at = ?
            WHERE request_id = ? AND driver_id = ?
        """, (status, now, request_id, driver_id))

        connection.commit()

        if cursor.rowcount != 1:
            return None

        row = connection.execute("""
            SELECT p.*, l.start_area, l.destination_area,
                   l.departure_time
            FROM payment_records p
            JOIN ride_listings l ON l.id = p.listing_id
            WHERE p.request_id = ? AND p.driver_id = ?
        """, (request_id, driver_id)).fetchone()

        return dict(row) if row else None