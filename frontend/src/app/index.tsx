
import { useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  View,
  Pressable,
  Linking,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';

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
};

const safetySections = [
  {
    number: '01',
    emoji: '🌼',
    title: 'Before your ride',
    description: 'A few things to check before getting on the road.',
    color: COLORS.yellow,
    key: 'before' as const,
  },
  {
    number: '02',
    emoji: '🚗',
    title: 'During your ride',
    description: 'Simple precautions to help keep your journey safe.',
    color: COLORS.sage,
    key: 'during' as const,
  },
  {
    number: '03',
    emoji: '🌸',
    title: 'After your ride',
    description: 'What to do once you have reached your destination.',
    color: COLORS.pink,
    key: 'after' as const,
  },
];

const safetyContent = {
  before: {
    title: 'Before your ride 🌼',
    subtitle: 'A little preparation goes a long way.',
    tips: [
      'Verify the driver and vehicle details before entering.',
      'Share your trip details with someone you trust.',
      'Keep your phone charged and accessible.',
      'Confirm your pickup and drop-off locations.',
      'Avoid sharing unnecessary personal information.',
    ],
  },
  during: {
    title: 'During your ride 🚗',
    subtitle: 'Stay aware throughout your journey.',
    tips: [
      'Wear your seatbelt throughout the ride.',
      'Keep your belongings close to you.',
      'Follow the planned route and stay aware of your surroundings.',
      'Avoid distracting the driver.',
      'Contact someone you trust if you feel uncomfortable.',
    ],
  },
  after: {
    title: 'After your ride 🌸',
    subtitle: 'Finish your journey safely.',
    tips: [
      'Make sure you have collected all your belongings.',
      'Exit the vehicle in a safe and suitable location.',
      'Let someone know when you have reached your destination.',
      'Report any inappropriate or unsafe behaviour.',
      'Share feedback about your ride when appropriate.',
    ],
  },
};

const emergencyContacts = [
  {
    name: 'Police Emergency',
    number: '15',
    description: 'For immediate police assistance.',
    emoji: '👮',
    color: COLORS.blue,
  },
  {
    name: 'Rescue 1122',
    number: '1122',
    description: 'For ambulance, rescue and fire emergencies.',
    emoji: '🚑',
    color: COLORS.pink,
  },
  {
    name: 'Islamabad Traffic Police',
    number: '1915',
    description: 'For traffic-related assistance.',
    emoji: '🚦',
    color: COLORS.yellow,
  },
];

type SectionKey = keyof typeof safetyContent;
type SelectedSection = SectionKey | 'emergency' | null;

