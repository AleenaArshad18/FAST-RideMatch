
import { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

const COLORS = {
  background: '#FAFAF7',
  white: '#FFFFFF',
  yellow: '#F5D76E',
  sage: '#A9BDA4',
  blue: '#A9D8ED',
  pink: '#F2C5D0',
  text: '#28332D',
  muted: '#778078',
  border: '#ECEEE8',
  red: '#873F3F',
};

type Ride = {
  id: number;
  driver_id: number;
  start_area: string;
  destination_area: string;
  departure_time: string;
  available_seats: number;
  vehicle_details: string;
  fare: number;
};

export default function ExploreScreen() {
  const router = useRouter();

  const [rides, setRides] = useState<Ride[]>([]);
  const [startArea, setStartArea] = useState('');
  const [destinationArea, setDestinationArea] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [minFare, setMinFare] = useState('');
  const [maxFare, setMaxFare] = useState('');
  const [minSeats, setMinSeats] = useState('');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchMessage, setSearchMessage] = useState('');
  const [requestingRideId, setRequestingRideId] = useState<number | null>(null);
  const [requestedRideIds, setRequestedRideIds] = useState<number[]>([]);
  const [requestFeedback, setRequestFeedback] = useState<
    Record<number, { type: 'success' | 'error'; message: string }>
  >({});

  const fetchRides = async (useFilters = false) => {
    try {
      setLoading(true);
      setError('');
      setSearchMessage('');

      const params = new URLSearchParams();

      if (useFilters) {
        if (startArea.trim()) {
          params.append('start_area', startArea.trim());
        }

        if (destinationArea.trim()) {
          params.append('destination_area', destinationArea.trim());
        }

        if (departureDate.trim()) {
          if (!/^\d{4}-\d{2}-\d{2}$/.test(departureDate.trim())) {
            throw new Error('Enter the date in YYYY-MM-DD format.');
          }

          params.append('departure_date', departureDate.trim());
        }

        if (minFare.trim()) {
          const value = Number(minFare);
          if (!Number.isFinite(value) || value < 0) {
            throw new Error('Minimum fare must be a valid non-negative number.');
          }
          params.append('min_fare', minFare.trim());
        }

        if (maxFare.trim()) {
          const value = Number(maxFare);
          if (!Number.isFinite(value) || value < 0) {
            throw new Error('Maximum fare must be a valid non-negative number.');
          }
          params.append('max_fare', maxFare.trim());
        }

        if (minSeats.trim()) {
          const value = Number(minSeats);
          if (!Number.isInteger(value) || value < 1) {
            throw new Error('Minimum seats must be a whole number of at least 1.');
          }
          params.append('min_seats', minSeats.trim());
        }

        if (
          minFare.trim() &&
          maxFare.trim() &&
          Number(minFare) > Number(maxFare)
        ) {
          throw new Error('Minimum fare cannot exceed maximum fare.');
        }
      }

      const query = params.toString();
      const url = `${API_URL}/ride-listings${query ? `?${query}` : ''}`;

      const response = await fetch(url);

      if (!response.ok) {
        const responseData = await response.json().catch(() => null);
        throw new Error(
          responseData?.detail || 'Unable to retrieve available rides.'
        );
      }

      const data: Ride[] = await response.json();
      setRides(data);
      setSearchMessage(
        data.length === 1
          ? '1 ride found'
          : `${data.length} rides found`
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not connect to the RideMatch server.'
      );
      setRides([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchRides();
  }, []);

  const resetFilters = () => {
    setStartArea('');
    setDestinationArea('');
    setDepartureDate('');
    setMinFare('');
    setMaxFare('');
    setMinSeats('');
    void fetchRides();
  };

  const formatDeparture = (value: string) => {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString('en-PK', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const requestRide = async (rideId: number) => {
    setRequestingRideId(rideId);
    setRequestFeedback((current) => {
      const next = { ...current };
      delete next[rideId];
      return next;
    });

    try {
      const response = await fetch(
        `${API_URL}/passenger/requests`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ listing_id: rideId }),
        }
      );

      const responseData = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          responseData?.detail || 'Unable to submit your ride request.'
        );
      }

      setRequestedRideIds((current) =>
        current.includes(rideId) ? current : [...current, rideId]
      );
      setRequestFeedback((current) => ({
        ...current,
        [rideId]: {
          type: 'success',
          message: 'Request submitted. The driver can now review it.',
        },
      }));
    } catch (err) {
      setRequestFeedback((current) => ({
        ...current,
        [rideId]: {
          type: 'error',
          message:
            err instanceof Error
              ? err.message
              : 'Could not connect to the RideMatch server.',
        },
      }));
    } finally {
      setRequestingRideId(null);
    }
  };

  const renderRideCard = (ride: Ride) => (
    <View key={ride.id} style={styles.rideCard}>
      <View style={styles.rideTopRow}>
        <View style={styles.availableBadge}>
          <Text style={styles.availableBadgeText}>AVAILABLE</Text>
        </View>
        <Text style={styles.rideId}>RIDE #{ride.id}</Text>
      </View>

      <View style={styles.routeContainer}>
        <View style={styles.routePoints}>
          <View style={styles.startDot} />
          <View style={styles.routeLine} />
          <View style={styles.destinationDot} />
        </View>

        <View style={styles.routeLabels}>
          <Text style={styles.routeLabel}>FROM</Text>
          <Text style={styles.routePlace}>{ride.start_area}</Text>

          <View style={styles.routeGap} />

          <Text style={styles.routeLabel}>TO</Text>
          <Text style={styles.routePlace}>{ride.destination_area}</Text>
        </View>
      </View>

      <View style={styles.rideDivider} />

      <View style={styles.infoRow}>
        <View style={styles.infoItem}>
          <Text style={styles.infoIcon}>◷</Text>
          <View style={styles.infoTextContainer}>
            <Text style={styles.infoLabel}>DEPARTURE</Text>
            <Text style={styles.infoValue}>
              {formatDeparture(ride.departure_time)}
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.detailsRow}>
        <View style={styles.detailChip}>
          <Text style={styles.detailEmoji}>👥</Text>
          <Text style={styles.detailText}>
            {ride.available_seats}{' '}
            {ride.available_seats === 1 ? 'seat' : 'seats'}
          </Text>
        </View>

        <View style={styles.detailChip}>
          <Text style={styles.detailEmoji}>🚗</Text>
          <Text style={styles.detailText}>{ride.vehicle_details}</Text>
        </View>
      </View>

      <View style={styles.fareRow}>
        <View>
          <Text style={styles.fareLabel}>FARE PER PASSENGER</Text>
          <Text style={styles.fareValue}>
            Rs. {Number(ride.fare).toLocaleString('en-PK')}
          </Text>
        </View>
        <View style={styles.fareIcon}>
          <Text style={styles.fareIconText}>PKR</Text>
        </View>
      </View>

      <Pressable
        style={({ pressed }) => [
          styles.requestButton,
          requestedRideIds.includes(ride.id) && styles.requestButtonSuccess,
          pressed && styles.pressed,
        ]}
        onPress={() => void requestRide(ride.id)}
        disabled={
          requestingRideId !== null ||
          requestedRideIds.includes(ride.id)
        }
      >
        {requestingRideId === ride.id ? (
          <View style={styles.requestLoading}>
            <ActivityIndicator size="small" color="#263B2B" />
            <Text style={styles.requestButtonText}>Submitting...</Text>
          </View>
        ) : (
          <Text style={styles.requestButtonText}>
            {requestedRideIds.includes(ride.id)
              ? 'Request Submitted'
              : 'Request Ride'}
          </Text>
        )}
      </Pressable>

      {requestFeedback[ride.id] ? (
        <Text
          style={[
            styles.requestFeedback,
            requestFeedback[ride.id].type === 'success'
              ? styles.requestSuccess
              : styles.requestError,
          ]}
        >
          {requestFeedback[ride.id].message}
        </Text>
      ) : null}
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.brand}>FAST RIDEMATCH</Text>
            <Text style={styles.greeting}>Find your next ride.</Text>
            <Text style={styles.subtitle}>
              Your journey, shared with others.
            </Text>
          </View>

          <View style={styles.headerIcon}>
            <Text style={styles.headerEmoji}>⌕</Text>
          </View>
        </View>

        {/* Passenger payment history shortcut */}
        <Pressable
          style={({ pressed }) => [
            styles.paymentsLink,
            pressed && styles.pressed,
          ]}
          onPress={() => router.push('/passenger-payments')}
        >
          <View>
            <Text style={styles.paymentsLinkTitle}>My Payments</Text>
            <Text style={styles.paymentsLinkSubtitle}>
              View your fare records and payment status
            </Text>
          </View>
          <Text style={styles.paymentsLinkArrow}>→</Text>
        </Pressable>

        <View style={styles.hero}>
          <View style={styles.heroContent}>
            <Text style={styles.heroTag}>LET'S GET MOVING</Text>
            <Text style={styles.heroTitle}>
              A seat for you,{'\n'}a lighter journey.
            </Text>
            <Text style={styles.heroDescription}>
              Discover rides shared by fellow FAST students.
            </Text>
          </View>
          <Text style={styles.heroEmoji}>🚙</Text>
        </View>

        <View style={styles.sectionHeading}>
          <Text style={styles.sectionTitle}>Find a ride</Text>
          <Text style={styles.sectionSubtitle}>
            Tell us where you're headed.
          </Text>
        </View>

        <View style={styles.filterCard}>
          <Text style={styles.inputLabel}>PICKUP AREA</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. F-10, G-11, FAST Islamabad"
            placeholderTextColor="#A0A79F"
            value={startArea}
            onChangeText={setStartArea}
            autoCapitalize="words"
          />

          <Text style={styles.inputLabel}>DESTINATION</Text>
          <TextInput
            style={styles.input}
            placeholder="Where do you want to go?"
            placeholderTextColor="#A0A79F"
            value={destinationArea}
            onChangeText={setDestinationArea}
            autoCapitalize="words"
          />

          <Text style={styles.inputLabel}>DEPARTURE DATE</Text>
          <TextInput
            style={styles.input}
            placeholder="YYYY-MM-DD (optional)"
            placeholderTextColor="#A0A79F"
            value={departureDate}
            onChangeText={setDepartureDate}
            autoCapitalize="none"
          />

          <View style={styles.twoColumnRow}>
            <View style={styles.halfInput}>
              <Text style={styles.inputLabel}>MIN FARE (PKR)</Text>
              <TextInput
                style={styles.input}
                placeholder="No minimum"
                placeholderTextColor="#A0A79F"
                value={minFare}
                onChangeText={setMinFare}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.halfInput}>
              <Text style={styles.inputLabel}>MAX FARE (PKR)</Text>
              <TextInput
                style={styles.input}
                placeholder="No maximum"
                placeholderTextColor="#A0A79F"
                value={maxFare}
                onChangeText={setMaxFare}
                keyboardType="numeric"
              />
            </View>
          </View>

          <Text style={styles.inputLabel}>MINIMUM AVAILABLE SEATS</Text>
          <TextInput
            style={styles.input}
            placeholder="Any number of seats"
            placeholderTextColor="#A0A79F"
            value={minSeats}
            onChangeText={setMinSeats}
            keyboardType="numeric"
          />

          <Pressable
            style={({ pressed }) => [
              styles.searchButton,
              pressed && styles.pressed,
            ]}
            onPress={() => void fetchRides(true)}
            disabled={loading}
          >
            <Text style={styles.searchButtonText}>
              {loading ? 'Searching...' : 'Search available rides  →'}
            </Text>
          </Pressable>

          <Pressable onPress={resetFilters} style={styles.resetButton}>
            <Text style={styles.resetButtonText}>Reset filters</Text>
          </Pressable>
        </View>

        <View style={styles.resultsHeading}>
          <View>
            <Text style={styles.sectionTitle}>Available rides</Text>
            <Text style={styles.sectionSubtitle}>
              {searchMessage || 'Upcoming rides with available seats'}
            </Text>
          </View>

          <View style={styles.resultsIcon}>
            <Text style={styles.resultsIconText}>↗</Text>
          </View>
        </View>

        {loading ? (
          <View style={styles.stateCard}>
            <ActivityIndicator size="large" color="#647D69" />
            <Text style={styles.stateTitle}>Finding rides...</Text>
            <Text style={styles.stateDescription}>
              Looking for available journeys.
            </Text>
          </View>
        ) : error ? (
          <View style={styles.errorCard}>
            <Text style={styles.stateEmoji}>⚠️</Text>
            <Text style={styles.stateTitle}>Couldn't load rides</Text>
            <Text style={styles.errorText}>{error}</Text>
            <Pressable
              style={styles.retryButton}
              onPress={() => void fetchRides()}
            >
              <Text style={styles.retryButtonText}>Try again</Text>
            </Pressable>
          </View>
        ) : rides.length === 0 ? (
          <View style={styles.stateCard}>
            <Text style={styles.stateEmoji}>🚘</Text>
            <Text style={styles.stateTitle}>No rides found</Text>
            <Text style={styles.stateDescription}>
              Try changing your search filters or check again later.
            </Text>
            <Pressable onPress={resetFilters} style={styles.retryButton}>
              <Text style={styles.retryButtonText}>Clear filters</Text>
            </Pressable>
          </View>
        ) : (
          rides.map(renderRideCard)
        )}

        <Text style={styles.footer}>
          Share the road. Make the journey better. 💚
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  container: {
    paddingHorizontal: 22,
    paddingTop: 14,
    paddingBottom: 35,
    maxWidth: 650,
    width: '100%',
    alignSelf: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  brand: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 2,
    color: COLORS.muted,
  },
  greeting: {
    fontSize: 25,
    fontWeight: '800',
    color: COLORS.text,
    marginTop: 7,
  },
  subtitle: {
    fontSize: 13,
    color: COLORS.muted,
    marginTop: 5,
  },
  headerIcon: {
    width: 48,
    height: 48,
    borderRadius: 16,
    backgroundColor: '#E5EDE1',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerEmoji: {
    fontSize: 30,
    color: COLORS.text,
  },
  paymentsLink: {
    backgroundColor: '#FFF3D1',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#F1E4B9',
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  paymentsLinkTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: COLORS.text,
  },
  paymentsLinkSubtitle: {
    fontSize: 11,
    color: COLORS.muted,
    marginTop: 4,
  },
  paymentsLinkArrow: {
    fontSize: 24,
    fontWeight: '700',
    color: COLORS.text,
    marginLeft: 10,
  },
  hero: {
    backgroundColor: COLORS.blue,
    borderRadius: 25,
    padding: 22,
    minHeight: 180,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    overflow: 'hidden',
  },
  heroContent: {
    flex: 1,
  },
  heroTag: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1.3,
    color: '#405C69',
    marginBottom: 12,
  },
  heroTitle: {
    fontSize: 27,
    lineHeight: 33,
    fontWeight: '800',
    color: COLORS.text,
  },
  heroDescription: {
    fontSize: 12,
    lineHeight: 18,
    color: '#405C69',
    marginTop: 9,
    maxWidth: 230,
  },
  heroEmoji: {
    fontSize: 45,
    marginLeft: 5,
  },
  sectionHeading: {
    marginTop: 28,
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 21,
    fontWeight: '800',
    color: COLORS.text,
  },
  sectionSubtitle: {
    fontSize: 13,
    color: COLORS.muted,
    marginTop: 5,
  },
  filterCard: {
    backgroundColor: COLORS.white,
    borderRadius: 21,
    borderWidth: 1,
    borderColor: COLORS.border,
    padding: 17,
  },
  inputLabel: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1,
    color: COLORS.muted,
    marginTop: 12,
    marginBottom: 7,
  },
  input: {
    minHeight: 47,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    paddingHorizontal: 13,
    paddingVertical: 10,
    color: COLORS.text,
    backgroundColor: '#FDFDFC',
    fontSize: 13,
  },
  twoColumnRow: {
    flexDirection: 'row',
    gap: 10,
  },
  halfInput: {
    flex: 1,
  },
  searchButton: {
    backgroundColor: COLORS.sage,
    borderRadius: 13,
    paddingVertical: 15,
    alignItems: 'center',
    marginTop: 20,
  },
  searchButtonText: {
    color: '#263B2B',
    fontSize: 14,
    fontWeight: '800',
  },
  pressed: {
    opacity: 0.7,
  },
  resetButton: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  resetButtonText: {
    color: COLORS.muted,
    fontSize: 12,
    fontWeight: '700',
  },
  resultsHeading: {
    marginTop: 30,
    marginBottom: 14,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  resultsIcon: {
    width: 39,
    height: 39,
    borderRadius: 13,
    backgroundColor: '#F8EBC0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  resultsIconText: {
    fontSize: 21,
    color: COLORS.text,
  },
  rideCard: {
    backgroundColor: COLORS.white,
    borderRadius: 21,
    borderWidth: 1,
    borderColor: COLORS.border,
    padding: 17,
    marginBottom: 14,
  },
  rideTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  availableBadge: {
    backgroundColor: '#E7F0E4',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  availableBadgeText: {
    color: '#526C50',
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.8,
  },
  rideId: {
    color: COLORS.muted,
    fontSize: 10,
    fontWeight: '700',
  },
  routeContainer: {
    flexDirection: 'row',
    marginTop: 19,
  },
  routePoints: {
    alignItems: 'center',
    width: 18,
    paddingTop: 4,
  },
  startDot: {
    width: 11,
    height: 11,
    borderRadius: 6,
    backgroundColor: COLORS.sage,
  },
  routeLine: {
    width: 2,
    height: 34,
    backgroundColor: '#DDE4D9',
  },
  destinationDot: {
    width: 11,
    height: 11,
    borderRadius: 3,
    backgroundColor: COLORS.pink,
  },
  routeLabels: {
    flex: 1,
    marginLeft: 11,
  },
  routeLabel: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 1,
    color: COLORS.muted,
  },
  routePlace: {
    fontSize: 16,
    fontWeight: '800',
    color: COLORS.text,
    marginTop: 3,
  },
  routeGap: {
    height: 17,
  },
  rideDivider: {
    height: 1,
    backgroundColor: COLORS.border,
    marginVertical: 16,
  },
  infoRow: {
    flexDirection: 'row',
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  infoIcon: {
    fontSize: 22,
    color: COLORS.muted,
    marginRight: 10,
  },
  infoTextContainer: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.8,
    color: COLORS.muted,
  },
  infoValue: {
    fontSize: 13,
    fontWeight: '700',
    color: COLORS.text,
    marginTop: 4,
  },
  detailsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 16,
  },
  detailChip: {
    backgroundColor: '#F5F6F1',
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  detailEmoji: {
    fontSize: 13,
  },
  detailText: {
    color: COLORS.text,
    fontSize: 11,
    fontWeight: '700',
  },
  fareRow: {
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    marginTop: 16,
    paddingTop: 14,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  fareLabel: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.9,
    color: COLORS.muted,
  },
  fareValue: {
    fontSize: 22,
    fontWeight: '800',
    color: COLORS.text,
    marginTop: 4,
  },
  fareIcon: {
    backgroundColor: '#FFF3D1',
    paddingHorizontal: 12,
    paddingVertical: 9,
    borderRadius: 10,
  },
  fareIconText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#66572F',
  },
  requestButton: {
    backgroundColor: COLORS.sage,
    borderRadius: 12,
    minHeight: 48,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 14,
  },
  requestButtonSuccess: {
    backgroundColor: '#DCE8D8',
  },
  requestButtonText: {
    color: '#263B2B',
    fontSize: 14,
    fontWeight: '800',
  },
  requestLoading: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  requestFeedback: {
    fontSize: 12,
    lineHeight: 18,
    marginTop: 9,
  },
  requestSuccess: {
    color: '#526C50',
  },
  requestError: {
    color: COLORS.red,
  },
  stateCard: {
    backgroundColor: COLORS.white,
    borderRadius: 20,
    padding: 25,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  stateEmoji: {
    fontSize: 34,
    marginBottom: 10,
  },
  stateTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: COLORS.text,
    marginTop: 12,
    textAlign: 'center',
  },
  stateDescription: {
    color: COLORS.muted,
    fontSize: 13,
    lineHeight: 20,
    textAlign: 'center',
    marginTop: 7,
  },
  errorCard: {
    backgroundColor: '#FCE7E7',
    borderRadius: 18,
    padding: 20,
    alignItems: 'center',
  },
  errorText: {
    color: COLORS.red,
    fontSize: 13,
    lineHeight: 19,
    textAlign: 'center',
    marginTop: 8,
  },
  retryButton: {
    backgroundColor: COLORS.sage,
    borderRadius: 12,
    paddingHorizontal: 20,
    paddingVertical: 11,
    marginTop: 15,
  },
  retryButtonText: {
    color: '#263B2B',
    fontSize: 12,
    fontWeight: '800',
  },
  footer: {
    textAlign: 'center',
    color: COLORS.muted,
    fontSize: 12,
    marginTop: 25,
  },
});
