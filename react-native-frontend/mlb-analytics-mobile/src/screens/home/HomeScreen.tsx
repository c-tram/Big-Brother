import React, { useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
} from 'react-native';
import {
  Text,
  Card,
  Title,
  Button,
  FAB,
  Portal,
  Modal,
  List,
  IconButton,
} from 'react-native-paper';
import { useDashboardStore, useAuthStore } from '../../store';
import { mlbApi } from '../../services/mlbApi';
import StandingsWidget from '../../components/widgets/StandingsWidget';
import PlayerStatsWidget from '../../components/widgets/PlayerStatsWidget';
import TeamStatsWidget from '../../components/widgets/TeamStatsWidget';
import RecentGamesWidget from '../../components/widgets/RecentGamesWidget';
import type { DashboardWidget } from '../../types';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const { user } = useAuthStore();
  const { widgets, addWidget, removeWidget, updateWidget } = useDashboardStore();
  const [refreshing, setRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);

  const availableWidgets = [
    {
      type: 'standings',
      title: 'League Standings',
      description: 'Current MLB standings',
      icon: 'format-list-numbered',
    },
    {
      type: 'team_stats',
      title: 'Team Statistics',
      description: 'Your favorite team stats',
      icon: 'chart-line',
    },
    {
      type: 'player_stats',
      title: 'Player Statistics',
      description: 'Track your favorite players',
      icon: 'account-star',
    },
    {
      type: 'recent_games',
      title: 'Recent Games',
      description: 'Latest game results',
      icon: 'baseball',
    },
  ];

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      // Refresh dashboard data
      await Promise.all([
        // Add any specific refresh logic here
      ]);
    } catch (error) {
      console.error('Error refreshing dashboard:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleAddWidget = (widgetType: string) => {
    const widgetConfig = availableWidgets.find(w => w.type === widgetType);
    if (widgetConfig) {
      const newWidget: DashboardWidget = {
        id: Date.now().toString(),
        type: widgetType as any,
        title: widgetConfig.title,
        config: {},
        position: widgets.length,
        isVisible: true,
      };
      addWidget(newWidget);
    }
    setShowAddModal(false);
  };

  const renderWidget = (widget: DashboardWidget) => {
    if (!widget.isVisible) return null;

    const widgetProps = {
      widget,
      onUpdate: updateWidget,
      isEditMode,
      onRemove: () => removeWidget(widget.id),
    };

    switch (widget.type) {
      case 'standings':
        return <StandingsWidget key={widget.id} {...widgetProps} />;
      case 'team_stats':
        return <TeamStatsWidget key={widget.id} {...widgetProps} />;
      case 'player_stats':
        return <PlayerStatsWidget key={widget.id} {...widgetProps} />;
      case 'recent_games':
        return <RecentGamesWidget key={widget.id} {...widgetProps} />;
      default:
        return (
          <Card key={widget.id} style={styles.widget}>
            <Card.Content>
              <Title>Widget Loading...</Title>
              <Text>Widget type '{widget.type}' not recognized</Text>
            </Card.Content>
          </Card>
        );
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.header}>
          <Title style={styles.welcomeText}>
            Welcome back, {user?.firstName || 'User'}!
          </Title>
          <IconButton
            icon={isEditMode ? 'check' : 'pencil'}
            mode={isEditMode ? 'contained' : 'outlined'}
            onPress={() => setIsEditMode(!isEditMode)}
            size={20}
          />
        </View>

        {widgets.length === 0 ? (
          <Card style={styles.emptyState}>
            <Card.Content>
              <Title style={styles.emptyTitle}>Your Dashboard is Empty</Title>
              <Text style={styles.emptyText}>
                Add widgets to customize your baseball analytics experience
              </Text>
              <Button
                mode="contained"
                onPress={() => setShowAddModal(true)}
                style={styles.addButton}
              >
                Add Your First Widget
              </Button>
            </Card.Content>
          </Card>
        ) : (
          <View style={styles.widgetsContainer}>
            {widgets
              .sort((a, b) => a.position - b.position)
              .map(renderWidget)}
          </View>
        )}
      </ScrollView>

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => setShowAddModal(true)}
        label={widgets.length === 0 ? undefined : 'Add Widget'}
      />

      <Portal>
        <Modal
          visible={showAddModal}
          onDismiss={() => setShowAddModal(false)}
          contentContainerStyle={styles.modalContent}
        >
          <Title style={styles.modalTitle}>Add Widget</Title>
          {availableWidgets.map((widget) => (
            <List.Item
              key={widget.type}
              title={widget.title}
              description={widget.description}
              left={(props) => <List.Icon {...props} icon={widget.icon} />}
              onPress={() => handleAddWidget(widget.type)}
              style={styles.widgetOption}
            />
          ))}
          <Button
            mode="outlined"
            onPress={() => setShowAddModal(false)}
            style={styles.cancelButton}
          >
            Cancel
          </Button>
        </Modal>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingBottom: 8,
  },
  welcomeText: {
    flex: 1,
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  emptyState: {
    margin: 16,
    padding: 20,
    alignItems: 'center',
  },
  emptyTitle: {
    textAlign: 'center',
    marginBottom: 8,
  },
  emptyText: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 16,
  },
  addButton: {
    marginTop: 8,
  },
  widgetsContainer: {
    padding: 8,
  },
  widget: {
    margin: 8,
    elevation: 2,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#1976d2',
  },
  modalContent: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 8,
  },
  modalTitle: {
    textAlign: 'center',
    marginBottom: 16,
  },
  widgetOption: {
    marginBottom: 8,
    borderRadius: 8,
    backgroundColor: '#f8f8f8',
  },
  cancelButton: {
    marginTop: 16,
  },
});
