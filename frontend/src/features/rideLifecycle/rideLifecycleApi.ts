
import { apiRequest } from '../../services/api';

export type RideStatus =
  | 'active'
  | 'cancelled'
  | 'completed';

export type RideLifecycleResponse = {
  listing_id: number;
  driver_id: number;
  status: RideStatus;
};

export type RideLifecycleHistory = {
  id: number;
  listing_id: number;
  driver_id: number;
  previous_status: RideStatus;
  new_status: RideStatus;
  changed_at: string;
};

// Cancel an active ride.
export function cancelRide(
  listingId: number,
  authToken: string
): Promise<RideLifecycleResponse> {
  return apiRequest<RideLifecycleResponse>(
    `/ride-listings/${listingId}/cancel`,
    {
      method: 'POST',
      authToken,
      requiresAuth: true,
    }
  );
}

// Mark an active ride as completed.
export function completeRide(
  listingId: number,
  authToken: string
): Promise<RideLifecycleResponse> {
  return apiRequest<RideLifecycleResponse>(
    `/ride-listings/${listingId}/complete`,
    {
      method: 'POST',
      authToken,
      requiresAuth: true,
    }
  );
}

// Retrieve the lifecycle history of a ride.
export function getRideLifecycleHistory(
  listingId: number,
  authToken: string
): Promise<RideLifecycleHistory[]> {
  return apiRequest<RideLifecycleHistory[]>(
    `/ride-listings/${listingId}/history`,
    {
      authToken,
      requiresAuth: true,
    }
  );
}
