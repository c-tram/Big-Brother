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
  bats: string;
  throws: string;
  stats: {
    batting?: BattingStats;
    pitching?: PitchingStats;
    fielding?: FieldingStats;
  };
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
  homeRuns: number;
  rbi: number;
  stolen_bases: number;
  batting_average: number;
  on_base_percentage: number;
  slugging_percentage: number;
  ops: number;
  strikeouts: number;
  walks: number;
}

export interface PitchingStats {
  games: number;
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
  holds?: number;
  blown_saves?: number;
}

export interface FieldingStats {
  games: number;
  putouts: number;
  assists: number;
  errors: number;
  fielding_percentage: number;
  double_plays?: number;
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
  favoriteTeam?: string;
  favoritePlayer?: string;
  dashboardWidgets: DashboardWidget[];
  theme: 'light' | 'dark';
  notifications: boolean;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}

export interface DashboardWidget {
  id: string;
  type: 'team_stats' | 'player_stats' | 'standings' | 'recent_games' | 'predictions' | 'chart';
  title: string;
  config: any;
  position: number;
  isVisible: boolean;
}

export interface Player {
  id: string;
  name: string;
  position: string;
  team: string;
  jerseyNumber: number;
  age: number;
  height: string;
  weight: string;
  bats: 'R' | 'L' | 'S';
  throws: 'R' | 'L';
  stats: PlayerStats;
  imageUrl?: string;
}

export interface PlayerStats {
  batting?: BattingStats;
  pitching?: PitchingStats;
  fielding?: FieldingStats;
}

export interface BattingStats {
  games: number;
  atBats: number;
  runs: number;
  hits: number;
  doubles: number;
  triples: number;
  homeRuns: number;
  rbi: number;
  stolen_bases: number;
  caught_stealing: number;
  walks: number;
  strikeouts: number;
  batting_average: number;
  on_base_percentage: number;
  slugging_percentage: number;
  ops: number;
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
  walks: number;
  strikeouts: number;
  era: number;
  whip: number;
  k_per_9: number;
  bb_per_9: number;
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

export interface Team {
  id: string;
  name: string;
  location: string;
  abbreviation: string;
  division: string;
  league: 'AL' | 'NL';
  logoUrl?: string;
  colors: {
    primary: string;
    secondary: string;
  };
  stats: TeamStats;
}

export interface TeamStats {
  wins: number;
  losses: number;
  winning_percentage: number;
  games_back: number;
  runs_scored: number;
  runs_allowed: number;
  run_differential: number;
  home_record: string;
  away_record: string;
  last_ten: string;
  streak: string;
}

export interface Game {
  id: string;
  date: string;
  homeTeam: Team;
  awayTeam: Team;
  homeScore?: number;
  awayScore?: number;
  status: 'scheduled' | 'in_progress' | 'final' | 'postponed' | 'cancelled';
  inning?: number;
  venue: string;
}

export interface SearchResult {
  id: string;
  type: 'player' | 'team' | 'stat' | 'game';
  title: string;
  subtitle: string;
  data: any;
  relevance: number;
}

export interface NaturalLanguageQuery {
  query: string;
  intent: string;
  entities: any[];
  response: string;
  data?: any;
}

export interface Venue {
  id: string;
  name: string;
  location: string;
  capacity: number;
  surface: string;
  dimensions: {
    leftField: number;
    centerField: number;
    rightField: number;
    foulTerritory: string;
  };
}

export interface ChartData {
  labels: string[];
  datasets: {
    data: number[];
    color?: (opacity: number) => string;
    strokeWidth?: number;
  }[];
}

export interface APIResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

export interface FavoriteItem {
  id: string;
  type: 'player' | 'team';
  name: string;
  details: any;
  dateAdded: string;
}
