
import { useState } from 'react';

import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';

import { ApiError } from '../../services/api';

import {
  cancelRide,
  completeRide,
  getRideLifecycleHistory,
} from './rideLifecycleApi';

import type {
  RideLifecycleHistory,
  RideLifecycleResponse,
} from './rideLifecycleApi';

type RideLifecycleScreenProps = {
  authToken?: string;
};

type RideAction = 'cancel' | 'complete';

export default function RideLifecycleScreen({
  authToken,
}: RideLifecycleScreenProps) {
  const [listingId, setListingId] = useState('');

  const [history, setHistory] =
    useState<RideLifecycleHistory[]>([]);

  const [rideResult, setRideResult] =
    useState<RideLifecycleResponse | null>(null);

  const [pendingAction, setPendingAction] =
    useState<RideAction | null>(null);

  const [isLoading, setIsLoading] = useState(false);

  const [historyLoaded, setHistoryLoaded] =
    useState(false);

  const [errorMessage, setErrorMessage] = useState('');

  const [successMessage, setSuccessMessage] =
    useState('');

  const getErrorMessage = (error: unknown): string => {
    return error instanceof ApiError
      ? error.message
      : 'An unexpected error occurred.';
  };

  // Validate the ride ID and authentication.
  const validateInput = (): number | null => {
    setErrorMessage('');
    setSuccessMessage('');

    if (!authToken?.trim()) {
      setErrorMessage(
        'Verified student sign-in is required.'
      );
      return null;
    }

    const id = Number(listingId);

    if (
      !/^\d+$/.test(listingId.trim()) ||
      !Number.isSafeInteger(id) ||
      id <= 0
    ) {
      setErrorMessage(
        'Please enter a valid ride ID.'
      );
      return null;
    }

    return id;
  };

  // Retrieve lifecycle history.
  const loadHistory = async () => {
    const id = validateInput();

    if (id === null || !authToken || isLoading) {
      return;
    }

    setIsLoading(true);
    setHistoryLoaded(false);
    setHistory([]);

    try {
      const result = await getRideLifecycleHistory(
        id,
        authToken
      );

      setHistory(result);
      setHistoryLoaded(true);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  // Request confirmation before changing status.
  const requestAction = (action: RideAction) => {
    if (isLoading) {
      return;
    }

    const id = validateInput();

    if (id !== null) {
      setPendingAction(action);
    }
  };

  // Execute the confirmed lifecycle action.
  const confirmAction = async () => {
    const id = validateInput();

    if (
      id === null ||
      !authToken ||
      !pendingAction ||
      isLoading
    ) {
      return;
    }

    const action = pendingAction;

    setPendingAction(null);
    setIsLoading(true);

    try {
      const result =
        action === 'cancel'
          ? await cancelRide(id, authToken)
          : await completeRide(id, authToken);

      setRideResult(result);

      setSuccessMessage(
        `Ride #${id} ${result.status} successfully.`
      );

      setHistory([]);
      setHistoryLoaded(false);

      // Refresh lifecycle history after the update.
      try {
        const updatedHistory =
          await getRideLifecycleHistory(
            id,
            authToken
          );

        setHistory(updatedHistory);
        setHistoryLoaded(true);
      } catch {
        setErrorMessage(
          'Ride updated, but history could not be refreshed.'
        );
      }
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const handleListingIdChange = (value: string) => {
    setListingId(value);
    setRideResult(null);
    setHistory([]);
    setHistoryLoaded(false);
    setPendingAction(null);
    setErrorMessage('');
    setSuccessMessage('');
  };

  const isInactive =
    rideResult !== null &&
    rideResult.status !== 'active';

  const actionsDisabled =
    isLoading ||
    pendingAction !== null ||
    isInactive;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      <Text style={styles.heading}>
        Manage Ride
      </Text>

      <Text style={styles.subtitle}>
        Cancel or complete your ride and view its
        lifecycle history.
      </Text>

      {!authToken?.trim() && (
        <Text style={styles.notice}>
          Verified student sign-in is required
          to manage rides.
        </Text>
      )}

      <Text style={styles.label}>
        Ride Listing ID
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Enter ride ID"
        keyboardType="numeric"
        value={listingId}
        editable={
          !isLoading && pendingAction === null
        }
        onChangeText={handleListingIdChange}
      />

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

      {rideResult && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>
            Ride #{rideResult.listing_id}
          </Text>

          <Text style={styles.detail}>
            Driver ID: {rideResult.driver_id}
          </Text>

          <Text style={styles.detail}>
            Status: {rideResult.status.toUpperCase()}
          </Text>
        </View>
      )}

      <TouchableOpacity
        style={[
          styles.button,
          styles.cancelButton,
          actionsDisabled && styles.disabled,
        ]}
        disabled={actionsDisabled}
        onPress={() => requestAction('cancel')}
      >
        <Text style={styles.buttonText}>
          Cancel Ride
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[
          styles.button,
          styles.completeButton,
          actionsDisabled && styles.disabled,
        ]}
        disabled={actionsDisabled}
        onPress={() => requestAction('complete')}
      >
        <Text style={styles.buttonText}>
          Mark as Completed
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[
          styles.button,
          styles.historyButton,
          (isLoading || pendingAction !== null) &&
            styles.disabled,
        ]}
        disabled={
          isLoading || pendingAction !== null
        }
        onPress={loadHistory}
      >
        <Text style={styles.buttonText}>
          View Lifecycle History
        </Text>
      </TouchableOpacity>

      {pendingAction && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>
            Confirm Action
          </Text>

          <Text style={styles.detail}>
            Are you sure you want to{' '}
            {pendingAction === 'cancel'
              ? 'cancel'
              : 'complete'}{' '}
            ride #{listingId}?
          </Text>

          <Text style={styles.detail}>
            This action cannot be reversed.
          </Text>

          <View style={styles.actionRow}>
            <TouchableOpacity
              style={[
                styles.actionButton,
                styles.completeButton,
              ]}
              onPress={confirmAction}
            >
              <Text style={styles.buttonText}>
                Confirm
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.actionButton,
                styles.neutralButton,
              ]}
              onPress={() => setPendingAction(null)}
            >
              <Text style={styles.buttonText}>
                Go Back
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {isLoading && (
        <ActivityIndicator
          size="large"
          color="#303B32"
          style={styles.loader}
        />
      )}

      {historyLoaded && (
        <>
          <Text style={styles.sectionTitle}>
            Lifecycle History
          </Text>

          {history.length === 0 && (
            <Text style={styles.emptyText}>
              No lifecycle changes recorded.
            </Text>
          )}

          {history.map((record) => (
            <View
              key={record.id}
              style={styles.card}
            >
              <Text style={styles.cardTitle}>
                Status Change
              </Text>

              <Text style={styles.detail}>
                Previous status:{' '}
                {record.previous_status}
              </Text>

              <Text style={styles.detail}>
                New status: {record.new_status}
              </Text>

              <Text style={styles.detail}>
                Changed on:{' '}
                {new Date(
                  record.changed_at
                ).toLocaleString()}
              </Text>
            </View>
          ))}
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

  label: {
    fontSize: 15,
    fontWeight: '600',
    color: '#303B32',
    marginBottom: 8,
  },

  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#DDDDDD',
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    marginBottom: 18,
  },

  button: {
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },

  cancelButton: {
    backgroundColor: '#F0C6D1',
  },

  completeButton: {
    backgroundColor: '#A7B9A2',
  },

  historyButton: {
    backgroundColor: '#F6DA72',
  },

  neutralButton: {
    backgroundColor: '#EEEEEE',
  },

  buttonText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#303B32',
  },

  disabled: {
    opacity: 0.5,
  },

  card: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#DDDDDD',
    borderRadius: 12,
    padding: 18,
    marginBottom: 15,
  },

  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#303B32',
    marginBottom: 10,
  },

  detail: {
    fontSize: 14,
    color: '#444444',
    marginBottom: 8,
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#303B32',
    marginVertical: 15,
  },

  actionRow: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 12,
  },

  actionButton: {
    flex: 1,
    padding: 13,
    borderRadius: 8,
    alignItems: 'center',
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

  notice: {
    backgroundColor: '#FFF4CE',
    color: '#66551F',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },

  emptyText: {
    color: '#777777',
    textAlign: 'center',
    marginVertical: 15,
  },

  loader: {
    marginVertical: 15,
  },
});
