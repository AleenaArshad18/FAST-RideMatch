
import { Platform } from 'react-native';

export const API_BASE_URL = (
  process.env.EXPO_PUBLIC_API_URL ||
  (Platform.OS === 'android'
    ? 'http://10.0.2.2:8000'
    : 'http://127.0.0.1:8000')
).replace(/\/+$/, '');

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

type ApiRequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  authToken?: string;
  requiresAuth?: boolean;
};

export async function apiRequest<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const {
    method = 'GET',
    body,
    authToken,
    requiresAuth = false,
  } = options;

  if (requiresAuth && !authToken?.trim()) {
    throw new ApiError(
      401,
      'Verified student sign-in is required.'
    );
  }

  const headers: Record<string, string> = {
    Accept: 'application/json',
  };

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  let response: Response;

  try {
    response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method,
        headers,
        body:
          body !== undefined
            ? JSON.stringify(body)
            : undefined,
      }
    );
  } catch {
    throw new ApiError(
      0,
      'Could not connect to the backend. Please check that FastAPI is running.'
    );
  }

  const result = await response.json().catch(() => null);

  if (!response.ok) {
    const defaultMessages: Record<number, string> = {
      400: 'Invalid request.',
      401: 'Please sign in again.',
      403: 'You are not authorized to perform this action.',
      404: 'The requested resource was not found.',
      409: 'This action conflicts with the current ride status.',
      422: 'Please check the submitted information.',
      500: 'An internal server error occurred.',
      503: 'The required backend service is not available yet.',
    };

    const message =
      typeof result?.detail === 'string'
        ? result.detail
        : defaultMessages[response.status] ||
          `Server returned ${response.status}.`;

    throw new ApiError(response.status, message);
  }

  return result as T;
}
