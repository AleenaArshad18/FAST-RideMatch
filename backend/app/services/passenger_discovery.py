
from datetime import datetime, timezone


def search_and_filter_rides(
    rides,
    start_area=None,
    destination_area=None,
    departure_date=None,
    min_fare=None,
    max_fare=None,
    min_seats=None
):
    """
    Search and filter available future rides.
    """

    filtered_rides = []

    for ride in rides:
        departure = datetime.fromisoformat(
            ride["departure_time"]
        )

        # Exclude past rides.
        if departure <= datetime.now(timezone.utc):
            continue

        # Exclude rides without available seats.
        if ride["available_seats"] <= 0:
            continue

        # Filter by starting area.
        if start_area:
            if start_area.strip().casefold() not in ride["start_area"].casefold():
                continue

        # Filter by destination.
        if destination_area:
            if destination_area.strip().casefold() not in ride["destination_area"].casefold():
                continue

        # Filter by departure date.
        if departure_date:
            if departure.date().isoformat() != departure_date:
                continue

        # Filter by minimum fare.
        if min_fare is not None:
            if ride["fare"] < min_fare:
                continue

        # Filter by maximum fare.
        if max_fare is not None:
            if ride["fare"] > max_fare:
                continue

        # Filter by minimum available seats.
        if min_seats is not None:
            if ride["available_seats"] < min_seats:
                continue

        filtered_rides.append(ride)

    return filtered_rides
