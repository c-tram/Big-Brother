import AsyncStorage from '@react-native-async-storage/async-storage';

export const storage = {
  // Store data
  setItem: async (key: string, value: any): Promise<void> => {
    try {
      const jsonValue = JSON.stringify(value);
      await AsyncStorage.setItem(key, jsonValue);
    } catch (error) {
      console.error('Error storing data:', error);
      throw error;
    }
  },

  // Retrieve data
  getItem: async <T>(key: string): Promise<T | null> => {
    try {
      const jsonValue = await AsyncStorage.getItem(key);
      return jsonValue != null ? JSON.parse(jsonValue) : null;
    } catch (error) {
      console.error('Error retrieving data:', error);
      return null;
    }
  },

  // Remove data
  removeItem: async (key: string): Promise<void> => {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing data:', error);
      throw error;
    }
  },

  // Clear all data
  clear: async (): Promise<void> => {
    try {
      await AsyncStorage.clear();
    } catch (error) {
      console.error('Error clearing storage:', error);
      throw error;
    }
  },
};

// Storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: '@mlb_app:auth_token',
  USER_DATA: '@mlb_app:user_data',
  DASHBOARD_WIDGETS: '@mlb_app:dashboard_widgets',
  SEARCH_HISTORY: '@mlb_app:search_history',
  FAVORITES: '@mlb_app:favorites',
  MLB_DATA_CACHE: '@mlb_app:mlb_data_cache',
  USER_PREFERENCES: '@mlb_app:user_preferences',
};

// Helper functions for specific data types
export const authStorage = {
  setToken: (token: string) => storage.setItem(STORAGE_KEYS.AUTH_TOKEN, token),
  getToken: () => storage.getItem<string>(STORAGE_KEYS.AUTH_TOKEN),
  removeToken: () => storage.removeItem(STORAGE_KEYS.AUTH_TOKEN),
  
  setUser: (user: any) => storage.setItem(STORAGE_KEYS.USER_DATA, user),
  getUser: () => storage.getItem<any>(STORAGE_KEYS.USER_DATA),
  removeUser: () => storage.removeItem(STORAGE_KEYS.USER_DATA),
};

export const cacheStorage = {
  set: (key: string, data: any, ttl: number = 5 * 60 * 1000) => {
    const cacheItem = {
      data,
      timestamp: Date.now(),
      ttl,
    };
    return storage.setItem(`cache:${key}`, cacheItem);
  },

  get: async <T>(key: string): Promise<T | null> => {
    const cacheItem = await storage.getItem<{
      data: T;
      timestamp: number;
      ttl: number;
    }>(`cache:${key}`);

    if (!cacheItem) return null;

    const isExpired = Date.now() - cacheItem.timestamp > cacheItem.ttl;
    if (isExpired) {
      await storage.removeItem(`cache:${key}`);
      return null;
    }

    return cacheItem.data;
  },

  remove: (key: string) => storage.removeItem(`cache:${key}`),
};

// Date formatting helpers
export const formatDate = (date: string | Date): string => {
  return new Date(date).toLocaleDateString();
};

export const formatDateTime = (date: string | Date): string => {
  return new Date(date).toLocaleString();
};

export const formatTime = (date: string | Date): string => {
  return new Date(date).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

// Baseball specific formatters
export const formatBattingAverage = (avg: number): string => {
  return avg.toFixed(3);
};

export const formatERA = (era: number): string => {
  return era.toFixed(2);
};

export const formatRecord = (wins: number, losses: number): string => {
  return `${wins}-${losses}`;
};

export const formatWinningPercentage = (pct: number): string => {
  return pct.toFixed(3);
};

// Validation helpers
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPassword = (password: string): boolean => {
  return password.length >= 8;
};

// Error handling
export const handleApiError = (error: any): string => {
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  if (error?.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

// Color helpers for team themes
export const getTeamColors = (teamAbbr: string): { primary: string; secondary: string } => {
  const teamColors: { [key: string]: { primary: string; secondary: string } } = {
    NYY: { primary: '#132448', secondary: '#C4CED4' },
    BOS: { primary: '#BD3039', secondary: '#0C2340' },
    TB: { primary: '#092C5C', secondary: '#8FBCE6' },
    TOR: { primary: '#134A8E', secondary: '#1D2D5C' },
    BAL: { primary: '#DF4601', secondary: '#000000' },
    // Add more teams as needed
  };
  
  return teamColors[teamAbbr] || { primary: '#1976d2', secondary: '#424242' };
};

// Debounce function for search
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};
