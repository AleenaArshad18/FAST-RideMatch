
import { apiRequest } from '../../services/api';

export type RequestStatus =
  | 'pending'
  | 'accepted'
  | 'rejected';

export type DriverRequest = {
  id: number;
  listing_id: number;
  driver_id: number;
  passenger_id: number;
  status: RequestStatus;
  created_at: string;
};

// Retrieve all requests belonging to the driver.
export function getDriverRequests(
  authToken: string
): Promise<DriverRequest[]> {
  return apiRequest<DriverRequest[]>(
    '/driver/requests',
    {
      authToken,
      requiresAuth: true,
    }
  );
}

// Retrieve individual request details.
export function getDriverRequest(
  requestId: number,
  authToken: string
): Promise<DriverRequest> {
  return apiRequest<DriverRequest>(
    `/driver/requests/${requestId}`,
    {
      authToken,
      requiresAuth: true,
    }
  );
}

// Accept a pending passenger request.
export function acceptDriverRequest(
  requestId: number,
  authToken: string
): Promise<DriverRequest> {
  return apiRequest<DriverRequest>(
    `/driver/requests/${requestId}/accept`,
    {
      method: 'POST',
      authToken,
      requiresAuth: true,
    }
  );
}

// Reject a pending passenger request.
export function rejectDriverRequest(
  requestId: number,
  authToken: string
): Promise<DriverRequest> {
  return apiRequest<DriverRequest>(
    `/driver/requests/${requestId}/reject`,
    {
      method: 'POST',
      authToken,
      requiresAuth: true,
    }
  );
}
