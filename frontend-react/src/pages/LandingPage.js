import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FiTarget, 
  FiTrendingUp, 
  FiZap, 
  FiUsers, 
  FiSun,
  FiCheckCircle,
  FiArrowRight,
  FiPlay
} from 'react-icons/fi';
import './LandingPage.css';

const LandingPage = () => {
  const features = [
    {
      icon: FiTarget,
      title: 'AI-Powered Skill Gap Analysis',
      description: 'Compare your skills against 1000+ real job descriptions using advanced machine learning algorithms.',
      color: '#2563eb'
    },
    {
      icon: FiTrendingUp,
      title: 'Professional ATS Resume Scoring',
      description: 'Get accurate ATS scores using our trained ML model on real resume screening data.',
      color: '#059669'
    },
    {
      icon: FiSun,
      title: 'Intelligent Career Suggestions',
      description: 'Receive personalized recommendations to improve your resume and career prospects.',
      color: '#d97706'
    },
    {
      icon: FiUsers,
      title: 'Role-Based Analysis',
      description: 'Analyze your profile against specific job roles with detailed skill matching.',
      color: '#dc2626'
    }
  ];

  const stats = [
    { number: '1000+', label: 'Job Descriptions Analyzed' },
    { number: '2200+', label: 'Skills in Database' },
    { number: '218', label: 'Job Roles Covered' },
    { number: '95%', label: 'Accuracy Rate' }
  ];

  const benefits = [
    'Focus your learning on high-priority skills',
    'Increase your job compatibility score',
    'Get strategic career development roadmap',
    'Stand out to employers with relevant skills',
    'Save time with AI-powered analysis',
    'Access real market insights'
  ];

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <motion.div
            className="hero-content"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="hero-badge">
              <FiZap className="badge-icon" />
              <span>AI-Powered Career Analysis</span>
            </div>
            
            <h1 className="hero-title">
              Bridge Your <span className="gradient-text">Skill Gap</span> with 
              <br />AI-Powered Career Intelligence
            </h1>
            
            <p className="hero-description">
              Discover exactly which skills you need to land your dream job. Our advanced AI analyzes 
              1000+ real job descriptions to give you personalized, actionable career insights.
            </p>
            
            <div className="hero-buttons">
              <Link to="/signup" className="btn btn-primary large">
                Start Free Analysis
                <FiArrowRight />
              </Link>
              <button className="btn btn-outline large demo-btn">
                <FiPlay />
                Watch Demo
              </button>
            </div>
            
            <div className="hero-stats">
              {stats.map((stat, index) => (
                <motion.div
                  key={index}
                  className="stat-item"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                >
                  <div className="stat-number">{stat.number}</div>
                  <div className="stat-label">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
          
          <motion.div
            className="hero-visual"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="visual-card">
              <div className="card-header">
                <div className="card-title">Skill Analysis Report</div>
                <div className="card-status">✅ Complete</div>
              </div>
              <div className="progress-section">
                <div className="progress-item">
                  <span>Match Score</span>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: '85%' }}></div>
                  </div>
                  <span>85%</span>
                </div>
                <div className="progress-item">
                  <span>ATS Score</span>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: '92%' }}></div>
                  </div>
                  <span>92%</span>
                </div>
              </div>
              <div className="skills-preview">
                <div className="skill-tag matched">React</div>
                <div className="skill-tag matched">Python</div>
                <div className="skill-tag missing">Docker</div>
                <div className="skill-tag matched">AWS</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <motion.div
            className="section-header"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="section-title">Powerful Features for Career Growth</h2>
            <p className="section-description">
              Everything you need to understand and bridge your skill gaps with AI precision
            </p>
          </motion.div>
          
          <div className="features-grid">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="feature-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -5 }}
              >
                <div className="feature-icon" style={{ background: feature.color }}>
                  <feature.icon />
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section">
        <div className="container">
          <div className="benefits-content">
            <motion.div
              className="benefits-text"
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="section-title">Why Choose SkillSync Pro?</h2>
              <p className="section-description">
                Our AI-powered platform gives you the competitive edge you need in today's job market.
              </p>
              
              <div className="benefits-list">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={index}
                    className="benefit-item"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    viewport={{ once: true }}
                  >
                    <FiCheckCircle className="benefit-icon" />
                    <span>{benefit}</span>
                  </motion.div>
                ))}
              </div>
              
              <Link to="/signup" className="btn btn-primary large">
                Get Started Now
                <FiArrowRight />
              </Link>
            </motion.div>
            
            <motion.div
              className="benefits-visual"
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <div className="dashboard-preview">
                <div className="preview-header">
                  <div className="preview-nav">
                    <div className="nav-dot active"></div>
                    <div className="nav-dot"></div>
                    <div className="nav-dot"></div>
                  </div>
                  <div className="preview-title">Career Dashboard</div>
                </div>
                <div className="preview-content">
                  <div className="metric-card">
                    <div className="metric-label">Career Readiness</div>
                    <div className="metric-value">87%</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-label">Skills Matched</div>
                    <div className="metric-value">24/28</div>
                  </div>
                  <div className="chart-placeholder">
                    <div className="chart-bar" style={{ height: '60%' }}></div>
                    <div className="chart-bar" style={{ height: '80%' }}></div>
                    <div className="chart-bar" style={{ height: '45%' }}></div>
                    <div className="chart-bar" style={{ height: '90%' }}></div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <motion.div
            className="cta-content"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="cta-title">Ready to Accelerate Your Career?</h2>
            <p className="cta-description">
              Join thousands of professionals who have already discovered their skill gaps and 
              accelerated their career growth with our AI-powered platform.
            </p>
            <div className="cta-buttons">
              <Link to="/signup" className="btn btn-primary large">
                Start Your Analysis
                <FiArrowRight />
              </Link>
              <Link to="/login" className="btn btn-outline large">
                Already have an account?
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;