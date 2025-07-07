import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import mlbApi from '../../services/mlbApi';

interface TeamStanding {
  id: number;
  name: string;
  abbreviation: string;
  wins: number;
  losses: number;
  winning_percentage: number;
  games_back: number;
  streak: string;
  last_10: string;
}

interface StandingsData {
  AL: {
    East: TeamStanding[];
    Central: TeamStanding[];
    West: TeamStanding[];
  };
  NL: {
    East: TeamStanding[];
    Central: TeamStanding[];
    West: TeamStanding[];
  };
}

const StandingsScreen: React.FC = () => {
  const [standings, setStandings] = useState<StandingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedLeague, setSelectedLeague] = useState<'AL' | 'NL'>('AL');

  const fetchStandings = async () => {
    try {
      setError(null);
      const data = await mlbApi.getStandings();
      setStandings(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch standings');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStandings();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchStandings();
  };

  const renderDivisionStandings = (teams: TeamStanding[], divisionName: string) => (
    <View style={styles.divisionContainer}>
      <Text style={styles.divisionTitle}>{divisionName}</Text>
      <View style={styles.tableHeader}>
        <Text style={[styles.headerText, styles.teamColumn]}>Team</Text>
        <Text style={[styles.headerText, styles.recordColumn]}>W-L</Text>
        <Text style={[styles.headerText, styles.pctColumn]}>PCT</Text>
        <Text style={[styles.headerText, styles.gbColumn]}>GB</Text>
        <Text style={[styles.headerText, styles.streakColumn]}>Streak</Text>
        <Text style={[styles.headerText, styles.last10Column]}>L10</Text>
      </View>
      {teams.map((team, index) => (
        <TouchableOpacity 
          key={team.id} 
          style={[
            styles.teamRow,
            index === 0 && styles.firstPlaceRow
          ]}
        >
          <Text style={[styles.teamText, styles.teamColumn]}>
            {team.abbreviation}
          </Text>
          <Text style={[styles.teamText, styles.recordColumn]}>
            {team.wins}-{team.losses}
          </Text>
          <Text style={[styles.teamText, styles.pctColumn]}>
            {team.winning_percentage.toFixed(3)}
          </Text>
          <Text style={[styles.teamText, styles.gbColumn]}>
            {team.games_back === 0 ? '-' : team.games_back.toString()}
          </Text>
          <Text style={[styles.teamText, styles.streakColumn]}>
            {team.streak}
          </Text>
          <Text style={[styles.teamText, styles.last10Column]}>
            {team.last_10}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#1976d2" />
        <Text style={styles.loadingText}>Loading standings...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="alert-circle" size={48} color="#d32f2f" />
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchStandings}>
          <Text style={styles.retryButtonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!standings) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>No standings data available</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* League Selector */}
      <View style={styles.leagueSelector}>
        <TouchableOpacity
          style={[
            styles.leagueButton,
            selectedLeague === 'AL' && styles.activeLeagueButton
          ]}
          onPress={() => setSelectedLeague('AL')}
        >
          <Text style={[
            styles.leagueButtonText,
            selectedLeague === 'AL' && styles.activeLeagueButtonText
          ]}>
            American League
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.leagueButton,
            selectedLeague === 'NL' && styles.activeLeagueButton
          ]}
          onPress={() => setSelectedLeague('NL')}
        >
          <Text style={[
            styles.leagueButtonText,
            selectedLeague === 'NL' && styles.activeLeagueButtonText
          ]}>
            National League
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {standings[selectedLeague] && (
          <>
            {renderDivisionStandings(standings[selectedLeague].East, `${selectedLeague} East`)}
            {renderDivisionStandings(standings[selectedLeague].Central, `${selectedLeague} Central`)}
            {renderDivisionStandings(standings[selectedLeague].West, `${selectedLeague} West`)}
          </>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  scrollView: {
    flex: 1,
  },
  leagueSelector: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  leagueButton: {
    flex: 1,
    paddingVertical: 15,
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  activeLeagueButton: {
    backgroundColor: '#1976d2',
  },
  leagueButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  activeLeagueButtonText: {
    color: '#ffffff',
  },
  divisionContainer: {
    backgroundColor: '#ffffff',
    marginTop: 10,
    marginHorizontal: 10,
    borderRadius: 8,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  divisionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1976d2',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#f5f5f5',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    textAlign: 'center',
  },
  teamRow: {
    flexDirection: 'row',
    paddingVertical: 12,
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  firstPlaceRow: {
    backgroundColor: '#e8f5e8',
  },
  teamText: {
    fontSize: 14,
    color: '#333',
    textAlign: 'center',
  },
  teamColumn: {
    flex: 2,
    textAlign: 'left',
  },
  recordColumn: {
    flex: 1.5,
  },
  pctColumn: {
    flex: 1,
  },
  gbColumn: {
    flex: 1,
  },
  streakColumn: {
    flex: 1,
  },
  last10Column: {
    flex: 1,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#d32f2f',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#1976d2',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default StandingsScreen;
