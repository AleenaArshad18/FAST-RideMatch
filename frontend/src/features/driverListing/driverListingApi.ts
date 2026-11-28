
import { apiRequest } from '../../services/api';

export type RideStatus =
  | 'active'
  | 'cancelled'
  | 'completed';

export type RideListingDetails = {
  start_area: string;
  destination_area: string;
  departure_time: string;
  available_seats: number;
  vehicle_details: string;
  fare: number;
};

export type RideListingCreate = RideListingDetails & {
  driver_id: number;
};

export type RideListingUpdate = RideListingDetails;

export type RideListing = RideListingDetails & {
  id: number;
  driver_id: number;
  status: RideStatus;
};

// Retrieve an existing ride listing.
export function getRideListing(
  listingId: number
): Promise<RideListing> {
  return apiRequest<RideListing>(
    `/ride-listings/${listingId}`
  );
}

// Publish a new ride.
export function createRideListing(
  listing: RideListingCreate,
  authToken: string
): Promise<RideListing> {
  return apiRequest<RideListing>(
    '/ride-listings',
    {
      method: 'POST',
      body: listing,
      authToken,
      requiresAuth: true,
    }
  );
}

// Update an existing ride.
export function updateRideListing(
  listingId: number,
  listing: RideListingUpdate,
  authToken: string
): Promise<RideListing> {
  return apiRequest<RideListing>(
    `/ride-listings/${listingId}`,
    {
      method: 'PUT',
      body: listing,
      authToken,
      requiresAuth: true,
    }
  );
}
