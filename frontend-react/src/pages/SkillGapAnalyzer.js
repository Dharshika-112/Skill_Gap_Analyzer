import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiTarget, 
  FiPlus, 
  FiX, 
  FiSearch, 
  FiTrendingUp, 
  FiAlertCircle,
  FiCheckCircle,
  FiZap,
  FiBookOpen,
  FiClock,
  FiAward,
  FiBarChart2,
  FiPieChart,
  FiActivity
} from 'react-icons/fi';
import './SkillGapAnalyzer.css';

const SkillGapAnalyzer = () => {
  const [userSkills, setUserSkills] = useState([]);
  const [skillInput, setSkillInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [skillSuggestions, setSkillSuggestions] = useState([]);
  const [allSkills, setAllSkills] = useState([]);
  const [skillCategories, setSkillCategories] = useState({});
  const [popularSkills, setPopularSkills] = useState([]);
  const [showCategorySkills, setShowCategorySkills] = useState(true);
  const [roleRecommendations, setRoleRecommendations] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [roleAnalysis, setRoleAnalysis] = useState(null);
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [quizResults, setQuizResults] = useState(null);
  const [showQuiz, setShowQuiz] = useState(false);
  const [step, setStep] = useState(1); // 1: Skills, 2: Role Suggestions, 3: Specific Analysis, 4: Quiz
  const [hasActiveAnalysis, setHasActiveAnalysis] = useState(false);
  const [currentAnalysisId, setCurrentAnalysisId] = useState(null);

  // Load available skills and check for existing analysis on component mount
  useEffect(() => {
    loadAllSkills();
    checkExistingAnalysis();
  }, []);

  const checkExistingAnalysis = async () => {
    try {
      const userId = localStorage.getItem('userId') || 'demo_user';
      const response = await fetch(`http://localhost:8006/api/user/${userId}/analyses`);
      const data = await response.json();
      
      if (data.success && data.has_active_analysis && data.active_analyses.length > 0) {
        const latestAnalysis = data.active_analyses[0];
        setHasActiveAnalysis(true);
        setCurrentAnalysisId(latestAnalysis.analysis_id);
        
        // Restore analysis state
        if (latestAnalysis.analysis_type === 'role_suggestions') {
          setUserSkills(latestAnalysis.user_skills);
          setRoleRecommendations(latestAnalysis.role_suggestions);
          setStep(2);
        } else if (latestAnalysis.analysis_type === 'specific_role') {
          setUserSkills(latestAnalysis.user_skills);
          setSelectedRole(latestAnalysis.target_role);
          setRoleAnalysis(latestAnalysis.analysis_result);
          setStep(3);
        }
      }
    } catch (error) {
      console.error('Failed to check existing analysis:', error);
    }
  };

  const loadAllSkills = async () => {
    try {
      const response = await fetch('http://localhost:8006/api/skills/all');
      const data = await response.json();
      
      if (data.success) {
        setAllSkills(data.all_skills || []);
        setSkillCategories(data.skill_categories || {});
        setPopularSkills(data.popular_skills || []);
      }
    } catch (error) {
      console.error('Failed to load skills:', error);
    }
  };

  useEffect(() => {
    // Filter skill suggestions based on input from dataset skills with categories
    if (skillInput.length > 0) {
      const filtered = allSkills.filter(skill => 
        skill.toLowerCase().includes(skillInput.toLowerCase()) &&
        !userSkills.map(s => s.toLowerCase()).includes(skill.toLowerCase())
      );
      setSkillSuggestions(filtered.slice(0, 15));
    } else {
      setSkillSuggestions([]);
    }
  }, [skillInput, userSkills, allSkills]);

  const addSkill = (skill) => {
    if (skill && !userSkills.map(s => s.toLowerCase()).includes(skill.toLowerCase())) {
      setUserSkills([...userSkills, skill]);
      setSkillInput('');
      setSkillSuggestions([]);
    }
  };

  const removeSkill = (skillToRemove) => {
    setUserSkills(userSkills.filter(skill => skill.toLowerCase() !== skillToRemove.toLowerCase()));
  };

  const handleSkillInputKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill(skillInput.trim());
    }
  };

  const getRoleSuggestions = async () => {
    if (userSkills.length === 0) {
      setError('Please add at least one skill');
      return;
    }

    setIsAnalyzing(true);
    setError('');

    try {
      const userId = localStorage.getItem('userId') || 'demo_user';
      const response = await fetch('http://localhost:8006/api/analysis/role-suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          selected_skills: userSkills
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setRoleRecommendations(data.role_suggestions || []);
        setCurrentAnalysisId(data.analysis_id);
        setHasActiveAnalysis(true);
        setStep(2);
      } else {
        throw new Error(data.error || 'Failed to get role suggestions');
      }

    } catch (err) {
      setError(err.message || 'An error occurred. Please check if the Enhanced Skill Gap Analyzer API is running on port 8006.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const analyzeSpecificRole = async (roleName) => {
    setIsAnalyzing(true);
    setError('');
    setRoleAnalysis(null);

    try {
      const userId = localStorage.getItem('userId') || 'demo_user';
      const response = await fetch('http://localhost:8006/api/analysis/specific-role', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          user_skills: userSkills,
          target_role: roleName
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setRoleAnalysis(data.analysis_result);
        setSelectedRole(roleName);
        setCurrentAnalysisId(data.analysis_id);
        setStep(3);
      } else {
        throw new Error(data.error || 'Analysis failed');
      }

    } catch (err) {
      setError(err.message || 'An error occurred during analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const startQuiz = async (roleName) => {
    try {
      const userId = localStorage.getItem('userId') || 'demo_user';
      const response = await fetch(`http://localhost:8006/api/quiz/${encodeURIComponent(roleName)}?user_id=${userId}`);
      const data = await response.json();
      
      if (data.success) {
        setCurrentQuiz(data);
        setShowQuiz(true);
        setStep(4);
      } else {
        throw new Error(data.error || 'Failed to load quiz');
      }
    } catch (err) {
      setError(err.message || 'Failed to start quiz');
    }
  };

  const submitQuiz = async (answers) => {
    try {
      const userId = localStorage.getItem('userId') || 'demo_user';
      const response = await fetch('http://localhost:8006/api/quiz/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          attempt_id: currentQuiz.attempt_id,
          answers: answers
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setQuizResults(data);
        setShowQuiz(false);
      } else {
        throw new Error(data.error || 'Failed to submit quiz');
      }
    } catch (err) {
      setError(err.message || 'Failed to submit quiz');
    }
  };

  const resetAnalysis = async () => {
    try {
      const userId = localStorage.getItem('userId') || 'demo_user';
      await fetch(`http://localhost:8006/api/user/${userId}/new-analysis`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Failed to clear analysis:', error);
    }
    
    setRoleRecommendations([]);
    setRoleAnalysis(null);
    setSelectedRole(null);
    setQuizResults(null);
    setCurrentQuiz(null);
    setShowQuiz(false);
    setError('');
    setUserSkills([]);
    setHasActiveAnalysis(false);
    setCurrentAnalysisId(null);
    setStep(1);
  };

  const getMatchColor = (percentage) => {
    if (percentage >= 80) return '#10b981';
    if (percentage >= 60) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="skill-gap-analyzer">
      <div className="container">
        {/* Header */}
        <motion.div 
          className="page-header"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="header-content">
            <div className="header-icon">
              <FiTarget />
            </div>
            <div>
              <h1>AI-Powered Skill Gap Analyzer</h1>
              <p>Advanced skill analysis with role recommendations and personalized learning paths</p>
            </div>
            {hasActiveAnalysis && (
              <div className="header-actions">
                <button 
                  className="new-analysis-btn"
                  onClick={resetAnalysis}
                >
                  <FiPlus />
                  New Analysis
                </button>
              </div>
            )}
          </div>
        </motion.div>

        {/* Step 1: Skills Input */}
        {step === 1 && (
          <div className="analyzer-form">
            <motion.div 
              className="skills-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <h2>Step 1: Enter Your Skills</h2>
              <p>Select your skills from our comprehensive dataset of {allSkills.length} skills</p>
              
              <div className="skills-input-container">
                <div className="skill-input-wrapper">
                  <input
                    type="text"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyPress={handleSkillInputKeyPress}
                    placeholder="Type a skill and press Enter (e.g., JavaScript, Python, React)"
                    className="skill-input"
                  />
                  <button 
                    className="add-skill-btn"
                    onClick={() => addSkill(skillInput.trim())}
                    disabled={!skillInput.trim()}
                  >
                    <FiPlus />
                  </button>
                </div>

                {/* Category-wise Skill Suggestions */}
                <AnimatePresence>
                  {skillSuggestions.length > 0 && (
                    <motion.div 
                      className="skill-suggestions-container"
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                    >
                      <div className="suggestions-header">
                        <span>Matching Skills ({skillSuggestions.length} found)</span>
                      </div>
                      
                      {/* Group suggestions by category */}
                      {Object.keys(skillCategories).map(category => {
                        const categorySkills = skillSuggestions.filter(skill => 
                          skillCategories[category].some(catSkill => 
                            catSkill.toLowerCase() === skill.toLowerCase()
                          )
                        );
                        
                        if (categorySkills.length === 0) return null;
                        
                        return (
                          <div key={category} className="skill-category-group">
                            <div className="category-title">
                              {category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}
                            </div>
                            <div className="category-skills">
                              {categorySkills.map((skill, index) => (
                                <button
                                  key={skill}
                                  className="skill-suggestion"
                                  onClick={() => addSkill(skill)}
                                >
                                  {skill}
                                </button>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                      
                      {/* Other skills not in categories */}
                      {(() => {
                        const uncategorizedSkills = skillSuggestions.filter(skill => 
                          !Object.values(skillCategories).flat().some(catSkill => 
                            catSkill.toLowerCase() === skill.toLowerCase()
                          )
                        );
                        
                        if (uncategorizedSkills.length === 0) return null;
                        
                        return (
                          <div className="skill-category-group">
                            <div className="category-title">Other Skills</div>
                            <div className="category-skills">
                              {uncategorizedSkills.map((skill, index) => (
                                <button
                                  key={skill}
                                  className="skill-suggestion"
                                  onClick={() => addSkill(skill)}
                                >
                                  {skill}
                                </button>
                              ))}
                            </div>
                          </div>
                        );
                      })()}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Current Skills */}
              <div className="current-skills">
                <AnimatePresence>
                  {userSkills.map((skill, index) => (
                    <motion.div
                      key={skill}
                      className="skill-tag"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.2 }}
                    >
                      <span>{skill}</span>
                      <button 
                        className="remove-skill"
                        onClick={() => removeSkill(skill)}
                      >
                        <FiX />
                      </button>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {userSkills.length > 0 && (
                <div className="skills-summary">
                  <p>✅ {userSkills.length} skills selected</p>
                </div>
              )}

              {/* Category-wise Popular Skills */}
              {showCategorySkills && userSkills.length < 10 && (
                <div className="popular-skills-section">
                  <h3>Popular Skills by Category</h3>
                  <p>Click to add skills quickly</p>
                  
                  {Object.keys(skillCategories).map(category => {
                    const categorySkills = skillCategories[category].filter(skill => 
                      !userSkills.map(s => s.toLowerCase()).includes(skill.toLowerCase())
                    ).slice(0, 8);
                    
                    if (categorySkills.length === 0) return null;
                    
                    return (
                      <div key={category} className="skill-category-section">
                        <h4 className="category-title">
                          {category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}
                        </h4>
                        <div className="category-skills-grid">
                          {categorySkills.map((skill, index) => (
                            <button
                              key={skill}
                              className="popular-skill-btn"
                              onClick={() => addSkill(skill)}
                            >
                              <span className="skill-name">{skill}</span>
                              <FiPlus className="add-icon" />
                            </button>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                  
                  {/* Most Popular Skills */}
                  {popularSkills.length > 0 && (
                    <div className="skill-category-section">
                      <h4 className="category-title">Most Popular Skills</h4>
                      <div className="category-skills-grid">
                        {popularSkills.slice(0, 12).filter(skill => 
                          !userSkills.map(s => s.toLowerCase()).includes(skill.toLowerCase())
                        ).map((skill, index) => (
                          <button
                            key={skill}
                            className="popular-skill-btn trending"
                            onClick={() => addSkill(skill)}
                          >
                            <span className="skill-name">{skill}</span>
                            <FiTrendingUp className="trending-icon" />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <button 
                    className="toggle-categories-btn"
                    onClick={() => setShowCategorySkills(false)}
                  >
                    Hide Suggestions
                  </button>
                </div>
              )}

              {!showCategorySkills && (
                <button 
                  className="toggle-categories-btn"
                  onClick={() => setShowCategorySkills(true)}
                >
                  Show Skill Suggestions
                </button>
              )}
            </motion.div>

            {/* Error Display */}
            <AnimatePresence>
              {error && (
                <motion.div 
                  className="error-message"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  <FiAlertCircle />
                  <span>{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Get Role Suggestions Button */}
            <motion.div 
              className="analyze-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <button 
                className="analyze-button"
                onClick={getRoleSuggestions}
                disabled={isAnalyzing || userSkills.length === 0}
              >
                {isAnalyzing ? (
                  <>
                    <div className="spinner" />
                    Analyzing with AI...
                  </>
                ) : (
                  <>
                    <FiZap />
                    Find Suitable Roles ({userSkills.length} skills)
                  </>
                )}
              </button>
            </motion.div>
          </div>
        )}

        {/* Step 2: Role Suggestions */}
        {step === 2 && roleRecommendations.length > 0 && (
          <motion.div 
            className="role-suggestions-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="section-header">
              <h2>Step 2: Most Suitable Roles Based on Your Skills</h2>
              <p>AI-powered role recommendations with match percentages and missing skills</p>
            </div>

            <div className="role-recommendations-grid">
              {roleRecommendations.map((role, index) => (
                <motion.div
                  key={role.role_name}
                  className="role-recommendation-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <div className="role-header">
                    <h3>{role.role_name}</h3>
                    <div className="match-badges">
                      <span className="match-percentage" style={{ backgroundColor: getMatchColor(role.match_percentage) }}>
                        {role.match_percentage}% Match
                      </span>
                      <span className="ai-confidence">
                        AI: {(role.ml_confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="role-stats">
                    <div className="stat">
                      <span className="stat-number">{role.matched_skills.length}</span>
                      <span className="stat-label">Matched</span>
                    </div>
                    <div className="stat">
                      <span className="stat-number">{role.missing_skills.length}</span>
                      <span className="stat-label">Missing</span>
                    </div>
                    <div className="stat">
                      <span className="stat-number">{role.total_required_skills}</span>
                      <span className="stat-label">Total</span>
                    </div>
                  </div>

                  <div className="role-skills-preview">
                    <div className="matched-skills-preview">
                      <strong>✅ Your Skills:</strong>
                      <div className="skills-preview">
                        {role.matched_skills.slice(0, 4).map(skill => (
                          <span key={skill} className="skill-preview matched">{skill}</span>
                        ))}
                        {role.matched_skills.length > 4 && (
                          <span className="more-skills">+{role.matched_skills.length - 4} more</span>
                        )}
                      </div>
                    </div>
                    
                    {role.missing_skills.length > 0 && (
                      <div className="missing-skills-preview">
                        <strong>❌ Missing Skills:</strong>
                        <div className="skills-preview">
                          {role.missing_skills.slice(0, 4).map(skill => (
                            <span key={skill} className="skill-preview missing">{skill}</span>
                          ))}
                          {role.missing_skills.length > 4 && (
                            <span className="more-skills">+{role.missing_skills.length - 4} more</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <button 
                    className="analyze-role-btn"
                    onClick={() => analyzeSpecificRole(role.role_name)}
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Detailed Analysis'}
                  </button>
                </motion.div>
              ))}
            </div>

            <div className="step-actions">
              <button className="btn btn-secondary" onClick={() => setStep(1)}>
                <FiTarget />
                Back to Skills
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3: Detailed Analysis */}
        {step === 3 && roleAnalysis && (
          <motion.div 
            className="results-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Analysis Header */}
            <div className="analysis-header">
              <h2>Step 3: Detailed Analysis for {roleAnalysis.role_name}</h2>
              <div className="analysis-meta">
                <span className="match-score">Match: {roleAnalysis.match_percentage}%</span>
                <span className="ai-confidence">AI Confidence: {roleAnalysis.ml_confidence}%</span>
                <span className="readiness">Readiness: {roleAnalysis.readiness_level}</span>
              </div>
            </div>

            {/* Match Overview */}
            <div className="match-overview">
              <div className="match-card">
                <div className="match-circle">
                  <svg viewBox="0 0 100 100" className="match-svg">
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="#e5e7eb"
                      strokeWidth="8"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke={getMatchColor(roleAnalysis.match_percentage)}
                      strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={`${roleAnalysis.match_percentage * 2.83} 283`}
                      transform="rotate(-90 50 50)"
                    />
                  </svg>
                  <div className="match-content">
                    <span className="match-number">{roleAnalysis.match_percentage}%</span>
                    <span className="match-label">Match</span>
                  </div>
                </div>
                <div className="match-details">
                  <h3>Skill Match for {roleAnalysis.role_name}</h3>
                  <p>
                    You match {roleAnalysis.matched_skills.length} out of {roleAnalysis.total_required_skills} required skills
                  </p>
                  <div className="match-stats">
                    <div className="stat">
                      <span className="stat-number">{roleAnalysis.matched_skills.length}</span>
                      <span className="stat-label">Matched Skills</span>
                    </div>
                    <div className="stat">
                      <span className="stat-number">{roleAnalysis.missing_skills.length}</span>
                      <span className="stat-label">Missing Skills</span>
                    </div>
                    <div className="stat">
                      <span className="stat-number">{roleAnalysis.job_count}</span>
                      <span className="stat-label">Jobs Available</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Skills Breakdown */}
            <div className="skills-breakdown">
              <div className="skills-grid">
                {/* Matched Skills */}
                <div className="skills-category matched">
                  <div className="category-header">
                    <FiCheckCircle />
                    <h3>Your Matching Skills ({roleAnalysis.matched_skills.length})</h3>
                  </div>
                  <div className="skills-list">
                    {roleAnalysis.matched_skills.map((skill, index) => (
                      <span key={index} className="skill-item matched">{skill}</span>
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="skills-category missing">
                  <div className="category-header">
                    <FiAlertCircle />
                    <h3>Skills to Learn ({roleAnalysis.missing_skills.length})</h3>
                  </div>
                  <div className="skills-list">
                    {roleAnalysis.missing_skills.map((skill, index) => (
                      <span key={index} className="skill-item missing">{skill}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Improvement Suggestions */}
            {roleAnalysis.improvement_suggestions && roleAnalysis.improvement_suggestions.length > 0 && (
              <div className="improvement-section">
                <h3>AI-Powered Improvement Suggestions</h3>
                <div className="suggestions-grid">
                  {roleAnalysis.improvement_suggestions.slice(0, 6).map((suggestion, index) => (
                    <div key={index} className="suggestion-card">
                      <div className="suggestion-header">
                        <h4>{suggestion.skill}</h4>
                        <div className="suggestion-badges">
                          <span className={`priority ${suggestion.priority > 0.7 ? 'high' : suggestion.priority > 0.4 ? 'medium' : 'low'}`}>
                            {suggestion.priority > 0.7 ? 'High' : suggestion.priority > 0.4 ? 'Medium' : 'Low'} Priority
                          </span>
                          <span className={`difficulty ${suggestion.difficulty.toLowerCase()}`}>
                            {suggestion.difficulty}
                          </span>
                        </div>
                      </div>
                      <p className="estimated-time">
                        <FiClock /> {suggestion.estimated_time}
                      </p>
                      {suggestion.learning_path && (
                        <div className="learning-path">
                          <strong>Learning Path:</strong>
                          <ol>
                            {suggestion.learning_path.slice(0, 3).map((step, stepIndex) => (
                              <li key={stepIndex}>{step}</li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quiz Section */}
            <div className="quiz-section">
              <h3>Step 4: Test Your Knowledge</h3>
              <div className="quiz-card">
                <div className="quiz-info">
                  <h4>Take Quiz for {roleAnalysis.role_name}</h4>
                  <p>Test your knowledge with 10 role-specific questions and get instant feedback</p>
                  <div className="quiz-stats">
                    <span>📝 10 Questions</span>
                    <span>⏱️ 10 Minutes</span>
                    <span>🎯 70% to Pass</span>
                  </div>
                </div>
                <button 
                  className="quiz-btn"
                  onClick={() => startQuiz(roleAnalysis.role_name)}
                  disabled={isAnalyzing}
                >
                  <FiAward />
                  Start Quiz
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="results-actions">
              <button className="btn btn-secondary" onClick={() => setStep(2)}>
                <FiTarget />
                Back to Role Suggestions
              </button>
              <button className="btn btn-secondary" onClick={resetAnalysis}>
                <FiTarget />
                Start Over
              </button>
              <button className="btn btn-primary" onClick={() => window.print()}>
                <FiBookOpen />
                Export Report
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 4: Quiz */}
        {step === 4 && showQuiz && currentQuiz && (
          <QuizComponent 
            quiz={currentQuiz}
            onSubmit={submitQuiz}
            onCancel={() => {
              setShowQuiz(false);
              setStep(3);
            }}
          />
        )}

        {/* Quiz Results */}
        {quizResults && (
          <QuizResultsComponent 
            results={quizResults}
            onClose={() => setQuizResults(null)}
          />
        )}
      </div>
    </div>
  );
};

// Quiz Component
const QuizComponent = ({ quiz, onSubmit, onCancel }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [timeLeft, setTimeLeft] = useState(quiz.time_limit);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleAnswerSelect = (answerIndex) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answerIndex;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = () => {
    onSubmit(answers);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const question = quiz.questions[currentQuestion];

  return (
    <motion.div 
      className="quiz-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="quiz-header">
        <h2>Quiz: {quiz.role_name}</h2>
        <div className="quiz-progress">
          <span>Question {currentQuestion + 1} of {quiz.questions.length}</span>
          <span className="time-left">⏱️ {formatTime(timeLeft)}</span>
        </div>
      </div>

      <div className="quiz-content">
        <div className="question-section">
          <h3>{question.question_text}</h3>
          <div className="options-list">
            {question.options.map((option, index) => (
              <button
                key={index}
                className={`option-btn ${answers[currentQuestion] === index ? 'selected' : ''}`}
                onClick={() => handleAnswerSelect(index)}
              >
                <span className="option-letter">{String.fromCharCode(65 + index)}</span>
                <span className="option-text">{option}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="quiz-navigation">
          <button 
            className="btn btn-secondary" 
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
          >
            Previous
          </button>
          
          <div className="question-indicators">
            {quiz.questions.map((_, index) => (
              <div
                key={index}
                className={`indicator ${index === currentQuestion ? 'current' : ''} ${answers[index] !== undefined ? 'answered' : ''}`}
                onClick={() => setCurrentQuestion(index)}
              >
                {index + 1}
              </div>
            ))}
          </div>

          {currentQuestion < quiz.questions.length - 1 ? (
            <button 
              className="btn btn-primary" 
              onClick={handleNext}
            >
              Next
            </button>
          ) : (
            <button 
              className="btn btn-success" 
              onClick={handleSubmit}
            >
              Submit Quiz
            </button>
          )}
        </div>
      </div>

      <div className="quiz-actions">
        <button className="btn btn-secondary" onClick={onCancel}>
          Cancel Quiz
        </button>
      </div>
    </motion.div>
  );
};

// Quiz Results Component
const QuizResultsComponent = ({ results, onClose }) => {
  return (
    <motion.div 
      className="quiz-results-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div 
        className="quiz-results-modal"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
      >
        <div className="results-header">
          <h2>Quiz Results</h2>
          <button className="close-btn" onClick={onClose}>
            <FiX />
          </button>
        </div>

        <div className="results-content">
          <div className="score-section">
            <div className={`score-circle ${results.passed ? 'passed' : 'failed'}`}>
              <span className="score-number">{results.score}%</span>
              <span className="score-label">{results.passed ? 'Passed' : 'Failed'}</span>
            </div>
            <div className="score-details">
              <p>{results.correct_answers} out of {results.total_questions} correct</p>
              <p>Passing score: 70%</p>
            </div>
          </div>

          {/* Improvement Suggestions */}
          {results.improvement_suggestions && results.improvement_suggestions.length > 0 && (
            <div className="improvement-suggestions">
              <h3>📈 Personalized Improvement Plan</h3>
              <div className="suggestions-list">
                {results.improvement_suggestions.map((suggestion, index) => (
                  <div key={index} className={`suggestion-item ${suggestion.priority}`}>
                    <div className="suggestion-header">
                      <h4>{suggestion.title}</h4>
                      <span className={`priority-badge ${suggestion.priority}`}>
                        {suggestion.priority.charAt(0).toUpperCase() + suggestion.priority.slice(1)} Priority
                      </span>
                    </div>
                    <p className="suggestion-description">{suggestion.description}</p>
                    <div className="suggestion-action">
                      <strong>Action:</strong> {suggestion.action}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="detailed-results">
            <h3>Question Review</h3>
            {results.detailed_results.map((result, index) => (
              <div key={index} className={`question-result ${result.is_correct ? 'correct' : 'incorrect'}`}>
                <div className="question-number">Q{index + 1}</div>
                <div className="result-icon">
                  {result.is_correct ? <FiCheckCircle /> : <FiX />}
                </div>
                <div className="result-text">
                  {result.is_correct ? 'Correct' : 'Incorrect'}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="results-actions">
          <button className="btn btn-primary" onClick={onClose}>
            Continue Analysis
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default SkillGapAnalyzer;