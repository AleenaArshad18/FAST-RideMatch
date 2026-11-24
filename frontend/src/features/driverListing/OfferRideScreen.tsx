
import React, { useEffect, useState } from 'react';
import {
  Platform,
  ScrollView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

// Local backend URL for Chrome.
// Android emulators and physical devices need a different host.
const API_BASE_URL = 'http://127.0.0.1:8000';

type OfferRideScreenProps = {
  // These must come from the team's trusted login system.
  driverId?: number;
  authToken?: string;

  // Omit listingId to create a ride.
  // Supply listingId to edit an existing ride.
  listingId?: number;
};

type RideListing = {
  id: number;
  driver_id: number;
  start_area: string;
  destination_area: string;
  departure_time: string;
  available_seats: number;
  vehicle_details: string;
  fare: number;
};

export default function OfferRideScreen({
  driverId,
  authToken,
  listingId,
}: OfferRideScreenProps) {
  const isEditMode =
    listingId !== undefined &&
    Number.isSafeInteger(listingId) &&
    listingId > 0;

  const [startArea, setStartArea] = useState('');
  const [destination, setDestination] = useState('');

  const [departureDate, setDepartureDate] =
    useState<Date | null>(null);

  const [departureTime, setDepartureTime] =
    useState<Date | null>(null);

  const [availableSeats, setAvailableSeats] = useState('');
  const [vehicleDetails, setVehicleDetails] = useState('');
  const [fare, setFare] = useState('');

  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);

  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingListing, setIsLoadingListing] = useState(false);
  const [listingLoaded, setListingLoaded] = useState(false);

  const clearFeedback = () => {
    setErrorMessage('');
    setSuccessMessage('');
  };

  const updateField = (
    setter: React.Dispatch<React.SetStateAction<string>>,
    value: string
  ) => {
    setter(value);
    clearFeedback();
  };

  const clearForm = () => {
    setStartArea('');
    setDestination('');
    setDepartureDate(null);
    setDepartureTime(null);
    setAvailableSeats('');
    setVehicleDetails('');
    setFare('');
    setListingLoaded(false);
    clearFeedback();
  };

  // Load existing ride information when editing.
  useEffect(() => {
    if (!isEditMode) {
      clearForm();
      return;
    }

    let cancelled = false;

    const loadListing = async () => {
      setIsLoadingListing(true);
      setListingLoaded(false);
      setErrorMessage('');
      setSuccessMessage('');

      try {
        const response = await fetch(
          `${API_BASE_URL}/ride-listings/${listingId}`
        );

        if (response.status === 404) {
          if (!cancelled) {
            setErrorMessage('Ride listing not found.');
          }
          return;
        }

        if (!response.ok) {
          throw new Error(
            `Server returned ${response.status}`
          );
        }

        const listing: RideListing = await response.json();

        if (cancelled) {
          return;
        }

        const departure = new Date(listing.departure_time);

        if (Number.isNaN(departure.getTime())) {
          setErrorMessage(
            'The saved departure date and time are invalid.'
          );
          return;
        }

        setStartArea(listing.start_area);
        setDestination(listing.destination_area);

        setDepartureDate(new Date(departure));
        setDepartureTime(new Date(departure));

        setAvailableSeats(String(listing.available_seats));
        setVehicleDetails(listing.vehicle_details);
        setFare(String(listing.fare));

        setListingLoaded(true);
      } catch (error) {
        console.error('Ride loading error:', error);

        if (!cancelled) {
          setErrorMessage(
            'Could not load the ride listing. ' +
            'Please check that FastAPI is running.'
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoadingListing(false);
        }
      }
    };

    loadListing();

    return () => {
      cancelled = true;
    };
  }, [isEditMode, listingId]);

  // Combine the selected date and time.
  const getDepartureDateTime = (): Date | null => {
    if (!departureDate || !departureTime) {
      return null;
    }

    const combined = new Date(
      departureDate.getFullYear(),
      departureDate.getMonth(),
      departureDate.getDate(),
      departureTime.getHours(),
      departureTime.getMinutes(),
      0,
      0
    );

    return Number.isNaN(combined.getTime())
      ? null
      : combined;
  };

  // Format for FastAPI with the device's timezone offset.
  const formatForBackend = (date: Date): string => {
    const pad = (value: number) =>
      String(value).padStart(2, '0');

    const offsetMinutes = -date.getTimezoneOffset();
    const sign = offsetMinutes >= 0 ? '+' : '-';

    const offsetHours = Math.floor(
      Math.abs(offsetMinutes) / 60
    );

    const offsetMins = Math.abs(offsetMinutes) % 60;

    return (
      `${date.getFullYear()}-` +
      `${pad(date.getMonth() + 1)}-` +
      `${pad(date.getDate())}` +
      `T${pad(date.getHours())}:` +
      `${pad(date.getMinutes())}:00` +
      `${sign}${pad(offsetHours)}:${pad(offsetMins)}`
    );
  };

  // Validate ride details before submitting.
  const validateRide = (): string | null => {
    const start = startArea.trim();
    const end = destination.trim();

    if (!start) {
      return 'Please enter your starting location.';
    }

    if (!end) {
      return 'Please enter your destination.';
    }

    if (start.toLowerCase() === end.toLowerCase()) {
      return (
        'Starting location and destination ' +
        'must be different.'
      );
    }

    if (!departureDate) {
      return 'Please select a departure date.';
    }

    if (!departureTime) {
      return 'Please select a departure time.';
    }

    const departure = getDepartureDateTime();

    if (!departure || departure.getTime() <= Date.now()) {
      return 'Departure date and time must be in the future.';
    }

    const seatsInput = availableSeats.trim();
    const seatsNumber = Number(seatsInput);

    if (
      !/^\d+$/.test(seatsInput) ||
      !Number.isSafeInteger(seatsNumber) ||
      seatsNumber <= 0
    ) {
      return 'Available seats must be a positive whole number.';
    }

    if (!vehicleDetails.trim()) {
      return 'Please enter your vehicle details.';
    }

    const fareInput = fare.trim();
    const fareNumber = Number(fareInput);

    if (
      !/^\d+(\.\d+)?$/.test(fareInput) ||
      !Number.isFinite(fareNumber)
    ) {
      return 'Fare must be a valid nonnegative number.';
    }

    return null;
  };

  // Publish a new ride or update an existing one.
  const handleSubmit = async () => {
    if (isSubmitting || isLoadingListing) {
      return;
    }

    clearFeedback();

    if (isEditMode && !listingLoaded) {
      setErrorMessage(
        'The existing ride must be loaded before editing.'
      );
      return;
    }

    const validationError = validateRide();

    if (validationError) {
      setErrorMessage(validationError);
      return;
    }

    const departure = getDepartureDateTime();

    if (!departure) {
      setErrorMessage(
        'Please select your departure date and time.'
      );
      return;
    }

    // Never invent a driver ID or authentication token.
    if (
      driverId === undefined ||
      !Number.isSafeInteger(driverId) ||
      driverId <= 0 ||
      !authToken
    ) {
      setErrorMessage(
        'Your ride details are valid, but verified student ' +
        'sign-in is not connected yet. ' +
        (isEditMode
          ? 'Updating is unavailable.'
          : 'Publishing is unavailable.')
      );
      return;
    }

    const rideDetails = {
      start_area: startArea.trim(),
      destination_area: destination.trim(),
      departure_time: formatForBackend(departure),
      available_seats: Number(availableSeats),
      vehicle_details: vehicleDetails.trim(),
      fare: Number(fare),
    };

    // Creating requires driver_id.
    // Editing deliberately excludes driver_id.
    const requestBody = isEditMode
      ? rideDetails
      : {
          driver_id: driverId,
          ...rideDetails,
        };

    const endpoint = isEditMode
      ? `${API_BASE_URL}/ride-listings/${listingId}`
      : `${API_BASE_URL}/ride-listings`;

    const method = isEditMode ? 'PUT' : 'POST';

    setIsSubmitting(true);

    try {
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify(requestBody),
      });

      const result = await response.json().catch(() => null);

      if (response.ok) {
        if (isEditMode) {
          setSuccessMessage(
            'Ride updated successfully!'
          );
        } else if (response.status === 201) {
          const createdListingId = result?.id;

          setSuccessMessage(
            createdListingId !== undefined
              ? `Ride published successfully! Listing ID: ${createdListingId}`
              : 'Ride published successfully!'
          );
        } else {
          setErrorMessage(
            'The server returned an unexpected response.'
          );
        }

        return;
      }

      if (response.status === 503) {
        setErrorMessage(
          isEditMode
            ? 'Driver ownership verification is not ' +
              'configured on the backend yet. ' +
              'Updating is unavailable.'
            : 'Student verification is not configured ' +
              'on the backend yet. Publishing is unavailable.'
        );
        return;
      }

      if (response.status === 401) {
        setErrorMessage(
          'Your session is not authenticated. ' +
          'Please sign in again.'
        );
        return;
      }

      if (response.status === 403) {
        setErrorMessage(
          isEditMode
            ? 'You are not authorized to edit this ride.'
            : 'You are not authorized to publish rides.'
        );
        return;
      }

      if (response.status === 404) {
        setErrorMessage('Ride listing not found.');
        return;
      }

      if (
        response.status === 400 ||
        response.status === 422
      ) {
        const detail = result?.detail;

        setErrorMessage(
          typeof detail === 'string'
            ? detail
            : 'The backend rejected some ride details. ' +
              'Please review your form.'
        );
        return;
      }

      setErrorMessage(
        `Unable to ${isEditMode ? 'update' : 'publish'} ` +
        `your ride. Server returned ${response.status}.`
      );
    } catch (error) {
      console.error('Ride submission error:', error);

      setErrorMessage(
        'Could not connect to the backend. ' +
        'Please check that FastAPI is running ' +
        'and browser access is configured.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (date: Date): string =>
    date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });

  const formatTime = (date: Date): string =>
    date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });

  // Date and time inputs for the web browser.
  const renderWebDateTimeInputs = () => {
    if (Platform.OS !== 'web') {
      return null;
    }

    const dateValue = departureDate
      ? `${departureDate.getFullYear()}-${String(
          departureDate.getMonth() + 1
        ).padStart(2, '0')}-${String(
          departureDate.getDate()
        ).padStart(2, '0')}`
      : '';

    const timeValue = departureTime
      ? `${String(
          departureTime.getHours()
        ).padStart(2, '0')}:${String(
          departureTime.getMinutes()
        ).padStart(2, '0')}`
      : '';

    return (
      <View>
        <Text style={styles.label}>Departure Date</Text>

        <View style={styles.webInputWrapper}>
          {React.createElement('input', {
            type: 'date',
            value: dateValue,

            onChange: (event: any) => {
              const value = event.target.value;

              if (!value) {
                setDepartureDate(null);
              } else {
                const [year, month, day] = value
                  .split('-')
                  .map(Number);

                setDepartureDate(
                  new Date(year, month - 1, day)
                );
              }

              clearFeedback();
            },

            style: {
              width: '100%',
              border: 'none',
              background: 'transparent',
              fontSize: 15,
              color: '#303B32',
              outline: 'none',
              fontFamily: 'inherit',
              colorScheme: 'light',
            },
          })}
        </View>

        <Text style={styles.label}>Departure Time</Text>

        <View style={styles.webInputWrapper}>
          {React.createElement('input', {
            type: 'time',
            value: timeValue,

            onChange: (event: any) => {
              const value = event.target.value;

              if (!value) {
                setDepartureTime(null);
              } else {
                const [hours, minutes] = value
                  .split(':')
                  .map(Number);

                const selectedTime = new Date();

                selectedTime.setHours(
                  hours,
                  minutes,
                  0,
                  0
                );

                setDepartureTime(selectedTime);
              }

              clearFeedback();
            },

            style: {
              width: '100%',
              border: 'none',
              background: 'transparent',
              fontSize: 15,
              color: '#303B32',
              outline: 'none',
              fontFamily: 'inherit',
              colorScheme: 'light',
            },
          })}
        </View>
      </View>
    );
  };

  // Native pickers for Android and iOS.
  const renderNativeDateTimeInputs = () => {
    if (Platform.OS === 'web') {
      return null;
    }

    return (
      <View>
        <Text style={styles.label}>Departure Date</Text>

        <TouchableOpacity
          style={styles.input}
          onPress={() => setShowDatePicker(true)}
        >
          <Text
            style={
              departureDate
                ? styles.valueText
                : styles.placeholderText
            }
          >
            {departureDate
              ? formatDate(departureDate)
              : 'Select a date 📅'}
          </Text>
        </TouchableOpacity>

        <Text style={styles.label}>Departure Time</Text>

        <TouchableOpacity
          style={styles.input}
          onPress={() => setShowTimePicker(true)}
        >
          <Text
            style={
              departureTime
                ? styles.valueText
                : styles.placeholderText
            }
          >
            {departureTime
              ? formatTime(departureTime)
              : 'Select a time 🕒'}
          </Text>
        </TouchableOpacity>

        {showDatePicker && (
          <DateTimePicker
            value={departureDate ?? new Date()}
            mode="date"
            minimumDate={new Date()}
            onChange={(event, selectedDate) => {
              setShowDatePicker(false);

              if (
                event.type === 'set' &&
                selectedDate
              ) {
                setDepartureDate(selectedDate);
                clearFeedback();
              }
            }}
          />
        )}

        {showTimePicker && (
          <DateTimePicker
            value={departureTime ?? new Date()}
            mode="time"
            is24Hour={false}
            onChange={(event, selectedTime) => {
              setShowTimePicker(false);

              if (
                event.type === 'set' &&
                selectedTime
              ) {
                setDepartureTime(selectedTime);
                clearFeedback();
              }
            }}
          />
        )}
      </View>
    );
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      keyboardShouldPersistTaps="handled"
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.eyebrow}>
          TRAVEL TOGETHER. RIDE SMART.
        </Text>

        <Text style={styles.heading}>
          {isEditMode
            ? 'Edit Your Ride 🚗'
            : 'Offer a Ride 🚗'}
        </Text>

        <Text style={styles.subtitle}>
          {isEditMode
            ? 'Update the details of your existing ride.'
            : 'Share your journey with fellow students.'}
        </Text>
      </View>

      {/* Loading existing ride */}
      {isLoadingListing && (
        <View style={styles.loadingCard}>
          <ActivityIndicator
            size="small"
            color="#303B32"
          />
          <Text style={styles.loadingText}>
            Loading ride details...
          </Text>
        </View>
      )}

      {/* Route information */}
      {(!isEditMode || listingLoaded) && (
        <>
          <View style={styles.card}>
            <View style={styles.sectionHeader}>
              <View style={styles.sageIcon}>
                <Text style={styles.iconText}>📍</Text>
              </View>

              <View style={styles.sectionHeadingGroup}>
                <Text style={styles.sectionEyebrow}>
                  STEP 01
                </Text>

                <Text style={styles.sectionTitle}>
                  Your Route
                </Text>
              </View>
            </View>

            <Text style={styles.label}>
              Starting Location
            </Text>

            <TextInput
              style={styles.input}
              placeholder="e.g. FAST University"
              placeholderTextColor="#858B84"
              value={startArea}
              onChangeText={(value) =>
                updateField(setStartArea, value)
              }
            />

            <Text style={styles.label}>
              Destination
            </Text>

            <TextInput
              style={styles.input}
              placeholder="Where are you heading?"
              placeholderTextColor="#858B84"
              value={destination}
              onChangeText={(value) =>
                updateField(setDestination, value)
              }
            />
          </View>

          {/* Ride information */}
          <View style={styles.card}>
            <View style={styles.sectionHeader}>
              <View style={styles.pinkIcon}>
                <Text style={styles.iconText}>🚙</Text>
              </View>

              <View style={styles.sectionHeadingGroup}>
                <Text style={styles.sectionEyebrow}>
                  STEP 02
                </Text>

                <Text style={styles.sectionTitle}>
                  Ride Details
                </Text>
              </View>
            </View>

            {renderWebDateTimeInputs()}
            {renderNativeDateTimeInputs()}

            <Text style={styles.label}>
              Available Seats
            </Text>

            <TextInput
              style={styles.input}
              placeholder="e.g. 3"
              placeholderTextColor="#858B84"
              keyboardType="number-pad"
              value={availableSeats}
              onChangeText={(value) =>
                updateField(setAvailableSeats, value)
              }
            />

            <Text style={styles.label}>
              Vehicle Details
            </Text>

            <TextInput
              style={styles.input}
              placeholder="e.g. Honda Civic - White"
              placeholderTextColor="#858B84"
              value={vehicleDetails}
              onChangeText={(value) =>
                updateField(setVehicleDetails, value)
              }
            />

            <Text style={styles.label}>
              Fare Per Seat (PKR)
            </Text>

            <TextInput
              style={styles.input}
              placeholder="e.g. 250"
              placeholderTextColor="#858B84"
              keyboardType="decimal-pad"
              value={fare}
              onChangeText={(value) =>
                updateField(setFare, value)
              }
            />
          </View>
        </>
      )}

      {/* Error message */}
      {errorMessage !== '' && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>
            ⚠️ {errorMessage}
          </Text>
        </View>
      )}

      {/* Success message */}
      {successMessage !== '' && (
        <View style={styles.successBox}>
          <Text style={styles.successText}>
            ✓ {successMessage}
          </Text>
        </View>
      )}

      {/* Submit button */}
      {(!isEditMode || listingLoaded) && (
        <TouchableOpacity
          style={[
            styles.publishButton,
            isSubmitting && styles.disabledButton,
          ]}
          activeOpacity={0.8}
          onPress={handleSubmit}
          disabled={isSubmitting || isLoadingListing}
        >
          {isSubmitting ? (
            <View style={styles.loadingRow}>
              <ActivityIndicator
                color="#303B32"
                size="small"
              />

              <Text style={styles.publishButtonText}>
                {isEditMode
                  ? 'Updating...'
                  : 'Publishing...'}
              </Text>
            </View>
          ) : (
            <Text style={styles.publishButtonText}>
              {isEditMode
                ? 'Update Ride'
                : 'Publish Ride'}
            </Text>
          )}
        </TouchableOpacity>
      )}

      <Text style={styles.footerText}>
        {isEditMode
          ? 'Review your changes before updating your ride.'
          : 'Make sure your ride details are correct before publishing.'}
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAF6',
  },

  content: {
    width: '100%',
    maxWidth: 780,
    alignSelf: 'center',
    padding: 24,
    paddingBottom: 50,
  },

  header: {
    backgroundColor: '#F6DA72',
    borderRadius: 28,
    padding: 28,
    marginTop: 20,
    marginBottom: 32,
  },

  eyebrow: {
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 1.5,
    color: '#5D5633',
    marginBottom: 12,
  },

  heading: {
    fontSize: 34,
    fontWeight: '800',
    color: '#303B32',
    lineHeight: 42,
  },

  subtitle: {
    fontSize: 15,
    color: '#666B61',
    marginTop: 10,
    lineHeight: 23,
  },

  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
    marginBottom: 18,
    borderWidth: 1,
    borderColor: '#E8EAE5',
  },

  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },

  sectionHeadingGroup: {
    flex: 1,
  },

  sectionEyebrow: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1.2,
    color: '#777F75',
    marginBottom: 5,
  },

  sectionTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#303B32',
  },

  sageIcon: {
    width: 54,
    height: 54,
    backgroundColor: '#A7B9A2',
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },

  pinkIcon: {
    width: 54,
    height: 54,
    backgroundColor: '#F0C6D1',
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },

  iconText: {
    fontSize: 25,
  },

  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#424B43',
    marginBottom: 8,
  },

  input: {
    backgroundColor: '#FAFAF7',
    borderWidth: 1,
    borderColor: '#E3E7DF',
    borderRadius: 15,
    padding: 15,
    fontSize: 15,
    color: '#303B32',
    marginBottom: 18,
  },

  webInputWrapper: {
    backgroundColor: '#FAFAF7',
    borderWidth: 1,
    borderColor: '#E3E7DF',
    borderRadius: 15,
    padding: 15,
    marginBottom: 18,
  },

  valueText: {
    fontSize: 15,
    color: '#303B32',
  },

  placeholderText: {
    fontSize: 15,
    color: '#858B84',
  },

  loadingCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 24,
    marginBottom: 18,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },

  loadingText: {
    fontSize: 14,
    color: '#424B43',
  },

  errorBox: {
    backgroundColor: '#FCE8E8',
    borderColor: '#E8B6B6',
    borderWidth: 1,
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
  },

  errorText: {
    color: '#923C3C',
    fontSize: 14,
    lineHeight: 21,
  },

  successBox: {
    backgroundColor: '#E8F2E7',
    borderColor: '#B5D2B2',
    borderWidth: 1,
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
  },

  successText: {
    color: '#315D37',
    fontSize: 14,
    lineHeight: 21,
  },

  publishButton: {
    backgroundColor: '#A7B9A2',
    borderRadius: 20,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },

  disabledButton: {
    opacity: 0.65,
  },

  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },

  publishButtonText: {
    color: '#303B32',
    fontSize: 16,
    fontWeight: '800',
  },

  footerText: {
    textAlign: 'center',
    color: '#858B84',
    fontSize: 13,
    marginTop: 18,
    lineHeight: 20,
  },
});
