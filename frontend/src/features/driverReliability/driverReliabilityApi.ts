
import { apiRequest } from '../../services/api';

export type DriverReliabilityResponse = {
  driver_id: number;
  completed_ride_count: number;
  average_rating: number | null;
};

// Retrieve reliability information for a driver.
export function getDriverReliability(
  driverId: number,
  authToken: string
): Promise<DriverReliabilityResponse> {
  return apiRequest<DriverReliabilityResponse>(
    `/drivers/${driverId}/reliability`,
    {
      authToken,
      requiresAuth: true,
    }
  );
}
