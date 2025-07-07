import React, { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import {
  Card,
  Title,
  Text,
  List,
  ActivityIndicator,
  IconButton,
  Chip,
} from 'react-native-paper';
import { mlbApi } from '../../services/mlbApi';
import type { DashboardWidget, Game } from '../../types';

interface Props {
  widget: DashboardWidget;
  onUpdate: (id: string, updates: Partial<DashboardWidget>) => void;
  isEditMode: boolean;
  onRemove: () => void;
}

export default function RecentGamesWidget({ widget, onUpdate, isEditMode, onRemove }: Props) {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecentGames();
  }, []);

  const loadRecentGames = async () => {
    setLoading(true);
    try {
      const response = await mlbApi.getRecentGames();
      if (response && Array.isArray(response)) {
        setGames(response.slice(0, 5)); // Show only 5 recent games
      }
    } catch (error) {
      console.error('Error loading recent games:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderGameItem = (game: Game) => {
    const isCompleted = game.status === 'final';
    const gameTitle = `${game.awayTeam.abbreviation} @ ${game.homeTeam.abbreviation}`;
    const gameDescription = isCompleted 
      ? `${game.awayScore} - ${game.homeScore} (Final)`
      : `${new Date(game.date).toLocaleDateString()} ${new Date(game.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

    return (
      <List.Item
        key={game.id}
        title={gameTitle}
        description={gameDescription}
        left={(props) => (
          <List.Icon 
            {...props} 
            icon={isCompleted ? 'check-circle' : 'clock'} 
            color={isCompleted ? '#4caf50' : '#ff9800'}
          />
        )}
        right={() => (
          isCompleted ? (
            <Chip 
              mode="outlined" 
              compact
              style={styles.statusChip}
            >
              Final
            </Chip>
          ) : (
            <Chip 
              mode="outlined" 
              compact
              style={styles.statusChip}
            >
              {game.status}
            </Chip>
          )
        )}
        style={styles.gameItem}
      />
    );
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
        ) : games.length > 0 ? (
          <View style={styles.gamesList}>
            {games.map(renderGameItem)}
          </View>
        ) : (
          <Text style={styles.noGamesText}>No recent games available</Text>
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
  gamesList: {
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    padding: 4,
  },
  gameItem: {
    paddingVertical: 4,
    backgroundColor: '#ffffff',
    marginBottom: 4,
    borderRadius: 6,
  },
  statusChip: {
    height: 24,
    alignSelf: 'center',
  },
  noGamesText: {
    textAlign: 'center',
    color: '#666',
    padding: 20,
    fontStyle: 'italic',
  },
});
