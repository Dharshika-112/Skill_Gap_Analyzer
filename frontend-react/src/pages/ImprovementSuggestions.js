import React, { useState, useEffect } from 'react';
import { FiSun, FiTrendingUp, FiBook, FiAward } from 'react-icons/fi';

const ImprovementSuggestions = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call for suggestions
    setTimeout(() => {
      setSuggestions([
        {
          id: 1,
          type: 'skill',
          title: 'Learn React.js',
          description: 'React is in high demand for frontend development roles',
          priority: 'high',
          timeToLearn: '2-3 months',
          resources: ['React Documentation', 'FreeCodeCamp', 'Udemy Courses']
        },
        {
          id: 2,
          type: 'certification',
          title: 'AWS Cloud Practitioner',
          description: 'Cloud skills are essential for modern development',
          priority: 'medium',
          timeToLearn: '1-2 months',
          resources: ['AWS Training', 'A Cloud Guru', 'Practice Exams']
        },
        {
          id: 3,
          type: 'experience',
          title: 'Build Portfolio Projects',
          description: 'Showcase your skills with real-world projects',
          priority: 'high',
          timeToLearn: 'Ongoing',
          resources: ['GitHub', 'Personal Website', 'Open Source']
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'low': return '#27ae60';
      default: return '#3498db';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'skill': return <FiTrendingUp />;
      case 'certification': return <FiAward />;
      case 'experience': return <FiBook />;
      default: return <FiSun />;
    }
  };

  if (loading) {
    return (
      <div className="improvement-suggestions">
        <div className="container">
          <h1>Loading Suggestions...</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="improvement-suggestions">
      <div className="container">
        <h1>Career Improvement Suggestions</h1>
        <p>Personalized recommendations to boost your career prospects</p>

        <div className="suggestions-grid">
          {suggestions.map(suggestion => (
            <div key={suggestion.id} className="suggestion-card">
              <div className="suggestion-header">
                <div className="suggestion-icon">
                  {getTypeIcon(suggestion.type)}
                </div>
                <div className="suggestion-meta">
                  <h3>{suggestion.title}</h3>
                  <span 
                    className="priority-badge"
                    style={{ backgroundColor: getPriorityColor(suggestion.priority) }}
                  >
                    {suggestion.priority} priority
                  </span>
                </div>
              </div>

              <p className="suggestion-description">
                {suggestion.description}
              </p>

              <div className="suggestion-details">
                <div className="time-estimate">
                  <strong>Time to Learn:</strong> {suggestion.timeToLearn}
                </div>
                
                <div className="resources">
                  <strong>Recommended Resources:</strong>
                  <ul>
                    {suggestion.resources.map((resource, index) => (
                      <li key={index}>{resource}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <button className="start-learning-btn">
                Start Learning
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ImprovementSuggestions;