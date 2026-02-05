/**
 * useAuth Hook
 *
 * React hook for JWT authentication management.
 * Handles login, logout, token refresh, and authentication state.
 */

import { useState, useEffect, useCallback } from 'react';
import { axiosClient } from '../lib/axios';

// ============================================================================
// Types
// ============================================================================

export interface User {
  user_id: string;
  username: string;
  email: string;
  roles: string[];
  permissions: string[];
  issued_at: number;
  expires_at: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// ============================================================================
// Token Storage
// ============================================================================

const TOKEN_STORAGE_KEY = 'auth_tokens';
const USER_STORAGE_KEY = 'auth_user';

const saveTokens = (tokens: AuthTokens) => {
  localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
};

const getTokens = (): AuthTokens | null => {
  const stored = localStorage.getItem(TOKEN_STORAGE_KEY);
  return stored ? JSON.parse(stored) : null;
};

const clearTokens = () => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
};

const saveUser = (user: User) => {
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
};

const getUser = (): User | null => {
  const stored = localStorage.getItem(USER_STORAGE_KEY);
  return stored ? JSON.parse(stored) : null;
};

// ============================================================================
// useAuth Hook
// ============================================================================

export const useAuth = () => {
  const [state, setState] = useState<AuthState>({
    user: getUser(),
    isAuthenticated: !!getTokens(),
    isLoading: false,
    error: null,
  });

  // Set auth header for axios
  useEffect(() => {
    const tokens = getTokens();
    if (tokens?.access_token) {
      axiosClient.defaults.headers.common['Authorization'] =
        `Bearer ${tokens.access_token}`;
    }
  }, []);

  // Register new user
  const register = useCallback(async (data: RegisterData) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await axiosClient.post('/auth/register', data);
      const user = response.data;

      // After registration, auto-login
      await login({ username: data.username, password: data.password });

      return user;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      setState((prev) => ({ ...prev, error: errorMessage, isLoading: false }));
      throw error;
    }
  }, []);

  // Login
  const login = useCallback(async (credentials: LoginCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Login request
      const response = await axiosClient.post<AuthTokens>('/auth/login', credentials);
      const tokens = response.data;

      // Save tokens
      saveTokens(tokens);

      // Set axios default header
      axiosClient.defaults.headers.common['Authorization'] =
        `Bearer ${tokens.access_token}`;

      // Get user info
      const userResponse = await axiosClient.get<User>('/auth/me');
      const user = userResponse.data;

      // Save user
      saveUser(user);

      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      return user;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      setState((prev) => ({
        ...prev,
        error: errorMessage,
        isLoading: false,
        isAuthenticated: false,
      }));
      clearTokens();
      throw error;
    }
  }, []);

  // Logout
  const logout = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const tokens = getTokens();

      if (tokens) {
        // Call logout endpoint
        await axiosClient.post('/auth/logout', {
          refresh_token: tokens.refresh_token,
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens and state regardless of API call result
      clearTokens();
      delete axiosClient.defaults.headers.common['Authorization'];

      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  }, []);

  // Refresh token
  const refreshToken = useCallback(async () => {
    const tokens = getTokens();

    if (!tokens?.refresh_token) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axiosClient.post<AuthTokens>('/auth/refresh', {
        refresh_token: tokens.refresh_token,
      });

      const newTokens = response.data;

      // Save new tokens
      saveTokens(newTokens);

      // Update axios header
      axiosClient.defaults.headers.common['Authorization'] =
        `Bearer ${newTokens.access_token}`;

      // Get updated user info
      const userResponse = await axiosClient.get<User>('/auth/me');
      const user = userResponse.data;

      saveUser(user);

      setState((prev) => ({
        ...prev,
        user,
        isAuthenticated: true,
      }));

      return newTokens;
    } catch (error) {
      // Refresh failed, logout user
      await logout();
      throw error;
    }
  }, [logout]);

  // Verify token
  const verifyToken = useCallback(async () => {
    try {
      await axiosClient.post('/auth/verify');
      return true;
    } catch (error) {
      return false;
    }
  }, []);

  // Check if user has permission
  const hasPermission = useCallback((permission: string): boolean => {
    if (!state.user) return false;

    // Check for wildcard permission
    if (state.user.permissions.includes('*')) return true;

    // Check for exact permission
    if (state.user.permissions.includes(permission)) return true;

    // Check for resource wildcard (e.g., "agents:*" matches "agents:write")
    const [resource] = permission.split(':');
    const wildcard = `${resource}:*`;

    return state.user.permissions.includes(wildcard);
  }, [state.user]);

  // Check if user has role
  const hasRole = useCallback((role: string): boolean => {
    if (!state.user) return false;
    return state.user.roles.includes(role);
  }, [state.user]);

  // Initialize: Check if token is still valid
  useEffect(() => {
    const initAuth = async () => {
      const tokens = getTokens();

      if (!tokens) {
        setState((prev) => ({ ...prev, isAuthenticated: false }));
        return;
      }

      // Check if token is expired (rough check based on user data)
      const user = getUser();
      if (user && user.expires_at) {
        const now = Math.floor(Date.now() / 1000);
        if (now > user.expires_at) {
          // Token expired, try to refresh
          try {
            await refreshToken();
          } catch (error) {
            // Refresh failed, clear tokens
            clearTokens();
            setState((prev) => ({ ...prev, isAuthenticated: false, user: null }));
          }
          return;
        }
      }

      // Verify token with server
      const isValid = await verifyToken();
      if (!isValid) {
        try {
          await refreshToken();
        } catch (error) {
          clearTokens();
          setState((prev) => ({ ...prev, isAuthenticated: false, user: null }));
        }
      }
    };

    initAuth();
  }, []);

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!state.user || !state.isAuthenticated) return;

    const refreshBeforeExpiry = 5 * 60 * 1000; // 5 minutes before expiry
    const expiryTime = state.user.expires_at * 1000; // Convert to milliseconds
    const now = Date.now();
    const timeUntilRefresh = expiryTime - now - refreshBeforeExpiry;

    if (timeUntilRefresh <= 0) {
      // Token already near expiry, refresh immediately
      refreshToken();
      return;
    }

    const timeoutId = setTimeout(() => {
      refreshToken();
    }, timeUntilRefresh);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [state.user, state.isAuthenticated, refreshToken]);

  return {
    ...state,
    register,
    login,
    logout,
    refreshToken,
    verifyToken,
    hasPermission,
    hasRole,
  };
};
