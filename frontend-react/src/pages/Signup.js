import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff, FiTarget, FiTrendingUp, FiZap } from 'react-icons/fi';
import './Auth.css';

const Signup = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Optional profile fields
  const [showOptionalFields, setShowOptionalFields] = useState(false);
  const [phone, setPhone] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [experience, setExperience] = useState('');
  const [degree, setDegree] = useState('');

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    // Include optional profile data
    const profileData = {
      name,
      email,
      password,
      ...(phone && { phone }),
      ...(specialization && { specialization }),
      ...(experience && { experience }),
      ...(degree && { degree })
    };

    const result = await signup(profileData.name, profileData.email, profileData.password, {
      phone: profileData.phone,
      specialization: profileData.specialization,
      experience: profileData.experience,
      degree: profileData.degree
    });
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

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
            <h1 className="auth-title">Create Account</h1>
            <p className="auth-subtitle">
              Join CareerBoost AI and accelerate your career with personalized insights
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
              <label htmlFor="name" className="form-label">Full Name</label>
              <div className="input-wrapper">
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={`form-input ${error ? 'error' : ''}`}
                  placeholder="Enter your full name"
                  required
                  disabled={loading}
                />
                <FiUser className="input-icon" />
              </div>
            </div>

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
                  placeholder="Create a password (min 6 characters)"
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

            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">Confirm Password</label>
              <div className="input-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`form-input ${error ? 'error' : ''}`}
                  placeholder="Confirm your password"
                  required
                  disabled={loading}
                />
                <FiLock className="input-icon" />
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
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </button>

            {/* Optional Profile Section */}
            <div className="optional-section">
              <button
                type="button"
                onClick={() => setShowOptionalFields(!showOptionalFields)}
                className="optional-toggle"
              >
                {showOptionalFields ? 'Hide' : 'Add'} Optional Profile Info
                <span className="optional-badge">Get Better Recommendations</span>
              </button>

              {showOptionalFields && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="optional-fields"
                >
                  <div className="form-group">
                    <label htmlFor="phone" className="form-label">Phone Number (Optional)</label>
                    <div className="input-wrapper">
                      <input
                        type="tel"
                        id="phone"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        className="form-input"
                        placeholder="Enter your phone number"
                        disabled={loading}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="specialization" className="form-label">Specialization (Optional)</label>
                    <div className="input-wrapper">
                      <select
                        id="specialization"
                        value={specialization}
                        onChange={(e) => setSpecialization(e.target.value)}
                        className="form-input"
                        disabled={loading}
                      >
                        <option value="">Select your field</option>
                        {specializationOptions.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="experience" className="form-label">Years of Experience (Optional)</label>
                    <div className="input-wrapper">
                      <select
                        id="experience"
                        value={experience}
                        onChange={(e) => setExperience(e.target.value)}
                        className="form-input"
                        disabled={loading}
                      >
                        <option value="">Select experience level</option>
                        {experienceOptions.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="degree" className="form-label">Education Level (Optional)</label>
                    <div className="input-wrapper">
                      <select
                        id="degree"
                        value={degree}
                        onChange={(e) => setDegree(e.target.value)}
                        className="form-input"
                        disabled={loading}
                      >
                        <option value="">Select education level</option>
                        {degreeOptions.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </form>

          <div className="auth-footer">
            Already have an account?{' '}
            <Link to="/login" className="auth-link">
              Sign In
            </Link>
          </div>
        </div>

        <div className="auth-visual">
          <div className="visual-content">
            <h2 className="visual-title">Start Your Career Journey</h2>
            <p className="visual-description">
              Join thousands of professionals who have accelerated their careers with AI-powered insights and personalized recommendations.
            </p>

            <div className="feature-highlights">
              <div className="highlight-item">
                <div className="highlight-icon">
                  <FiTarget />
                </div>
                <div>
                  <div className="highlight-title">Smart Skill Analysis</div>
                  <div className="highlight-desc">AI-powered skill gap identification</div>
                </div>
              </div>

              <div className="highlight-item">
                <div className="highlight-icon">
                  <FiTrendingUp />
                </div>
                <div>
                  <div className="highlight-title">ATS Optimization</div>
                  <div className="highlight-desc">Resume scoring with real ATS logic</div>
                </div>
              </div>

              <div className="highlight-item">
                <div className="highlight-icon">
                  <FiZap />
                </div>
                <div>
                  <div className="highlight-title">Instant Insights</div>
                  <div className="highlight-desc">Get actionable career recommendations</div>
                </div>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number">218</div>
                <div className="stat-label">Job Roles</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">95%</div>
                <div className="stat-label">Accuracy Rate</div>
              </div>
            </div>

            <div className="testimonial">
              <div className="testimonial-text">
                "The skill gap analysis was spot-on! I got my dream job within 2 months of following their recommendations."
              </div>
              <div className="testimonial-author">
                <div className="author-avatar">SM</div>
                <div>
                  <div className="author-name">Sarah Miller</div>
                  <div className="author-title">Data Scientist</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Signup;