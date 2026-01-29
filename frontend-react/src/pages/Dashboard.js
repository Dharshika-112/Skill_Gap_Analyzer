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
  FiClock,
  FiX,
  FiPhone,
  FiBookOpen,
  FiBook,
  FiBriefcase,
  FiCheck,
  FiChevronRight,
  FiCheckCircle
} from 'react-icons/fi';
import './Dashboard.css';

// Profile Completion Modal Component
const ProfileCompletionModal = ({ user, onComplete }) => {
  const { updateProfile } = useAuth();
  const [formData, setFormData] = useState({
    phone: user?.phone || '',
    specialization: user?.specialization || '',
    experience: user?.experience || '',
    degree: user?.degree || ''
  });
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const specializationOptions = [
    'Software Development',
    'Data Science',
    'Cybersecurity',
    'DevOps',
    'AI/Machine Learning',
    'Web Development',
    'Mobile Development',
    'Cloud Computing',
    'Product Management',
    'Digital Marketing',
    'UI/UX Design',
    'Business Analysis'
  ];

  const experienceOptions = [
    'Fresh Graduate (0 years)',
    'Entry Level (1-2 years)',
    'Mid Level (3-5 years)',
    'Senior Level (6-10 years)',
    'Expert Level (10+ years)'
  ];

  const degreeOptions = [
    'High School',
    'Associate Degree',
    'Bachelor\'s Degree',
    'Master\'s Degree',
    'PhD',
    'Professional Certification',
    'Bootcamp Graduate',
    'Self-Taught'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Calculate completion percentage
      let completion = 25; // Base for name, email, password
      if (formData.phone) completion += 15;
      if (formData.specialization) completion += 20;
      if (formData.experience) completion += 20;
      if (formData.degree) completion += 20;

      const profileData = {
        ...formData,
        profile_completion: completion,
        needs_profile_completion: completion < 100
      };

      const result = await updateProfile(profileData);
      
      if (result.success) {
        if (completion === 100) {
          setShowSuccess(true);
          setTimeout(() => {
            onComplete();
          }, 3000);
        } else {
          onComplete();
        }
      }
    } catch (error) {
      console.error('Profile update failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const calculateCompletion = () => {
    let completion = 25; // Base
    if (formData.phone) completion += 15;
    if (formData.specialization) completion += 20;
    if (formData.experience) completion += 20;
    if (formData.degree) completion += 20;
    return completion;
  };

  const currentCompletion = calculateCompletion();

  if (showSuccess) {
    return (
      <div className="modal-overlay">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="success-modal"
        >
          <div className="success-content">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="success-icon"
            >
              <FiCheck />
            </motion.div>
            <h2>Profile 100% Complete!</h2>
            <p>Congratulations! Your profile is now complete and you can access all features.</p>
            <div className="success-animation">
              <div className="confetti"></div>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="modal-overlay">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="profile-modal"
      >
        <div className="modal-header">
          <h2>Complete Your Profile</h2>
          <p>Help us provide better recommendations by completing your profile</p>
          <button onClick={onComplete} className="modal-close">
            <FiX />
          </button>
        </div>

        <div className="completion-progress">
          <div className="progress-info">
            <span>Profile Completion</span>
            <span>{currentCompletion}%</span>
          </div>
          <div className="progress-bar">
            <motion.div 
              className="progress-fill"
              animate={{ width: `${currentCompletion}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        <form onSubmit={handleSubmit} className="profile-form">
          <div className="form-grid">
            <div className="form-group">
              <label>
                <FiPhone className="field-icon" />
                Phone Number
                <span className="optional">+15 points</span>
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                placeholder="Enter your phone number"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label>
                <FiBookOpen className="field-icon" />
                Specialization
                <span className="required">+20 points</span>
              </label>
              <select
                value={formData.specialization}
                onChange={(e) => handleChange('specialization', e.target.value)}
                className="form-input"
              >
                <option value="">Select your field</option>
                {specializationOptions.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>
                <FiBriefcase className="field-icon" />
                Years of Experience
                <span className="required">+20 points</span>
              </label>
              <select
                value={formData.experience}
                onChange={(e) => handleChange('experience', e.target.value)}
                className="form-input"
              >
                <option value="">Select experience level</option>
                {experienceOptions.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>
                <FiBook className="field-icon" />
                Education Level
                <span className="required">+20 points</span>
              </label>
              <select
                value={formData.degree}
                onChange={(e) => handleChange('degree', e.target.value)}
                className="form-input"
              >
                <option value="">Select education level</option>
                {degreeOptions.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              onClick={onComplete}
              className="btn btn-secondary"
            >
              Skip for Now
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showProfileCompletion, setShowProfileCompletion] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchRoles();
    // Check if user needs to complete profile
    if (user?.needs_profile_completion && user?.profile_completion < 100) {
      setShowProfileCompletion(true);
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      // Mock data since the proxy isn't working
      const mockStats = {
        total_jobs: '1,066',
        total_roles: '218', 
        total_skills: '2,346',
        total_resumes: '150+'
      };
      
      const mockActivity = [];
      
      setStats(mockStats);
      setRecentActivity(mockActivity);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await axios.get('http://localhost:8004/api/roles');
      console.log('Roles fetched:', response.data);
      setRoles(response.data || []);
    } catch (error) {
      console.error('Failed to fetch roles:', error);
      // Fallback to empty array if API fails
      setRoles([]);
    } finally {
      setLoading(false);
    }
  };

  const marketStats = [
    {
      label: 'Total Jobs',
      value: stats?.total_jobs || '1,066',
      icon: FiActivity,
      color: '#3b82f6',
      description: 'Active job postings analyzed'
    },
    {
      label: 'Career Roles',
      value: stats?.total_roles || '218',
      icon: FiTarget,
      color: '#10b981',
      description: 'Professional career paths'
    },
    {
      label: 'Skills Tracked',
      value: stats?.total_skills || '2,346',
      icon: FiAward,
      color: '#f59e0b',
      description: 'Technical skills in database'
    },
    {
      label: 'Resume Analyses',
      value: stats?.total_resumes || '150+',
      icon: FiTrendingUp,
      color: '#8b5cf6',
      description: 'Resumes scored this month'
    }
  ];

  const featureCards = [
    {
      title: 'AI Skill Gap Analysis',
      description: 'Discover missing skills for your target role with ML-powered analysis and personalized learning paths. Get detailed skill breakdowns and improvement roadmaps.',
      icon: FiTarget,
      path: '/skill-gap-analyzer',
      color: '#3b82f6',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
      features: ['2,346+ Skills Database', 'ML-powered matching', 'Role recommendations', 'Learning roadmaps', 'Quiz assessments'],
      stats: { total: '2,346', label: 'Skills Tracked' }
    },
    {
      title: 'Advanced Resume Scoring',
      description: 'Get comprehensive ATS scores with PDF processing, role-based analysis, and detailed feedback. Improve your resume with AI-powered suggestions.',
      icon: FiFileText,
      path: '/resume-scoring',
      color: '#10b981',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
      features: ['PDF processing', 'ATS compatibility', 'Role-based scoring', 'Improvement suggestions', 'Industry benchmarks'],
      stats: { total: '150+', label: 'Resumes Analyzed' }
    },
    {
      title: 'Career Role Explorer',
      description: 'Explore detailed career paths with skill requirements, salary insights, and growth opportunities. Find your perfect career match.',
      icon: FiBriefcase,
      path: '/dashboard#roles',
      color: '#f59e0b',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      features: ['218 Career Roles', 'Skill requirements', 'Career progression', 'Market insights', 'Salary data'],
      stats: { total: '218', label: 'Career Roles' }
    },
    {
      title: 'Profile & Activity Tracking',
      description: 'Track your progress with detailed analytics, activity history, and personalized recommendations. Monitor your career growth journey.',
      icon: FiUser,
      path: '/profile',
      color: '#8b5cf6',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
      features: ['Activity tracking', 'Progress analytics', 'Achievement badges', 'Goal setting', 'Performance insights'],
      stats: { total: '1,066', label: 'Job Opportunities' }
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
      {/* Profile Completion Modal */}
      {showProfileCompletion && (
        <ProfileCompletionModal 
          user={user}
          onComplete={() => setShowProfileCompletion(false)}
        />
      )}
      
      <div className="dashboard-container">
        {/* Animated Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="welcome-section"
        >
          <div className="welcome-content">
            <motion.h1
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.2 }}
              className="animated-welcome"
            >
              Hello {user?.name}! 👋
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="animated-subtitle"
            >
              Start to build your skills
            </motion.p>
          </div>
          
          {!showProfileCompletion && user?.profile_completion < 100 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="profile-completion"
            >
              <div className="completion-header">
                <span>Profile Completion</span>
                <span>{user?.profile_completion || 25}%</span>
              </div>
              <div className="completion-bar">
                <motion.div 
                  className="completion-fill" 
                  initial={{ width: 0 }}
                  animate={{ width: `${user?.profile_completion || 25}%` }}
                  transition={{ duration: 1, delay: 0.8 }}
                ></motion.div>
              </div>
              <button 
                onClick={() => setShowProfileCompletion(true)}
                className="complete-profile"
              >
                Complete Profile <FiArrowRight />
              </button>
            </motion.div>
          )}
        </motion.div>

        {/* Enhanced Feature Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="feature-cards-section"
        >
          <div className="section-header">
            <h2>Powerful AI Features</h2>
            <p>Accelerate your career with our comprehensive suite of AI-powered tools</p>
          </div>
          
          <div className="feature-cards-grid">
            {featureCards.map((card, index) => (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="feature-card"
                style={{ '--card-gradient': card.gradient }}
              >
                <Link to={card.path} className="feature-card-link">
                  <div className="feature-card-header">
                    <div className="feature-icon" style={{ backgroundColor: card.color }}>
                      <card.icon size={24} color="white" />
                    </div>
                    <h3>{card.title}</h3>
                  </div>
                  
                  <p className="feature-description">{card.description}</p>
                  
                  <div className="feature-list">
                    {card.features.map((feature, idx) => (
                      <div key={idx} className="feature-item">
                        <FiCheckCircle size={14} />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  {card.stats && (
                    <div className="feature-stats">
                      <div className="stat-highlight">
                        <span className="stat-number">{card.stats.total}</span>
                        <span className="stat-label">{card.stats.label}</span>
                      </div>
                    </div>
                  )}
                  
                  <div className="feature-card-footer">
                    <span className="explore-text">Get Started</span>
                    <FiChevronRight className="arrow-icon" />
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Role Cards Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="roles-section"
        >
          <div className="section-header">
            <h2>Explore Career Roles</h2>
            <p>Discover detailed information about different career paths and their requirements</p>
          </div>
          
          <div className="roles-grid">
            {roles.map((role, index) => (
              <motion.div
                key={role.roleId}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.05 }}
                whileHover={{ y: -5, scale: 1.02 }}
                className="role-card"
              >
                <Link to={`/role/${role.roleId}`} className="role-link">
                  <div className="role-header">
                    <h3 className="role-title">{role.title}</h3>
                    <div className="role-order">#{role.order}</div>
                  </div>
                  
                  <p className="role-subtitle">{role.cardSubtitle}</p>
                  
                  <div className="role-skills">
                    <div className="skills-label">Key Skills:</div>
                    <div className="skills-tags">
                      {role.topSkills.map((skill, skillIndex) => (
                        <span key={skillIndex} className="skill-tag">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="role-footer">
                    <span className="explore-text">Explore Role</span>
                    <FiArrowRight className="arrow-icon" />
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
          
          {roles.length === 0 && !loading && (
            <div className="no-roles">
              <FiTarget className="no-roles-icon" />
              <p>No career roles available at the moment</p>
              <p>Please check back later or contact support</p>
            </div>
          )}
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