import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mlbApi } from '../services/mlbApi';
import { useAuthStore, useFavoritesStore } from '../store';
import type { Player, Team, Game } from '../types';

// Authentication hooks
export const useAuth = () => {
  const { user, isAuthenticated, login, logout } = useAuthStore();
  
  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      mlbApi.login(email, password),
    onSuccess: (data) => {
      login(data.user, data.token);
    },
  });

  const registerMutation = useMutation({
    mutationFn: (userData: any) => mlbApi.register(userData),
    onSuccess: (data) => {
      login(data.user, data.token);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => mlbApi.logout(),
    onSuccess: () => {
      logout();
    },
  });

  return {
    user,
    isAuthenticated,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
};

// Player data hooks
export const usePlayer = (playerId: string) => {
  return useQuery({
    queryKey: ['player', playerId],
    queryFn: () => mlbApi.getPlayerProfile(parseInt(playerId, 10)),
    enabled: !!playerId && !isNaN(parseInt(playerId, 10)),
  });
};

export const usePlayerSearch = (query: string) => {
  return useQuery({
    queryKey: ['players', 'search', query],
    queryFn: () => mlbApi.searchPlayers(query),
    enabled: query.length > 2,
  });
};

// Team data hooks
export const useTeam = (teamId: string) => {
  return useQuery({
    queryKey: ['team', teamId],
    queryFn: () => mlbApi.getTeamProfile(parseInt(teamId, 10)),
    enabled: !!teamId && !isNaN(parseInt(teamId, 10)),
  });
};

export const useTeamGames = (teamId: string) => {
  return useQuery({
    queryKey: ['team', teamId, 'games'],
    queryFn: () => mlbApi.getTeamGames(parseInt(teamId, 10)),
    enabled: !!teamId && !isNaN(parseInt(teamId, 10)),
  });
};

// Standings hook
export const useStandings = (division?: string) => {
  return useQuery({
    queryKey: ['standings', division],
    queryFn: () => mlbApi.getStandings(division),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Games hooks
export const useRecentGames = () => {
  return useQuery({
    queryKey: ['games', 'recent'],
    queryFn: () => mlbApi.getRecentGames(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useUpcomingGames = () => {
  return useQuery({
    queryKey: ['games', 'upcoming'],
    queryFn: () => mlbApi.getUpcomingGames(),
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
};

// Natural language search hook
export const useNaturalLanguageSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const search = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults(null);
      return;
    }

    setLoading(true);
    try {
      const response = await mlbApi.naturalLanguageSearch(searchQuery);
      if (response.success) {
        setResults(response.data);
      }
    } catch (error) {
      console.error('Natural language search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return {
    query,
    setQuery,
    results,
    loading,
    search,
  };
};

// Favorites hooks
export const useFavorites = () => {
  const { favoriteTeams, favoritePlayers, addFavoriteTeam, addFavoritePlayer, removeFavoriteTeam, removeFavoritePlayer } = useFavoritesStore();
  const queryClient = useQueryClient();

  const addTeamMutation = useMutation({
    mutationFn: (teamId: number) => addFavoriteTeam(teamId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  const addPlayerMutation = useMutation({
    mutationFn: (playerId: number) => addFavoritePlayer(playerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  return {
    favoriteTeams,
    favoritePlayers,
    addFavoriteTeam: addTeamMutation.mutate,
    addFavoritePlayer: addPlayerMutation.mutate,
    removeFavoriteTeam,
    removeFavoritePlayer,
    isAddingFavorite: addTeamMutation.isPending || addPlayerMutation.isPending,
  };
};

// Dashboard hooks
export const useDashboard = () => {
  const queryClient = useQueryClient();

  const refreshDashboard = () => {
    queryClient.invalidateQueries({ queryKey: ['standings'] });
    queryClient.invalidateQueries({ queryKey: ['games'] });
    queryClient.invalidateQueries({ queryKey: ['favorites'] });
  };

  return {
    refreshDashboard,
  };
};

// Custom hook for data fetching with loading states
export const useAsyncData = <T>(
  fetchFn: () => Promise<T>,
  dependencies: any[] = []
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchFn();
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'An error occurred');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, dependencies);

  const refetch = () => {
    setLoading(true);
    setError(null);
    fetchFn()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : 'An error occurred'))
      .finally(() => setLoading(false));
  };

  return { data, loading, error, refetch };
};

// Hook for managing form state
export const useForm = <T extends Record<string, any>>(
  initialValues: T,
  validationRules?: Partial<Record<keyof T, (value: any) => string | null>>
) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const setValue = (field: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const setFieldTouched = (field: keyof T) => {
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  const validate = (): boolean => {
    if (!validationRules) return true;

    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;

    Object.keys(validationRules).forEach((field) => {
      const rule = validationRules[field as keyof T];
      if (rule) {
        const error = rule(values[field as keyof T]);
        if (error) {
          newErrors[field as keyof T] = error;
          isValid = false;
        }
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const reset = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  };

  return {
    values,
    errors,
    touched,
    setValue,
    setFieldTouched,
    validate,
    reset,
    isValid: Object.keys(errors).length === 0,
  };
};
