import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiUpload, 
  FiFileText, 
  FiTrendingUp, 
  FiTarget, 
  FiZap,
  FiCheckCircle,
  FiAlertCircle,
  FiInfo,
  FiDownload,
  FiRefreshCw,
  FiCpu,
  FiLayers
} from 'react-icons/fi';
import './ResumeScoring.css';

const ResumeScoring = () => {
  const [file, setFile] = useState(null);
  const [scoringType, setScoringType] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    console.log('Files dropped:', e.dataTransfer.files);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      console.log('Dropped file:', droppedFile.name, droppedFile.type);
      
      if (droppedFile.type === 'application/pdf' || droppedFile.name.toLowerCase().endsWith('.pdf')) {
        if (droppedFile.size > 10 * 1024 * 1024) { // 10MB limit
          setError('File size must be less than 10MB');
          return;
        }
        setFile(droppedFile);
        setError('');
        console.log('Dropped file set successfully');
      } else {
        setError('Please upload a PDF file only');
        console.log('Invalid dropped file type');
      }
    }
  }, []);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    console.log('File selected:', selectedFile);
    
    if (selectedFile) {
      console.log('File type:', selectedFile.type);
      console.log('File name:', selectedFile.name);
      
      if (selectedFile.type === 'application/pdf' || selectedFile.name.toLowerCase().endsWith('.pdf')) {
        if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
          setError('File size must be less than 10MB');
          return;
        }
        setFile(selectedFile);
        setError('');
        console.log('File set successfully:', selectedFile.name);
      } else {
        setError('Please upload a PDF file only');
        console.log('Invalid file type');
      }
    }
  };

  const handleScoreResume = async () => {
    if (!file) {
      setError('Please upload a resume first');
      return;
    }

    if (!scoringType) {
      setError('Please select a scoring type');
      return;
    }

    if (scoringType === 'role-based' && !targetRole) {
      setError('Please enter a target role for role-based scoring');
      return;
    }

    setIsProcessing(true);
    setError('');
    setResults(null);

    try {
      // Step 1: Upload and parse resume
      setProcessingStep('Step 1: Document Processing & OCR');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', localStorage.getItem('userId') || 'demo_user');

      const uploadResponse = await fetch('http://localhost:8007/api/resume/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload resume');
      }

      const uploadResult = await uploadResponse.json();

      // Step 2: Extract and analyze content
      setProcessingStep('Step 2: Deep Learning Analysis & Skill Extraction');
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate processing

      // Step 3: Score based on type
      let scoringEndpoint = 'http://localhost:8007/api/resume/score-general';
      let requestBody = { 
        resume_data: uploadResult.parsed_data 
      };

      if (scoringType === 'role-based') {
        setProcessingStep('Step 3: Role-Based ML Scoring');
        scoringEndpoint = 'http://localhost:8007/api/resume/score-role-based';
        requestBody = {
          resume_data: uploadResult.parsed_data,
          target_role: targetRole
        };
      } else {
        setProcessingStep('Step 3: General ATS Scoring');
      }

      const scoringResponse = await fetch(scoringEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!scoringResponse.ok) {
        throw new Error('Failed to score resume');
      }

      const scoringResult = await scoringResponse.json();

      // Step 4: Generate insights and recommendations
      setProcessingStep('Step 4: Generating Insights & Recommendations');
      await new Promise(resolve => setTimeout(resolve, 1000));

      setResults({
        ...scoringResult,
        resume_data: uploadResult.parsed_data,
        scoring_type: scoringType,
        target_role: targetRole
      });

    } catch (err) {
      setError(err.message || 'An error occurred while processing your resume');
    } finally {
      setIsProcessing(false);
      setProcessingStep('');
    }
  };

  const resetForm = () => {
    setFile(null);
    setScoringType('');
    setTargetRole('');
    setResults(null);
    setError('');
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // Green
    if (score >= 60) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  const getScoreLevel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Average';
    return 'Needs Improvement';
  };

  return (
    <div className="resume-scoring">
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
              <FiTrendingUp />
            </div>
            <div>
              <h1>Resume Scoring</h1>
              <p>Get your ATS score using advanced AI and machine learning algorithms</p>
            </div>
          </div>
        </motion.div>

        {!results ? (
          <div className="scoring-form">
            {/* File Upload Section */}
            <motion.div 
              className="upload-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <h2>Upload Your Resume</h2>
              <div 
                className={`upload-area ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => {
                  if (!file) {
                    document.querySelector('.file-input').click();
                  }
                }}
                style={{ cursor: file ? 'default' : 'pointer' }}
              >
                {file ? (
                  <div className="file-info">
                    <FiFileText className="file-icon" />
                    <div className="file-details">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                    <button 
                      className="remove-file"
                      onClick={() => setFile(null)}
                    >
                      ×
                    </button>
                  </div>
                ) : (
                  <div className="upload-placeholder">
                    <FiUpload className="upload-icon" />
                    <h3>Drop your resume here or click to browse</h3>
                    <p>Supports PDF files up to 10MB</p>
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileChange}
                      className="file-input"
                    />
                  </div>
                )}
              </div>
            </motion.div>

            {/* Scoring Type Selection */}
            <motion.div 
              className="scoring-options"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <h2>Choose Scoring Type</h2>
              <div className="scoring-types">
                <div 
                  className={`scoring-type ${scoringType === 'general' ? 'selected' : ''}`}
                  onClick={() => setScoringType('general')}
                >
                  <div className="type-icon">
                    <FiCpu />
                  </div>
                  <div className="type-content">
                    <h3>General ATS Scoring</h3>
                    <p>Universal ATS score based on industry standards and best practices</p>
                    <div className="type-features">
                      <span>✓ Industry-standard scoring</span>
                      <span>✓ General optimization tips</span>
                      <span>✓ Quick results</span>
                    </div>
                  </div>
                </div>

                <div 
                  className={`scoring-type ${scoringType === 'role-based' ? 'selected' : ''}`}
                  onClick={() => setScoringType('role-based')}
                >
                  <div className="type-icon">
                    <FiLayers />
                  </div>
                  <div className="type-content">
                    <h3>Role-Based Scoring</h3>
                    <p>Specialized scoring trained on specific job roles and requirements</p>
                    <div className="type-features">
                      <span>✓ Role-specific analysis</span>
                      <span>✓ Targeted recommendations</span>
                      <span>✓ Industry benchmarks</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Target Role Input */}
              <AnimatePresence>
                {scoringType === 'role-based' && (
                  <motion.div 
                    className="role-input"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <label htmlFor="targetRole">Target Job Role</label>
                    <input
                      id="targetRole"
                      type="text"
                      value={targetRole}
                      onChange={(e) => setTargetRole(e.target.value)}
                      placeholder="e.g., .NET Developer, Data Scientist, Software Engineer"
                      className="role-input-field"
                    />
                    <p className="input-help">
                      Enter the specific job role you're targeting for personalized scoring
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
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

            {/* Action Button */}
            <motion.div 
              className="action-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <button 
                className="score-button"
                onClick={handleScoreResume}
                disabled={isProcessing || !file || !scoringType}
              >
                {isProcessing ? (
                  <>
                    <FiRefreshCw className="spinning" />
                    Processing...
                  </>
                ) : (
                  <>
                    <FiZap />
                    Score My Resume
                  </>
                )}
              </button>
            </motion.div>
          </div>
        ) : (
          /* Results Section */
          <motion.div 
            className="results-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Score Overview */}
            <div className="score-overview">
              <div className="score-card">
                <div className="score-circle">
                  <svg viewBox="0 0 100 100" className="score-svg">
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
                      stroke={getScoreColor(results.score)}
                      strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={`${results.score * 2.83} 283`}
                      transform="rotate(-90 50 50)"
                    />
                  </svg>
                  <div className="score-content">
                    <span className="score-number">{results.score}</span>
                    <span className="score-label">ATS Score</span>
                  </div>
                </div>
                <div className="score-details">
                  <h3>{getScoreLevel(results.score)}</h3>
                  <p>
                    {scoringType === 'role-based' 
                      ? `Your resume scores ${results.score}/100 for ${targetRole} positions`
                      : `Your resume has a general ATS score of ${results.score}/100`
                    }
                  </p>
                  {results.benchmarks && (
                    <div className="benchmark-info">
                      <span>Industry Average: {results.benchmarks.average_score}</span>
                      <span>Top 10%: {results.benchmarks.percentiles['90th']}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Detailed Analysis */}
            <div className="analysis-grid">
              {/* Skills Analysis */}
              <div className="analysis-card">
                <div className="card-header">
                  <FiTarget />
                  <h3>Skills Analysis</h3>
                </div>
                <div className="card-content">
                  <div className="skills-stats">
                    <div className="stat">
                      <span className="stat-number">{results.resume_data?.skills?.length || 0}</span>
                      <span className="stat-label">Skills Identified</span>
                    </div>
                    {results.component_scores?.skills && (
                      <div className="stat">
                        <span className="stat-number">{Math.round(results.component_scores.skills)}%</span>
                        <span className="stat-label">Skills Score</span>
                      </div>
                    )}
                  </div>
                  <div className="skills-list">
                    {results.resume_data?.skills?.slice(0, 8).map((skill, index) => (
                      <span key={index} className="skill-tag">{skill}</span>
                    ))}
                    {results.resume_data?.skills?.length > 8 && (
                      <span className="more-skills">+{results.resume_data.skills.length - 8} more</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Experience Analysis */}
              <div className="analysis-card">
                <div className="card-header">
                  <FiTrendingUp />
                  <h3>Experience Profile</h3>
                </div>
                <div className="card-content">
                  <div className="experience-info">
                    <div className="exp-item">
                      <span className="exp-label">Years of Experience</span>
                      <span className="exp-value">{results.resume_data?.experience?.total_years || 0} years</span>
                    </div>
                    <div className="exp-item">
                      <span className="exp-label">Companies</span>
                      <span className="exp-value">{results.resume_data?.experience?.companies?.length || 0}</span>
                    </div>
                    <div className="exp-item">
                      <span className="exp-label">Experience Score</span>
                      <span className="exp-value">{Math.round(results.component_scores?.experience || 0)}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Content Quality */}
              <div className="analysis-card">
                <div className="card-header">
                  <FiInfo />
                  <h3>Content Quality</h3>
                </div>
                <div className="card-content">
                  <div className="quality-metrics">
                    <div className="metric-item">
                      <span className="metric-label">Overall Quality</span>
                      <span className="metric-value">{Math.round(results.component_scores?.content_quality || 0)}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Keywords</span>
                      <span className="metric-value">{results.resume_data?.keywords?.length || 0}</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Word Count</span>
                      <span className="metric-value">{results.resume_data?.word_count || 0}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Improvement Priorities */}
            {results.improvement_priority && results.improvement_priority.length > 0 && (
              <div className="improvement-priorities">
                <h3>Top Improvement Priorities</h3>
                <div className="priorities-list">
                  {results.improvement_priority.map((priority, index) => (
                    <div key={index} className={`priority-item ${priority.priority.toLowerCase()}`}>
                      <div className="priority-header">
                        <span className="priority-component">{priority.component}</span>
                        <span className="priority-badge">{priority.priority} Priority</span>
                      </div>
                      <div className="priority-score">
                        Current Score: {Math.round(priority.score)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Recommendations */}
            {results.recommendations && results.recommendations.length > 0 && (
              <div className="recommendations-section">
                <h3>Detailed Recommendations</h3>
                <div className="recommendations-list">
                  {results.recommendations.map((rec, index) => (
                    <div key={index} className={`recommendation-card ${rec.priority.toLowerCase()}`}>
                      <div className="rec-header">
                        <h4>{rec.category}</h4>
                        <span className="rec-priority">{rec.priority} Priority</span>
                      </div>
                      <p className="rec-suggestion">{rec.suggestion}</p>
                      <p className="rec-impact"><strong>Impact:</strong> {rec.impact}</p>
                      {rec.action_items && (
                        <div className="action-items">
                          <strong>Action Items:</strong>
                          <ul>
                            {rec.action_items.map((item, idx) => (
                              <li key={idx}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="results-actions">
              <button className="btn btn-secondary" onClick={resetForm}>
                <FiRefreshCw />
                Score Another Resume
              </button>
              <button className="btn btn-primary">
                <FiDownload />
                Download Report
              </button>
            </div>
          </motion.div>
        )}

        {/* Processing Overlay */}
        <AnimatePresence>
          {isProcessing && (
            <motion.div 
              className="processing-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="processing-content">
                <div className="processing-spinner">
                  <FiRefreshCw className="spinning" />
                </div>
                <h3>Processing Your Resume</h3>
                <p>{processingStep}</p>
                <div className="processing-steps">
                  <div className={`step ${processingStep.includes('Step 1') ? 'active' : processingStep.includes('Step 2') || processingStep.includes('Step 3') || processingStep.includes('Step 4') ? 'completed' : ''}`}>
                    <FiCheckCircle />
                    <span>Document Processing</span>
                  </div>
                  <div className={`step ${processingStep.includes('Step 2') ? 'active' : processingStep.includes('Step 3') || processingStep.includes('Step 4') ? 'completed' : ''}`}>
                    <FiCheckCircle />
                    <span>AI Analysis</span>
                  </div>
                  <div className={`step ${processingStep.includes('Step 3') ? 'active' : processingStep.includes('Step 4') ? 'completed' : ''}`}>
                    <FiCheckCircle />
                    <span>ML Scoring</span>
                  </div>
                  <div className={`step ${processingStep.includes('Step 4') ? 'active' : ''}`}>
                    <FiCheckCircle />
                    <span>Generating Report</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ResumeScoring;