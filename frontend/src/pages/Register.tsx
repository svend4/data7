/**
 * Register Page Component
 *
 * User registration page with validation and JWT auto-login.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  full_name: string;
}

export const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading, error, isAuthenticated } = useAuth();

  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors({
        ...validationErrors,
        [name]: '',
      });
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // Username validation
    if (formData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    }
    if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      errors.username = 'Username can only contain letters, numbers, and underscores';
    }

    // Email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Invalid email address';
    }

    // Password validation
    if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }
    if (!/(?=.*[a-z])(?=.*[A-Z])|(?=.*\d)/.test(formData.password)) {
      errors.password = 'Password must contain uppercase, lowercase, or numbers';
    }

    // Confirm password
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || undefined,
      });

      toast.success('Registration successful! Logging you in...');
      // The useAuth hook automatically logs in after registration
      navigate('/dashboard');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    }
  };

  const isFormValid =
    formData.username.trim() !== '' &&
    formData.email.trim() !== '' &&
    formData.password !== '' &&
    formData.confirmPassword !== '';

  return (
    <div className="register-page">
      <div className="register-container">
        {/* Art Deco Header */}
        <div className="register-header">
          <div className="art-deco-ornament">◆</div>
          <h1 className="register-title">Join the Switchboard</h1>
          <p className="register-subtitle">Create your operator account</p>
          <div className="art-deco-ornament">◆</div>
        </div>

        {/* Register Form */}
        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="username">
              Username <span className="required">*</span>
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              autoComplete="username"
              required
              disabled={isLoading}
            />
            {validationErrors.username && (
              <span className="field-error">{validationErrors.username}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="email">
              Email <span className="required">*</span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your.email@example.com"
              autoComplete="email"
              required
              disabled={isLoading}
            />
            {validationErrors.email && (
              <span className="field-error">{validationErrors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="full_name">Full Name (Optional)</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="John Doe"
              autoComplete="name"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password <span className="required">*</span>
            </label>
            <div className="password-input-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="At least 8 characters"
                autoComplete="new-password"
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
            {validationErrors.password && (
              <span className="field-error">{validationErrors.password}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">
              Confirm Password <span className="required">*</span>
            </label>
            <input
              type={showPassword ? 'text' : 'password'}
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Re-enter your password"
              autoComplete="new-password"
              required
              disabled={isLoading}
            />
            {validationErrors.confirmPassword && (
              <span className="field-error">{validationErrors.confirmPassword}</span>
            )}
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="register-button"
            disabled={!isFormValid || isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner" />
                Creating account...
              </>
            ) : (
              'Create Account'
            )}
          </button>

          <div className="register-footer">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="login-link">
                Login here
              </Link>
            </p>
          </div>
        </form>
      </div>

      <style>{`
        .register-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
          padding: 2rem;
        }

        .register-container {
          max-width: 500px;
          width: 100%;
          background: #2a2a2a;
          border: 2px solid #d4af37;
          border-radius: 4px;
          padding: 3rem;
          box-shadow: 0 8px 32px rgba(212, 175, 55, 0.2);
        }

        .register-header {
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

        .register-title {
          font-size: 1.8rem;
          font-weight: 700;
          color: #d4af37;
          margin: 0.5rem 0;
          font-family: 'Georgia', serif;
        }

        .register-subtitle {
          font-size: 0.9rem;
          color: #999;
          font-style: italic;
        }

        .register-form {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
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

        .required {
          color: #ff6b6b;
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

        .field-error {
          font-size: 0.8rem;
          color: #ff6b6b;
          margin-top: -0.25rem;
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

        .register-button {
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
          margin-top: 0.5rem;
        }

        .register-button:hover:not(:disabled) {
          background: #f0c84a;
          box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        }

        .register-button:disabled {
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

        .register-footer {
          text-align: center;
          padding-top: 1rem;
          border-top: 1px solid #444;
          margin-top: 0.5rem;
        }

        .register-footer p {
          color: #999;
          font-size: 0.9rem;
        }

        .login-link {
          color: #d4af37;
          text-decoration: none;
          font-weight: 600;
          transition: color 0.3s ease;
        }

        .login-link:hover {
          color: #f0c84a;
          text-decoration: underline;
        }

        @media (max-width: 640px) {
          .register-container {
            padding: 2rem 1.5rem;
          }

          .register-title {
            font-size: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};
