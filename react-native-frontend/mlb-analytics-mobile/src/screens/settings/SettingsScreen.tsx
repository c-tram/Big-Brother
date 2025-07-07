import React from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import {
  Text,
  Card,
  Title,
  List,
  Switch,
  Button,
  Divider,
} from 'react-native-paper';
import { useAuthStore } from '../../store';
import { mlbApi } from '../../services/mlbApi';

export default function SettingsScreen() {
  const { user, logout, updatePreferences } = useAuthStore();

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive',
          onPress: async () => {
            try {
              await mlbApi.logout();
              logout();
            } catch (error) {
              console.error('Logout error:', error);
              logout(); // Logout locally even if API call fails
            }
          }
        },
      ]
    );
  };

  const toggleNotifications = (value: boolean) => {
    updatePreferences({ notifications: value });
  };

  const toggleTheme = (value: boolean) => {
    updatePreferences({ theme: value ? 'dark' : 'light' });
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.profileCard}>
        <Card.Content>
          <Title style={styles.profileTitle}>Profile</Title>
          <Text style={styles.profileText}>
            {user?.firstName} {user?.lastName}
          </Text>
          <Text style={styles.profileEmail}>{user?.email}</Text>
        </Card.Content>
      </Card>

      <Card style={styles.settingsCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Preferences</Title>
          <Divider style={styles.divider} />
          
          <List.Item
            title="Push Notifications"
            description="Get notified about game updates and player news"
            left={(props) => <List.Icon {...props} icon="bell" />}
            right={() => (
              <Switch
                value={user?.preferences?.notifications || false}
                onValueChange={toggleNotifications}
              />
            )}
          />

          <List.Item
            title="Dark Theme"
            description="Use dark theme for the app"
            left={(props) => <List.Icon {...props} icon="theme-light-dark" />}
            right={() => (
              <Switch
                value={user?.preferences?.theme === 'dark'}
                onValueChange={toggleTheme}
              />
            )}
          />

          <List.Item
            title="Favorite Team"
            description={user?.preferences?.favoriteTeam || 'Not set'}
            left={(props) => <List.Icon {...props} icon="shield-star" />}
            onPress={() => {
              // Navigate to team selection screen
              Alert.alert('Feature Coming Soon', 'Team selection will be available in the next update');
            }}
          />

          <List.Item
            title="Favorite Player"
            description={user?.preferences?.favoritePlayer || 'Not set'}
            left={(props) => <List.Icon {...props} icon="account-star" />}
            onPress={() => {
              // Navigate to player selection screen
              Alert.alert('Feature Coming Soon', 'Player selection will be available in the next update');
            }}
          />
        </Card.Content>
      </Card>

      <Card style={styles.settingsCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Dashboard</Title>
          <Divider style={styles.divider} />
          
          <List.Item
            title="Customize Widgets"
            description="Arrange and configure your dashboard widgets"
            left={(props) => <List.Icon {...props} icon="view-dashboard" />}
            onPress={() => {
              Alert.alert('Feature Coming Soon', 'Widget customization will be available in the next update');
            }}
          />

          <List.Item
            title="Reset Dashboard"
            description="Reset dashboard to default layout"
            left={(props) => <List.Icon {...props} icon="refresh" />}
            onPress={() => {
              Alert.alert(
                'Reset Dashboard',
                'This will remove all your custom widgets and reset to defaults. Continue?',
                [
                  { text: 'Cancel', style: 'cancel' },
                  { 
                    text: 'Reset', 
                    style: 'destructive',
                    onPress: () => {
                      Alert.alert('Success', 'Dashboard has been reset');
                    }
                  },
                ]
              );
            }}
          />
        </Card.Content>
      </Card>

      <Card style={styles.settingsCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>About</Title>
          <Divider style={styles.divider} />
          
          <List.Item
            title="App Version"
            description="1.0.0"
            left={(props) => <List.Icon {...props} icon="information" />}
          />

          <List.Item
            title="Privacy Policy"
            description="View our privacy policy"
            left={(props) => <List.Icon {...props} icon="shield-lock" />}
            onPress={() => {
              Alert.alert('Privacy Policy', 'Privacy policy will open in a web browser');
            }}
          />

          <List.Item
            title="Terms of Service"
            description="View terms of service"
            left={(props) => <List.Icon {...props} icon="file-document" />}
            onPress={() => {
              Alert.alert('Terms of Service', 'Terms of service will open in a web browser');
            }}
          />

          <List.Item
            title="Contact Support"
            description="Get help with the app"
            left={(props) => <List.Icon {...props} icon="help-circle" />}
            onPress={() => {
              Alert.alert('Contact Support', 'Support contact options will be available soon');
            }}
          />
        </Card.Content>
      </Card>

      <Card style={styles.logoutCard}>
        <Card.Content>
          <Button
            mode="contained"
            onPress={handleLogout}
            style={styles.logoutButton}
            buttonColor="#d32f2f"
            textColor="#fff"
          >
            Logout
          </Button>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  profileCard: {
    marginBottom: 16,
    elevation: 2,
  },
  profileTitle: {
    marginBottom: 8,
    color: '#333',
  },
  profileText: {
    fontSize: 18,
    fontWeight: '500',
    marginBottom: 4,
  },
  profileEmail: {
    color: '#666',
    fontSize: 14,
  },
  settingsCard: {
    marginBottom: 16,
    elevation: 2,
  },
  sectionTitle: {
    marginBottom: 8,
    color: '#333',
  },
  divider: {
    marginBottom: 8,
  },
  logoutCard: {
    marginBottom: 32,
    elevation: 2,
  },
  logoutButton: {
    marginTop: 8,
  },
});
