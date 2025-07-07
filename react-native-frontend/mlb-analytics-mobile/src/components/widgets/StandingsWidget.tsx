import React, { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import {
  Card,
  Title,
  Text,
  List,
  ActivityIndicator,
  IconButton,
} from 'react-native-paper';
import { mlbApi } from '../../services/mlbApi';
import type { DashboardWidget, Team } from '../../types';

interface Props {
  widget: DashboardWidget;
  onUpdate: (id: string, updates: Partial<DashboardWidget>) => void;
  isEditMode: boolean;
  onRemove: () => void;
}

interface Standing {
  team: Team;
  wins: number;
  losses: number;
  winningPercentage: number;
  gamesBack: number;
}

export default function StandingsWidget({ widget, onUpdate, isEditMode, onRemove }: Props) {
  const [standings, setStandings] = useState<Standing[]>([]);
  const [loading, setLoading] = useState(true);
  const [division, setDivision] = useState('AL East'); // Default division

  useEffect(() => {
    loadStandings();
  }, [division]);

  const loadStandings = async () => {
    setLoading(true);
    try {
      const data = await mlbApi.getStandings(division);
      setStandings(data);
    } catch (error) {
      console.error('Error loading standings:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderStandingItem = (standing: Standing, index: number) => (
    <List.Item
      key={standing.team.id}
      title={`${index + 1}. ${standing.team.name}`}
      description={`${standing.wins}-${standing.losses} (${standing.winningPercentage.toFixed(3)})`}
      right={() => (
        <Text style={styles.gamesBack}>
          {standing.gamesBack === 0 ? '-' : standing.gamesBack.toString()}
        </Text>
      )}
      style={styles.standingItem}
    />
  );

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
        
        <Text style={styles.subtitle}>{division}</Text>
        
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator animating={true} />
          </View>
        ) : (
          <View style={styles.standingsList}>
            {standings.slice(0, 5).map(renderStandingItem)}
          </View>
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
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
  standingsList: {
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    padding: 4,
  },
  standingItem: {
    paddingVertical: 4,
  },
  gamesBack: {
    fontSize: 12,
    color: '#666',
    alignSelf: 'center',
  },
});
