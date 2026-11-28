
from contextlib import closing
from datetime import datetime, timezone

from fastapi import HTTPException

from app.database.driver_listing_db import get_connection


def initialize_ride_lifecycle_table():
    with closing(get_connection()) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS ride_lifecycle_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id INTEGER NOT NULL,
                    driver_id INTEGER NOT NULL,
                    previous_status TEXT NOT NULL,
                    new_status TEXT NOT NULL,
                    changed_at TEXT NOT NULL,
                    FOREIGN KEY (listing_id)
                        REFERENCES ride_listings(id)
                )
            """)


def update_ride_status(
    listing_id: int,
    driver_id: int,
    new_status: str
):
    if new_status not in ("cancelled", "completed"):
        raise HTTPException(
            status_code=400,
            detail="Invalid ride status."
        )

    connection = get_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")

        listing = connection.execute(
            """
            SELECT *
            FROM ride_listings
            WHERE id = ?
            """,
            (listing_id,)
        ).fetchone()

        if listing is None:
            raise HTTPException(
                status_code=404,
                detail="Ride listing not found."
            )

        if listing["driver_id"] != driver_id:
            raise HTTPException(
                status_code=403,
                detail="You can only manage your own rides."
            )

        if listing["status"] != "active":
            raise HTTPException(
                status_code=409,
                detail="Only active rides can be cancelled or completed."
            )

        if new_status == "completed":
            departure_time = datetime.fromisoformat(
                listing["departure_time"]
            )

            if departure_time.tzinfo is None:
                raise HTTPException(
                    status_code=409,
                    detail="Ride departure timezone is missing."
                )

            if departure_time > datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=409,
                    detail="A ride cannot be completed before departure."
                )

            # Resolve pending requests before completing a ride.
            pending_request = connection.execute(
                """
                SELECT id
                FROM ride_requests
                WHERE listing_id = ?
                  AND status = 'pending'
                LIMIT 1
                """,
                (listing_id,)
            ).fetchone()

            if pending_request is not None:
                raise HTTPException(
                    status_code=409,
                    detail="Resolve all pending requests before completing the ride."
                )

        if new_status == "cancelled":
            existing_request = connection.execute(
                """
                SELECT id
                FROM ride_requests
                WHERE listing_id = ?
                  AND status IN ('pending', 'accepted')
                LIMIT 1
                """,
                (listing_id,)
            ).fetchone()

            if existing_request is not None:
                raise HTTPException(
                    status_code=409,
                    detail="Cancellation requires passenger request coordination."
                )

        status_update = connection.execute(
            """
            UPDATE ride_listings
            SET status = ?
            WHERE id = ?
              AND driver_id = ?
              AND status = 'active'
            """,
            (new_status, listing_id, driver_id)
        )

        # Ensure the status was successfully updated.
        if status_update.rowcount != 1:
            raise HTTPException(
                status_code=409,
                detail="Ride status could not be updated."
            )

        connection.execute(
            """
            INSERT INTO ride_lifecycle_history (
                listing_id,
                driver_id,
                previous_status,
                new_status,
                changed_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                listing_id,
                driver_id,
                listing["status"],
                new_status,
                datetime.now(timezone.utc).isoformat()
            )
        )

        connection.commit()

        return {
            "listing_id": listing_id,
            "driver_id": driver_id,
            "status": new_status
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_ride_lifecycle_history(
    listing_id: int,
    driver_id: int
):
    with closing(get_connection()) as connection:
        listing = connection.execute(
            """
            SELECT driver_id
            FROM ride_listings
            WHERE id = ?
            """,
            (listing_id,)
        ).fetchone()

        if listing is None:
            raise HTTPException(
                status_code=404,
                detail="Ride listing not found."
            )

        if listing["driver_id"] != driver_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own ride history."
            )

        rows = connection.execute(
            """
            SELECT *
            FROM ride_lifecycle_history
            WHERE listing_id = ?
              AND driver_id = ?
            ORDER BY changed_at DESC, id DESC
            """,
            (listing_id, driver_id)
        ).fetchall()

        return [dict(row) for row in rows]
