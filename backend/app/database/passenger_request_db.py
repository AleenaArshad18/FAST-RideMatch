import sqlite3
from pathlib import Path

from fastapi import HTTPException


DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "ride_match.db"
)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_passenger_request_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ride_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                driver_id INTEGER NOT NULL,
                passenger_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'accepted', 'rejected')),
                created_at TEXT NOT NULL,
                FOREIGN KEY (listing_id)
                    REFERENCES ride_listings(id)
            )
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
                idx_one_pending_request_per_ride
            ON ride_requests(listing_id, passenger_id)
            WHERE status = 'pending'
        """)
        connection.commit()


def save_passenger_request(
    listing_id: int,
    driver_id: int,
    passenger_id: int,
    created_at: str
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO ride_requests (
                listing_id,
                driver_id,
                passenger_id,
                status,
                created_at
            )
            VALUES (?, ?, ?, 'pending', ?)
            """,
            (
                listing_id,
                driver_id,
                passenger_id,
                created_at
            )
        )
        connection.commit()
        return cursor.lastrowid


def get_passenger_request(request_id: int):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ride_requests
            WHERE id = ?
            """,
            (request_id,)
        ).fetchone()
        return dict(row) if row is not None else None


def get_passenger_requests(passenger_id: int):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM ride_requests
            WHERE passenger_id = ?
            ORDER BY created_at DESC
            """,
            (passenger_id,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_pending_passenger_request(listing_id: int, passenger_id: int):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ride_requests
            WHERE listing_id = ?
              AND passenger_id = ?
              AND status = 'pending'
            LIMIT 1
            """,
            (listing_id, passenger_id)
        ).fetchone()
        return dict(row) if row is not None else None


def get_requests_for_driver(driver_id: int):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM ride_requests
            WHERE driver_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (driver_id,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_request_by_id(request_id: int):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ride_requests
            WHERE id = ?
            """,
            (request_id,)
        ).fetchone()
        return dict(row) if row is not None else None


def process_request_decision(
    driver_id: int,
    request_id: int,
    decision: str
):
    if decision not in ("accept", "reject"):
        raise ValueError(f"Unsupported request decision: {decision}")

    connection = get_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")

        request = connection.execute(
            """
            SELECT *
            FROM ride_requests
            WHERE id = ?
            """,
            (request_id,)
        ).fetchone()

        if request is None:
            raise HTTPException(
                status_code=404,
                detail="Ride request not found."
            )

        request = dict(request)

        if request["driver_id"] != driver_id:
            raise HTTPException(
                status_code=403,
                detail="You cannot access another driver's requests."
            )

        if request["status"] != "pending":
            raise HTTPException(
                status_code=409,
                detail="Only pending requests can be accepted or rejected."
            )

        if decision == "accept":
            listing = connection.execute(
                """
                SELECT driver_id, status, available_seats
                FROM ride_listings
                WHERE id = ?
                """,
                (request["listing_id"],)
            ).fetchone()

            if listing is None:
                raise HTTPException(
                    status_code=409,
                    detail="The ride listing is no longer available."
                )

            if listing["driver_id"] != driver_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only manage requests for your own rides."
                )

            if request["driver_id"] != listing["driver_id"]:
                raise HTTPException(
                    status_code=409,
                    detail="Ride request ownership does not match the listing."
                )

            if listing["status"] != "active":
                raise HTTPException(
                    status_code=409,
                    detail="Only active rides can be accepted."
                )

            if listing["available_seats"] <= 0:
                raise HTTPException(
                    status_code=409,
                    detail="This ride has no available seats."
                )

            seat_update = connection.execute(
                """
                UPDATE ride_listings
                SET available_seats = available_seats - 1
                WHERE id = ?
                  AND driver_id = ?
                  AND status = 'active'
                  AND available_seats > 0
                """,
                (request["listing_id"], driver_id)
            )

            if seat_update.rowcount != 1:
                raise HTTPException(
                    status_code=409,
                    detail="This ride has no available seats."
                )

        new_status = "accepted" if decision == "accept" else "rejected"
        request_update = connection.execute(
            """
            UPDATE ride_requests
            SET status = ?
            WHERE id = ?
              AND driver_id = ?
              AND status = 'pending'
            """,
            (new_status, request_id, driver_id)
        )

        if request_update.rowcount != 1:
            raise HTTPException(
                status_code=409,
                detail="Only pending requests can be accepted or rejected."
            )

        connection.commit()

        updated_request = connection.execute(
            """
            SELECT *
            FROM ride_requests
            WHERE id = ?
            """,
            (request_id,)
        ).fetchone()
        return dict(updated_request)
    except (HTTPException, sqlite3.Error):
        connection.rollback()
        raise
    finally:
        connection.close()
