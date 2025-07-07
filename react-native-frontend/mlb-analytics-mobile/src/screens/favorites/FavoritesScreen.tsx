import React, { useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import {
  Text,
  Card,
  Title,
  List,
  IconButton,
  Chip,
  Divider,
  Button,
} from 'react-native-paper';
import { useFavoritesStore } from '../../store';
import type { FavoriteItem } from '../../types';

interface Props {
  navigation: any;
}

export default function FavoritesScreen({ navigation }: Props) {
  const { favoriteTeams, favoritePlayers, removeFavoriteTeam, removeFavoritePlayer } = useFavoritesStore();
  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = async () => {
    setRefreshing(true);
    // Just refresh the UI, data is already in store
    setRefreshing(false);
  };

  const handleItemPress = (item: { id: number; type: 'player' | 'team' }) => {
    if (item.type === 'player') {
      navigation.navigate('PlayerProfile', { playerId: item.id.toString() });
    } else if (item.type === 'team') {
      navigation.navigate('TeamDetails', { teamId: item.id.toString() });
    }
  };

  const handleRemoveFavorite = (id: number, type: 'player' | 'team') => {
    if (type === 'player') {
      removeFavoritePlayer(id);
    } else {
      removeFavoriteTeam(id);
    }
  };

  // Convert store arrays to display format
  const playerFavorites = favoritePlayers.map(id => ({ id, type: 'player' as const }));
  const teamFavorites = favoriteTeams.map(id => ({ id, type: 'team' as const }));

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {playerFavorites.length === 0 && teamFavorites.length === 0 ? (
        <Card style={styles.emptyCard}>
          <Card.Content>
            <Title style={styles.emptyTitle}>No Favorites Yet</Title>
            <Text style={styles.emptyText}>
              Start exploring players and teams to add them to your favorites.
            </Text>
            <Button
              mode="contained"
              onPress={() => navigation.navigate('Search')}
              style={styles.searchButton}
            >
              Search Players & Teams
            </Button>
          </Card.Content>
        </Card>
      ) : (
        <>
          {teamFavorites.length > 0 && (
            <Card style={styles.sectionCard}>
              <Card.Content>
                <View style={styles.sectionHeader}>
                  <Title style={styles.sectionTitle}>Favorite Teams</Title>
                  <Chip mode="outlined">{teamFavorites.length}</Chip>
                </View>
                <Divider style={styles.divider} />
                {teamFavorites.map((item) => (
                  <List.Item
                    key={item.id}
                    title={`Team ${item.id}`}
                    description="Tap to view details"
                    left={(props) => <List.Icon {...props} icon="shield" />}
                    right={(props) => (
                      <IconButton
                        {...props}
                        icon="heart-remove"
                        onPress={() => handleRemoveFavorite(item.id, item.type)}
                      />
                    )}
                    onPress={() => handleItemPress(item)}
                    style={styles.listItem}
                  />
                ))}
              </Card.Content>
            </Card>
          )}

          {playerFavorites.length > 0 && (
            <Card style={styles.sectionCard}>
              <Card.Content>
                <View style={styles.sectionHeader}>
                  <Title style={styles.sectionTitle}>Favorite Players</Title>
                  <Chip mode="outlined">{playerFavorites.length}</Chip>
                </View>
                <Divider style={styles.divider} />
                {playerFavorites.map((item) => (
                  <List.Item
                    key={item.id}
                    title={`Player ${item.id}`}
                    description="Tap to view details"
                    left={(props) => <List.Icon {...props} icon="account-star" />}
                    right={(props) => (
                      <IconButton
                        {...props}
                        icon="heart-remove"
                        onPress={() => handleRemoveFavorite(item.id, item.type)}
                      />
                    )}
                    onPress={() => handleItemPress(item)}
                    style={styles.listItem}
                  />
                ))}
              </Card.Content>
            </Card>
          )}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  emptyCard: {
    marginTop: 50,
    alignItems: 'center',
  },
  emptyTitle: {
    textAlign: 'center',
    marginBottom: 8,
  },
  emptyText: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 20,
    lineHeight: 20,
  },
  searchButton: {
    marginTop: 8,
  },
  sectionCard: {
    marginBottom: 16,
    elevation: 2,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sectionTitle: {
    color: '#333',
  },
  divider: {
    marginBottom: 8,
  },
  listItem: {
    backgroundColor: '#f8f8f8',
    marginBottom: 4,
    borderRadius: 8,
  },
});
