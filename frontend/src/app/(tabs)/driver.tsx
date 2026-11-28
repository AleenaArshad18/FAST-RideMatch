import { useRouter } from 'expo-router';
import {
  ScrollView,
  StyleSheet,
  Text,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function DriverDashboard() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>

        <Text style={styles.title}>
          Driver Dashboard
        </Text>

        <Text style={styles.subtitle}>
          Manage your rides and passenger requests.
        </Text>

        <Pressable
          style={styles.button}
          onPress={() => router.push('/offer-ride')}
        >
          <Text style={styles.buttonTitle}>
            Offer a Ride
          </Text>

          <Text style={styles.description}>
            Create and publish a new ride listing.
          </Text>
        </Pressable>

        <Pressable
          style={styles.button}
          onPress={() => router.push('/driver-requests')}
        >
          <Text style={styles.buttonTitle}>
            Passenger Requests
          </Text>

          <Text style={styles.description}>
            View, accept or reject passenger requests.
          </Text>
        </Pressable>

        <Pressable
          style={styles.button}
          onPress={() => router.push('/ride-lifecycle')}
        >
          <Text style={styles.buttonTitle}>
            Manage Ride Lifecycle
          </Text>

          <Text style={styles.description}>
            Cancel or complete rides and view ride history.
          </Text>
        </Pressable>

        <Pressable
          style={styles.button}
          onPress={() => router.push('/driver-reliability')}
        >
          <Text style={styles.buttonTitle}>
            Driver Reliability
          </Text>

          <Text style={styles.description}>
            View completed rides and available ratings.
          </Text>
        </Pressable>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FAFAF6',
  },

  container: {
    padding: 24,
    paddingTop: 90,
    paddingBottom: 40,
    width: '100%',
    maxWidth: 650,
    alignSelf: 'center',
  },

  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#303B32',
    marginBottom: 8,
  },

  subtitle: {
    fontSize: 15,
    color: '#778078',
    marginBottom: 24,
  },

  button: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#DDE3D9',
    borderRadius: 12,
    padding: 20,
    marginBottom: 14,
  },

  buttonTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#303B32',
    marginBottom: 6,
  },

  description: {
    fontSize: 14,
    color: '#778078',
    lineHeight: 20,
  },
});