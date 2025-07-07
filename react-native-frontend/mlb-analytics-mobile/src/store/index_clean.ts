import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { mlbApi } from '../services/mlbApi';
import type { User, UserPreferences, DashboardWidget } from '../types';

// Auth Store
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const { token, user } = await mlbApi.login(email, password);
          set({ 
            user, 
            isAuthenticated: true, 
            isLoading: false 
          });
        } catch (error: any) {
          set({ 
            error: error.message, 
            isLoading: false 
          });
          throw error;
        }
      },

      register: async (userData: any) => {
        set({ isLoading: true, error: null });
        try {
          const { token, user } = await mlbApi.register(userData);
          set({ 
            user, 
            isAuthenticated: true, 
            isLoading: false 
          });
        } catch (error: any) {
          set({ 
            error: error.message, 
            isLoading: false 
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await mlbApi.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false,
            error: null
          });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      updatePreferences: async (preferences: Partial<UserPreferences>) => {
        const { user } = get();
        if (!user) return;
        
        try {
          const updatedPreferences = { ...user.preferences, ...preferences };
          // For now, just update locally
          set({ 
            user: { ...user, preferences: updatedPreferences } 
          });
        } catch (error: any) {
          set({ error: error.message });
          throw error;
        }
      }
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// Dashboard Store
interface DashboardState {
  widgets: DashboardWidget[];
  isLoading: boolean;
  lastUpdated: number | null;
  
  // Actions
  loadDashboard: () => Promise<void>;
  addWidget: (widget: DashboardWidget) => void;
  removeWidget: (id: string) => void;
  updateWidget: (id: string, data: any) => void;
  reorderWidgets: (widgets: DashboardWidget[]) => void;
  toggleWidget: (id: string) => void;
  refreshDashboard: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set, get) => ({
      widgets: [],
      isLoading: false,
      lastUpdated: null,

      loadDashboard: async () => {
        set({ isLoading: true });
        try {
          // For now, create default widgets
          const defaultWidgets: DashboardWidget[] = [
            {
              id: '1',
              type: 'standings',
              title: 'AL East Standings',
              config: { division: 'AL East' },
              position: 0,
              isVisible: true,
              size: 'medium'
            }
          ];
          set({ 
            widgets: defaultWidgets,
            lastUpdated: Date.now(),
            isLoading: false
          });
        } catch (error) {
          console.error('Dashboard load error:', error);
          set({ isLoading: false });
        }
      },

      addWidget: (widget: DashboardWidget) => {
        const { widgets } = get();
        set({ widgets: [...widgets, widget] });
      },

      removeWidget: (id: string) => {
        const { widgets } = get();
        set({ widgets: widgets.filter(w => w.id !== id) });
      },

      updateWidget: (id: string, data: any) => {
        const { widgets } = get();
        const updatedWidgets = widgets.map(widget =>
          widget.id === id ? { ...widget, data } : widget
        );
        set({ widgets: updatedWidgets });
      },

      reorderWidgets: (widgets: DashboardWidget[]) => {
        set({ widgets });
      },

      toggleWidget: (id: string) => {
        const { widgets } = get();
        const updatedWidgets = widgets.map(widget =>
          widget.id === id ? { ...widget, isVisible: !widget.isVisible } : widget
        );
        set({ widgets: updatedWidgets });
      },

      refreshDashboard: async () => {
        // Reload dashboard data
        await get().loadDashboard();
      }
    }),
    {
      name: 'dashboard-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// Search Store
interface SearchState {
  recentSearches: Array<{
    id: string;
    query: string;
    timestamp: number;
    results: number;
  }>;
  isSearching: boolean;
  currentResults: any[];
  
  // Actions
  addSearch: (query: string, results: any[]) => void;
  clearSearchHistory: () => void;
  setSearchResults: (results: any[]) => void;
  setSearching: (isSearching: boolean) => void;
}

export const useSearchStore = create<SearchState>()(
  persist(
    (set, get) => ({
      recentSearches: [],
      isSearching: false,
      currentResults: [],

      addSearch: (query: string, results: any[]) => {
        const { recentSearches } = get();
        const newSearch = {
          id: Date.now().toString(),
          query,
          timestamp: Date.now(),
          results: results.length
        };
        
        // Keep only last 20 searches
        const updatedSearches = [newSearch, ...recentSearches.slice(0, 19)];
        set({ recentSearches: updatedSearches });
      },

      clearSearchHistory: () => {
        set({ recentSearches: [] });
      },

      setSearchResults: (results: any[]) => {
        set({ currentResults: results });
      },

      setSearching: (isSearching: boolean) => {
        set({ isSearching });
      }
    }),
    {
      name: 'search-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// Favorites Store
interface FavoritesState {
  favoriteTeams: number[];
  favoritePlayers: number[];
  
  // Actions
  addFavoriteTeam: (teamId: number) => Promise<void>;
  removeFavoriteTeam: (teamId: number) => void;
  addFavoritePlayer: (playerId: number) => Promise<void>;
  removeFavoritePlayer: (playerId: number) => void;
  isFavoriteTeam: (teamId: number) => boolean;
  isFavoritePlayer: (playerId: number) => boolean;
}

export const useFavoritesStore = create<FavoritesState>()(
  persist(
    (set, get) => ({
      favoriteTeams: [],
      favoritePlayers: [],

      addFavoriteTeam: async (teamId: number) => {
        try {
          await mlbApi.addFavoriteTeam(teamId);
          const { favoriteTeams } = get();
          if (!favoriteTeams.includes(teamId)) {
            set({ favoriteTeams: [...favoriteTeams, teamId] });
          }
        } catch (error) {
          console.error('Add favorite team error:', error);
          throw error;
        }
      },

      removeFavoriteTeam: (teamId: number) => {
        const { favoriteTeams } = get();
        set({ favoriteTeams: favoriteTeams.filter(id => id !== teamId) });
      },

      addFavoritePlayer: async (playerId: number) => {
        try {
          await mlbApi.addFavoritePlayer(playerId);
          const { favoritePlayers } = get();
          if (!favoritePlayers.includes(playerId)) {
            set({ favoritePlayers: [...favoritePlayers, playerId] });
          }
        } catch (error) {
          console.error('Add favorite player error:', error);
          throw error;
        }
      },

      removeFavoritePlayer: (playerId: number) => {
        const { favoritePlayers } = get();
        set({ favoritePlayers: favoritePlayers.filter(id => id !== playerId) });
      },

      isFavoriteTeam: (teamId: number) => {
        return get().favoriteTeams.includes(teamId);
      },

      isFavoritePlayer: (playerId: number) => {
        return get().favoritePlayers.includes(playerId);
      }
    }),
    {
      name: 'favorites-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
