import { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { ApiError } from '../../services/api';
import {
  getPassengerPayments,
  getPassengerPaymentDetails,
  PaymentRecord,
} from './paymentsApi';

type Props = {
  authToken?: string;
};

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

export default function PassengerPaymentsScreen({
  authToken,
}: Props) {
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRequestId, setSelectedRequestId] = useState<number | null>(null);
  const [selectedPayment, setSelectedPayment] = useState<PaymentRecord | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  const loadPayments = useCallback(async () => {
    if (!authToken?.trim()) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const data = await getPassengerPayments(authToken);
      setPayments(data);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : 'Unable to load your payment history.'
      );
    } finally {
      setLoading(false);
    }
  }, [authToken]);

  useEffect(() => {
    void loadPayments();
  }, [loadPayments]);

  const formatDate = (value: string) => {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString('en-PK', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const formatAmount = (amount: number) =>
    `Rs. ${Number(amount).toLocaleString('en-PK')}`;

  const getStatusStyle = (status: PaymentRecord['status']) => {
    if (status === 'paid') return styles.paidBadge;
    if (status === 'failed') return styles.failedBadge;
    return styles.pendingBadge;
  };

  const openDetails = async (payment: PaymentRecord) => {
    if (selectedRequestId === payment.request_id) {
      setSelectedRequestId(null);
      setSelectedPayment(null);
      return;
    }

    if (!authToken?.trim()) return;

    setSelectedRequestId(payment.request_id);
    setSelectedPayment(null);
    setDetailError('');
    setDetailLoading(true);

    try {
      const details = await getPassengerPaymentDetails(
        payment.request_id,
        authToken
      );
      setSelectedPayment(details);
    } catch (err) {
      setDetailError(
        err instanceof ApiError
          ? err.message
          : 'Unable to load payment details.'
      );
    } finally {
      setDetailLoading(false);
    }
  };

  const renderPayment = (payment: PaymentRecord) => {
    const isSelected = selectedRequestId === payment.request_id;

    return (
      <View key={payment.id} style={styles.paymentCard}>
        <View style={styles.cardTop}>
          <Text style={styles.requestId}>
            PAYMENT #{payment.id}
          </Text>
          <View style={[styles.statusBadge, getStatusStyle(payment.status)]}>
            <Text style={styles.statusText}>
              {payment.status.toUpperCase()}
            </Text>
          </View>
        </View>

        <View style={styles.route}>
          <View style={styles.routeDots}>
            <View style={styles.startDot} />
            <View style={styles.routeLine} />
            <View style={styles.endDot} />
          </View>

          <View style={styles.routeText}>
            <Text style={styles.routeLabel}>FROM</Text>
            <Text style={styles.routePlace}>{payment.start_area}</Text>

            <View style={styles.routeGap} />

            <Text style={styles.routeLabel}>TO</Text>
            <Text style={styles.routePlace}>{payment.destination_area}</Text>
          </View>
        </View>

        <View style={styles.divider} />

        <Text style={styles.infoLabel}>DEPARTURE</Text>
        <Text style={styles.infoValue}>
          {formatDate(payment.departure_time)}
        </Text>

        <View style={styles.amountRow}>
          <View>
            <Text style={styles.infoLabel}>YOUR SHARE</Text>
            <Text style={styles.amount}>
              {formatAmount(payment.amount)}
            </Text>
          </View>

          <View style={styles.pkrBadge}>
            <Text style={styles.pkrText}>PKR</Text>
          </View>
        </View>

        <Pressable
          style={({ pressed }) => [
            styles.detailsButton,
            pressed && styles.pressed,
          ]}
          onPress={() => void openDetails(payment)}
        >
          <Text style={styles.detailsButtonText}>
            {isSelected ? 'Hide details' : 'View payment details'}
          </Text>
        </Pressable>

        {isSelected ? (
          <View style={styles.detailsPanel}>
            {detailLoading ? (
              <ActivityIndicator color="#647D69" />
            ) : detailError ? (
              <Text style={styles.errorText}>{detailError}</Text>
            ) : selectedPayment ? (
              <>
                <DetailRow
                  label="Request ID"
                  value={`#${selectedPayment.request_id}`}
                />
                <DetailRow
                  label="Ride listing"
                  value={`#${selectedPayment.listing_id}`}
                />
                <DetailRow
                  label="Total ride fare"
                  value={formatAmount(selectedPayment.total_fare)}
                />
                <DetailRow
                  label="Accepted passengers"
                  value={String(selectedPayment.accepted_passengers)}
                />
                <DetailRow
                  label="Your payment"
                  value={formatAmount(selectedPayment.amount)}
                />
                <DetailRow
                  label="Created"
                  value={formatDate(selectedPayment.created_at)}
                />
                <DetailRow
                  label="Last updated"
                  value={formatDate(selectedPayment.updated_at)}
                />
              </>
            ) : null}
          </View>
        ) : null}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        contentContainerStyle={styles.container}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <Text style={styles.brand}>FAST RIDEMATCH</Text>
          <Text style={styles.title}>My Payments</Text>
          <Text style={styles.subtitle}>
            Keep track of your shared ride expenses.
          </Text>
        </View>

        <View style={styles.hero}>
          <Text style={styles.heroTag}>YOUR JOURNEY, YOUR RECORDS</Text>
          <Text style={styles.heroTitle}>Payment history</Text>
          <Text style={styles.heroDescription}>
            All your accepted ride payment records in one place.
          </Text>
        </View>

        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionTitle}>Your transactions</Text>
            <Text style={styles.sectionSubtitle}>
              {payments.length} {payments.length === 1 ? 'record' : 'records'}
            </Text>
          </View>

          <Pressable
            onPress={() => void loadPayments()}
            disabled={loading || !authToken?.trim()}
            style={styles.refreshButton}
          >
            <Text style={styles.refreshText}>Refresh</Text>
          </Pressable>
        </View>

        {!authToken?.trim() ? (
          <View style={styles.stateCard}>
            <Text style={styles.stateEmoji}>🔒</Text>
            <Text style={styles.stateTitle}>Sign-in required</Text>
            <Text style={styles.stateDescription}>
              Please sign in with your verified student account to view your
              payment history.
            </Text>
          </View>
        ) : loading ? (
          <View style={styles.stateCard}>
            <ActivityIndicator size="large" color="#647D69" />
            <Text style={styles.stateTitle}>Loading payments...</Text>
          </View>
        ) : error ? (
          <View style={styles.errorCard}>
            <Text style={styles.stateTitle}>Couldn't load payments</Text>
            <Text style={styles.errorText}>{error}</Text>
            <Pressable
              style={styles.retryButton}
              onPress={() => void loadPayments()}
            >
              <Text style={styles.retryText}>Try again</Text>
            </Pressable>
          </View>
        ) : payments.length === 0 ? (
          <View style={styles.stateCard}>
            <Text style={styles.stateEmoji}>🧾</Text>
            <Text style={styles.stateTitle}>No payment records yet</Text>
            <Text style={styles.stateDescription}>
              Payment records will appear here when your ride requests are
              accepted.
            </Text>
          </View>
        ) : (
          payments.map(renderPayment)
        )}

        <Text style={styles.footer}>
          Ride together. Keep everything in check. 💚
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  container: {
    paddingHorizontal: 22,
    paddingTop: 20,
    paddingBottom: 40,
    maxWidth: 650,
    width: '100%',
    alignSelf: 'center',
  },
  header: {
    marginBottom: 22,
  },
  brand: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 2,
    color: COLORS.muted,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: COLORS.text,
    marginTop: 8,
  },
  subtitle: {
    fontSize: 13,
    color: COLORS.muted,
    marginTop: 5,
  },
  hero: {
    backgroundColor: COLORS.yellow,
    borderRadius: 22,
    padding: 21,
    marginBottom: 27,
  },
  heroTag: {
    color: '#66572F',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1,
  },
  heroTitle: {
    color: COLORS.text,
    fontSize: 23,
    fontWeight: '800',
    marginTop: 10,
  },
  heroDescription: {
    color: '#66572F',
    fontSize: 12,
    lineHeight: 18,
    marginTop: 6,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 19,
    fontWeight: '800',
    color: COLORS.text,
  },
  sectionSubtitle: {
    fontSize: 12,
    color: COLORS.muted,
    marginTop: 4,
  },
  refreshButton: {
    backgroundColor: COLORS.sage,
    paddingHorizontal: 15,
    paddingVertical: 9,
    borderRadius: 10,
  },
  refreshText: {
    color: '#263B2B',
    fontSize: 12,
    fontWeight: '800',
  },
  paymentCard: {
    backgroundColor: COLORS.white,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: COLORS.border,
    padding: 17,
    marginBottom: 14,
  },
  cardTop: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  requestId: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.8,
    color: COLORS.muted,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  paidBadge: {
    backgroundColor: '#E1EFE0',
  },
  pendingBadge: {
    backgroundColor: '#FFF1C9',
  },
  failedBadge: {
    backgroundColor: '#F9DEDE',
  },
  statusText: {
    fontSize: 9,
    fontWeight: '800',
    color: COLORS.text,
  },
  route: {
    flexDirection: 'row',
    marginTop: 20,
  },
  routeDots: {
    width: 18,
    alignItems: 'center',
    paddingTop: 4,
  },
  startDot: {
    width: 11,
    height: 11,
    borderRadius: 6,
    backgroundColor: COLORS.sage,
  },
  routeLine: {
    height: 30,
    width: 2,
    backgroundColor: '#DDE4D9',
  },
  endDot: {
    width: 11,
    height: 11,
    borderRadius: 3,
    backgroundColor: COLORS.pink,
  },
  routeText: {
    flex: 1,
    marginLeft: 10,
  },
  routeLabel: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 1,
    color: COLORS.muted,
  },
  routePlace: {
    fontSize: 15,
    fontWeight: '800',
    color: COLORS.text,
    marginTop: 3,
  },
  routeGap: {
    height: 15,
  },
  divider: {
    height: 1,
    backgroundColor: COLORS.border,
    marginVertical: 15,
  },
  infoLabel: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.8,
    color: COLORS.muted,
  },
  infoValue: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.text,
    marginTop: 5,
  },
  amountRow: {
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    marginTop: 15,
    paddingTop: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  amount: {
    fontSize: 23,
    fontWeight: '800',
    color: COLORS.text,
    marginTop: 4,
  },
  pkrBadge: {
    backgroundColor: '#FFF3D1',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 9,
  },
  pkrText: {
    color: '#66572F',
    fontSize: 11,
    fontWeight: '800',
  },
  detailsButton: {
    marginTop: 15,
    paddingVertical: 12,
    alignItems: 'center',
    backgroundColor: '#F1F4EF',
    borderRadius: 11,
  },
  detailsButtonText: {
    color: '#526C50',
    fontSize: 12,
    fontWeight: '800',
  },
  detailsPanel: {
    marginTop: 13,
    padding: 13,
    borderRadius: 12,
    backgroundColor: '#F8F9F5',
    gap: 12,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  detailLabel: {
    color: COLORS.muted,
    fontSize: 11,
    flex: 1,
  },
  detailValue: {
    color: COLORS.text,
    fontSize: 11,
    fontWeight: '700',
    flex: 1,
    textAlign: 'right',
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
    fontSize: 32,
    marginBottom: 8,
  },
  stateTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: COLORS.text,
    textAlign: 'center',
  },
  stateDescription: {
    color: COLORS.muted,
    fontSize: 13,
    lineHeight: 20,
    textAlign: 'center',
    marginTop: 8,
  },
  errorCard: {
    backgroundColor: '#FCE7E7',
    borderRadius: 18,
    padding: 20,
    alignItems: 'center',
  },
  errorText: {
    color: COLORS.red,
    fontSize: 12,
    lineHeight: 19,
    textAlign: 'center',
    marginTop: 8,
  },
  retryButton: {
    backgroundColor: COLORS.sage,
    borderRadius: 10,
    paddingHorizontal: 20,
    paddingVertical: 11,
    marginTop: 14,
  },
  retryText: {
    color: COLORS.text,
    fontSize: 12,
    fontWeight: '800',
  },
  pressed: {
    opacity: 0.7,
  },
  footer: {
    textAlign: 'center',
    color: COLORS.muted,
    fontSize: 12,
    marginTop: 25,
  },
});
