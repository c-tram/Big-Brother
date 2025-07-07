/**
 * MLB Analytics API Service
 * Connects to Django backend with comprehensive MLB API coverage
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

// API Configuration
const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl || 
  (__DEV__ ? 'http://10.0.0.22:8000' : 'https://your-production-api.com');

interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

interface PlayerSearchResult {
  id: number;
  fullName: string;
  primaryPosition: string;
  currentTeam: string;
  active: boolean;
}

interface VenuePerformance {
  player: {
    id: number;
    name: string;
    position: string;
    currentTeam: string;
  };
  venue: {
    id: number;
    name: string;
    city: string;
    state: string;
  };
  seasons: number[];
  games: Array<{
    gameId: number;
    date: string;
    opponent: string;
    stats: {
      atBats: number;
      hits: number;
      homeRuns: number;
      rbis: number;
      average: number;
    };
  }>;
  summary: {
    totalGames: number;
    totalAtBats: number;
    totalHits: number;
    totalHomeRuns: number;
    totalRbis: number;
    battingAverage: number;
  };
}

interface PlayerProfile {
  basicInfo: {
    id: number;
    fullName: string;
    birthDate: string;
    position: string;
    team: string;
    jerseyNumber: number;
    bats: string;
    throws: string;
  };
  careerStats: {
    games: number;
    atBats: number;
    hits: number;
    homeRuns: number;
    rbis: number;
    average: number;
    ops: number;
  };
  currentSeasonStats: {
    games: number;
    atBats: number;
    hits: number;
    homeRuns: number;
    rbis: number;
    average: number;
    ops: number;
  };
  recentGames: Array<{
    date: string;
    opponent: string;
    stats: any;
  }>;
}

interface GameData {
  gameId: number;
  date: string;
  teams: {
    home: { name: string; score: number };
    away: { name: string; score: number };
  };
  status: string;
  inning?: number;
  events: Array<{
    inning: number;
    player: string;
    event: string;
    description: string;
  }>;
}

interface SearchQuery {
  query: string;
  type?: 'player' | 'team' | 'venue' | 'general';
  season?: number;
}

interface SearchResult {
  type: 'player' | 'team' | 'venue' | 'stat' | 'game';
  title: string;
  subtitle: string;
  data: any;
  relevance: number;
}

class MLBApiService {
  private api: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadAuthToken();
  }

  private setupInterceptors() {
    // Request interceptor for auth
    this.api.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Token ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh or logout
          await this.handleAuthError();
        }
        return Promise.reject(error);
      }
    );
  }

  private async loadAuthToken() {
    try {
      this.authToken = await SecureStore.getItemAsync('auth_token');
    } catch (error) {
      console.log('No auth token found');
    }
  }

  private async handleAuthError() {
    // Clear auth token and redirect to login
    await SecureStore.deleteItemAsync('auth_token');
    this.authToken = null;
    // You would typically navigate to login screen here
  }

  // Authentication
  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    try {
      const response = await this.api.post('/api/v1/auth/login/', { email, password });
      const { token, user } = response.data;
      
      this.authToken = token;
      await SecureStore.setItemAsync('auth_token', token);
      
      return { token, user };
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  }

  async register(userData: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
  }): Promise<{ token: string; user: any }> {
    try {
      const response = await this.api.post('/api/v1/auth/register/', userData);
      const { token, user } = response.data;
      
      this.authToken = token;
      await SecureStore.setItemAsync('auth_token', token);
      
      return { token, user };
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Registration failed');
    }
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/api/v1/auth/logout/');
    } catch (error) {
      // Even if logout fails, clear local data
    } finally {
      await SecureStore.deleteItemAsync('auth_token');
      this.authToken = null;
    }
  }

  // Core MLB API Methods
  async searchPlayers(query: string): Promise<PlayerSearchResult[]> {
    try {
      const response = await this.api.get('/api/players/search/', {
        params: { q: query, limit: 20 }
      });
      return response.data.results;
    } catch (error: any) {
      console.error('Player search error:', error);
      throw new Error('Failed to search players');
    }
  }

  async getPlayerProfile(playerId: number): Promise<PlayerProfile> {
    try {
      const response = await this.api.get(`/api/v1/players/players/${playerId}/profile/`);
      return response.data;
    } catch (error: any) {
      console.error('Player profile error:', error);
      throw new Error('Failed to get player profile');
    }
  }

  async getPlayerVenuePerformance(
    playerId: number, 
    venueId: number, 
    seasons?: number[]
  ): Promise<VenuePerformance> {
    try {
      const params: any = { venue_id: venueId };
      if (seasons && seasons.length > 0) {
        params.seasons = seasons.join(',');
      }
      
      const response = await this.api.get(`/api/players/${playerId}/venue-performance/`, { params });
      return response.data;
    } catch (error: any) {
      console.error('Venue performance error:', error);
      throw new Error('Failed to get venue performance');
    }
  }

  // Team methods
  async getTeamProfile(teamId: number): Promise<any> {
    try {
      const response = await this.api.get(`/api/v1/teams/teams/${teamId}/profile/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to fetch team profile');
    }
  }

  async getTeamGames(teamId: number): Promise<any[]> {
    try {
      const response = await this.api.get(`/api/v1/teams/teams/${teamId}/games/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to fetch team games');
    }
  }

  // Standings method
  async getStandings(division?: string): Promise<any> {
    try {
      const params = division ? { division } : {};
      const response = await this.api.get('/api/v1/standings/', { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to fetch standings');
    }
  }

  // Games methods
  async getRecentGames(): Promise<any[]> {
    try {
      const response = await this.api.get('/api/v1/games/games/recent/');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to fetch recent games');
    }
  }

  async getUpcomingGames(): Promise<any[]> {
    try {
      const response = await this.api.get('/api/v1/games/games/upcoming/');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to fetch upcoming games');
    }
  }

  // Natural language search
  async naturalLanguageSearch(query: string): Promise<any> {
    try {
      const response = await this.api.post('/api/v1/search/natural/', { query });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Search failed');
    }
  }

  // Favorites methods
  async addFavorite(item: any): Promise<any> {
    try {
      const response = await this.api.post('/api/favorites/', item);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to add favorite');
    }
  }

  async removeFavorite(id: string): Promise<void> {
    try {
      await this.api.delete(`/api/favorites/${id}/`);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to remove favorite');
    }
  }

  // Specific favorite methods for teams and players
  async addFavoriteTeam(teamId: number): Promise<any> {
    try {
      const response = await this.api.post('/api/favorites/teams/', { teamId });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to add favorite team');
    }
  }

  async addFavoritePlayer(playerId: number): Promise<any> {
    try {
      const response = await this.api.post('/api/favorites/players/', { playerId });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to add favorite player');
    }
  }

  // Dashboard method
  async getUserDashboard(): Promise<any> {
    try {
      const response = await this.api.get('/api/dashboard/');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to fetch dashboard');
    }
  }

  // Cache management
  async clearCache(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([
        '@cache_teams',
        '@cache_favorites',
        '@cache_recent_searches'
      ]);
    } catch (error) {
      console.error('Cache clear error:', error);
    }
  }
}

// Export singleton instance
export const mlbApi = new MLBApiService();
export default mlbApi;

// Export types for use in components
export type {
  PlayerSearchResult,
  VenuePerformance,
  PlayerProfile,
  GameData,
  SearchQuery,
  SearchResult
};
