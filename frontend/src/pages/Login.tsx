/**
 * Login Page Component
 *
 * User authentication page with JWT token-based login.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

interface LoginFormData {
  username: string;
  password: string;
}

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading, error, isAuthenticated } = useAuth();

  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: '',
  });

  const [showPassword, setShowPassword] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await login({
        username: formData.username,
        password: formData.password,
      });

      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Login failed');
    }
  };

  const isFormValid = formData.username.trim() !== '' && formData.password !== '';

  return (
    <div className="login-page">
      <div className="login-container">
        {/* Art Deco Header */}
        <div className="login-header">
          <div className="art-deco-ornament">◆</div>
          <h1 className="login-title">Meta-Orchestrator Switchboard</h1>
          <p className="login-subtitle">Art Deco Telephonic Exchange</p>
          <div className="art-deco-ornament">◆</div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter your username"
              autoComplete="username"
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                autoComplete="current-password"
                required
                disabled={isLoading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={!isFormValid || isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner" />
                Logging in...
              </>
            ) : (
              'Login'
            )}
          </button>

          <div className="login-footer">
            <p>
              Don't have an account?{' '}
              <Link to="/register" className="register-link">
                Register here
              </Link>
            </p>
          </div>
        </form>

        {/* Demo Credentials */}
        <div className="demo-credentials">
          <p className="demo-title">Demo Credentials:</p>
          <code>Username: admin | Password: admin123</code>
        </div>
      </div>

      <style>{`
        .login-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
          padding: 2rem;
        }

        .login-container {
          max-width: 450px;
          width: 100%;
          background: #2a2a2a;
          border: 2px solid #d4af37;
          border-radius: 4px;
          padding: 3rem;
          box-shadow: 0 8px 32px rgba(212, 175, 55, 0.2);
        }

        .login-header {
          text-align: center;
          margin-bottom: 2rem;
          padding-bottom: 2rem;
          border-bottom: 1px solid #d4af37;
        }

        .art-deco-ornament {
          color: #d4af37;
          font-size: 2rem;
          margin: 0.5rem 0;
        }

        .login-title {
          font-size: 1.8rem;
          font-weight: 700;
          color: #d4af37;
          margin: 0.5rem 0;
          font-family: 'Georgia', serif;
        }

        .login-subtitle {
          font-size: 0.9rem;
          color: #999;
          font-style: italic;
        }

        .login-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group label {
          font-size: 0.9rem;
          font-weight: 600;
          color: #d4af37;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .form-group input {
          padding: 0.75rem 1rem;
          font-size: 1rem;
          border: 1px solid #444;
          background: #1a1a1a;
          color: #fff;
          border-radius: 4px;
          transition: all 0.3s ease;
        }

        .form-group input:focus {
          outline: none;
          border-color: #d4af37;
          box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.1);
        }

        .form-group input:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .password-input-wrapper {
          position: relative;
        }

        .password-toggle {
          position: absolute;
          right: 0.75rem;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          cursor: pointer;
          font-size: 1.2rem;
          padding: 0.25rem;
        }

        .error-message {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: rgba(255, 0, 0, 0.1);
          border: 1px solid rgba(255, 0, 0, 0.3);
          border-radius: 4px;
          color: #ff6b6b;
          font-size: 0.9rem;
        }

        .login-button {
          padding: 1rem;
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
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
        }

        .login-button:hover:not(:disabled) {
          background: #f0c84a;
          box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        }

        .login-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #1a1a1a;
          border-top: 2px solid transparent;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .login-footer {
          text-align: center;
          padding-top: 1rem;
          border-top: 1px solid #444;
        }

        .login-footer p {
          color: #999;
          font-size: 0.9rem;
        }

        .register-link {
          color: #d4af37;
          text-decoration: none;
          font-weight: 600;
          transition: color 0.3s ease;
        }

        .register-link:hover {
          color: #f0c84a;
          text-decoration: underline;
        }

        .demo-credentials {
          margin-top: 2rem;
          padding: 1rem;
          background: rgba(212, 175, 55, 0.1);
          border: 1px solid rgba(212, 175, 55, 0.3);
          border-radius: 4px;
          text-align: center;
        }

        .demo-title {
          font-size: 0.8rem;
          color: #999;
          margin-bottom: 0.5rem;
        }

        .demo-credentials code {
          color: #d4af37;
          font-size: 0.9rem;
        }

        @media (max-width: 640px) {
          .login-container {
            padding: 2rem 1.5rem;
          }

          .login-title {
            font-size: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};
