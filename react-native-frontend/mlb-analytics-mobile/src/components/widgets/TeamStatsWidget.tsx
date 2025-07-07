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
import type { DashboardWidget, Team } from '../../types';

interface Props {
  widget: DashboardWidget;
  onUpdate: (id: string, updates: Partial<DashboardWidget>) => void;
  isEditMode: boolean;
  onRemove: () => void;
}

export default function TeamStatsWidget({ widget, onUpdate, isEditMode, onRemove }: Props) {
  const [team, setTeam] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const teamId = widget.config?.teamId || 'default-team-id';

  useEffect(() => {
    loadTeamStats();
  }, [teamId]);

  const loadTeamStats = async () => {
    setLoading(true);
    try {
      const teamIdNumber = parseInt(teamId, 10);
      if (isNaN(teamIdNumber)) {
        console.error('Invalid team ID:', teamId);
        return;
      }
      const response = await mlbApi.getTeamProfile(teamIdNumber);
      setTeam(response);
    } catch (error) {
      console.error('Error loading team stats:', error);
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
        ) : team ? (
          <View style={styles.teamContent}>
            <Text style={styles.teamName}>{team.location} {team.name}</Text>
            <View style={styles.teamDetails}>
              <Chip mode="outlined" style={styles.chip}>{team.abbreviation}</Chip>
              <Chip mode="outlined" style={styles.chip}>{team.division}</Chip>
              <Chip mode="outlined" style={styles.chip}>{team.league}</Chip>
            </View>
            
            <View style={styles.recordContainer}>
              <View style={styles.recordItem}>
                <Text style={styles.recordValue}>{team.stats.wins}</Text>
                <Text style={styles.recordLabel}>W</Text>
              </View>
              <View style={styles.recordItem}>
                <Text style={styles.recordValue}>{team.stats.losses}</Text>
                <Text style={styles.recordLabel}>L</Text>
              </View>
              <View style={styles.recordItem}>
                <Text style={styles.recordValue}>
                  {team.stats.winning_percentage.toFixed(3)}
                </Text>
                <Text style={styles.recordLabel}>PCT</Text>
              </View>
            </View>
            
            <View style={styles.additionalStats}>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>Runs Scored:</Text>
                <Text style={styles.statValue}>{team.stats.runs_scored}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>Runs Allowed:</Text>
                <Text style={styles.statValue}>{team.stats.runs_allowed}</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>Run Differential:</Text>
                <Text style={[
                  styles.statValue,
                  team.stats.run_differential > 0 ? styles.positive : styles.negative
                ]}>
                  {team.stats.run_differential > 0 ? '+' : ''}{team.stats.run_differential}
                </Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>Streak:</Text>
                <Text style={styles.statValue}>{team.stats.streak}</Text>
              </View>
            </View>
          </View>
        ) : (
          <Text style={styles.errorText}>Team not found</Text>
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
  teamContent: {
    backgroundColor: '#f8f8f8',
    padding: 12,
    borderRadius: 8,
  },
  teamName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333',
  },
  teamDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  chip: {
    marginRight: 6,
    marginBottom: 4,
    height: 24,
  },
  recordContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 12,
    paddingVertical: 8,
    backgroundColor: '#ffffff',
    borderRadius: 6,
  },
  recordItem: {
    alignItems: 'center',
  },
  recordValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1976d2',
  },
  recordLabel: {
    fontSize: 10,
    color: '#666',
    marginTop: 2,
  },
  additionalStats: {
    backgroundColor: '#ffffff',
    padding: 8,
    borderRadius: 6,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  statValue: {
    fontSize: 12,
    fontWeight: '500',
    color: '#333',
  },
  positive: {
    color: '#4caf50',
  },
  negative: {
    color: '#f44336',
  },
  errorText: {
    textAlign: 'center',
    color: '#666',
    padding: 20,
  },
});
