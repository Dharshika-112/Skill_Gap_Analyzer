import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiUser, 
  FiMail, 
  FiBriefcase, 
  FiEdit2, 
  FiSave, 
  FiActivity, 
  FiTarget, 
  FiSearch, 
  FiAward, 
  FiClock,
  FiPhone,
  FiBookOpen,
  FiTrendingUp,
  FiCalendar,
  FiGlobe,
  FiChevronRight,
  FiEye,
  FiBarChart,
  FiRefreshCw,
  FiAlertCircle,
  FiCheckCircle
} from 'react-icons/fi';
import axios from 'axios';
import './Profile.css';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [editing, setEditing] = useState(false);
  const [userActivities, setUserActivities] = useState([]);
  const [loadingActivities, setLoadingActivities] = useState(true);
  const [activitiesError, setActivitiesError] = useState('');
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [showActivityDetails, setShowActivityDetails] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    experience: user?.experience || '',
    skills: user?.skills || [],
    phone: user?.phone || '',
    specialization: user?.specialization || '',
    degree: user?.degree || ''
  });

  useEffect(() => {
    fetchUserActivities();
  }, [user]);

  const fetchUserActivities = async (showRefresh = false) => {
    try {
      if (showRefresh) setRefreshing(true);
      setActivitiesError('');
      
      const userId = user?.id || localStorage.getItem('userId') || 'demo_user';
      console.log('Fetching activities for user:', userId);
      
      const response = await axios.get(`http://localhost:8006/api/user/${userId}/activities`, {
        timeout: 10000 // 10 second timeout
      });
      
      if (response.data.success) {
        setUserActivities(response.data.recent_activities || []);
        console.log('Successfully fetched activities:', response.data.recent_activities?.length || 0);
      } else {
        throw new Error('Failed to fetch activities');
      }
    } catch (error) {
      console.error('Failed to fetch user activities:', error);
      setActivitiesError(error.response?.data?.detail || error.message || 'Failed to load activity history');
      // Set some mock data for demonstration if API fails
      setUserActivities([
        {
          activity_id: 'demo_1',
          activity_type: 'skill_analysis',
          activity_data: {
            user_skills: ['Python', 'JavaScript', 'React'],
            total_suggestions: 5
          },
          timestamp: new Date().toISOString()
        },
        {
          activity_id: 'demo_2',
          activity_type: 'quiz_taken',
          activity_data: {
            role_name: 'Frontend Developer',
            score: 85,
            correct_answers: 8,
            total_questions: 10
          },
          timestamp: new Date(Date.now() - 86400000).toISOString()
        }
      ]);
    } finally {
      setLoadingActivities(false);
      if (showRefresh) setRefreshing(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async () => {
    try {
      await updateProfile(formData);
      setEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  const viewActivityDetails = (activity) => {
    setSelectedActivity(activity);
    setShowActivityDetails(true);
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'skill_analysis': return FiTarget;
      case 'role_search': return FiSearch;
      case 'quiz_taken': return FiAward;
      default: return FiActivity;
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'skill_analysis': return '#3b82f6';
      case 'role_search': return '#10b981';
      case 'quiz_taken': return '#f59e0b';
      default: return '#64748b';
    }
  };

  return (
    <div className="profile-page">
      <div className="profile-container">
        {/* Profile Header */}
        <motion.div 
          className="profile-header-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="profile-banner">
            <div className="banner-gradient"></div>
            <div className="profile-header-content">
              <div className="profile-avatar-section">
                <div className="profile-avatar-large">
                  <FiUser size={48} />
                </div>
                <div className="profile-basic-info">
                  <h1 className="profile-name">{user?.name || 'User'}</h1>
                  <p className="profile-email">{user?.email}</p>
                  <div className="profile-badges">
                    <span className="profile-badge">
                      <FiCalendar size={14} />
                      Member since {user?.created_at ? new Date(user.created_at).getFullYear() : '2026'}
                    </span>
                    <span className="profile-badge">
                      <FiTrendingUp size={14} />
                      {user?.profile_completion || 25}% Complete
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="profile-actions">
                <button 
                  onClick={() => setEditing(!editing)}
                  className={`edit-profile-btn ${editing ? 'saving' : ''}`}
                >
                  {editing ? <FiSave /> : <FiEdit2 />}
                  {editing ? 'Save Changes' : 'Edit Profile'}
                </button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Profile Stats Cards */}
        <motion.div 
          className="profile-stats-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="stats-cards-grid">
            <div className="stat-card">
              <div className="stat-icon" style={{ backgroundColor: '#3b82f6' }}>
                <FiTarget color="white" />
              </div>
              <div className="stat-content">
                <h3>{user?.total_analyses || userActivities.filter(a => a.activity_type === 'skill_analysis').length}</h3>
                <p>Skill Analyses</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon" style={{ backgroundColor: '#10b981' }}>
                <FiSearch color="white" />
              </div>
              <div className="stat-content">
                <h3>{userActivities.filter(a => a.activity_type === 'role_search').length}</h3>
                <p>Role Searches</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon" style={{ backgroundColor: '#f59e0b' }}>
                <FiAward color="white" />
              </div>
              <div className="stat-content">
                <h3>{user?.total_quizzes || userActivities.filter(a => a.activity_type === 'quiz_taken').length}</h3>
                <p>Quizzes Taken</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon" style={{ backgroundColor: '#8b5cf6' }}>
                <FiBarChart color="white" />
              </div>
              <div className="stat-content">
                <h3>{user?.profile_completion || 25}%</h3>
                <p>Profile Complete</p>
              </div>
            </div>
          </div>
        </motion.div>

        <div className="profile-content-grid">
          {/* Profile Information */}
          <motion.div 
            className="profile-info-section"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="section-card">
              <div className="section-header">
                <h2>Profile Information</h2>
                {!editing && (
                  <button 
                    onClick={() => setEditing(true)}
                    className="edit-btn-small"
                  >
                    <FiEdit2 size={16} />
                  </button>
                )}
              </div>
              
              <div className="profile-form">
                <div className="form-group">
                  <label>
                    <FiUser />
                    Full Name
                  </label>
                  {editing ? (
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      className="form-input"
                    />
                  ) : (
                    <span className="form-value">{formData.name || 'Not provided'}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <FiMail />
                    Email Address
                  </label>
                  {editing ? (
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="form-input"
                    />
                  ) : (
                    <span className="form-value">{formData.email || 'Not provided'}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <FiPhone />
                    Phone Number
                  </label>
                  {editing ? (
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone || ''}
                      onChange={handleInputChange}
                      className="form-input"
                      placeholder="Enter your phone number"
                    />
                  ) : (
                    <span className="form-value">{user?.phone || 'Not provided'}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <FiBriefcase />
                    Experience Level
                  </label>
                  {editing ? (
                    <select
                      name="experience"
                      value={formData.experience}
                      onChange={handleInputChange}
                      className="form-select"
                    >
                      <option value="">Select Experience Level</option>
                      <option value="Fresh Graduate (0 years)">Fresh Graduate (0 years)</option>
                      <option value="Entry Level (1-2 years)">Entry Level (1-2 years)</option>
                      <option value="Mid Level (3-5 years)">Mid Level (3-5 years)</option>
                      <option value="Senior Level (6-10 years)">Senior Level (6-10 years)</option>
                      <option value="Expert Level (10+ years)">Expert Level (10+ years)</option>
                    </select>
                  ) : (
                    <span className="form-value">{user?.experience || 'Not specified'}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <FiBookOpen />
                    Specialization
                  </label>
                  {editing ? (
                    <select
                      name="specialization"
                      value={formData.specialization || ''}
                      onChange={handleInputChange}
                      className="form-select"
                    >
                      <option value="">Select Specialization</option>
                      <option value="Software Development">Software Development</option>
                      <option value="Data Science">Data Science</option>
                      <option value="Cybersecurity">Cybersecurity</option>
                      <option value="DevOps">DevOps</option>
                      <option value="AI/Machine Learning">AI/Machine Learning</option>
                      <option value="Web Development">Web Development</option>
                      <option value="Mobile Development">Mobile Development</option>
                      <option value="Cloud Computing">Cloud Computing</option>
                      <option value="Product Management">Product Management</option>
                      <option value="Digital Marketing">Digital Marketing</option>
                      <option value="UI/UX Design">UI/UX Design</option>
                      <option value="Business Analysis">Business Analysis</option>
                    </select>
                  ) : (
                    <span className="form-value">{user?.specialization || 'Not specified'}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <FiGlobe />
                    Education
                  </label>
                  {editing ? (
                    <select
                      name="degree"
                      value={formData.degree || ''}
                      onChange={handleInputChange}
                      className="form-select"
                    >
                      <option value="">Select Education Level</option>
                      <option value="High School">High School</option>
                      <option value="Associate Degree">Associate Degree</option>
                      <option value="Bachelor's Degree">Bachelor's Degree</option>
                      <option value="Master's Degree">Master's Degree</option>
                      <option value="PhD">PhD</option>
                      <option value="Professional Certification">Professional Certification</option>
                      <option value="Bootcamp Graduate">Bootcamp Graduate</option>
                      <option value="Self-Taught">Self-Taught</option>
                    </select>
                  ) : (
                    <span className="form-value">{user?.degree || 'Not specified'}</span>
                  )}
                </div>

                {editing && (
                  <div className="form-actions">
                    <button onClick={handleSave} className="save-btn">
                      <FiSave />
                      Save Changes
                    </button>
                    <button 
                      onClick={() => setEditing(false)} 
                      className="cancel-btn"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>
          </motion.div>

          {/* Activity History */}
          <motion.div 
            className="activity-history-section"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="section-card">
              <div className="section-header">
                <h2>Activity History</h2>
                <div className="activity-header-actions">
                  <span className="activity-count">{userActivities.length} activities</span>
                  <button 
                    className="refresh-btn"
                    onClick={() => fetchUserActivities(true)}
                    disabled={refreshing}
                  >
                    <FiRefreshCw className={refreshing ? 'spinning' : ''} />
                    {refreshing ? 'Refreshing...' : 'Refresh'}
                  </button>
                </div>
              </div>
              
              {/* Error State */}
              {activitiesError && (
                <div className="activities-error">
                  <FiAlertCircle />
                  <div>
                    <p><strong>Unable to load activity history</strong></p>
                    <p>{activitiesError}</p>
                    <button 
                      className="retry-btn"
                      onClick={() => fetchUserActivities(true)}
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              )}
              
              {/* Loading State */}
              {loadingActivities ? (
                <div className="loading-activities">
                  <div className="spinner"></div>
                  <p>Loading your activity history...</p>
                </div>
              ) : userActivities.length > 0 ? (
                <div className="activities-timeline">
                  {userActivities.map((activity, index) => {
                    const IconComponent = getActivityIcon(activity.activity_type);
                    const color = getActivityColor(activity.activity_type);
                    
                    return (
                      <motion.div
                        key={activity.activity_id || index}
                        className="activity-timeline-item"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4, delay: index * 0.1 }}
                        onClick={() => viewActivityDetails(activity)}
                      >
                        <div className="activity-timeline-marker" style={{ backgroundColor: color }}>
                          <IconComponent size={16} color="white" />
                        </div>
                        
                        <div className="activity-timeline-content">
                          <div className="activity-timeline-header">
                            <h4>
                              {activity.activity_type === 'skill_analysis' && '🎯 Skill Analysis'}
                              {activity.activity_type === 'role_search' && '🔍 Role Analysis'}
                              {activity.activity_type === 'quiz_taken' && '🧠 Quiz Completed'}
                            </h4>
                            <span className="activity-time">
                              {new Date(activity.timestamp).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                          </div>
                          
                          <div className="activity-timeline-details">
                            {activity.activity_type === 'skill_analysis' && (
                              <div className="activity-summary">
                                <p><strong>Skills Analyzed:</strong> {activity.activity_data?.user_skills?.length || 0}</p>
                                <div className="skills-preview">
                                  {activity.activity_data?.user_skills?.slice(0, 3).map(skill => (
                                    <span key={skill} className="skill-tag-small">{skill}</span>
                                  ))}
                                  {activity.activity_data?.user_skills?.length > 3 && (
                                    <span className="more-skills">+{activity.activity_data.user_skills.length - 3} more</span>
                                  )}
                                </div>
                                <div className="activity-stats">
                                  <span className="stat-badge">
                                    <FiTarget size={12} />
                                    {activity.activity_data?.total_suggestions || 0} roles found
                                  </span>
                                </div>
                              </div>
                            )}
                            
                            {activity.activity_type === 'role_search' && (
                              <div className="activity-summary">
                                <p><strong>Role:</strong> {activity.activity_data?.target_role}</p>
                                <div className="role-match-info">
                                  <span className="match-badge">
                                    {activity.activity_data?.match_percentage}% Match
                                  </span>
                                  <span className="readiness-badge">
                                    {activity.activity_data?.readiness_level}
                                  </span>
                                </div>
                                <div className="activity-stats">
                                  <span className="stat-badge">
                                    <FiCheckCircle size={12} />
                                    AI Confidence: {activity.activity_data?.ml_confidence}%
                                  </span>
                                </div>
                              </div>
                            )}
                            
                            {activity.activity_type === 'quiz_taken' && (
                              <div className="activity-summary">
                                <p><strong>Role:</strong> {activity.activity_data?.role_name}</p>
                                <div className="quiz-result-info">
                                  <span className={`score-badge ${activity.activity_data?.score >= 70 ? 'passed' : 'failed'}`}>
                                    {activity.activity_data?.score}% Score
                                  </span>
                                  <span className="result-text">
                                    {activity.activity_data?.score >= 70 ? '✅ Passed' : '❌ Failed'}
                                  </span>
                                </div>
                                <div className="activity-stats">
                                  <span className="stat-badge">
                                    <FiAward size={12} />
                                    {activity.activity_data?.correct_answers}/{activity.activity_data?.total_questions} correct
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                          
                          <button className="view-details-btn">
                            <FiEye size={14} />
                            View Details
                            <FiChevronRight size={14} />
                          </button>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              ) : (
                <div className="no-activities">
                  <FiActivity size={48} />
                  <h3>No Activities Yet</h3>
                  <p>Start using the Skill Gap Analyzer to see your activity history here.</p>
                  <button 
                    className="start-analysis-btn"
                    onClick={() => window.location.href = '/skill-gap-analyzer'}
                  >
                    <FiTarget />
                    Start Your First Analysis
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Activity Details Modal */}
      <AnimatePresence>
        {showActivityDetails && selectedActivity && (
          <motion.div 
            className="activity-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowActivityDetails(false)}
          >
            <motion.div 
              className="activity-modal"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3>Activity Details</h3>
                <button 
                  onClick={() => setShowActivityDetails(false)}
                  className="close-modal-btn"
                >
                  ×
                </button>
              </div>
              
              <div className="modal-content">
                <div className="activity-detail-header">
                  <div className="activity-icon-large" style={{ backgroundColor: getActivityColor(selectedActivity.activity_type) }}>
                    {React.createElement(getActivityIcon(selectedActivity.activity_type), { size: 24, color: 'white' })}
                  </div>
                  <div>
                    <h4>
                      {selectedActivity.activity_type === 'skill_analysis' && 'Skill Analysis Session'}
                      {selectedActivity.activity_type === 'role_search' && 'Role Analysis Session'}
                      {selectedActivity.activity_type === 'quiz_taken' && 'Quiz Session'}
                    </h4>
                    <p className="activity-timestamp">
                      {new Date(selectedActivity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                
                <div className="activity-detail-content">
                  {selectedActivity.activity_type === 'skill_analysis' && (
                    <div className="skill-analysis-details">
                      <h5>Skills You Selected ({selectedActivity.activity_data?.user_skills?.length || 0})</h5>
                      <div className="skills-grid">
                        {selectedActivity.activity_data?.user_skills?.map(skill => (
                          <span key={skill} className="skill-tag-detailed">{skill}</span>
                        ))}
                      </div>
                      <div className="analysis-info">
                        <p><strong>Analysis Type:</strong> Role Recommendations</p>
                        <p><strong>Total Roles Found:</strong> {selectedActivity.activity_data?.total_suggestions || 'N/A'}</p>
                      </div>
                    </div>
                  )}
                  
                  {selectedActivity.activity_type === 'role_search' && (
                    <div className="role-search-details">
                      <h5>Role Analysis Results</h5>
                      <div className="role-analysis-summary">
                        <div className="analysis-metric">
                          <span className="metric-label">Target Role:</span>
                          <span className="metric-value">{selectedActivity.activity_data?.target_role}</span>
                        </div>
                        <div className="analysis-metric">
                          <span className="metric-label">Match Percentage:</span>
                          <span className="metric-value">{selectedActivity.activity_data?.match_percentage}%</span>
                        </div>
                        <div className="analysis-metric">
                          <span className="metric-label">ML Confidence:</span>
                          <span className="metric-value">{selectedActivity.activity_data?.ml_confidence}%</span>
                        </div>
                        <div className="analysis-metric">
                          <span className="metric-label">Readiness Level:</span>
                          <span className="metric-value">{selectedActivity.activity_data?.readiness_level}</span>
                        </div>
                      </div>
                      
                      <h6>Your Skills Used in Analysis</h6>
                      <div className="skills-grid">
                        {selectedActivity.activity_data?.user_skills?.map(skill => (
                          <span key={skill} className="skill-tag-detailed matched">{skill}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {selectedActivity.activity_type === 'quiz_taken' && (
                    <div className="quiz-details">
                      <h5>Quiz Performance</h5>
                      <div className="quiz-summary">
                        <div className="quiz-score-display">
                          <div className={`score-circle ${selectedActivity.activity_data?.score >= 70 ? 'passed' : 'failed'}`}>
                            <span className="score-number">{selectedActivity.activity_data?.score}%</span>
                          </div>
                          <div className="score-info">
                            <p><strong>Role:</strong> {selectedActivity.activity_data?.role_name}</p>
                            <p><strong>Questions:</strong> {selectedActivity.activity_data?.total_questions || 'N/A'}</p>
                            <p><strong>Correct:</strong> {selectedActivity.activity_data?.correct_answers || 'N/A'}</p>
                            <p><strong>Result:</strong> 
                              <span className={selectedActivity.activity_data?.score >= 70 ? 'passed-text' : 'failed-text'}>
                                {selectedActivity.activity_data?.score >= 70 ? ' Passed' : ' Failed'}
                              </span>
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Profile;