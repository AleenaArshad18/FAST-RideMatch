from app.database.driver_listing_db import get_connection


def get_completed_ride_count(driver_id: int) -> int:
    """
    Count explicitly completed rides for a driver.

    Active and cancelled rides are excluded.
    """

    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT COUNT(*) AS completed_ride_count
            FROM ride_listings
            WHERE driver_id = ?
                AND status = 'completed'
            """,
            (driver_id,)
        )

        row = cursor.fetchone()

        return row["completed_ride_count"]