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
  Paragraph,
  Button,
  Chip,
  ActivityIndicator,
  IconButton,
} from 'react-native-paper';
import { LineChart } from 'react-native-chart-kit';
import { useFavoritesStore } from '../../store';
import { mlbApi } from '../../services/mlbApi';
import type { Player, ChartData } from '../../types';

interface Props {
  route: {
    params: {
      playerId: string;
    };
  };
  navigation: any;
}

const { width } = Dimensions.get('window');

export default function PlayerProfileScreen({ route, navigation }: Props) {
  const { playerId } = route.params;
  const [player, setPlayer] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [statsChart, setStatsChart] = useState<ChartData | null>(null);
  const { favoritePlayers, addFavoritePlayer, removeFavoritePlayer, isFavoritePlayer } = useFavoritesStore();

  const playerIdNumber = parseInt(playerId, 10);
  const isFavorite = isFavoritePlayer(playerIdNumber);

  useEffect(() => {
    loadPlayerData();
  }, [playerId]);

  const loadPlayerData = async () => {
    try {
      const response = await mlbApi.getPlayerProfile(playerIdNumber);
      setPlayer(response);
      navigation.setOptions({ title: response.basicInfo.fullName });
      
      // Load chart data for batting average over time (mock data for now)
      if (response.careerStats) {
        setStatsChart({
          labels: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
          datasets: [{
            data: [0.250, 0.275, 0.290, 0.285, 0.295, 0.301],
            color: (opacity = 1) => `rgba(25, 118, 210, ${opacity})`,
            strokeWidth: 2,
          }],
        });
      }
    } catch (error) {
      console.error('Error loading player data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadPlayerData();
    setRefreshing(false);
  };

  const toggleFavorite = () => {
    if (!player) return;

    if (isFavorite) {
      removeFavoritePlayer(playerIdNumber);
    } else {
      addFavoritePlayer(playerIdNumber);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading player data...</Text>
      </View>
    );
  }

  if (!player) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Player not found</Text>
        <Button onPress={() => navigation.goBack()}>Go Back</Button>
      </View>
    );
  }

  const { batting, pitching, fielding } = player.stats;

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
            <View style={styles.playerInfo}>
              <Title style={styles.playerName}>{player.name}</Title>
              <View style={styles.playerDetails}>
                <Chip mode="outlined" style={styles.chip}>#{player.jerseyNumber}</Chip>
                <Chip mode="outlined" style={styles.chip}>{player.position}</Chip>
                <Chip mode="outlined" style={styles.chip}>{player.team}</Chip>
              </View>
            </View>
            <IconButton
              icon={isFavorite ? 'heart' : 'heart-outline'}
              iconColor={isFavorite ? '#d32f2f' : '#666'}
              size={24}
              onPress={toggleFavorite}
            />
          </View>
          
          <View style={styles.bioInfo}>
            <Text style={styles.bioText}>Age: {player.age}</Text>
            <Text style={styles.bioText}>Height: {player.height}</Text>
            <Text style={styles.bioText}>Weight: {player.weight}</Text>
            <Text style={styles.bioText}>Bats: {player.bats} | Throws: {player.throws}</Text>
          </View>
        </Card.Content>
      </Card>

      {batting && (
        <Card style={styles.statsCard}>
          <Card.Content>
            <Title style={styles.statsTitle}>Batting Statistics</Title>
            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{batting.batting_average.toFixed(3)}</Text>
                <Text style={styles.statLabel}>AVG</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{batting.homeRuns}</Text>
                <Text style={styles.statLabel}>HR</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{batting.rbi}</Text>
                <Text style={styles.statLabel}>RBI</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{batting.ops.toFixed(3)}</Text>
                <Text style={styles.statLabel}>OPS</Text>
              </View>
            </View>
            
            <View style={styles.detailedStats}>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>Games:</Text>
                <Text style={styles.statRowValue}>{batting.games}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>At Bats:</Text>
                <Text style={styles.statRowValue}>{batting.atBats}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>Hits:</Text>
                <Text style={styles.statRowValue}>{batting.hits}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>Runs:</Text>
                <Text style={styles.statRowValue}>{batting.runs}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>Stolen Bases:</Text>
                <Text style={styles.statRowValue}>{batting.stolen_bases}</Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      )}

      {pitching && (
        <Card style={styles.statsCard}>
          <Card.Content>
            <Title style={styles.statsTitle}>Pitching Statistics</Title>
            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{pitching.era.toFixed(2)}</Text>
                <Text style={styles.statLabel}>ERA</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{pitching.wins}</Text>
                <Text style={styles.statLabel}>W</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{pitching.losses}</Text>
                <Text style={styles.statLabel}>L</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{pitching.whip.toFixed(2)}</Text>
                <Text style={styles.statLabel}>WHIP</Text>
              </View>
            </View>
            
            <View style={styles.detailedStats}>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>Games:</Text>
                <Text style={styles.statRowValue}>{pitching.games}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>Innings Pitched:</Text>
                <Text style={styles.statRowValue}>{pitching.innings_pitched.toFixed(1)}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>Strikeouts:</Text>
                <Text style={styles.statRowValue}>{pitching.strikeouts}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statRowLabel}>Saves:</Text>
                <Text style={styles.statRowValue}>{pitching.saves}</Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      )}

      {statsChart && (
        <Card style={styles.chartCard}>
          <Card.Content>
            <Title style={styles.chartTitle}>Batting Average Trend</Title>
            <LineChart
              data={statsChart}
              width={width - 64}
              height={220}
              chartConfig={{
                backgroundColor: '#ffffff',
                backgroundGradientFrom: '#ffffff',
                backgroundGradientTo: '#ffffff',
                decimalPlaces: 3,
                color: (opacity = 1) => `rgba(25, 118, 210, ${opacity})`,
                labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                style: {
                  borderRadius: 16,
                },
                propsForDots: {
                  r: '6',
                  strokeWidth: '2',
                  stroke: '#1976d2',
                },
              }}
              bezier
              style={styles.chart}
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
  playerInfo: {
    flex: 1,
  },
  playerName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  playerDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  chip: {
    marginRight: 8,
    marginBottom: 4,
  },
  bioInfo: {
    backgroundColor: '#f8f8f8',
    padding: 12,
    borderRadius: 8,
  },
  bioText: {
    fontSize: 14,
    color: '#666',
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
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  statLabel: {
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
  chartCard: {
    margin: 16,
    marginTop: 0,
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
