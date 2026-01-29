import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
  FiArrowLeft, 
  FiTarget, 
  FiCheckCircle, 
  FiTool, 
  FiBookOpen,
  FiTrendingUp,
  FiUsers,
  FiAward,
  FiExternalLink
} from 'react-icons/fi';
import './RoleDetail.css';

const RoleDetail = () => {
  const { roleId } = useParams();
  const navigate = useNavigate();
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRoleDetails();
  }, [roleId]);

  const fetchRoleDetails = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:8004/api/roles/${roleId}`);
      setRole(response.data);
    } catch (error) {
      console.error('Failed to fetch role details:', error);
      if (error.response?.status === 404) {
        setError('Role not found');
      } else {
        setError('Failed to load role details');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="role-detail-loading">
        <div className="loading-spinner"></div>
        <p>Loading role details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="role-detail-error">
        <div className="error-content">
          <h2>Oops! Something went wrong</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
              Back to Dashboard
            </button>
            <button onClick={fetchRoleDetails} className="btn btn-secondary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!role) {
    return null;
  }

  return (
    <div className="role-detail">
      <div className="role-detail-container">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="role-header"
        >
          <Link to="/dashboard" className="back-button">
            <FiArrowLeft />
            Back to Dashboard
          </Link>
          
          <div className="role-title-section">
            <h1 className="role-title">{role.title}</h1>
            <p className="role-subtitle">{role.cardSubtitle}</p>
          </div>
        </motion.div>

        {/* Overview Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="role-section"
        >
          <div className="section-header">
            <FiBookOpen className="section-icon" />
            <h2>Role Overview</h2>
          </div>
          <div className="section-content">
            <p className="overview-text">{role.overview}</p>
          </div>
        </motion.section>

        {/* Responsibilities Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="role-section"
        >
          <div className="section-header">
            <FiTarget className="section-icon" />
            <h2>Key Responsibilities</h2>
          </div>
          <div className="section-content">
            <ul className="responsibilities-list">
              {role.responsibilities.map((responsibility, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                  className="responsibility-item"
                >
                  <FiCheckCircle className="check-icon" />
                  <span>{responsibility}</span>
                </motion.li>
              ))}
            </ul>
          </div>
        </motion.section>

        {/* Skills Section */}
        <div className="skills-sections">
          {/* Must Have Skills */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="role-section skills-section"
          >
            <div className="section-header">
              <FiAward className="section-icon" />
              <h2>Must-Have Skills</h2>
            </div>
            <div className="section-content">
              <div className="skills-grid">
                {role.mustHaveSkills.map((skill, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.4 + index * 0.05 }}
                    className="skill-card must-have"
                  >
                    {skill}
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.section>

          {/* Good to Have Skills */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="role-section skills-section"
          >
            <div className="section-header">
              <FiTrendingUp className="section-icon" />
              <h2>Good-to-Have Skills</h2>
            </div>
            <div className="section-content">
              <div className="skills-grid">
                {role.goodToHaveSkills.map((skill, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.5 + index * 0.05 }}
                    className="skill-card good-to-have"
                  >
                    {skill}
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.section>
        </div>

        {/* Tools Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="role-section"
        >
          <div className="section-header">
            <FiTool className="section-icon" />
            <h2>Tools & Technologies</h2>
          </div>
          <div className="section-content">
            <div className="tools-grid">
              {role.tools.map((tool, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.6 + index * 0.05 }}
                  className="tool-card"
                >
                  <FiTool className="tool-icon" />
                  <span>{tool}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Action Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="role-actions"
        >
          <div className="actions-content">
            <h3>Ready to pursue this career?</h3>
            <p>Use our AI-powered tools to analyze your skills and get personalized recommendations</p>
            <div className="action-buttons">
              <Link to="/skill-gap-analyzer" className="btn btn-primary">
                <FiTarget />
                Analyze Skill Gap
              </Link>
              <Link to="/resume-scoring" className="btn btn-secondary">
                <FiUsers />
                Score My Resume
              </Link>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  );
};

export default RoleDetail;