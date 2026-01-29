import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { FiMail, FiLock, FiEye, FiEyeOff, FiShield } from 'react-icons/fi';
import './AdminLogin.css';

const AdminLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8004/api/admin/auth/login', {
        email,
        password
      });

      if (response.data.success) {
        // Store admin session (in real app, would use proper JWT)
        localStorage.setItem('admin_session', JSON.stringify(response.data.admin));
        navigate('/admin/dashboard');
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="admin-login-container"
      >
        <div className="admin-login-card">
          <div className="admin-header">
            <div className="admin-icon">
              <FiShield />
            </div>
            <h1>Admin Panel</h1>
            <p>CareerBoost AI Role Management</p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="error-message"
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="admin-form">
            <div className="form-group">
              <label htmlFor="email">Admin Email</label>
              <div className="input-wrapper">
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@careerboost.ai"
                  required
                  disabled={loading}
                />
                <FiMail className="input-icon" />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="input-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter admin password"
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
              className="admin-login-btn"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="spinner"></div>
                  Signing In...
                </>
              ) : (
                'Sign In to Admin Panel'
              )}
            </button>
          </form>

          <div className="admin-footer">
            <div className="default-credentials">
              <h4>Default Credentials:</h4>
              <p><strong>Email:</strong> admin@careerboost.ai</p>
              <p><strong>Password:</strong> admin123</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AdminLogin;