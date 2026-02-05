/**
 * AuthContext
 *
 * Centralized authentication state management using React Context.
 * Provides authentication state and functions to all components.
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useAuth as useAuthHook, User, LoginCredentials, RegisterData } from '../hooks/useAuth';

// ============================================================================
// Types
// ============================================================================

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  register: (data: RegisterData) => Promise<User>;
  login: (credentials: LoginCredentials) => Promise<User>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<any>;
  verifyToken: () => Promise<boolean>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

// ============================================================================
// Context
// ============================================================================

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// ============================================================================
// Provider
// ============================================================================

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const auth = useAuthHook();

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};

// ============================================================================
// Hook
// ============================================================================

/**
 * useAuth hook
 *
 * Access authentication context from any component.
 *
 * @throws Error if used outside AuthProvider
 */
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};

// ============================================================================
// HOCs
// ============================================================================

/**
 * withAuth HOC
 *
 * Injects authentication state and methods as props.
 */
export const withAuth = <P extends object>(
  Component: React.ComponentType<P & { auth: AuthContextValue }>
) => {
  return (props: P) => {
    const auth = useAuth();
    return <Component {...props} auth={auth} />;
  };
};
