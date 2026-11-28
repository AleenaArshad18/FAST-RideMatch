
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
  getDriverReliability,
} from './driverReliabilityApi';

import type {
  DriverReliabilityResponse,
} from './driverReliabilityApi';

type DriverReliabilityScreenProps = {
  authToken?: string;
};

export default function DriverReliabilityScreen({
  authToken,
}: DriverReliabilityScreenProps) {
  const [driverId, setDriverId] = useState('');

  const [reliability, setReliability] =
    useState<DriverReliabilityResponse | null>(null);

  const [isLoading, setIsLoading] = useState(false);

  const [errorMessage, setErrorMessage] = useState('');

  // Retrieve reliability information.
  const loadReliability = async () => {
    if (isLoading) {
      return;
    }

    setErrorMessage('');
    setReliability(null);

    if (!authToken?.trim()) {
      setErrorMessage(
        'Verified student sign-in is required.'
      );
      return;
    }

    const id = Number(driverId);

    if (
      !/^\d+$/.test(driverId.trim()) ||
      !Number.isSafeInteger(id) ||
      id <= 0
    ) {
      setErrorMessage(
        'Please enter a valid driver ID.'
      );
      return;
    }

    setIsLoading(true);

    try {
      const result = await getDriverReliability(
        id,
        authToken
      );

      setReliability(result);
    } catch (error) {
      setErrorMessage(
        error instanceof ApiError
          ? error.message
          : 'An unexpected error occurred.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDriverIdChange = (value: string) => {
    setDriverId(value);
    setReliability(null);
    setErrorMessage('');
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      <Text style={styles.heading}>
        Driver Reliability
      </Text>

      <Text style={styles.subtitle}>
        View available reliability information
        for a driver.
      </Text>

      {!authToken?.trim() && (
        <Text style={styles.notice}>
          Verified student sign-in is required
          to view driver reliability information.
        </Text>
      )}

      <Text style={styles.label}>
        Driver ID
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Enter driver ID"
        keyboardType="numeric"
        value={driverId}
        editable={!isLoading}
        onChangeText={handleDriverIdChange}
      />

      <TouchableOpacity
        style={[
          styles.button,
          isLoading && styles.disabled,
        ]}
        disabled={isLoading}
        onPress={loadReliability}
      >
        <Text style={styles.buttonText}>
          {isLoading
            ? 'Loading...'
            : 'View Reliability'}
        </Text>
      </TouchableOpacity>

      {isLoading && (
        <ActivityIndicator
          size="large"
          color="#303B32"
          style={styles.loader}
        />
      )}

      {errorMessage !== '' && (
        <Text style={styles.error}>
          {errorMessage}
        </Text>
      )}

      {reliability && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>
            Driver #{reliability.driver_id}
          </Text>

          <View style={styles.indicator}>
            <Text style={styles.indicatorValue}>
              {reliability.completed_ride_count}
            </Text>

            <Text style={styles.indicatorLabel}>
              Completed Rides
            </Text>
          </View>

          <View style={styles.indicator}>
            <Text style={styles.indicatorValue}>
              {reliability.average_rating === null
                ? 'Not available'
                : reliability.average_rating.toFixed(1)}
            </Text>

            <Text style={styles.indicatorLabel}>
              Average Rating
            </Text>
          </View>

          <Text style={styles.footerText}>
            Reliability information is based on
            available recorded ride data.
            It does not guarantee future ride safety.
          </Text>
        </View>
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
    backgroundColor: '#A7B9A2',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
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
    padding: 20,
    marginTop: 10,
  },

  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#303B32',
    marginBottom: 18,
  },

  indicator: {
    backgroundColor: '#FAFAF6',
    borderRadius: 10,
    padding: 20,
    alignItems: 'center',
    marginBottom: 12,
  },

  indicatorValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#303B32',
    marginBottom: 6,
  },

  indicatorLabel: {
    fontSize: 14,
    color: '#666666',
  },

  notice: {
    backgroundColor: '#FFF4CE',
    color: '#66551F',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },

  error: {
    backgroundColor: '#FCE8E8',
    color: '#923C3C',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },

  loader: {
    marginVertical: 15,
  },

  footerText: {
    fontSize: 13,
    color: '#858B84',
    textAlign: 'center',
    lineHeight: 20,
    marginTop: 10,
  },
});
