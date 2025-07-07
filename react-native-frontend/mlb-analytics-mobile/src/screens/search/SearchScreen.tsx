import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  FlatList,
  Dimensions,
} from 'react-native';
import {
  Text,
  Searchbar,
  Card,
  Title,
  Paragraph,
  Chip,
  List,
  ActivityIndicator,
  Button,
  Divider,
} from 'react-native-paper';
import { useSearchStore } from '../../store';
import { mlbApi } from '../../services/mlbApi';
import type { SearchResult, NaturalLanguageQuery } from '../../types';

interface Props {
  navigation: any;
}

const { width } = Dimensions.get('window');

export default function SearchScreen({ navigation }: Props) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [nlResponse, setNlResponse] = useState<NaturalLanguageQuery | null>(null);
  const { recentSearches, addSearch } = useSearchStore();

  const popularQueries = [
    "Who leads the league in home runs?",
    "Show me the Yankees roster",
    "What are Shohei Ohtani's stats this season?",
    "AL West standings",
    "Best ERA in the National League",
    "Red Sox vs Yankees head to head",
    "Top rookie performers",
    "Injury reports this week",
  ];

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      // Try natural language search first
      const nlResult = await mlbApi.naturalLanguageSearch(searchQuery);
      if (nlResult) {
        setNlResponse(nlResult);
        addSearch(searchQuery, nlResult.results || []);
      }

      // Also get general search results
      const searchResult = await mlbApi.searchPlayers(searchQuery);
      if (searchResult && searchResult.length > 0) {
        const searchResults: SearchResult[] = searchResult.map((player: any) => ({
          id: player.id,
          type: 'player' as const,
          title: player.name,
          subtitle: `${player.position} - ${player.team}`,
          data: player,
          relevance: 1,
        }));
        setResults(searchResults);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResultPress = (result: SearchResult) => {
    switch (result.type) {
      case 'player':
        navigation.navigate('PlayerProfile', { playerId: result.id });
        break;
      case 'team':
        navigation.navigate('TeamDetails', { teamId: result.id });
        break;
      default:
        // Handle other result types
        break;
    }
  };

  const renderSearchResult = ({ item }: { item: SearchResult }) => (
    <List.Item
      title={item.title}
      description={item.subtitle}
      left={(props) => (
        <List.Icon
          {...props}
          icon={
            item.type === 'player' ? 'account' :
            item.type === 'team' ? 'shield' :
            item.type === 'game' ? 'baseball' : 'chart-line'
          }
        />
      )}
      onPress={() => handleResultPress(item)}
      style={styles.resultItem}
    />
  );

  const renderPopularQuery = (queryText: string, index: number) => (
    <Chip
      key={index}
      mode="outlined"
      onPress={() => {
        setQuery(queryText);
        handleSearch(queryText);
      }}
      style={styles.chip}
    >
      {queryText}
    </Chip>
  );

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <Searchbar
          placeholder="Ask anything about baseball..."
          onChangeText={setQuery}
          value={query}
          onSubmitEditing={() => handleSearch(query)}
          style={styles.searchbar}
          inputStyle={styles.searchInput}
        />
        {loading && (
          <ActivityIndicator
            animating={true}
            style={styles.loadingIndicator}
          />
        )}
      </View>

      <ScrollView style={styles.content}>
        {nlResponse && (
          <Card style={styles.nlResponseCard}>
            <Card.Content>
              <Title style={styles.nlTitle}>Answer</Title>
              <Paragraph style={styles.nlResponse}>
                {nlResponse.response}
              </Paragraph>
              {nlResponse.data && (
                <View style={styles.nlDataContainer}>
                  <Text style={styles.nlDataLabel}>Related Data:</Text>
                  <Text style={styles.nlData}>
                    {JSON.stringify(nlResponse.data, null, 2)}
                  </Text>
                </View>
              )}
            </Card.Content>
          </Card>
        )}

        {results.length > 0 && (
          <Card style={styles.resultsCard}>
            <Card.Content>
              <Title style={styles.sectionTitle}>Search Results</Title>
              <FlatList
                data={results}
                renderItem={renderSearchResult}
                keyExtractor={(item) => item.id}
                scrollEnabled={false}
              />
            </Card.Content>
          </Card>
        )}

        {!loading && query === '' && (
          <>
            <Card style={styles.popularCard}>
              <Card.Content>
                <Title style={styles.sectionTitle}>Popular Searches</Title>
                <View style={styles.chipsContainer}>
                  {popularQueries.map(renderPopularQuery)}
                </View>
              </Card.Content>
            </Card>

            {recentSearches.length > 0 && (
              <Card style={styles.historyCard}>
                <Card.Content>
                  <Title style={styles.sectionTitle}>Recent Searches</Title>
                  {recentSearches.slice(0, 5).map((historyItem, index) => (
                    <List.Item
                      key={index}
                      title={historyItem.query}
                      left={(props) => <List.Icon {...props} icon="history" />}
                      onPress={() => {
                        setQuery(historyItem.query);
                        handleSearch(historyItem.query);
                      }}
                    />
                  ))}
                </Card.Content>
              </Card>
            )}
          </>
        )}

        {!loading && query !== '' && results.length === 0 && !nlResponse && (
          <Card style={styles.noResultsCard}>
            <Card.Content>
              <Title style={styles.noResultsTitle}>No Results Found</Title>
              <Paragraph style={styles.noResultsText}>
                Try rephrasing your search or use different keywords.
              </Paragraph>
              <Button
                mode="outlined"
                onPress={() => setQuery('')}
                style={styles.clearButton}
              >
                Clear Search
              </Button>
            </Card.Content>
          </Card>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchContainer: {
    padding: 16,
    backgroundColor: '#fff',
    elevation: 2,
  },
  searchbar: {
    elevation: 0,
    backgroundColor: '#f8f8f8',
  },
  searchInput: {
    fontSize: 16,
  },
  loadingIndicator: {
    marginTop: 10,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  nlResponseCard: {
    marginBottom: 16,
    backgroundColor: '#e3f2fd',
  },
  nlTitle: {
    color: '#1976d2',
    marginBottom: 8,
  },
  nlResponse: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
  },
  nlDataContainer: {
    marginTop: 12,
    padding: 8,
    backgroundColor: '#f5f5f5',
    borderRadius: 4,
  },
  nlDataLabel: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  nlData: {
    fontSize: 12,
    fontFamily: 'monospace',
    color: '#666',
  },
  resultsCard: {
    marginBottom: 16,
  },
  sectionTitle: {
    marginBottom: 12,
    color: '#333',
  },
  resultItem: {
    backgroundColor: '#f8f8f8',
    marginBottom: 4,
    borderRadius: 8,
  },
  popularCard: {
    marginBottom: 16,
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    marginBottom: 8,
    marginRight: 8,
  },
  historyCard: {
    marginBottom: 16,
  },
  noResultsCard: {
    marginTop: 32,
    alignItems: 'center',
  },
  noResultsTitle: {
    textAlign: 'center',
    marginBottom: 8,
  },
  noResultsText: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 16,
  },
  clearButton: {
    marginTop: 8,
  },
});
