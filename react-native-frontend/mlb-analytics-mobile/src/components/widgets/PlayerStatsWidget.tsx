import React, { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import {
  Card,
  Title,
  Text,
  ActivityIndicator,
  IconButton,
  Chip,
} from 'react-native-paper';
import { mlbApi } from '../../services/mlbApi';
import type { DashboardWidget, Player } from '../../types';

interface Props {
  widget: DashboardWidget;
  onUpdate: (id: string, updates: Partial<DashboardWidget>) => void;
  isEditMode: boolean;
  onRemove: () => void;
}

export default function PlayerStatsWidget({ widget, onUpdate, isEditMode, onRemove }: Props) {
  const [player, setPlayer] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const playerId = widget.config?.playerId || 'default-player-id';

  useEffect(() => {
    loadPlayerStats();
  }, [playerId]);

  const loadPlayerStats = async () => {
    setLoading(true);
    try {
      const playerIdNumber = parseInt(playerId, 10);
      if (isNaN(playerIdNumber)) {
        console.error('Invalid player ID:', playerId);
        return;
      }
      const response = await mlbApi.getPlayerProfile(playerIdNumber);
      setPlayer(response);
    } catch (error) {
      console.error('Error loading player stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card style={styles.container}>
      <Card.Content>
        <View style={styles.header}>
          <Title style={styles.title}>{widget.title}</Title>
          {isEditMode && (
            <IconButton
              icon="close"
              size={20}
              onPress={onRemove}
              iconColor="#f44336"
            />
          )}
        </View>
        
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator animating={true} />
          </View>
        ) : player ? (
          <View style={styles.playerContent}>
            <Text style={styles.playerName}>{player.name}</Text>
            <View style={styles.playerDetails}>
              <Chip mode="outlined" style={styles.chip}>#{player.jerseyNumber}</Chip>
              <Chip mode="outlined" style={styles.chip}>{player.position}</Chip>
              <Chip mode="outlined" style={styles.chip}>{player.team}</Chip>
            </View>
            
            {player.stats.batting && (
              <View style={styles.statsContainer}>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>
                    {player.stats.batting.batting_average.toFixed(3)}
                  </Text>
                  <Text style={styles.statLabel}>AVG</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{player.stats.batting.homeRuns}</Text>
                  <Text style={styles.statLabel}>HR</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{player.stats.batting.rbi}</Text>
                  <Text style={styles.statLabel}>RBI</Text>
                </View>
              </View>
            )}
            
            {player.stats.pitching && (
              <View style={styles.statsContainer}>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>
                    {player.stats.pitching.era.toFixed(2)}
                  </Text>
                  <Text style={styles.statLabel}>ERA</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{player.stats.pitching.wins}</Text>
                  <Text style={styles.statLabel}>W</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{player.stats.pitching.strikeouts}</Text>
                  <Text style={styles.statLabel}>K</Text>
                </View>
              </View>
            )}
          </View>
        ) : (
          <Text style={styles.errorText}>Player not found</Text>
        )}
      </Card.Content>
    </Card>
  );
}

const styles = StyleSheet.create({
  container: {
    margin: 8,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  title: {
    fontSize: 18,
    color: '#333',
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
  playerContent: {
    backgroundColor: '#f8f8f8',
    padding: 12,
    borderRadius: 8,
  },
  playerName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333',
  },
  playerDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  chip: {
    marginRight: 6,
    marginBottom: 4,
    height: 24,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1976d2',
  },
  statLabel: {
    fontSize: 10,
    color: '#666',
    marginTop: 2,
  },
  errorText: {
    textAlign: 'center',
    color: '#666',
    padding: 20,
  },
});
