
import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "ride_match.db"
)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_driver_listing_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ride_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                start_area TEXT NOT NULL,
                destination_area TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                available_seats INTEGER NOT NULL
                    CHECK (available_seats >= 0),
                vehicle_details TEXT NOT NULL,
                fare REAL NOT NULL
                    CHECK (fare >= 0),
                status TEXT NOT NULL DEFAULT 'active'
                    CHECK (
                        status IN (
                            'active',
                            'completed',
                            'cancelled'
                        )
                    )
            )
        """)

        # Check whether an existing database needs migration.
        columns = connection.execute(
            "PRAGMA table_info(ride_listings)"
        ).fetchall()

        column_names = [
            column["name"] for column in columns
        ]

        if "status" not in column_names:
            connection.execute("""
                ALTER TABLE ride_listings
                ADD COLUMN status TEXT NOT NULL
                    DEFAULT 'active'
                    CHECK (
                        status IN (
                            'active',
                            'completed',
                            'cancelled'
                        )
                    )
            """)

        connection.commit()

        schema = connection.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'ride_listings'
            """
        ).fetchone()

        normalized_schema = "".join(
            schema["sql"].lower().split()
        ) if schema is not None else ""

        if "available_seats>0" in normalized_schema:
            connection.execute("PRAGMA foreign_keys = OFF")

            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("""
                    CREATE TABLE ride_listings_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        driver_id INTEGER NOT NULL,
                        start_area TEXT NOT NULL,
                        destination_area TEXT NOT NULL,
                        departure_time TEXT NOT NULL,
                        available_seats INTEGER NOT NULL
                            CHECK (available_seats >= 0),
                        vehicle_details TEXT NOT NULL,
                        fare REAL NOT NULL
                            CHECK (fare >= 0),
                        status TEXT NOT NULL DEFAULT 'active'
                            CHECK (
                                status IN (
                                    'active',
                                    'completed',
                                    'cancelled'
                                )
                            )
                    )
                """)
                connection.execute("""
                    INSERT INTO ride_listings_new (
                        id,
                        driver_id,
                        start_area,
                        destination_area,
                        departure_time,
                        available_seats,
                        vehicle_details,
                        fare,
                        status
                    )
                    SELECT
                        id,
                        driver_id,
                        start_area,
                        destination_area,
                        departure_time,
                        available_seats,
                        vehicle_details,
                        fare,
                        status
                    FROM ride_listings
                """)
                connection.execute("DROP TABLE ride_listings")
                connection.execute(
                    "ALTER TABLE ride_listings_new RENAME TO ride_listings"
                )
                connection.commit()
            except sqlite3.Error:
                connection.rollback()
                raise
            finally:
                connection.execute("PRAGMA foreign_keys = ON")


def save_ride_listing(listing):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO ride_listings (
                driver_id,
                start_area,
                destination_area,
                departure_time,
                available_seats,
                vehicle_details,
                fare
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                listing.driver_id,
                listing.start_area,
                listing.destination_area,
                listing.departure_time.isoformat(),
                listing.available_seats,
                listing.vehicle_details,
                listing.fare
            )
        )

        connection.commit()
        return cursor.lastrowid


def get_ride_listing(listing_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT *
            FROM ride_listings
            WHERE id = ?
            """,
            (listing_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)


def update_ride_listing(listing_id: int, listing):
    """
    Update an existing active ride listing.

    The driver_id is intentionally not updated.
    Ownership must be checked by the API before
    calling this function.

    Cancelled and completed rides cannot be edited.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE ride_listings
            SET
                start_area = ?,
                destination_area = ?,
                departure_time = ?,
                available_seats = ?,
                vehicle_details = ?,
                fare = ?
            WHERE id = ?
              AND status = 'active'
            """,
            (
                listing.start_area,
                listing.destination_area,
                listing.departure_time.isoformat(),
                listing.available_seats,
                listing.vehicle_details,
                listing.fare,
                listing_id
            )
        )

        connection.commit()
        return cursor.rowcount > 0


def get_all_ride_listings():
    """
    Retrieve all ride listings from the database.
    Earliest departure times are returned first.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT *
            FROM ride_listings
            ORDER BY departure_time ASC
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]