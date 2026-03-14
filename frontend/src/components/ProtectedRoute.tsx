/**
 * ProtectedRoute Component
 *
 * Wrapper component for routes that require authentication.
 * Redirects to login if user is not authenticated.
 * Optionally checks for specific permissions or roles.
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string;
  requiredRole?: string;
  fallback?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermission,
  requiredRole,
  fallback,
}) => {
  const { isAuthenticated, isLoading, hasPermission, hasRole } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="protected-route-loading">
        <div className="spinner-large" />
        <p>Loading...</p>
      </div>
    );
  }

  // Not authenticated - redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check required permission
  if (requiredPermission && !hasPermission(requiredPermission)) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="access-denied">
        <div className="access-denied-content">
          <div className="art-deco-ornament">◆</div>
          <h1>Access Denied</h1>
          <p>You don't have permission to access this resource.</p>
          <p className="permission-required">
            Required permission: <code>{requiredPermission}</code>
          </p>
          <button onClick={() => window.history.back()} className="back-button">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Check required role
  if (requiredRole && !hasRole(requiredRole)) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="access-denied">
        <div className="access-denied-content">
          <div className="art-deco-ornament">◆</div>
          <h1>Access Denied</h1>
          <p>You don't have the required role to access this resource.</p>
          <p className="permission-required">
            Required role: <code>{requiredRole}</code>
          </p>
          <button onClick={() => window.history.back()} className="back-button">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Authenticated and authorized - render children
  return <>{children}</>;
};

/**
 * withPermission HOC
 *
 * Higher-order component to conditionally render based on permission.
 */
export const withPermission = (
  Component: React.ComponentType<any>,
  requiredPermission: string
) => {
  return (props: any) => {
    const { hasPermission } = useAuth();

    if (!hasPermission(requiredPermission)) {
      return null;
    }

    return <Component {...props} />;
  };
};

/**
 * withRole HOC
 *
 * Higher-order component to conditionally render based on role.
 */
export const withRole = (Component: React.ComponentType<any>, requiredRole: string) => {
  return (props: any) => {
    const { hasRole } = useAuth();

    if (!hasRole(requiredRole)) {
      return null;
    }

    return <Component {...props} />;
  };
};

/**
 * PermissionGate Component
 *
 * Conditionally renders children based on permission.
 */
interface PermissionGateProps {
  permission: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionGate: React.FC<PermissionGateProps> = ({
  permission,
  children,
  fallback = null,
}) => {
  const { hasPermission } = useAuth();

  if (!hasPermission(permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};

/**
 * RoleGate Component
 *
 * Conditionally renders children based on role.
 */
interface RoleGateProps {
  role: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleGate: React.FC<RoleGateProps> = ({
  role,
  children,
  fallback = null,
}) => {
  const { hasRole } = useAuth();

  if (!hasRole(role)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};

// Inline styles (could be moved to CSS file)
const styles = `
  .protected-route-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: #1a1a1a;
    color: #d4af37;
  }

  .spinner-large {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(212, 175, 55, 0.2);
    border-top: 4px solid #d4af37;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .access-denied {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    padding: 2rem;
  }

  .access-denied-content {
    max-width: 600px;
    text-align: center;
    background: #2a2a2a;
    border: 2px solid #d4af37;
    border-radius: 4px;
    padding: 3rem;
    box-shadow: 0 8px 32px rgba(212, 175, 55, 0.2);
  }

  .access-denied-content .art-deco-ornament {
    color: #d4af37;
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .access-denied-content h1 {
    font-size: 2rem;
    color: #d4af37;
    margin: 1rem 0;
    font-family: 'Georgia', serif;
  }

  .access-denied-content p {
    color: #ccc;
    font-size: 1rem;
    margin: 0.5rem 0;
  }

  .permission-required {
    margin-top: 1.5rem;
    padding: 1rem;
    background: rgba(212, 175, 55, 0.1);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 4px;
  }

  .permission-required code {
    color: #d4af37;
    font-weight: 600;
  }

  .back-button {
    margin-top: 2rem;
    padding: 0.75rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    color: #1a1a1a;
    background: #d4af37;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
  }

  .back-button:hover {
    background: #f0c84a;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
}
