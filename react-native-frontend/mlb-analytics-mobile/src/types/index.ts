// filepath: /Users/coletrammell/Documents/GitHub/Big-Brother/react-native-frontend/mlb-analytics-mobile/src/types/index.ts
// Comprehensive type definitions for MLB Analytics Mobile App

// Core MLB Data Types
export interface Player {
  id: string;
  name: string;
  jerseyNumber: number;
  position: string;
  team: string;
  age: number;
  height: string;
  weight: string;
  bats: 'R' | 'L' | 'S';
  throws: 'R' | 'L';
  stats: {
    batting?: BattingStats;
    pitching?: PitchingStats;
    fielding?: FieldingStats;
  };
  imageUrl?: string;
}

export interface Team {
  id: string;
  name: string;
  location: string;
  abbreviation: string;
  division: string;
  league: string;
  stats: TeamStats;
}

export interface Game {
  id: string;
  date: string;
  status: 'scheduled' | 'live' | 'final' | 'postponed' | 'cancelled';
  homeTeam: Team;
  awayTeam: Team;
  homeScore?: number;
  awayScore?: number;
  inning?: number;
  venue?: string;
}

// Statistics Types
export interface BattingStats {
  games: number;
  atBats: number;
  hits: number;
  runs: number;
  doubles: number;
  triples: number;
  homeRuns: number;
  rbi: number;
  stolen_bases: number;
  caught_stealing: number;
  batting_average: number;
  on_base_percentage: number;
  slugging_percentage: number;
  ops: number;
  strikeouts: number;
  walks: number;
}

export interface PitchingStats {
  games: number;
  games_started: number;
  wins: number;
  losses: number;
  saves: number;
  innings_pitched: number;
  hits_allowed: number;
  runs_allowed: number;
  earned_runs: number;
  era: number;
  strikeouts: number;
  walks: number;
  whip: number;
  k_per_9: number;
  bb_per_9: number;
  holds?: number;
  blown_saves?: number;
}

export interface FieldingStats {
  games: number;
  innings: number;
  chances: number;
  putouts: number;
  assists: number;
  errors: number;
  fielding_percentage: number;
  double_plays: number;
}

export interface TeamStats {
  wins: number;
  losses: number;
  winning_percentage: number;
  games_back: number;
  home_record: string;
  away_record: string;
  last_ten: string;
  streak: string;
  runs_scored: number;
  runs_allowed: number;
  run_differential: number;
}

// User Types
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  preferences?: UserPreferences;
  dateJoined: string;
  lastLogin?: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  notifications: boolean;
  favoriteTeam?: string;
  favoritePlayer?: string;
  defaultDivision?: string;
  autoRefresh: boolean;
  [key: string]: any;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Dashboard Types
export interface DashboardWidget {
  id: string;
  type: 'standings' | 'team_stats' | 'player_stats' | 'recent_games' | 'upcoming_games' | 'favorites';
  title: string;
  config: WidgetConfig;
  position: number;
  isVisible: boolean;
  size?: 'small' | 'medium' | 'large';
}

export interface WidgetConfig {
  teamId?: string;
  playerId?: string;
  division?: string;
  league?: string;
  statType?: string;
  timeframe?: string;
  [key: string]: any;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T = any> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
  page?: number;
  total_pages?: number;
}

// Search Types
export interface SearchResult {
  id: string;
  type: 'player' | 'team' | 'game' | 'stat';
  title: string;
  subtitle: string;
  data: any;
  relevance: number;
}

export interface NaturalLanguageQuery {
  query: string;
  response: string;
  data?: any;
  confidence: number;
  timestamp: string;
}

export interface SearchHistoryItem {
  id: string;
  query: string;
  timestamp: string;
  results_count: number;
}

// Favorites Types
export interface FavoriteItem {
  id: string;
  type: 'player' | 'team';
  name: string;
  details?: any;
  dateAdded: string;
}

// Chart Types
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  data: number[];
  color?: (opacity?: number) => string;
  strokeWidth?: number;
  label?: string;
}

// Store Types
export interface DashboardStore {
  widgets: DashboardWidget[];
  addWidget: (widget: DashboardWidget) => void;
  removeWidget: (id: string) => void;
  updateWidget: (id: string, updates: Partial<DashboardWidget>) => void;
  reorderWidgets: (widgets: DashboardWidget[]) => void;
  loadWidgets: () => Promise<void>;
  saveWidgets: () => Promise<void>;
}

export interface SearchStore {
  searchHistory: SearchHistoryItem[];
  recentResults: SearchResult[];
  addToHistory: (query: string) => void;
  clearHistory: () => void;
  saveResults: (results: SearchResult[]) => void;
  loadHistory: () => Promise<void>;
}

export interface FavoritesStore {
  favorites: FavoriteItem[];
  addFavorite: (item: FavoriteItem) => void;
  removeFavorite: (id: string) => void;
  isFavorite: (id: string, type: 'player' | 'team') => boolean;
  loadFavorites: () => Promise<void>;
  saveFavorites: () => Promise<void>;
}

export interface MLBDataStore {
  teams: Team[];
  players: Player[];
  games: Game[];
  standings: any[];
  lastUpdated: { [key: string]: number };
  cacheTeams: (teams: Team[]) => void;
  cachePlayers: (players: Player[]) => void;
  cacheGames: (games: Game[]) => void;
  cacheStandings: (standings: any[]) => void;
  isDataStale: (key: string, ttl?: number) => boolean;
  clearCache: () => void;
}

// Navigation Types
export type RootStackParamList = {
  AuthStack: undefined;
  MainTabs: undefined;
  PlayerProfile: { playerId: string };
  TeamDetails: { teamId: string };
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Search: undefined;
  Favorites: undefined;
  Settings: undefined;
};

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: any;
}

// Advanced Types
export interface Venue {
  id: string;
  name: string;
  location: string;
  capacity: number;
  surface: string;
  opened: number;
}

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  content: string;
  author: string;
  publishedAt: string;
  category: 'trade' | 'injury' | 'stats' | 'general';
  relatedPlayers?: string[];
  relatedTeams?: string[];
  imageUrl?: string;
}

export interface Notification {
  id: string;
  type: 'game_start' | 'game_end' | 'player_milestone' | 'trade' | 'injury';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  data?: any;
}
