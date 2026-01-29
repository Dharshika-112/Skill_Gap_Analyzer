import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { FiMail, FiLock, FiEye, FiEyeOff, FiTarget, FiTrendingUp, FiZap } from 'react-icons/fi';
import './Auth.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(email, password);
    
    if (result.success) {
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="auth-container"
      >
        <div className="auth-card">
          <div className="auth-header">
            <h1 className="auth-title">Welcome Back</h1>
            <p className="auth-subtitle">
              Sign in to your CareerBoost AI account to continue your career journey
            </p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="error-message"
              style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '20px',
                color: '#dc2626',
                fontSize: '14px'
              }}
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">Email Address</label>
              <div className="input-wrapper">
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`form-input ${error ? 'error' : ''}`}
                  placeholder="Enter your email"
                  required
                  disabled={loading}
                />
                <FiMail className="input-icon" />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">Password</label>
              <div className="input-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`form-input ${error ? 'error' : ''}`}
                  placeholder="Enter your password"
                  required
                  disabled={loading}
                />
                <FiLock className="input-icon" />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="password-toggle"
                  disabled={loading}
                >
                  {showPassword ? <FiEyeOff /> : <FiEye />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary full-width"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="spinner"></div>
                  Signing In...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="auth-footer">
            Don't have an account?{' '}
            <Link to="/signup" className="auth-link">
              Sign Up
            </Link>
          </div>
        </div>

        <div className="auth-visual">
          <div className="visual-content">
            <h2 className="visual-title">Boost Your Career with AI</h2>
            <p className="visual-description">
              Get personalized insights, skill gap analysis, and resume optimization powered by advanced AI technology.
            </p>

            <div className="feature-highlights">
              <div className="highlight-item">
                <div className="highlight-icon">
                  <FiTarget />
                </div>
                <div>
                  <div className="highlight-title">Skill Gap Analysis</div>
                  <div className="highlight-desc">Identify missing skills for your target role</div>
                </div>
              </div>

              <div className="highlight-item">
                <div className="highlight-icon">
                  <FiTrendingUp />
                </div>
                <div>
                  <div className="highlight-title">Resume Scoring</div>
                  <div className="highlight-desc">Get ATS-optimized resume scores</div>
                </div>
              </div>

              <div className="highlight-item">
                <div className="highlight-icon">
                  <FiZap />
                </div>
                <div>
                  <div className="highlight-title">Career Insights</div>
                  <div className="highlight-desc">Receive personalized career recommendations</div>
                </div>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number">1000+</div>
                <div className="stat-label">Resumes Analyzed</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">2300+</div>
                <div className="stat-label">Skills Tracked</div>
              </div>
            </div>

            <div className="testimonial">
              <div className="testimonial-text">
                "CareerBoost AI helped me identify the exact skills I needed for my dream job. The insights were incredibly accurate!"
              </div>
              <div className="testimonial-author">
                <div className="author-avatar">JS</div>
                <div>
                  <div className="author-name">John Smith</div>
                  <div className="author-title">Software Engineer</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;