import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiUser, 
  FiLogOut, 
  FiMenu, 
  FiX, 
  FiTarget, 
  FiTrendingUp, 
  FiLightbulb,
  FiHome,
  FiActivity
} from 'react-icons/fi';
import './Navbar.css';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsProfileOpen(false);
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: FiHome },
    { path: '/skill-gap-analyzer', label: 'Skill Gap Analyzer', icon: FiTarget },
    { path: '/resume-scoring', label: 'Resume Scoring', icon: FiTrendingUp },
    { path: '/improvement-suggestions', label: 'Suggestions', icon: FiLightbulb }
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <div className="logo-icon">
            <FiActivity />
          </div>
          <span className="logo-text">SkillSync Pro</span>
        </Link>

        {/* Desktop Navigation */}
        {isAuthenticated && (
          <div className="navbar-menu desktop-menu">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
              >
                <item.icon className="nav-icon" />
                <span>{item.label}</span>
              </Link>
            ))}
          </div>
        )}

        {/* Right Side */}
        <div className="navbar-right">
          {isAuthenticated ? (
            <>
              {/* Profile Dropdown */}
              <div className="profile-dropdown">
                <button
                  className="profile-button"
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                >
                  <div className="profile-avatar">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <span className="profile-name">{user?.name || 'User'}</span>
                </button>

                <AnimatePresence>
                  {isProfileOpen && (
                    <motion.div
                      className="profile-menu"
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="profile-info">
                        <div className="profile-avatar large">
                          {user?.name?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <div className="profile-details">
                          <div className="profile-name">{user?.name || 'User'}</div>
                          <div className="profile-email">{user?.email || 'user@example.com'}</div>
                        </div>
                      </div>
                      
                      <div className="profile-menu-divider"></div>
                      
                      <Link
                        to="/profile"
                        className="profile-menu-item"
                        onClick={() => setIsProfileOpen(false)}
                      >
                        <FiUser />
                        <span>Profile Settings</span>
                      </Link>
                      
                      <button
                        className="profile-menu-item logout"
                        onClick={handleLogout}
                      >
                        <FiLogOut />
                        <span>Logout</span>
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Mobile Menu Button */}
              <button
                className="mobile-menu-button"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                {isMenuOpen ? <FiX /> : <FiMenu />}
              </button>
            </>
          ) : (
            <div className="auth-buttons">
              <Link to="/login" className="btn btn-outline">
                Login
              </Link>
              <Link to="/signup" className="btn btn-primary">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen && isAuthenticated && (
          <motion.div
            className="mobile-menu"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`mobile-nav-link ${isActive(item.path) ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <item.icon className="nav-icon" />
                <span>{item.label}</span>
              </Link>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Overlay for mobile menu */}
      {isMenuOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setIsMenuOpen(false)}
        />
      )}
    </nav>
  );
};

export default Navbar;