export default function HomeScreen() {
  const [selectedSection, setSelectedSection] =
    useState<SelectedSection>(null);

  const selectedContent =
    selectedSection && selectedSection !== 'emergency'
      ? safetyContent[selectedSection]
      : null;

  const callEmergencyNumber = (number: string) => {
    Linking.openURL(`tel:${number}`).catch(() => {
      Alert.alert(
        'Unable to open phone',
        `Please dial ${number} manually from your phone.`
      );
    });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.container}
      >
        {selectedSection === 'emergency' ? (
          <View>
            <Pressable
              onPress={() => setSelectedSection(null)}
              style={styles.backButton}
            >
              <Text style={styles.backText}>
                ‹  Back to safety guide
              </Text>
            </Pressable>

            <Text style={styles.detailTitle}>
              Emergency help 🆘
            </Text>

            <Text style={styles.detailSubtitle}>
              Important emergency contacts for Islamabad.
              Keep these numbers accessible.
            </Text>

            <View style={styles.warningCard}>
              <Text style={styles.warningTitle}>
                In immediate danger?
              </Text>
              <Text style={styles.warningText}>
                Move to a safe public place if possible and contact
                the appropriate emergency service immediately.
              </Text>
            </View>

            <Text style={styles.contactHeading}>
              Emergency contacts
            </Text>

            {emergencyContacts.map((contact) => (
              <View key={contact.number} style={styles.contactCard}>
                <View
                  style={[
                    styles.contactIcon,
                    { backgroundColor: contact.color },
                  ]}
                >
                  <Text style={styles.contactEmoji}>
                    {contact.emoji}
                  </Text>
                </View>

                <View style={styles.contactContent}>
                  <Text style={styles.contactName}>
                    {contact.name}
                  </Text>
                  <Text style={styles.contactDescription}>
                    {contact.description}
                  </Text>
                  <Text style={styles.contactNumber}>
                    {contact.number}
                  </Text>
                </View>

                <Pressable
                  style={styles.callButton}
                  onPress={() => callEmergencyNumber(contact.number)}
                >
                  <Text style={styles.callButtonText}>
                    Call
                  </Text>
                </Pressable>
              </View>
            ))}

            <View style={styles.reminderCard}>
              <Text style={styles.reminderEmoji}>💛</Text>
              <Text style={styles.reminderText}>
                These buttons open your device's phone app.
                They do not automatically contact emergency services.
              </Text>
            </View>
          </View>
        ) : selectedContent ? (
          <View>
            <Pressable
              onPress={() => setSelectedSection(null)}
              style={styles.backButton}
            >
              <Text style={styles.backText}>
                ‹  Back to safety guide
              </Text>
            </Pressable>

            <Text style={styles.detailTitle}>
              {selectedContent.title}
            </Text>

            <Text style={styles.detailSubtitle}>
              {selectedContent.subtitle}
            </Text>

            {selectedContent.tips.map((tip, index) => (
              <View key={index} style={styles.tipCard}>
                <View style={styles.tipNumber}>
                  <Text style={styles.tipNumberText}>
                    {index + 1}
                  </Text>
                </View>

                <Text style={styles.tipText}>{tip}</Text>
              </View>
            ))}

            <View style={styles.reminderCard}>
              <Text style={styles.reminderEmoji}>💛</Text>
              <Text style={styles.reminderText}>
                Your safety comes first. Never ignore a situation
                that makes you feel uncomfortable.
              </Text>
            </View>
          </View>
        ) : (
          <>
            {/* Header */}
            <View style={styles.header}>
              <View>
                <Text style={styles.brand}>FAST RIDEMATCH</Text>
                <Text style={styles.greeting}>
                  Your safety matters 💛
                </Text>
              </View>

              <View style={styles.headerIcon}>
                <Text style={styles.headerEmoji}>🛡️</Text>
              </View>
            </View>

            {/* Hero */}
            <View style={styles.hero}>
              <View style={styles.heroText}>
                <Text style={styles.heroTag}>
                  TRAVEL SMART. STAY SAFE.
                </Text>

                <Text style={styles.heroTitle}>
                  A safer ride{'\n'}starts with you.
                </Text>

                <Text style={styles.heroDescription}>
                  Helpful guidance for every step of your journey.
                </Text>
              </View>

              <Text style={styles.heroEmoji}>🚘</Text>
            </View>

            {/* Safety sections */}
            <View style={styles.sectionHeading}>
              <Text style={styles.sectionTitle}>
                Your safety guide
              </Text>

              <Text style={styles.sectionSubtitle}>
                Three simple steps for a safer journey
              </Text>
            </View>

            {safetySections.map((section) => (
              <Pressable
                key={section.number}
                style={({ pressed }) => [
                  styles.safetyCard,
                  pressed && styles.cardPressed,
                ]}
                onPress={() => setSelectedSection(section.key)}
              >
                <View
                  style={[
                    styles.cardIcon,
                    { backgroundColor: section.color },
                  ]}
                >
                  <Text style={styles.cardEmoji}>
                    {section.emoji}
                  </Text>
                </View>

                <View style={styles.cardContent}>
                  <Text style={styles.cardNumber}>
                    STEP {section.number}
                  </Text>

                  <Text style={styles.cardTitle}>
                    {section.title}
                  </Text>

                  <Text style={styles.cardDescription}>
                    {section.description}
                  </Text>
                </View>

                <Text style={styles.cardArrow}>›</Text>
              </Pressable>
            ))}

            {/* Emergency information */}
            <Pressable
              style={({ pressed }) => [
                styles.emergencyCard,
                pressed && styles.cardPressed,
              ]}
              onPress={() => setSelectedSection('emergency')}
            >
              <View style={styles.emergencyTop}>
                <Text style={styles.emergencyEmoji}>🆘</Text>
                <Text style={styles.emergencyLabel}>
                  IMPORTANT
                </Text>
              </View>

              <Text style={styles.emergencyTitle}>
                Need help in an emergency?
              </Text>

              <Text style={styles.emergencyDescription}>
                Find important emergency contacts and get help when
                you need it.
              </Text>

              <Text style={styles.emergencyLink}>
                View emergency contacts  →
              </Text>
            </Pressable>

            <Text style={styles.footer}>
              Ride together. Ride responsibly. 💚
            </Text>
          </>
        )}
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
    marginBottom: 25,
  },
  brand: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 2,
    color: COLORS.muted,
  },
  greeting: {
    fontSize: 19,
    fontWeight: '700',
    color: COLORS.text,
    marginTop: 5,
  },
  headerIcon: {
    width: 46,
    height: 46,
    borderRadius: 16,
    backgroundColor: '#E5EDE1',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerEmoji: {
    fontSize: 23,
  },
  hero: {
    backgroundColor: COLORS.yellow,
    borderRadius: 25,
    padding: 23,
    minHeight: 195,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    overflow: 'hidden',
  },
  heroText: {
    flex: 1,
  },
  heroTag: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1.3,
    color: '#65572C',
    marginBottom: 12,
  },
  heroTitle: {
    fontSize: 30,
    lineHeight: 36,
    fontWeight: '800',
    color: '#303629',
  },
  heroDescription: {
    fontSize: 13,
    lineHeight: 19,
    color: '#5E583F',
    marginTop: 10,
    maxWidth: 230,
  },
  heroEmoji: {
    fontSize: 55,
    marginLeft: 5,
  },
  sectionHeading: {
    marginTop: 30,
    marginBottom: 15,
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
  safetyCard: {
    backgroundColor: COLORS.white,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: COLORS.border,
    padding: 15,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  cardPressed: {
    opacity: 0.75,
  },
  cardIcon: {
    width: 55,
    height: 55,
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardEmoji: {
    fontSize: 25,
  },
  cardContent: {
    flex: 1,
    marginLeft: 14,
  },
  cardNumber: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 1.2,
    color: COLORS.muted,
    marginBottom: 4,
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: COLORS.text,
  },
  cardDescription: {
    fontSize: 11,
    lineHeight: 16,
    color: COLORS.muted,
    marginTop: 4,
  },
  cardArrow: {
    fontSize: 28,
    color: '#A0A79F',
    marginLeft: 8,
  },
  emergencyCard: {
    backgroundColor: '#E8EFF8',
    borderRadius: 21,
    padding: 20,
    marginTop: 17,
  },
  emergencyTop: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  emergencyEmoji: {
    fontSize: 22,
    marginRight: 9,
  },
  emergencyLabel: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1.2,
    color: '#536C8B',
  },
  emergencyTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#293B52',
  },
  emergencyDescription: {
    fontSize: 13,
    lineHeight: 20,
    color: '#53677F',
    marginTop: 8,
  },
  emergencyLink: {
    color: '#405D7A',
    fontWeight: '800',
    fontSize: 13,
    marginTop: 15,
  },
  footer: {
    textAlign: 'center',
    color: COLORS.muted,
    fontSize: 12,
    marginTop: 25,
  },
  backButton: {
    alignSelf: 'flex-start',
    paddingVertical: 12,
    paddingHorizontal: 4,
    marginBottom: 20,
  },
  backText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#647D69',
  },
  detailTitle: {
    fontSize: 27,
    fontWeight: '800',
    color: COLORS.text,
    marginBottom: 8,
  },
  detailSubtitle: {
    fontSize: 14,
    lineHeight: 21,
    color: COLORS.muted,
    marginBottom: 25,
  },
  tipCard: {
    backgroundColor: COLORS.white,
    borderRadius: 17,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  tipNumber: {
    width: 34,
    height: 34,
    borderRadius: 12,
    backgroundColor: COLORS.sage,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 13,
  },
  tipNumberText: {
    fontWeight: '800',
    color: '#263B2B',
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 21,
    color: COLORS.text,
  },
  reminderCard: {
    backgroundColor: '#FFF3D1',
    borderRadius: 18,
    padding: 18,
    marginTop: 15,
    flexDirection: 'row',
    alignItems: 'center',
  },
  reminderEmoji: {
    fontSize: 23,
    marginRight: 12,
  },
  reminderText: {
    flex: 1,
    fontSize: 13,
    lineHeight: 19,
    color: '#66572F',
  },
  warningCard: {
    backgroundColor: '#FCE7E7',
    borderRadius: 18,
    padding: 18,
    marginBottom: 25,
  },
  warningTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#873F3F',
    marginBottom: 7,
  },
  warningText: {
    fontSize: 13,
    lineHeight: 20,
    color: '#744B4B',
  },
  contactHeading: {
    fontSize: 19,
    fontWeight: '800',
    color: COLORS.text,
    marginBottom: 14,
  },
  contactCard: {
    backgroundColor: COLORS.white,
    borderRadius: 19,
    borderWidth: 1,
    borderColor: COLORS.border,
    padding: 14,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  contactIcon: {
    width: 48,
    height: 48,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  contactEmoji: {
    fontSize: 23,
  },
  contactContent: {
    flex: 1,
    marginLeft: 12,
  },
  contactName: {
    fontSize: 14,
    fontWeight: '800',
    color: COLORS.text,
  },
  contactDescription: {
    fontSize: 11,
    lineHeight: 16,
    color: COLORS.muted,
    marginTop: 3,
  },
  contactNumber: {
    fontSize: 16,
    fontWeight: '800',
    color: '#536C8B',
    marginTop: 5,
  },
  callButton: {
    backgroundColor: COLORS.sage,
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 12,
    marginLeft: 8,
  },
  callButtonText: {
    color: '#263B2B',
    fontSize: 12,
    fontWeight: '800',
  },
});
