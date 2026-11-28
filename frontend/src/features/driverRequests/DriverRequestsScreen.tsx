
import { useCallback, useEffect, useState } from 'react';

import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';

import { ApiError } from '../../services/api';

import {
  getDriverRequests,
  getDriverRequest,
  acceptDriverRequest,
  rejectDriverRequest,
} from './driverRequestsApi';

import type {
  DriverRequest,
  RequestStatus,
} from './driverRequestsApi';

type DriverRequestsScreenProps = {
  authToken?: string;
};

type RequestFilter = 'all' | RequestStatus;

export default function DriverRequestsScreen({
  authToken,
}: DriverRequestsScreenProps) {
  const [requests, setRequests] = useState<DriverRequest[]>([]);

  const [selectedRequest, setSelectedRequest] =
    useState<DriverRequest | null>(null);

  const [filter, setFilter] =
    useState<RequestFilter>('all');

  const [isLoading, setIsLoading] = useState(false);

  const [isProcessing, setIsProcessing] =
    useState(false);

  const [errorMessage, setErrorMessage] = useState('');

  const [successMessage, setSuccessMessage] = useState('');

  // Convert API errors into readable messages.
  const getErrorMessage = (error: unknown): string => {
    return error instanceof ApiError
      ? error.message
      : 'An unexpected error occurred.';
  };

  // Load all incoming and previous requests.
  const loadRequests = useCallback(async () => {
    setErrorMessage('');
    setIsLoading(true);

    if (!authToken?.trim()) {
      setRequests([]);
      setSelectedRequest(null);
      setErrorMessage(
        'Verified student sign-in is required.'
      );
      setIsLoading(false);
      return;
    }

    try {
      const result = await getDriverRequests(authToken);
      setRequests(result);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [authToken]);

  useEffect(() => {
    setSelectedRequest(null);
    setRequests([]);
    setSuccessMessage('');
    loadRequests();
  }, [loadRequests]);

  // Retrieve the details of a selected request.
  const viewRequest = async (requestId: number) => {
    if (!authToken || isProcessing || isLoading) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const result = await getDriverRequest(
        requestId,
        authToken
      );

      setSelectedRequest(result);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsProcessing(false);
    }
  };

  // Accept or reject a pending request.
  const handleDecision = async (
    requestId: number,
    decision: 'accept' | 'reject'
  ) => {
    if (!authToken || isProcessing || isLoading) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const result =
        decision === 'accept'
          ? await acceptDriverRequest(
              requestId,
              authToken
            )
          : await rejectDriverRequest(
              requestId,
              authToken
            );

      setRequests((previous) =>
        previous.map((request) =>
          request.id === result.id
            ? result
            : request
        )
      );

      setSelectedRequest((previous) =>
        previous?.id === result.id
          ? result
          : previous
      );

      setSuccessMessage(
        `Request ${result.status} successfully.`
      );
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsProcessing(false);
    }
  };

  // Filter requests by their current status.
  const filteredRequests = requests.filter(
    (request) =>
      filter === 'all' ||
      request.status === filter
  );

  const filters: RequestFilter[] = [
    'all',
    'pending',
    'accepted',
    'rejected',
  ];

  const renderRequest = (
    request: DriverRequest,
    showDetailsButton: boolean
  ) => (
    <View style={styles.card} key={request.id}>
      <Text style={styles.cardTitle}>
        Request #{request.id}
      </Text>

      <Text style={styles.detail}>
        Ride ID: {request.listing_id}
      </Text>

      <Text style={styles.detail}>
        Passenger ID: {request.passenger_id}
      </Text>

      <Text style={styles.detail}>
        Requested on:{' '}
        {new Date(request.created_at).toLocaleString()}
      </Text>

      <Text style={styles.status}>
        Status: {request.status.toUpperCase()}
      </Text>

      {showDetailsButton && (
        <TouchableOpacity
          style={styles.button}
          disabled={isProcessing || isLoading}
          onPress={() => viewRequest(request.id)}
        >
          <Text style={styles.buttonText}>
            View Details
          </Text>
        </TouchableOpacity>
      )}

      {request.status === 'pending' && (
        <View style={styles.actionRow}>
          <TouchableOpacity
            style={[
              styles.actionButton,
              styles.acceptButton,
              isProcessing && styles.disabled,
            ]}
            disabled={isProcessing || isLoading}
            onPress={() =>
              handleDecision(request.id, 'accept')
            }
          >
            <Text style={styles.buttonText}>
              Accept
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.actionButton,
              styles.rejectButton,
              isProcessing && styles.disabled,
            ]}
            disabled={isProcessing || isLoading}
            onPress={() =>
              handleDecision(request.id, 'reject')
            }
          >
            <Text style={styles.buttonText}>
              Reject
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      <Text style={styles.heading}>
        Driver Requests
      </Text>

      <Text style={styles.subtitle}>
        Manage incoming passenger requests and
        view your request history.
      </Text>

      {errorMessage !== '' && (
        <Text style={styles.error}>
          {errorMessage}
        </Text>
      )}

      {successMessage !== '' && (
        <Text style={styles.success}>
          {successMessage}
        </Text>
      )}

      {(isLoading || isProcessing) && (
        <ActivityIndicator
          size="large"
          color="#303B32"
          style={styles.loader}
        />
      )}

      {selectedRequest ? (
        <>
          <TouchableOpacity
            style={styles.button}
            disabled={isProcessing}
            onPress={() => {
              setSelectedRequest(null);
              setErrorMessage('');
              setSuccessMessage('');
            }}
          >
            <Text style={styles.buttonText}>
              Back to Requests
            </Text>
          </TouchableOpacity>

          <Text style={styles.sectionTitle}>
            Request Details
          </Text>

          {renderRequest(selectedRequest, false)}
        </>
      ) : (
        <>
          <TouchableOpacity
            style={styles.button}
            disabled={
              isLoading ||
              isProcessing ||
              !authToken?.trim()
            }
            onPress={loadRequests}
          >
            <Text style={styles.buttonText}>
              Refresh Requests
            </Text>
          </TouchableOpacity>

          <View style={styles.filterRow}>
            {filters.map((item) => (
              <TouchableOpacity
                key={item}
                style={[
                  styles.filterButton,
                  filter === item &&
                    styles.activeFilter,
                ]}
                onPress={() => setFilter(item)}
              >
                <Text style={styles.buttonText}>
                  {item.charAt(0).toUpperCase() +
                    item.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {!isLoading &&
            !errorMessage &&
            filteredRequests.length === 0 && (
              <Text style={styles.emptyText}>
                No {filter === 'all' ? '' : filter + ' '}
                requests found.
              </Text>
            )}

          {filteredRequests.map((request) =>
            renderRequest(request, true)
          )}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAF6',
  },

  content: {
    padding: 20,
    paddingBottom: 40,
    width: '100%',
    maxWidth: 780,
    alignSelf: 'center',
  },

  heading: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#303B32',
    marginBottom: 8,
  },

  subtitle: {
    fontSize: 15,
    color: '#666666',
    marginBottom: 20,
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 15,
    color: '#303B32',
  },

  card: {
    backgroundColor: '#FFFFFF',
    padding: 18,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#DDDDDD',
    marginBottom: 15,
  },

  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#303B32',
  },

  detail: {
    fontSize: 14,
    marginBottom: 8,
    color: '#444444',
  },

  status: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#303B32',
    marginBottom: 12,
  },

  button: {
    backgroundColor: '#A7B9A2',
    padding: 13,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },

  buttonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#303B32',
  },

  actionRow: {
    flexDirection: 'row',
    gap: 10,
  },

  actionButton: {
    flex: 1,
    padding: 13,
    borderRadius: 8,
    alignItems: 'center',
  },

  acceptButton: {
    backgroundColor: '#A7B9A2',
  },

  rejectButton: {
    backgroundColor: '#F0C6D1',
  },

  filterRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 20,
  },

  filterButton: {
    padding: 10,
    borderRadius: 8,
    backgroundColor: '#EEEEEE',
  },

  activeFilter: {
    backgroundColor: '#F6DA72',
  },

  disabled: {
    opacity: 0.5,
  },

  error: {
    backgroundColor: '#FCE8E8',
    color: '#923C3C',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },

  success: {
    backgroundColor: '#E8F2E7',
    color: '#315D37',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },

  emptyText: {
    textAlign: 'center',
    color: '#777777',
    marginTop: 20,
  },

  loader: {
    marginVertical: 15,
  },
});
