import { apiRequest } from '../../services/api';

export type PaymentStatus =
  | 'pending'
  | 'paid'
  | 'failed';

export type PaymentRecord = {
  id: number;
  request_id: number;
  listing_id: number;
  driver_id: number;
  passenger_id: number;
  total_fare: number;
  accepted_passengers: number;
  amount: number;
  status: PaymentStatus;
  created_at: string;
  updated_at: string;
  start_area: string;
  destination_area: string;
  departure_time: string;
};

// Retrieve the passenger's complete payment history.
export function getPassengerPayments(
  authToken: string
): Promise<PaymentRecord[]> {
  return apiRequest<PaymentRecord[]>(
    '/passenger/payments',
    {
      authToken,
      requiresAuth: true,
    }
  );
}

// Retrieve details of one payment using its request ID.
export function getPassengerPaymentDetails(
  requestId: number,
  authToken: string
): Promise<PaymentRecord> {
  return apiRequest<PaymentRecord>(
    `/passenger/payments/${requestId}`,
    {
      authToken,
      requiresAuth: true,
    }
  );
}
