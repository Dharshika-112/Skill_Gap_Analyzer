import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  FiTarget, 
  FiFileText, 
  FiTrendingUp, 
  FiActivity,
  FiArrowRight,
  FiUpload,
  FiUser,
  FiAward,
  FiClock
} from 'react-icons/fi';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch user stats and recent activity
      const [statsResponse, activityResponse] = await Promise.all([
        axios.get('/api/resume/ats-insights'),
        axios.get('/api/resume/user-analysis-history')
      ]);

      setStats(statsResponse.data.market_insights);
      setRecentActivity(activityResponse.data.history || []);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Skill Gap Analyzer',
      description: 'Compare your skills with job requirements',
      icon: FiTarget,
      path: '/skill-gap-analyzer',
      color: '#3b82f6',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)'
    },
    {
      title: 'Resume Scoring',
      description: 'Get AI-powered ATS score for your resume',
      icon: FiFileText,
      path: '/resume-scoring',
      color: '#10b981',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
    },
    {
      title: 'Get Suggestions',
      description: 'Receive personalized career recommendations',
      icon: FiTrendingUp,
      path: '/suggestions',
      color: '#f59e0b',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
    }
  ];

  const marketStats = [
    {
      label: 'Total Jobs',
      value: stats?.total_jobs || '1,066',
      icon: FiActivity,
      color: '#3b82f6'
    },
    {
      label: 'Career Roles',
      value: stats?.total_roles || '218',
      icon: FiTarget,
      color: '#10b981'
    },
    {
      label: 'Skills Tracked',
      value: stats?.total_skills || '2,207',
      icon: FiAward,
      color: '#f59e0b'
    }
  ];

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-container">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="welcome-section"
        >
          <div className="welcome-content">
            <h1>Welcome back, {user?.name}! 👋</h1>
            <p>Ready to advance your career? Let's analyze your skills and find opportunities.</p>
          </div>
          
          <div className="profile-completion">
            <div className="completion-header">
              <span>Profile Completion</span>
              <span>75%</span>
            </div>
            <div className="completion-bar">
              <div className="completion-fill" style={{ width: '75%' }}></div>
            </div>
            <Link to="/profile" className="complete-profile">
              Complete Profile <FiArrowRight />
            </Link>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="quick-actions-section"
        >
          <h2>Quick Actions</h2>
          <div className="quick-actions-grid">
            {quickActions.map((action, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                whileHover={{ y: -5 }}
                className="action-card"
              >
                <Link to={action.path} className="action-link">
                  <div 
                    className="action-icon"
                    style={{ background: action.gradient }}
                  >
                    <action.icon />
                  </div>
                  <div className="action-content">
                    <h3>{action.title}</h3>
                    <p>{action.description}</p>
                  </div>
                  <FiArrowRight className="action-arrow" />
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Market Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="market-stats-section"
        >
          <h2>Market Overview</h2>
          <div className="stats-grid">
            {marketStats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
                className="stat-card"
              >
                <div className="stat-icon" style={{ color: stat.color }}>
                  <stat.icon />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{stat.value}</div>
                  <div className="stat-label">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="recent-activity-section"
        >
          <div className="section-header">
            <h2>Recent Activity</h2>
            <Link to="/profile" className="view-all">
              View All <FiArrowRight />
            </Link>
          </div>
          
          <div className="activity-list">
            {recentActivity.length > 0 ? (
              recentActivity.slice(0, 5).map((activity, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
                  className="activity-item"
                >
                  <div className="activity-icon">
                    <FiActivity />
                  </div>
                  <div className="activity-content">
                    <div className="activity-title">
                      Analyzed {activity.role_title || 'Skills'}
                    </div>
                    <div className="activity-time">
                      <FiClock />
                      {new Date(activity.analyzed_at).toLocaleDateString()}
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="no-activity">
                <FiActivity className="no-activity-icon" />
                <p>No recent activity</p>
                <p>Start by analyzing your skills or uploading a resume</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Getting Started */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="getting-started-section"
        >
          <div className="getting-started-card">
            <div className="getting-started-content">
              <h3>New to SkillSync Pro?</h3>
              <p>Start with uploading your resume or manually selecting your skills to get personalized career insights.</p>
              <div className="getting-started-actions">
                <Link to="/resume-scoring" className="btn btn-primary">
                  <FiUpload />
                  Upload Resume
                </Link>
                <Link to="/skill-gap-analyzer" className="btn btn-secondary">
                  <FiTarget />
                  Select Skills
                </Link>
              </div>
            </div>
            <div className="getting-started-visual">
              <div className="visual-element">
                <div className="pulse-circle"></div>
                <FiUser className="visual-icon" />
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;