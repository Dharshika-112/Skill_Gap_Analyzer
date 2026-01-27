// Enhanced Skill Gap Analyzer - Complete Workflow Implementation
const API_BASE = 'http://localhost:8000';

// Global state
let currentUser = null;
let authToken = null;
let availableSkills = [];
let categorizedSkills = {};
let userSkills = [];
let availableRoles = [];
let currentAnalysis = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    loadAvailableSkills();
});

// Authentication functions
async function signup() {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    
    console.log('Signup attempt:', { name, email, password: '***' });
    
    if (!name || !email || !password) {
        showError('signup-error', 'Please fill in all fields');
        return;
    }
    
    try {
        console.log('Sending signup request to:', `${API_BASE}/api/auth/signup`);
        
        const response = await fetch(`${API_BASE}/api/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        
        console.log('Signup response status:', response.status);
        
        const data = await response.json();
        console.log('Signup response data:', data);
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = { name, email, user_id: data.user_id };
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            console.log('Signup successful, showing dashboard');
            showDashboard();
        } else {
            console.log('Signup failed:', data.detail);
            showError('signup-error', data.detail || 'Signup failed');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showError('signup-error', 'Network error. Please try again.');
    }
}

async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    console.log('Login attempt:', { email, password: '***' });
    
    if (!email || !password) {
        showError('login-error', 'Please fill in all fields');
        return;
    }
    
    try {
        console.log('Sending login request to:', `${API_BASE}/api/auth/login`);
        
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        console.log('Login response status:', response.status);
        
        const data = await response.json();
        console.log('Login response data:', data);
        
        if (response.ok) {
            authToken = data.access_token;
            
            // Get user profile
            console.log('Getting user profile...');
            const profileResponse = await fetch(`${API_BASE}/api/auth/me`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            console.log('Profile response status:', profileResponse.status);
            
            if (profileResponse.ok) {
                currentUser = await profileResponse.json();
                console.log('Profile data:', currentUser);
                localStorage.setItem('authToken', authToken);
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                console.log('Login successful, showing dashboard');
                showDashboard();
            } else {
                console.log('Profile fetch failed');
                showError('login-error', 'Failed to get user profile');
            }
        } else {
            console.log('Login failed:', data.detail);
            showError('login-error', data.detail || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('login-error', 'Network error. Please try again.');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    showPage('landing-page');
}

function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('currentUser');
    
    if (token && user) {
        authToken = token;
        currentUser = JSON.parse(user);
        showDashboard();
    }
}

// Dashboard and workflow functions
function showDashboard() {
    console.log('showDashboard called with currentUser:', currentUser);
    
    if (!currentUser || !currentUser.name) {
        console.error('No current user data available');
        alert('User data not available. Please try logging in again.');
        return;
    }
    
    console.log('Showing dashboard page');
    
    // First, make sure we're working with the right page
    const dashboardPage = document.getElementById('dashboard-page');
    if (!dashboardPage) {
        console.error('Dashboard page element not found in DOM');
        alert('Dashboard page not found. Please refresh the page.');
        return;
    }
    
    // Hide all pages first
    const pages = document.querySelectorAll('.page');
    console.log('Found pages:', pages.length);
    pages.forEach(page => {
        page.classList.remove('active');
        page.style.display = 'none';
    });
    
    // Show dashboard page
    dashboardPage.classList.add('active');
    dashboardPage.style.display = 'block';
    console.log('Dashboard page shown successfully');
    
    // Set user name
    const userNameElement = document.getElementById('user-name');
    if (userNameElement) {
        userNameElement.textContent = currentUser.name;
        console.log('Set user name to:', currentUser.name);
    } else {
        console.error('user-name element not found');
    }
    
    // Load dataset roles
    try {
        loadDatasetRoles();
    } catch (error) {
        console.error('Error loading dataset roles:', error);
    }
}

// Step 1: Resume Upload and Analysis (with fallback to manual selection)
async function handleResumeUpload() {
    const fileInput = document.getElementById('resume-file');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    showLoading(true, 'Analyzing your resume with AI...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/api/resume/upload-and-analyze`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` },
            body: formData
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (response.ok) {
            if (data.status === 'warning' || (data.extracted_skills && data.extracted_skills.length < 3)) {
                // Resume parsing failed or extracted too few skills - switch to manual mode
                showResumeParsingFallback(data);
            } else {
                displayResumeAnalysis(data);
            }
        } else {
            showStatusMessage('resume-status', data.detail || 'Upload failed', 'error');
            // Show manual selection as fallback
            showManualSkillSelection();
        }
    } catch (error) {
        showLoading(false);
        showStatusMessage('resume-status', 'Network error during upload', 'error');
        // Show manual selection as fallback
        showManualSkillSelection();
    }
}

function showResumeParsingFallback(data) {
    const statusContainer = document.getElementById('resume-status');
    
    let message = '';
    if (data.status === 'warning') {
        message = data.message;
    } else {
        message = `Only ${data.extracted_skills?.length || 0} skills were extracted from your resume.`;
    }
    
    statusContainer.innerHTML = `
        <div class="status-message warning">
            <h4>⚠️ Resume Parsing Issue</h4>
            <p>${message}</p>
            <p><strong>Don't worry!</strong> You can manually select your skills from our comprehensive database.</p>
            <button onclick="showManualSkillSelection()" class="btn-primary">
                📝 Select Skills Manually
            </button>
            ${data.extracted_skills && data.extracted_skills.length > 0 ? 
                `<button onclick="useExtractedSkills(${JSON.stringify(data.extracted_skills).replace(/"/g, '&quot;')})" class="btn-secondary">
                    ✅ Use ${data.extracted_skills.length} Extracted Skills
                </button>` : ''
            }
        </div>
    `;
}

function useExtractedSkills(extractedSkills) {
    userSkills = [...extractedSkills];
    showManualSkillSelection();
    populateUserSkillsEditor();
    showStatusMessage('skill-management', `✅ Using ${extractedSkills.length} skills from resume`, 'success');
}

async function showManualSkillSelection() {
    // Hide resume upload section and show manual selection
    document.getElementById('resume-upload').style.display = 'none';
    document.getElementById('manual-skill-selection').style.display = 'block';
    document.getElementById('skill-management').style.display = 'block';
    
    // Load all available skills if not already loaded
    if (availableSkills.length === 0) {
        await loadAllSkillsForManualSelection();
    }
    
    // Populate the skill selector
    populateSkillSelector();
    populateUserSkillsEditor();
}

async function loadAllSkillsForManualSelection() {
    showLoading(true, 'Loading skill database...');
    
    try {
        const response = await fetch(`${API_BASE}/api/resume/all-skills`);
        const data = await response.json();
        
        if (response.ok) {
            availableSkills = data.skills || [];
            categorizedSkills = data.categorized_skills || {};
            
            showLoading(false);
            showStatusMessage('skill-management', `✅ Loaded ${availableSkills.length} skills from job market database`, 'success');
        } else {
            showLoading(false);
            showStatusMessage('skill-management', 'Failed to load skills database', 'error');
        }
    } catch (error) {
        showLoading(false);
        showStatusMessage('skill-management', 'Network error loading skills', 'error');
    }
}

function populateSkillSelector() {
    const container = document.getElementById('skill-selector-container');
    
    if (!categorizedSkills || Object.keys(categorizedSkills).length === 0) {
        container.innerHTML = `
            <div class="skill-search-box">
                <input type="text" id="skill-search" placeholder="🔍 Search skills (e.g., Python, React, AWS)..." 
                       onkeyup="searchSkills()" autocomplete="off">
                <div id="skill-suggestions" class="skill-suggestions"></div>
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="skill-search-box">
            <input type="text" id="skill-search" placeholder="🔍 Search skills (e.g., Python, React, AWS)..." 
                   onkeyup="searchSkills()" autocomplete="off">
            <div id="skill-suggestions" class="skill-suggestions"></div>
        </div>
        
        <div class="skill-categories">
            <h4>📚 Browse Skills by Category:</h4>
    `;
    
    // Create category tabs
    const categories = Object.keys(categorizedSkills);
    html += '<div class="category-tabs">';
    categories.forEach((category, index) => {
        const isActive = index === 0 ? 'active' : '';
        html += `<button class="category-tab ${isActive}" onclick="showSkillCategory('${category}')">${category}</button>`;
    });
    html += '</div>';
    
    // Create category content
    categories.forEach((category, index) => {
        const isActive = index === 0 ? 'active' : '';
        const skills = categorizedSkills[category] || [];
        
        html += `
            <div id="category-${category.replace(/\s+/g, '-')}" class="category-content ${isActive}">
                <div class="skills-grid">
                    ${skills.slice(0, 50).map(skill => `
                        <button class="skill-option ${userSkills.includes(skill) ? 'selected' : ''}" 
                                onclick="toggleSkill('${skill.replace(/'/g, "\\'")}')">
                            ${skill}
                        </button>
                    `).join('')}
                    ${skills.length > 50 ? `<p class="more-skills">... and ${skills.length - 50} more (use search to find specific skills)</p>` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function showSkillCategory(category) {
    // Update tab active state
    document.querySelectorAll('.category-tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update content active state
    document.querySelectorAll('.category-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`category-${category.replace(/\s+/g, '-')}`).classList.add('active');
}

function toggleSkill(skill) {
    if (userSkills.includes(skill)) {
        removeUserSkill(skill);
    } else {
        addUserSkill(skill);
    }
    
    // Update button state
    const button = event.target;
    button.classList.toggle('selected');
}

async function analyzeManualSkills() {
    if (userSkills.length === 0) {
        showStatusMessage('skill-management', '⚠️ Please select at least one skill', 'warning');
        return;
    }
    
    showLoading(true, 'Running comprehensive ATS analysis...');
    
    try {
        const response = await fetch(`${API_BASE}/api/resume/ats-analysis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                user_skills: userSkills,
                experience_years: parseFloat(document.getElementById('experience-years')?.value || '0'),
                education: "Bachelor's",
                certifications: [],
                target_role: null,
                projects_count: 0
            })
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (response.ok) {
            displayComprehensiveATSAnalysis(data);
        } else {
            showStatusMessage('skill-management', data.detail || 'Analysis failed', 'error');
        }
    } catch (error) {
        showLoading(false);
        showStatusMessage('skill-management', 'Network error during analysis', 'error');
    }
}

function displayComprehensiveATSAnalysis(data) {
    // Show success message
    showStatusMessage('skill-management', `✅ Comprehensive ATS analysis completed!`, 'success');
    
    // Display ATS Score (Main Score)
    const scoreCard = document.getElementById('resume-score');
    const atsScoring = data.ats_scoring;
    scoreCard.innerHTML = `
        <div class="ats-score-card">
            <div class="score-number">${atsScoring.ats_score}%</div>
            <div class="score-category">${atsScoring.category}</div>
            <div class="ats-recommendation">${atsScoring.recommendation}</div>
            <small>Confidence: ${atsScoring.confidence}</small>
        </div>
    `;
    
    // Display Role-Based Scoring
    displayRoleBasedScoring(data.role_based_scoring);
    
    // Display Skill Importance Ranking
    displaySkillImportanceRanking(data.skill_importance_ranking);
    
    // Display Improvement Suggestions
    displayImprovementSuggestions(data.improvement_suggestions);
    
    // Display Intelligent Role Matches
    displayIntelligentRoleMatches(data.intelligent_role_matches);
    
    // Show analysis sections
    document.getElementById('resume-analysis').style.display = 'block';
    document.getElementById('role-selection').style.display = 'block';
    
    // Add ATS-specific sections
    showATSSpecificSections(data);
    
    // Scroll to results
    document.getElementById('resume-analysis').scrollIntoView({ behavior: 'smooth' });
}

function displayRoleBasedScoring(roleScoring) {
    if (!roleScoring || roleScoring.error) {
        return;
    }
    
    const container = document.getElementById('role-based-scores') || createRoleBasedScoresContainer();
    
    let html = '<h4>🎯 Role-Based ATS Scoring:</h4>';
    
    if (roleScoring.role_scores && roleScoring.role_scores.length > 0) {
        html += '<div class="role-scores-grid">';
        
        roleScoring.role_scores.slice(0, 6).forEach((role, index) => {
            const scoreClass = role.combined_score >= 80 ? 'excellent' : 
                              role.combined_score >= 60 ? 'good' : 
                              role.combined_score >= 40 ? 'average' : 'poor';
            
            html += `
                <div class="role-score-card ${scoreClass}">
                    <div class="role-title">${role.role}</div>
                    <div class="combined-score">${role.combined_score.toFixed(1)}%</div>
                    <div class="score-breakdown">
                        <small>ATS: ${role.ats_score}% | Match: ${role.match_percentage}%</small>
                    </div>
                    <div class="readiness-badge">${role.readiness}</div>
                    <div class="job-count">${role.job_count} jobs</div>
                    <button onclick="analyzeSpecificRole('${role.role}')" class="btn-small">Analyze</button>
                </div>
            `;
        });
        
        html += '</div>';
        
        if (roleScoring.best_match) {
            html += `
                <div class="best-match-highlight">
                    <h5>🏆 Best Match: ${roleScoring.best_match.role}</h5>
                    <p>Combined Score: ${roleScoring.best_match.combined_score.toFixed(1)}% | Readiness: ${roleScoring.best_match.readiness}</p>
                </div>
            `;
        }
    }
    
    container.innerHTML = html;
}

function displaySkillImportanceRanking(skillImportance) {
    const container = document.getElementById('skill-importance') || createSkillImportanceContainer();
    
    let html = '<h4>📊 Your Skills Ranked by Market Importance:</h4>';
    
    if (skillImportance && skillImportance.length > 0) {
        html += '<div class="skill-importance-grid">';
        
        skillImportance.forEach((skillData, index) => {
            const priorityClass = skillData.priority.toLowerCase();
            const rank = index + 1;
            
            html += `
                <div class="skill-importance-item ${priorityClass}">
                    <div class="skill-rank">#${rank}</div>
                    <div class="skill-name">${skillData.skill}</div>
                    <div class="importance-score">${(skillData.importance * 100).toFixed(1)}%</div>
                    <div class="priority-badge ${priorityClass}">${skillData.priority}</div>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Add summary
        const highPriorityCount = skillImportance.filter(s => s.priority === 'High').length;
        html += `
            <div class="importance-summary">
                <p>💎 You have <strong>${highPriorityCount}</strong> high-priority skills out of ${skillImportance.length} total skills.</p>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function displayImprovementSuggestions(suggestions) {
    const container = document.getElementById('improvement-suggestions') || createImprovementSuggestionsContainer();
    
    let html = '<h4>💡 AI-Powered Improvement Suggestions:</h4>';
    
    if (suggestions && suggestions.length > 0) {
        html += '<div class="suggestions-list">';
        
        suggestions.forEach((suggestion, index) => {
            html += `
                <div class="suggestion-item">
                    <div class="suggestion-number">${index + 1}</div>
                    <div class="suggestion-text">${suggestion}</div>
                </div>
            `;
        });
        
        html += '</div>';
    } else {
        html += '<p class="no-suggestions">🎉 Great job! Your profile looks strong. Keep building on your current skills.</p>';
    }
    
    container.innerHTML = html;
}

function showATSSpecificSections(data) {
    // Create ATS-specific sections if they don't exist
    const analysisContainer = document.getElementById('resume-analysis');
    
    // Add role-based scoring section
    if (!document.getElementById('role-based-scores')) {
        const roleSection = document.createElement('div');
        roleSection.id = 'role-based-scores';
        roleSection.className = 'ats-section';
        analysisContainer.appendChild(roleSection);
    }
    
    // Add skill importance section
    if (!document.getElementById('skill-importance')) {
        const importanceSection = document.createElement('div');
        importanceSection.id = 'skill-importance';
        importanceSection.className = 'ats-section';
        analysisContainer.appendChild(importanceSection);
    }
    
    // Add improvement suggestions section
    if (!document.getElementById('improvement-suggestions')) {
        const suggestionsSection = document.createElement('div');
        suggestionsSection.id = 'improvement-suggestions';
        suggestionsSection.className = 'ats-section';
        analysisContainer.appendChild(suggestionsSection);
    }
}

function createRoleBasedScoresContainer() {
    const container = document.createElement('div');
    container.id = 'role-based-scores';
    container.className = 'ats-section';
    document.getElementById('resume-analysis').appendChild(container);
    return container;
}

function createSkillImportanceContainer() {
    const container = document.createElement('div');
    container.id = 'skill-importance';
    container.className = 'ats-section';
    document.getElementById('resume-analysis').appendChild(container);
    return container;
}

function createImprovementSuggestionsContainer() {
    const container = document.createElement('div');
    container.id = 'improvement-suggestions';
    container.className = 'ats-section';
    document.getElementById('resume-analysis').appendChild(container);
    return container;
}

function displayResumeAnalysis(data) {
    if (data.status === 'warning') {
        showStatusMessage('resume-status', data.message, 'warning');
        const suggestions = data.suggestions.map(s => `• ${s}`).join('<br>');
        document.getElementById('resume-status').innerHTML += `<br><strong>Suggestions:</strong><br>${suggestions}`;
        return;
    }
    
    // Show success message
    showStatusMessage('resume-status', `✅ Resume analyzed successfully! Found ${data.skills_count} skills.`, 'success');
    
    // Display resume score
    const scoreCard = document.getElementById('resume-score');
    const score = data.resume_score;
    scoreCard.innerHTML = `
        <div class="score-number">${score.overall_score}%</div>
        <div class="score-category">${score.category}</div>
        <p>Your resume matches ${score.matching_skills_count} out of ${score.total_dataset_skills} skills in our job dataset</p>
        <small>Skill Relevance: ${score.skill_relevance}% | Coverage: ${score.skill_coverage}%</small>
    `;
    
    // Display extracted skills with importance scores
    displayExtractedSkillsWithImportance(data.extracted_skills, data.skill_importance_scores);
    
    // Display intelligent role matches
    displayIntelligentRoleMatches(data.intelligent_role_matches);
    
    // Display skill recommendations
    displaySkillRecommendations(data.skill_recommendations);
    
    // Store user skills
    userSkills = data.extracted_skills;
    
    // Show next sections
    document.getElementById('resume-analysis').style.display = 'block';
    document.getElementById('skill-management').style.display = 'block';
    document.getElementById('role-selection').style.display = 'block';
    
    // Populate user skills editor
    populateUserSkillsEditor();
}

function displayExtractedSkillsWithImportance(skills, skillImportanceScores) {
    const container = document.getElementById('extracted-skills');
    
    if (skills.length === 0) {
        container.innerHTML = '<p class="warning">No skills were extracted from your resume.</p>';
        return;
    }
    
    // Create importance map
    const importanceMap = {};
    skillImportanceScores.forEach(item => {
        importanceMap[item.skill] = item.importance;
    });
    
    // Group skills by category and sort by importance
    const categories = {
        'Programming Languages': [],
        'Web Technologies': [],
        'Databases': [],
        'Machine Learning': [],
        'Cloud & DevOps': [],
        'Other': []
    };
    
    skills.forEach(skill => {
        const skillLower = skill.toLowerCase();
        const importance = importanceMap[skill] || 0;
        const skillData = { skill, importance };
        
        if (['python', 'java', 'javascript', 'c#', 'c++', 'php', 'ruby', 'typescript'].some(lang => skillLower.includes(lang))) {
            categories['Programming Languages'].push(skillData);
        } else if (['react', 'angular', 'vue', 'node', 'html', 'css', 'express', 'django'].some(tech => skillLower.includes(tech))) {
            categories['Web Technologies'].push(skillData);
        } else if (['mysql', 'mongodb', 'postgresql', 'sql', 'redis'].some(db => skillLower.includes(db))) {
            categories['Databases'].push(skillData);
        } else if (['tensorflow', 'pytorch', 'machine learning', 'deep learning', 'scikit-learn'].some(ml => skillLower.includes(ml))) {
            categories['Machine Learning'].push(skillData);
        } else if (['docker', 'kubernetes', 'aws', 'azure', 'git', 'jenkins'].some(devops => skillLower.includes(devops))) {
            categories['Cloud & DevOps'].push(skillData);
        } else {
            categories['Other'].push(skillData);
        }
    });
    
    // Sort each category by importance
    Object.keys(categories).forEach(category => {
        categories[category].sort((a, b) => b.importance - a.importance);
    });
    
    let html = '<h4>📋 Your Skills with Market Importance:</h4>';
    
    Object.entries(categories).forEach(([category, categorySkills]) => {
        if (categorySkills.length > 0) {
            html += `
                <div class="skill-category">
                    <h4>${category}</h4>
                    <div class="skill-tags">
                        ${categorySkills.map(skillData => {
                            const importance = skillData.importance;
                            let importanceClass = 'low';
                            let importanceText = 'Low';
                            
                            if (importance > 0.5) {
                                importanceClass = 'high';
                                importanceText = 'High';
                            } else if (importance > 0.2) {
                                importanceClass = 'medium';
                                importanceText = 'Medium';
                            }
                            
                            return `
                                <span class="skill-tag matching ${importanceClass}" title="Market Importance: ${importanceText} (${(importance * 100).toFixed(1)}%)">
                                    ${skillData.skill}
                                    <small class="importance-badge">${importanceText}</small>
                                </span>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
    });
    
    container.innerHTML = html;
}

function displayIntelligentRoleMatches(intelligentMatches) {
    const container = document.getElementById('initial-matches');
    
    if (!intelligentMatches || intelligentMatches.length === 0) {
        container.innerHTML = '<p>No intelligent role matches found.</p>';
        return;
    }
    
    let html = '<h4>🧠 AI-Powered Role Matches (Prioritized by Skill Importance):</h4>';
    
    intelligentMatches.forEach((role, index) => {
        const matchScore = role.intelligent_score;
        const priorityScore = role.high_priority_match_percentage;
        
        let matchClass = 'low-match';
        if (matchScore >= 70) matchClass = 'high-match';
        else if (matchScore >= 50) matchClass = 'medium-match';
        
        html += `
            <div class="role-match intelligent-match ${matchClass}">
                <div class="role-header">
                    <div class="role-title">${role.role}</div>
                    <div class="match-scores">
                        <div class="intelligent-score">AI Score: ${matchScore}%</div>
                        <div class="priority-score">Priority Match: ${priorityScore}%</div>
                    </div>
                </div>
                <div class="match-details">
                    <p><strong>🎯 High Priority Skills Matched:</strong> ${role.high_priority_matches}/${role.high_priority_total}</p>
                    <p><strong>✅ Total Matching Skills:</strong> ${role.total_matching_skills} | <strong>❌ Missing:</strong> ${role.total_missing_skills}</p>
                    <div class="skill-preview">
                        <strong>Top Missing Skills:</strong> 
                        ${role.missing_skills.slice(0, 3).map(skill => `<span class="missing-skill">${skill}</span>`).join(', ')}
                    </div>
                </div>
                <div class="role-actions">
                    <button onclick="analyzeIntelligentRole('${role.role}')" class="btn-small btn-primary">Deep Analysis</button>
                    <button onclick="analyzeSpecificRole('${role.role}')" class="btn-small">Basic Analysis</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function displaySkillRecommendations(recommendations) {
    const container = document.getElementById('skill-recommendations');
    
    if (!recommendations || !recommendations.high_priority_skills) {
        container.innerHTML = '<p>No skill recommendations available.</p>';
        return;
    }
    
    let html = '<h4>💡 AI Skill Recommendations:</h4>';
    
    // High priority skills to learn
    if (recommendations.high_priority_skills.length > 0) {
        html += `
            <div class="recommendation-section">
                <h5>🔥 High Priority Skills to Learn:</h5>
                <div class="recommended-skills">
                    ${recommendations.high_priority_skills.slice(0, 8).map(skillData => `
                        <div class="recommended-skill high-priority">
                            <span class="skill-name">${skillData.skill}</span>
                            <div class="skill-stats">
                                <small>Importance: ${(skillData.importance * 100).toFixed(1)}%</small>
                                <small>Used in ${skillData.job_count} jobs</small>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Market trends
    if (recommendations.market_trends && recommendations.market_trends.top_skills_by_demand) {
        html += `
            <div class="recommendation-section">
                <h5>📈 Market Trends - Most In-Demand Skills:</h5>
                <div class="market-trends">
                    ${recommendations.market_trends.top_skills_by_demand.slice(0, 6).map(skillData => `
                        <div class="trend-skill">
                            <span class="skill-name">${skillData.skill}</span>
                            <span class="job-count">${skillData.job_count} jobs</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
    document.getElementById('skill-recommendations').style.display = 'block';
}

function displayInitialRoleMatches(roleMatches) {
    const container = document.getElementById('initial-matches');
    
    if (roleMatches.length === 0) {
        container.innerHTML = '<p>No role matches found.</p>';
        return;
    }
    
    let html = '<h4>🎯 Top Matching Roles Based on Your Resume:</h4>';
    
    roleMatches.forEach(role => {
        html += `
            <div class="role-match">
                <div class="role-title">${role.role}</div>
                <div class="match-percentage">${role.match_percentage}% Match</div>
                <p><strong>Matching:</strong> ${role.matching_skills_count} skills | <strong>Missing:</strong> ${role.total_missing_skills} skills</p>
                <button onclick="analyzeSpecificRole('${role.role}')" class="btn-small">Analyze This Role</button>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Step 2: Skill Management
function populateUserSkillsEditor() {
    const container = document.getElementById('user-skills');
    container.innerHTML = '';
    
    userSkills.forEach(skill => {
        const skillElement = document.createElement('div');
        skillElement.className = 'user-skill';
        skillElement.innerHTML = `
            ${skill}
            <button class="remove-skill" onclick="removeUserSkill('${skill.replace(/'/g, "\\'")}')">×</button>
        `;
        container.appendChild(skillElement);
    });
    
    // Update skill count
    const countElement = document.getElementById('selected-count');
    if (countElement) {
        countElement.textContent = userSkills.length;
    }
    
    // Update analyze button state
    const analyzeBtn = document.getElementById('analyze-skills-btn');
    if (analyzeBtn) {
        if (userSkills.length === 0) {
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = '🧠 Select Skills to Analyze';
        } else {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = `🧠 Analyze ${userSkills.length} Skills with AI`;
        }
    }
}

async function searchSkills() {
    const query = document.getElementById('skill-search').value.toLowerCase();
    const suggestions = document.getElementById('skill-suggestions');
    
    if (query.length < 2) {
        suggestions.innerHTML = '';
        return;
    }
    
    const filteredSkills = availableSkills.filter(skill => 
        skill.toLowerCase().includes(query) && !userSkills.includes(skill)
    ).slice(0, 10);
    
    suggestions.innerHTML = filteredSkills.map(skill => 
        `<div class="suggestion" onclick="addUserSkill('${skill}')">${skill}</div>`
    ).join('');
}

function addUserSkill(skill) {
    if (!userSkills.includes(skill)) {
        userSkills.push(skill);
        populateUserSkillsEditor();
        document.getElementById('skill-search').value = '';
        document.getElementById('skill-suggestions').innerHTML = '';
    }
}

function removeUserSkill(skill) {
    userSkills = userSkills.filter(s => s !== skill);
    populateUserSkillsEditor();
}

async function saveUserSkills() {
    try {
        const response = await fetch(`${API_BASE}/api/skills/save-objects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                user_skills: userSkills.map(skill => ({ skill, source: 'manual' }))
            })
        });
        
        if (response.ok) {
            showStatusMessage('skill-management', '✅ Skills saved successfully!', 'success');
        } else {
            showStatusMessage('skill-management', '❌ Failed to save skills', 'error');
        }
    } catch (error) {
        showStatusMessage('skill-management', '❌ Network error', 'error');
    }
}

// Step 3: Load Dataset Roles
async function loadDatasetRoles() {
    try {
        const response = await fetch(`${API_BASE}/api/resume/dataset-roles`);
        const data = await response.json();
        
        if (response.ok) {
            availableRoles = data.roles;
            populateRoleSelectors();
        }
    } catch (error) {
        console.error('Failed to load roles:', error);
    }
}

function populateRoleSelectors() {
    const selectors = ['role-select', 'additional-role-select'];
    
    selectors.forEach(selectorId => {
        const select = document.getElementById(selectorId);
        if (select) {
            select.innerHTML = '<option value="">-- Select a Role --</option>';
            
            availableRoles.forEach(role => {
                const option = document.createElement('option');
                option.value = role.title;
                option.textContent = `${role.title} (${role.job_count} jobs)`;
                select.appendChild(option);
            });
        }
    });
}

// Step 4: Role Analysis
async function analyzeSelectedRole() {
    const roleTitle = document.getElementById('role-select').value;
    if (!roleTitle) return;
    
    await performRoleAnalysis(roleTitle);
}

async function analyzeSpecificRole(roleTitle) {
    document.getElementById('role-select').value = roleTitle;
    await performRoleAnalysis(roleTitle);
}

async function analyzeIntelligentRole(roleTitle) {
    if (!userSkills.length) {
        alert('Please add your skills first or upload a resume.');
        return;
    }
    
    showLoading(true, 'Performing AI-powered role analysis...');
    
    try {
        const response = await fetch(`${API_BASE}/api/resume/intelligent-role-analysis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                role_title: roleTitle,
                user_skills: userSkills
            })
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (response.ok) {
            displayIntelligentAnalysisResults(data.analysis);
            document.getElementById('role-analysis').style.display = 'block';
            document.getElementById('role-analysis').scrollIntoView({ behavior: 'smooth' });
        } else {
            showStatusMessage('role-analysis', data.detail || 'Analysis failed', 'error');
        }
    } catch (error) {
        showLoading(false);
        showStatusMessage('role-analysis', 'Network error during analysis', 'error');
    }
}

function displayIntelligentAnalysisResults(analysis) {
    const container = document.getElementById('analysis-results');
    
    let html = `
        <div class="analysis-header">
            <h3>🧠 AI-Powered Analysis: ${analysis.role_title}</h3>
        </div>
    `;
    
    // Intelligent match data
    if (analysis.intelligent_match_data) {
        const matchData = analysis.intelligent_match_data;
        html += `
            <div class="intelligent-match-summary">
                <div class="match-score-card">
                    <div class="score-big">${matchData.intelligent_score}%</div>
                    <div class="score-label">AI Match Score</div>
                </div>
                <div class="priority-stats">
                    <div class="stat">
                        <span class="stat-number">${matchData.high_priority_matches}</span>
                        <span class="stat-label">High Priority Matches</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${matchData.total_matching_skills}</span>
                        <span class="stat-label">Total Matches</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    // User skill importance analysis
    if (analysis.user_skill_importance && analysis.user_skill_importance.length > 0) {
        html += `
            <div class="skill-importance-section">
                <h4>📊 Your Skills Ranked by Market Importance:</h4>
                <div class="skill-importance-grid">
                    ${analysis.user_skill_importance.slice(0, 12).map(skillData => `
                        <div class="skill-importance-card ${skillData.priority.toLowerCase()}">
                            <div class="skill-name">${skillData.skill}</div>
                            <div class="importance-score">${(skillData.importance_score * 100).toFixed(1)}%</div>
                            <div class="priority-badge ${skillData.priority.toLowerCase()}">${skillData.priority}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Skill recommendations
    if (analysis.skill_recommendations && analysis.skill_recommendations.high_priority_skills) {
        html += `
            <div class="recommendations-section">
                <h4>💡 AI Recommendations for This Role:</h4>
                <div class="recommendations-grid">
                    ${analysis.skill_recommendations.high_priority_skills.slice(0, 8).map(skillData => `
                        <div class="recommendation-card">
                            <div class="rec-skill">${skillData.skill}</div>
                            <div class="rec-stats">
                                <small>Importance: ${(skillData.importance * 100).toFixed(1)}%</small>
                                <small>Jobs: ${skillData.job_count}</small>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Market insights
    if (analysis.market_insights) {
        const insights = analysis.market_insights;
        html += `
            <div class="market-insights-section">
                <h4>📈 Market Insights:</h4>
                <div class="insights-grid">
                    <div class="insight-card">
                        <div class="insight-number">${insights.role_demand}</div>
                        <div class="insight-label">Job Openings</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-text">${insights.experience_levels.join(', ')}</div>
                        <div class="insight-label">Experience Levels</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
    currentAnalysis = analysis;
}

function displayGapAnalysis(analysis) {
    // Analysis header
    const header = document.getElementById('analysis-header');
    const readinessClass = analysis.readiness_color === 'green' ? 'ready' : 
                          analysis.readiness_color === 'orange' ? 'almost' :
                          analysis.readiness_color === 'yellow' ? 'needs-prep' : 'significant-gap';
    
    header.innerHTML = `
        <h3>${analysis.role_title}</h3>
        <div class="score-number">${analysis.match_percentage}%</div>
        <div class="readiness-badge ${readinessClass}">${analysis.readiness}</div>
        <p>${analysis.total_matching_skills} out of ${analysis.total_required_skills} skills matched</p>
    `;
    
    // Skills breakdown
    const breakdown = document.getElementById('skills-breakdown');
    breakdown.innerHTML = `
        <div class="skills-column matching">
            <h4>✅ Your Matching Skills (${analysis.matching_skills.length})</h4>
            ${displaySkillsByCategory(analysis.matching_skills_categorized)}
        </div>
        <div class="skills-column missing">
            <h4>❌ Missing Skills (${analysis.missing_skills.length})</h4>
            ${displaySkillsByCategory(analysis.missing_skills_categorized)}
        </div>
    `;
    
    // Recommendations
    const recommendations = document.getElementById('recommendations');
    recommendations.innerHTML = `
        <h4>💡 Recommendations</h4>
        ${analysis.recommendations.map(rec => `<div class="recommendation">${rec}</div>`).join('')}
    `;
}

function displaySkillsByCategory(categorizedSkills) {
    let html = '';
    
    Object.entries(categorizedSkills).forEach(([category, skills]) => {
        html += `
            <div class="skill-category">
                <h5>${category}</h5>
                <div class="skill-tags">
                    ${skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                </div>
            </div>
        `;
    });
    
    return html || '<p>No skills in this category</p>';
}

// Additional functions
function selectAnotherRole() {
    document.getElementById('additional-analysis').style.display = 'block';
    document.getElementById('additional-analysis').scrollIntoView({ behavior: 'smooth' });
}

async function analyzeAdditionalRole() {
    const roleTitle = document.getElementById('additional-role-select').value;
    if (!roleTitle) return;
    
    await performRoleAnalysis(roleTitle);
}

async function exportAnalysis() {
    if (!currentAnalysis) {
        alert('No analysis to export');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/data/export-report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                type: 'txt',
                role: currentAnalysis.role_title,
                analysis: currentAnalysis
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `skill_gap_analysis_${currentAnalysis.role_title.replace(/\s+/g, '_')}.txt`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
    } catch (error) {
        alert('Export failed');
    }
}

// Load available skills
async function loadAvailableSkills() {
    try {
        const response = await fetch(`${API_BASE}/api/data/skills`);
        const data = await response.json();
        
        if (response.ok) {
            availableSkills = data.skills || [];
        }
    } catch (error) {
        console.error('Failed to load skills:', error);
    }
}

// Utility functions
function showPage(pageId) {
    console.log('showPage called with:', pageId);
    
    const pages = document.querySelectorAll('.page');
    console.log('Found pages:', pages.length);
    
    // Hide all pages
    pages.forEach(page => {
        page.classList.remove('active');
        page.style.display = 'none';
        console.log('Hidden page:', page.id);
    });
    
    // Show target page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        targetPage.style.display = 'block';
        console.log('Shown page:', pageId);
    } else {
        console.error('Page not found:', pageId);
        alert('Page not found: ' + pageId);
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.style.display = 'block';
    setTimeout(() => element.style.display = 'none', 5000);
}

function showStatusMessage(containerId, message, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = `<div class="status-message ${type}">${message}</div>`;
}

function showLoading(show, message = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.querySelector('p').textContent = message;
        overlay.style.display = 'flex';
    } else {
        overlay.style.display = 'none';
    }
}

// Profile management
async function updateProfile() {
    const name = document.getElementById('update-name').value;
    const experienceType = document.getElementById('experience-type').value;
    const experienceYears = document.getElementById('experience-years').value;
    
    const updateData = {};
    if (name) updateData.name = name;
    if (experienceType) {
        updateData.experience = {
            type: experienceType,
            years: experienceYears ? parseFloat(experienceYears) : 0
        };
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(updateData)
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showStatusMessage('profile-status', '✅ Profile updated successfully!', 'success');
        } else {
            showStatusMessage('profile-status', '❌ Failed to update profile', 'error');
        }
    } catch (error) {
        showStatusMessage('profile-status', '❌ Network error', 'error');
    }
}

async function performRoleAnalysis(roleTitle) {
    if (!userSkills.length) {
        alert('Please add your skills first or upload a resume.');
        return;
    }
    
    showLoading(true, 'Analyzing role requirements and skill gaps...');
    
    try {
        const response = await fetch(`${API_BASE}/api/resume/role-analysis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                role_title: roleTitle,
                user_skills: userSkills
            })
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (response.ok) {
            displayGapAnalysis(data.analysis);
            document.getElementById('role-analysis').style.display = 'block';
            document.getElementById('role-analysis').scrollIntoView({ behavior: 'smooth' });
        } else {
            showStatusMessage('role-analysis', data.detail || 'Analysis failed', 'error');
        }
    } catch (error) {
        showLoading(false);
        showStatusMessage('role-analysis', 'Network error during analysis', 'error');
    }
}

// Market Analysis Functions
async function getMarketAnalysis() {
    showLoading(true, 'Analyzing market trends and your skill portfolio...');
    
    try {
        const response = await fetch(`${API_BASE}/api/resume/skill-market-analysis`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (response.ok) {
            displayMarketAnalysis(data);
            document.getElementById('market-analysis').style.display = 'block';
            document.getElementById('market-analysis').scrollIntoView({ behavior: 'smooth' });
        } else {
            showStatusMessage('market-analysis', data.detail || 'Market analysis failed', 'error');
        }
    } catch (error) {
        showLoading(false);
        showStatusMessage('market-analysis', 'Network error during market analysis', 'error');
    }
}

function displayMarketAnalysis(data) {
    const container = document.getElementById('market-results');
    
    if (data.status === 'warning') {
        container.innerHTML = `<p class="warning">${data.message}</p>`;
        return;
    }
    
    let html = '<div class="market-overview">';
    
    // User skills analysis
    if (data.user_skills_analysis) {
        const skillsAnalysis = data.user_skills_analysis;
        html += `
            <div class="skills-portfolio-section">
                <h4>📊 Your Skill Portfolio Analysis:</h4>
                <div class="portfolio-stats">
                    <div class="stat-card">
                        <div class="stat-number">${skillsAnalysis.total_skills}</div>
                        <div class="stat-label">Total Skills</div>
                    </div>
                    <div class="stat-card high-value">
                        <div class="stat-number">${skillsAnalysis.high_value_skills}</div>
                        <div class="stat-label">High-Value Skills</div>
                    </div>
                </div>
                
                <div class="skill-portfolio-grid">
                    ${skillsAnalysis.skill_portfolio.slice(0, 12).map(skill => `
                        <div class="portfolio-skill ${skill.demand_level.toLowerCase()}">
                            <div class="skill-name">${skill.skill}</div>
                            <div class="skill-category">${skill.category}</div>
                            <div class="demand-badge ${skill.demand_level.toLowerCase()}">${skill.demand_level} Demand</div>
                            <div class="importance-score">${(skill.market_importance * 100).toFixed(1)}%</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Career insights
    if (data.career_insights) {
        const insights = data.career_insights;
        html += `
            <div class="career-insights-section">
                <h4>🎯 Career Insights:</h4>
                <div class="insights-cards">
                    <div class="insight-card">
                        <h5>Strongest Area</h5>
                        <p>${insights.strongest_skill_category}</p>
                    </div>
                    <div class="insight-card">
                        <h5>Career Readiness</h5>
                        <p>${insights.career_readiness}</p>
                    </div>
                </div>
                
                <div class="focus-areas">
                    <h5>🔥 Recommended Focus Areas:</h5>
                    <div class="focus-skills">
                        ${insights.recommended_focus_areas.map(skill => 
                            `<span class="focus-skill">${skill}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Intelligent role matches
    if (data.intelligent_role_matches && data.intelligent_role_matches.length > 0) {
        html += `
            <div class="market-roles-section">
                <h4>🧠 AI-Recommended Career Paths:</h4>
                <div class="market-roles-grid">
                    ${data.intelligent_role_matches.slice(0, 6).map(role => `
                        <div class="market-role-card">
                            <div class="role-title">${role.role}</div>
                            <div class="ai-score">AI Score: ${role.intelligent_score}%</div>
                            <div class="role-stats">
                                <small>Priority Match: ${role.high_priority_match_percentage}%</small>
                                <small>Skills Match: ${role.total_matching_skills}/${role.total_matching_skills + role.total_missing_skills}</small>
                            </div>
                            <button onclick="analyzeIntelligentRole('${role.role}')" class="btn-small">Analyze</button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}