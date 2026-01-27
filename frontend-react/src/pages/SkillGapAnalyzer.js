import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import Select from 'react-select';
import { 
  FiTarget, 
  FiSearch, 
  FiCheck, 
  FiX, 
  FiTrendingUp,
  FiBookOpen,
  FiAward,
  FiUsers,
  FiRefreshCw
} from 'react-icons/fi';
import './SkillGapAnalyzer.css';

const SkillGapAnalyzer = () => {
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [availableSkills, setAvailableSkills] = useState([]);
  const [availableRoles, setAvailableRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [skillsLoading, setSkillsLoading] = useState(true);

  // Load available skills and roles on component mount
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [skillsResponse, rolesResponse] = await Promise.all([
        axios.get('/api/resume/all-skills'),
        axios.get('/api/resume/dataset-roles')
      ]);

      if (skillsResponse.data.status === 'success') {
        const skillOptions = skillsResponse.data.skills.map(skill => ({
          value: skill,
          label: skill
        }));
        setAvailableSkills(skillOptions);
      }

      if (rolesResponse.data.status === 'success') {
        const roleOptions = rolesResponse.data.roles.map(role => ({
          value: role.title,
          label: `${role.title} (${role.job_count} jobs)`,
          jobCount: role.job_count,
          experienceLevels: role.experience_levels
        }));
        setAvailableRoles(roleOptions);
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      setSkillsLoading(false);
    }
  };

  const handleSkillChange = (selectedOptions) => {
    setSelectedSkills(selectedOptions || []);
  };

  const handleRoleChange = (selectedOption) => {
    setSelectedRole(selectedOption);
  };

  const analyzeSkillGap = async () => {
    if (!selectedRole || selectedSkills.length === 0) {
      toast.error('Please select skills and a role');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/resume/analyze-role-gap', {
        role_title: selectedRole.title,
        user_skills: selectedSkills
      });

      setAnalysis(response.data.analysis);
      setStep(3);
      toast.success('Analysis completed!');
    } catch (error) {
      toast.error('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    setStep(1);
    setSelectedSkills([]);
    setSelectedRole(null);
    setAnalysis(null);
    setSearchTerm('');
    setSelectedCategory('all');
  };

  const filteredSkills = availableSkills.filter(skill => {
    const matchesSearch = skill.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || 
      (categorizedSkills[selectedCategory] && categorizedSkills[selectedCategory].includes(skill));
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...Object.keys(categorizedSkills)];

  const roleOptions = availableRoles.map(role => ({
    value: role.title,
    label: `${role.title} (${role.job_count} jobs)`,
    title: role.title,
    job_count: role.job_count
  }));

  return (
    <div className="skill-gap-analyzer">
      <div className="analyzer-container">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="analyzer-header"
        >
          <div className="header-content">
            <div className="header-icon">
              <FiTarget />
            </div>
            <div>
              <h1>Skill Gap Analyzer</h1>
              <p>Compare your skills with real job requirements from 1000+ job descriptions</p>
            </div>
          </div>
          
          <div className="progress-indicator">
            <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
              <span>1</span>
              <label>Select Skills</label>
            </div>
            <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
              <span>2</span>
              <label>Choose Role</label>
            </div>
            <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
              <span>3</span>
              <label>View Analysis</label>
            </div>
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          {/* Step 1: Skill Selection */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="step-content"
            >
              <div className="step-header">
                <h2>Select Your Skills</h2>
                <p>Choose from 2200+ technical skills. Selected: {selectedSkills.length}</p>
              </div>

              <div className="skills-controls">
                <div className="search-box">
                  <FiSearch className="search-icon" />
                  <input
                    type="text"
                    placeholder="Search skills..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="search-input"
                  />
                </div>

                <div className="category-filter">
                  <FiFilter className="filter-icon" />
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="category-select"
                  >
                    {categories.map(category => (
                      <option key={category} value={category}>
                        {category === 'all' ? 'All Categories' : category}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {selectedSkills.length > 0 && (
                <div className="selected-skills-summary">
                  <h3>Selected Skills ({selectedSkills.length})</h3>
                  <div className="selected-skills-list">
                    {selectedSkills.map(skill => (
                      <div key={skill} className="skill-tag selected">
                        {skill}
                        <button
                          onClick={() => handleSkillToggle(skill)}
                          className="remove-skill"
                        >
                          <FiX />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="skills-grid">
                {skillsLoading ? (
                  <div className="skills-loading">
                    <div className="loading-spinner"></div>
                    <p>Loading skills...</p>
                  </div>
                ) : (
                  filteredSkills.map(skill => (
                    <motion.button
                      key={skill}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSkillToggle(skill)}
                      className={`skill-tag ${selectedSkills.includes(skill) ? 'selected' : ''}`}
                    >
                      {skill}
                      {selectedSkills.includes(skill) && <FiCheck className="check-icon" />}
                    </motion.button>
                  ))
                )}
              </div>

              <div className="step-actions">
                <button
                  onClick={() => setStep(2)}
                  disabled={selectedSkills.length === 0}
                  className="btn btn-primary"
                >
                  Continue to Role Selection
                  <FiArrowRight />
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 2: Role Selection */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="step-content"
            >
              <div className="step-header">
                <h2>Choose Target Role</h2>
                <p>Select a role to analyze your skill gaps against real job requirements</p>
              </div>

              <div className="role-selection">
                <Select
                  options={roleOptions}
                  value={selectedRole ? { 
                    value: selectedRole.title, 
                    label: `${selectedRole.title} (${selectedRole.job_count} jobs)` 
                  } : null}
                  onChange={(option) => handleRoleSelect({
                    title: option.title,
                    job_count: option.job_count
                  })}
                  placeholder="Search and select a role..."
                  isSearchable
                  className="role-select"
                  classNamePrefix="select"
                />
              </div>

              {selectedRole && (
                <div className="role-preview">
                  <h3>Selected Role</h3>
                  <div className="role-card">
                    <div className="role-info">
                      <div className="role-title">{selectedRole.title}</div>
                      <div className="role-stats">
                        {selectedRole.job_count} jobs available
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="selected-skills-preview">
                <h3>Your Skills ({selectedSkills.length})</h3>
                <div className="skills-preview-list">
                  {selectedSkills.slice(0, 10).map(skill => (
                    <span key={skill} className="skill-tag">{skill}</span>
                  ))}
                  {selectedSkills.length > 10 && (
                    <span className="more-skills">+{selectedSkills.length - 10} more</span>
                  )}
                </div>
              </div>

              <div className="step-actions">
                <button
                  onClick={() => setStep(1)}
                  className="btn btn-secondary"
                >
                  Back to Skills
                </button>
                <button
                  onClick={analyzeSkillGap}
                  disabled={!selectedRole || loading}
                  className="btn btn-primary"
                >
                  {loading ? (
                    <>
                      <div className="loading-spinner small" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze Skill Gap
                      <FiTrendingUp />
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Analysis Results */}
          {step === 3 && analysis && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="step-content"
            >
              <div className="analysis-header">
                <h2>Skill Gap Analysis Results</h2>
                <p>Analysis for {analysis.role_title}</p>
              </div>

              <div className="analysis-overview">
                <div className="overview-card match-score">
                  <div className="card-header">
                    <h3>Match Score</h3>
                    <div className={`score ${analysis.readiness_color}`}>
                      {analysis.match_percentage}%
                    </div>
                  </div>
                  <div className="readiness-badge" style={{ backgroundColor: analysis.readiness_color }}>
                    {analysis.readiness}
                  </div>
                </div>

                <div className="overview-card skills-breakdown">
                  <h3>Skills Breakdown</h3>
                  <div className="breakdown-stats">
                    <div className="stat">
                      <div className="stat-number">{analysis.total_matching_skills}</div>
                      <div className="stat-label">Matching</div>
                    </div>
                    <div className="stat">
                      <div className="stat-number">{analysis.total_missing_skills}</div>
                      <div className="stat-label">Missing</div>
                    </div>
                    <div className="stat">
                      <div className="stat-number">{analysis.total_required_skills}</div>
                      <div className="stat-label">Required</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="skills-analysis">
                <div className="skills-section">
                  <h3>✅ Matching Skills ({analysis.total_matching_skills})</h3>
                  <div className="skills-list">
                    {analysis.matching_skills.map(skill => (
                      <span key={skill} className="skill-tag matching">{skill}</span>
                    ))}
                  </div>
                </div>

                <div className="skills-section">
                  <h3>❌ Missing Skills ({analysis.total_missing_skills})</h3>
                  <div className="skills-list">
                    {analysis.missing_skills.map(skill => (
                      <span key={skill} className="skill-tag missing">{skill}</span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="recommendations-section">
                <h3>📚 Recommendations</h3>
                <div className="recommendations-list">
                  {analysis.recommendations.map((rec, index) => (
                    <div key={index} className="recommendation-item">
                      <FiCheck className="rec-icon" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="step-actions">
                <button
                  onClick={resetAnalysis}
                  className="btn btn-secondary"
                >
                  <FiRefreshCw />
                  New Analysis
                </button>
                <button
                  onClick={() => window.print()}
                  className="btn btn-primary"
                >
                  Export Report
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default SkillGapAnalyzer;