import React, { useState } from 'react';
import { api } from '../api';

interface LoginViewProps {
  onLoginSuccess: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('admin@drishtimail.local');
  const [password, setPassword] = useState('ChangeMe!2026');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await api.login(email.trim(), password);
      onLoginSuccess();
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const setPreset = (presetEmail: string) => {
    setEmail(presetEmail);
    setPassword('ChangeMe!2026');
    setError(null);
  };

  return (
    <div className="login-page-container">
      <div className="login-card">
        <div className="login-header">
          <div className="brand-logo login-logo">
            <span className="brand-icon">🛡️</span>
            <div>
              <div className="brand-title">DRISHTIMAIL</div>
              <div className="brand-sub">FORENSIC SECURITY PLATFORM (SIH26106)</div>
            </div>
          </div>
          <p className="login-desc">
            Restricted Security Gateway. Enter your authorized credentials to access forensic evidence, threat scoring, and analysis ledgers.
          </p>
        </div>

        {error && (
          <div className="alert-box error mt-3">
            <span>⚠️ {error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form mt-4">
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input font-mono"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="analyst@drishtimail.local"
              required
              autoFocus
            />
          </div>

          <div className="form-group mt-3">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input font-mono"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block mt-4"
            disabled={loading}
          >
            {loading ? '🔐 Verifying Credentials...' : '🔓 Authenticate Session'}
          </button>
        </form>

        <div className="login-presets mt-4">
          <span className="preset-label">Quick-Fill Authorized Roles:</span>
          <div className="preset-buttons">
            <button
              type="button"
              className="preset-btn"
              onClick={() => setPreset('admin@drishtimail.local')}
            >
              Admin
            </button>
            <button
              type="button"
              className="preset-btn"
              onClick={() => setPreset('investigator@drishtimail.local')}
            >
              Investigator
            </button>
            <button
              type="button"
              className="preset-btn"
              onClick={() => setPreset('analyst@drishtimail.local')}
            >
              Analyst
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
