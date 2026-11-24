
import React from 'react';
import { useLocalSearchParams } from 'expo-router';
import { View, Text, StyleSheet } from 'react-native';

import OfferRideScreen from '../features/driverListing/OfferRideScreen';

export default function EditRidePage() {
  const { listingId } = useLocalSearchParams<{
    listingId?: string;
  }>();

  const parsedListingId = Number(listingId);

  if (
    !listingId ||
    !Number.isSafeInteger(parsedListingId) ||
    parsedListingId <= 0
  ) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>
          Please provide a valid ride listing ID.
        </Text>
      </View>
    );
  }

  return <OfferRideScreen listingId={parsedListingId} />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAF6',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },

  message: {
    fontSize: 16,
    color: '#303B32',
    textAlign: 'center',
  },
});
