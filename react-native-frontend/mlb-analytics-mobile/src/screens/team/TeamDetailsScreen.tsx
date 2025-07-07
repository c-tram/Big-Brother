import React, { useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Dimensions,
  RefreshControl,
} from 'react-native';
import {
  Text,
  Card,
  Title,
  Button,
  Chip,
  ActivityIndicator,
  IconButton,
  List,
  Divider,
} from 'react-native-paper';
import { BarChart } from 'react-native-chart-kit';
import { useFavoritesStore } from '../../store';
import { mlbApi } from '../../services/mlbApi';
import type { Team, Game, ChartData } from '../../types';

interface Props {
  route: {
    params: {
      teamId: string;
    };
  };
  navigation: any;
}

const { width } = Dimensions.get('window');

export default function TeamDetailsScreen({ route, navigation }: Props) {
  const { teamId } = route.params;
  const [team, setTeam] = useState<Team | null>(null);
  const [recentGames, setRecentGames] = useState<Game[]>([]);
  const [upcomingGames, setUpcomingGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [statsChart, setStatsChart] = useState<ChartData | null>(null);
  const { favoriteTeams, addFavoriteTeam, removeFavoriteTeam, isFavoriteTeam } = useFavoritesStore();

  const teamIdNumber = parseInt(teamId, 10);
  const isFavorite = isFavoriteTeam(teamIdNumber);

  useEffect(() => {
    loadTeamData();
  }, [teamId]);

  const loadTeamData = async () => {
    try {
      const [teamResponse, gamesResponse] = await Promise.all([
        mlbApi.getTeamProfile(teamIdNumber),
        mlbApi.getTeamGames(teamIdNumber),
      ]);

      setTeam(teamResponse);
      navigation.setOptions({ title: `${teamResponse.location} ${teamResponse.name}` });

      if (gamesResponse && Array.isArray(gamesResponse)) {
        const now = new Date();
        const recent = gamesResponse.filter((game: Game) => 
          new Date(game.date) < now && game.status === 'final'
        ).slice(0, 5);
        const upcoming = gamesResponse.filter((game: Game) => 
          new Date(game.date) >= now
        ).slice(0, 5);
        
        setRecentGames(recent);
        setUpcomingGames(upcoming);
      }

      // Mock stats chart data
      setStatsChart({
        labels: ['Wins', 'Losses', 'Runs', 'ERA'],
        datasets: [{
          data: [65, 45, 750, 3.85],
        }],
      });
      
    } catch (error) {
      console.error('Error loading team data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTeamData();
    setRefreshing(false);
  };

  const toggleFavorite = () => {
    if (!team) return;

    if (isFavorite) {
      removeFavoriteTeam(teamIdNumber);
    } else {
      addFavoriteTeam(teamIdNumber);
    }
  };

  const renderGame = (game: Game, index: number) => {
    const isHome = game.homeTeam.id === teamId;
    const opponent = isHome ? game.awayTeam : game.homeTeam;
    const teamScore = isHome ? game.homeScore : game.awayScore;
    const opponentScore = isHome ? game.awayScore : game.homeScore;
    
    return (
      <List.Item
        key={game.id}
        title={`vs ${opponent.name}`}
        description={`${new Date(game.date).toLocaleDateString()} - ${game.status}`}
        left={(props) => (
          <List.Icon 
            {...props} 
            icon={isHome ? 'home' : 'airplane'} 
          />
        )}
        right={() => (
          game.status === 'final' ? (
            <View style={styles.scoreContainer}>
              <Text style={[
                styles.score, 
                teamScore !== undefined && opponentScore !== undefined && teamScore > opponentScore 
                  ? styles.winScore 
                  : styles.lossScore
              ]}>
                {teamScore} - {opponentScore}
              </Text>
            </View>
          ) : (
            <Text style={styles.gameTime}>
              {new Date(game.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </Text>
          )
        )}
      />
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading team data...</Text>
      </View>
    );
  }

  if (!team) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Team not found</Text>
        <Button onPress={() => navigation.goBack()}>Go Back</Button>
      </View>
    );
  }

  const { stats } = team;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Card style={styles.profileCard}>
        <Card.Content>
          <View style={styles.profileHeader}>
            <View style={styles.teamInfo}>
              <Title style={styles.teamName}>
                {team.location} {team.name}
              </Title>
              <View style={styles.teamDetails}>
                <Chip mode="outlined" style={styles.chip}>{team.abbreviation}</Chip>
                <Chip mode="outlined" style={styles.chip}>{team.division}</Chip>
                <Chip mode="outlined" style={styles.chip}>{team.league}</Chip>
              </View>
            </View>
            <IconButton
              icon={isFavorite ? 'heart' : 'heart-outline'}
              iconColor={isFavorite ? '#d32f2f' : '#666'}
              size={24}
              onPress={toggleFavorite}
            />
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.statsCard}>
        <Card.Content>
          <Title style={styles.statsTitle}>Season Record</Title>
          <View style={styles.recordContainer}>
            <View style={styles.recordItem}>
              <Text style={styles.recordValue}>{stats.wins}</Text>
              <Text style={styles.recordLabel}>Wins</Text>
            </View>
            <View style={styles.recordItem}>
              <Text style={styles.recordValue}>{stats.losses}</Text>
              <Text style={styles.recordLabel}>Losses</Text>
            </View>
            <View style={styles.recordItem}>
              <Text style={styles.recordValue}>{stats.winning_percentage.toFixed(3)}</Text>
              <Text style={styles.recordLabel}>Win %</Text>
            </View>
            <View style={styles.recordItem}>
              <Text style={styles.recordValue}>{stats.games_back}</Text>
              <Text style={styles.recordLabel}>GB</Text>
            </View>
          </View>
          
          <View style={styles.detailedStats}>
            <View style={styles.statRow}>
              <Text style={styles.statRowLabel}>Home Record:</Text>
              <Text style={styles.statRowValue}>{stats.home_record}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statRowLabel}>Away Record:</Text>
              <Text style={styles.statRowValue}>{stats.away_record}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statRowLabel}>Last 10:</Text>
              <Text style={styles.statRowValue}>{stats.last_ten}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statRowLabel}>Streak:</Text>
              <Text style={styles.statRowValue}>{stats.streak}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statRowLabel}>Runs Scored:</Text>
              <Text style={styles.statRowValue}>{stats.runs_scored}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statRowLabel}>Runs Allowed:</Text>
              <Text style={styles.statRowValue}>{stats.runs_allowed}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statRowLabel}>Run Differential:</Text>
              <Text style={[
                styles.statRowValue,
                stats.run_differential > 0 ? styles.positive : styles.negative
              ]}>
                {stats.run_differential > 0 ? '+' : ''}{stats.run_differential}
              </Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      {recentGames.length > 0 && (
        <Card style={styles.gamesCard}>
          <Card.Content>
            <Title style={styles.gamesTitle}>Recent Games</Title>
            <Divider style={styles.divider} />
            {recentGames.map(renderGame)}
          </Card.Content>
        </Card>
      )}

      {upcomingGames.length > 0 && (
        <Card style={styles.gamesCard}>
          <Card.Content>
            <Title style={styles.gamesTitle}>Upcoming Games</Title>
            <Divider style={styles.divider} />
            {upcomingGames.map(renderGame)}
          </Card.Content>
        </Card>
      )}

      {statsChart && (
        <Card style={styles.chartCard}>
          <Card.Content>
            <Title style={styles.chartTitle}>Season Overview</Title>
            <BarChart
              data={statsChart}
              width={width - 64}
              height={220}
              chartConfig={{
                backgroundColor: '#ffffff',
                backgroundGradientFrom: '#ffffff',
                backgroundGradientTo: '#ffffff',
                decimalPlaces: 0,
                color: (opacity = 1) => `rgba(25, 118, 210, ${opacity})`,
                labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                style: {
                  borderRadius: 16,
                },
              }}
              style={styles.chart}
              yAxisSuffix=""
              yAxisLabel=""
              showValuesOnTopOfBars
            />
          </Card.Content>
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 20,
  },
  profileCard: {
    margin: 16,
    elevation: 4,
  },
  profileHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  teamInfo: {
    flex: 1,
  },
  teamName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  teamDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  chip: {
    marginRight: 8,
    marginBottom: 4,
  },
  statsCard: {
    margin: 16,
    marginTop: 0,
    elevation: 4,
  },
  statsTitle: {
    marginBottom: 16,
    color: '#1976d2',
  },
  recordContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  recordItem: {
    alignItems: 'center',
  },
  recordValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  recordLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  detailedStats: {
    backgroundColor: '#f8f8f8',
    padding: 12,
    borderRadius: 8,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statRowLabel: {
    fontSize: 14,
    color: '#666',
  },
  statRowValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  positive: {
    color: '#4caf50',
  },
  negative: {
    color: '#f44336',
  },
  gamesCard: {
    margin: 16,
    marginTop: 0,
    elevation: 4,
  },
  gamesTitle: {
    marginBottom: 8,
    color: '#1976d2',
  },
  divider: {
    marginBottom: 8,
  },
  scoreContainer: {
    alignItems: 'center',
  },
  score: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  winScore: {
    color: '#4caf50',
  },
  lossScore: {
    color: '#f44336',
  },
  gameTime: {
    fontSize: 12,
    color: '#666',
  },
  chartCard: {
    margin: 16,
    marginTop: 0,
    marginBottom: 32,
    elevation: 4,
  },
  chartTitle: {
    marginBottom: 16,
    color: '#1976d2',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
});
