"""
CareerBoost AI - Enhanced Skill Gap Analyzer (Simplified)
ML-powered skill analysis with activity tracking and quiz system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import sys
import os
from datetime import datetime
import uuid
import json

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import ML skill matcher
from app.services.ml_skill_matcher import ml_skill_matcher

app = FastAPI(
    title="CareerBoost AI - Enhanced Skill Gap Analyzer",
    description="ML-powered skill analysis with activity tracking and quiz system",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003", "http://localhost:3002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
user_activities = {}
user_profiles = {}
quiz_questions = {}
quiz_attempts = {}
user_analyses = {}  # Store persistent analysis results

# Request models
class SkillSelectionRequest(BaseModel):
    user_id: str
    selected_skills: List[str]

class RoleAnalysisRequest(BaseModel):
    user_id: str
    user_skills: List[str]
    target_role: str

class QuizRequest(BaseModel):
    user_id: str
    role_name: str

class QuizSubmissionRequest(BaseModel):
    user_id: str
    attempt_id: str
    answers: List[int]

# Helper functions
def log_user_activity(user_id: str, activity_type: str, activity_data: Dict):
    """Log user activity."""
    activity_id = str(uuid.uuid4())
    activity = {
        "activity_id": activity_id,
        "user_id": user_id,
        "activity_type": activity_type,
        "activity_data": activity_data,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id not in user_activities:
        user_activities[user_id] = []
    
    user_activities[user_id].append(activity)
    
    # Update user profile
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            "user_id": user_id,
            "current_skills": [],
            "target_roles": [],
            "completed_quizzes": [],
            "total_activities": 0,
            "last_analysis_date": None
        }
    
    user_profiles[user_id]['total_activities'] += 1
    user_profiles[user_id]['last_analysis_date'] = datetime.now().isoformat()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "CareerBoost AI - Enhanced Skill Gap Analyzer",
        "version": "2.0.0",
        "description": "ML-powered skill analysis with activity tracking and quiz system",
        "features": [
            "🤖 Machine Learning Skill Matching",
            "📊 Real-time Role Recommendations", 
            "🎯 Detailed Skill Gap Analysis",
            "📈 User Activity Tracking",
            "🧠 Intelligent Quiz System"
        ],
        "endpoints": {
            "skills": "/api/skills/all",
            "role_suggestions": "/api/analysis/role-suggestions",
            "specific_analysis": "/api/analysis/specific-role",
            "user_activities": "/api/user/{user_id}/activities",
            "quiz": "/api/quiz/{role_name}"
        }
    }

@app.get("/api/skills/all")
async def get_all_skills():
    """Get all available skills from dataset for dropdown."""
    try:
        all_skills = ml_skill_matcher.all_skills
        
        # Get skill statistics
        skill_stats = {}
        for role_data in ml_skill_matcher.job_data.values():
            for skill in role_data.get('required_skills', []):
                skill_lower = skill.lower().strip()
                skill_stats[skill_lower] = skill_stats.get(skill_lower, 0) + 1
        
        # Sort skills by popularity
        popular_skills = sorted(skill_stats.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "success": True,
            "total_skills": len(all_skills),
            "all_skills": all_skills,
            "popular_skills": [skill for skill, count in popular_skills[:50]],
            "skill_categories": {
                "programming": [s for s in all_skills if any(lang in s for lang in ['python', 'java', 'javascript', 'c#', 'c++'])],
                "web": [s for s in all_skills if any(web in s for web in ['html', 'css', 'react', 'angular', 'vue'])],
                "database": [s for s in all_skills if any(db in s for db in ['sql', 'mongodb', 'postgresql', 'mysql'])],
                "cloud": [s for s in all_skills if any(cloud in s for cloud in ['aws', 'azure', 'gcp', 'docker', 'kubernetes'])],
                "ai_ml": [s for s in all_skills if any(ai in s for ai in ['machine learning', 'tensorflow', 'pytorch', 'pandas'])]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skills: {str(e)}")

@app.post("/api/analysis/role-suggestions")
async def get_role_suggestions(request: SkillSelectionRequest):
    """Get ML-based role suggestions based on user skills."""
    try:
        # Log activity
        log_user_activity(
            request.user_id,
            "skill_analysis",
            {
                "user_skills": request.selected_skills,
                "analysis_type": "role_suggestions",
                "total_suggestions": 0  # Will be updated below
            }
        )
        
        # Get ML-based role predictions
        role_suggestions = ml_skill_matcher.predict_suitable_roles(
            request.selected_skills, top_k=15
        )
        
        # Store analysis results persistently
        analysis_id = str(uuid.uuid4())
        analysis_data = {
            "analysis_id": analysis_id,
            "user_id": request.user_id,
            "user_skills": request.selected_skills,
            "role_suggestions": role_suggestions,
            "analysis_type": "role_suggestions",
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        if request.user_id not in user_analyses:
            user_analyses[request.user_id] = []
        
        user_analyses[request.user_id].append(analysis_data)
        
        # Update activity with total suggestions
        if request.user_id in user_activities and user_activities[request.user_id]:
            user_activities[request.user_id][-1]["activity_data"]["total_suggestions"] = len(role_suggestions)
        
        # Update user profile
        if request.user_id not in user_profiles:
            user_profiles[request.user_id] = {
                "user_id": request.user_id,
                "current_skills": [],
                "target_roles": [],
                "completed_quizzes": [],
                "total_activities": 0,
                "total_analyses": 0,
                "total_quizzes": 0,
                "last_analysis_date": None
            }
        
        user_profiles[request.user_id]['current_skills'] = request.selected_skills
        user_profiles[request.user_id]['total_analyses'] = user_profiles[request.user_id].get('total_analyses', 0) + 1
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "user_id": request.user_id,
            "user_skills": request.selected_skills,
            "total_suggestions": len(role_suggestions),
            "role_suggestions": role_suggestions,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analysis/specific-role")
async def analyze_specific_role(request: RoleAnalysisRequest):
    """Perform detailed analysis for a specific role using ML algorithms."""
    try:
        # Perform ML-based analysis
        analysis_result = ml_skill_matcher.analyze_specific_role(
            request.user_skills, request.target_role
        )
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=404, detail=analysis_result['error'])
        
        # Store detailed analysis results
        analysis_id = str(uuid.uuid4())
        detailed_analysis = {
            "analysis_id": analysis_id,
            "user_id": request.user_id,
            "user_skills": request.user_skills,
            "target_role": request.target_role,
            "analysis_result": analysis_result,
            "analysis_type": "specific_role",
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        if request.user_id not in user_analyses:
            user_analyses[request.user_id] = []
        
        user_analyses[request.user_id].append(detailed_analysis)
        
        # Log activity
        log_user_activity(
            request.user_id,
            "role_search",
            {
                "user_skills": request.user_skills,
                "target_role": request.target_role,
                "match_percentage": analysis_result['match_percentage'],
                "ml_confidence": analysis_result['ml_confidence'],
                "readiness_level": analysis_result['readiness_level'],
                "analysis_id": analysis_id
            }
        )
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "user_id": request.user_id,
            "analysis_result": analysis_result,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/user/{user_id}/activities")
async def get_user_activities(user_id: str, limit: int = 20):
    """Get user's recent activities."""
    try:
        activities = user_activities.get(user_id, [])
        profile = user_profiles.get(user_id, {})
        
        # Sort activities by timestamp (most recent first)
        sorted_activities = sorted(
            activities, 
            key=lambda x: x['timestamp'], 
            reverse=True
        )[:limit]
        
        return {
            "success": True,
            "user_id": user_id,
            "total_activities": len(activities),
            "recent_activities": sorted_activities,
            "user_profile": profile
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activities: {str(e)}")

@app.get("/api/user/{user_id}/analyses")
async def get_user_analyses(user_id: str):
    """Get user's persistent analysis results."""
    try:
        analyses = user_analyses.get(user_id, [])
        
        # Sort analyses by timestamp (most recent first)
        sorted_analyses = sorted(
            analyses, 
            key=lambda x: x['created_at'], 
            reverse=True
        )
        
        # Get active analyses only
        active_analyses = [a for a in sorted_analyses if a.get('status') == 'active']
        
        return {
            "success": True,
            "user_id": user_id,
            "total_analyses": len(analyses),
            "active_analyses": active_analyses,
            "has_active_analysis": len(active_analyses) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analyses: {str(e)}")

@app.post("/api/user/{user_id}/new-analysis")
async def start_new_analysis(user_id: str):
    """Clear current analyses and start fresh."""
    try:
        # Mark all existing analyses as inactive
        if user_id in user_analyses:
            for analysis in user_analyses[user_id]:
                analysis['status'] = 'inactive'
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "Ready for new analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start new analysis: {str(e)}")

@app.get("/api/quiz/{role_name}")
async def get_role_quiz(role_name: str, user_id: str):
    """Get quiz questions for a specific role."""
    try:
        # Generate default questions for the role
        questions = generate_default_questions(role_name)
        
        # Create quiz attempt
        attempt_id = str(uuid.uuid4())
        quiz_attempt = {
            "attempt_id": attempt_id,
            "user_id": user_id,
            "role_name": role_name,
            "questions": [q['question_id'] for q in questions],
            "correct_answers": [q['correct_answer'] for q in questions],
            "started_at": datetime.now().isoformat()
        }
        
        quiz_attempts[attempt_id] = quiz_attempt
        
        # Remove correct answers from questions sent to frontend
        quiz_questions_for_user = []
        for q in questions:
            question_copy = q.copy()
            del question_copy['correct_answer']
            quiz_questions_for_user.append(question_copy)
        
        return {
            "success": True,
            "attempt_id": attempt_id,
            "role_name": role_name,
            "total_questions": len(questions),
            "time_limit": 600,
            "passing_score": 70.0,
            "questions": quiz_questions_for_user
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quiz: {str(e)}")

@app.post("/api/quiz/submit")
async def submit_quiz(request: QuizSubmissionRequest):
    """Submit quiz answers and get results."""
    try:
        attempt = quiz_attempts.get(request.attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Quiz attempt not found")
        
        # Calculate score
        correct_answers = attempt['correct_answers']
        user_answers = request.answers
        
        correct_count = sum(1 for i, answer in enumerate(user_answers) 
                          if i < len(correct_answers) and answer == correct_answers[i])
        
        score = (correct_count / len(correct_answers)) * 100
        
        # Update attempt
        attempt['user_answers'] = user_answers
        attempt['score'] = score
        attempt['completed_at'] = datetime.now().isoformat()
        
        # Log activity
        log_user_activity(
            request.user_id,
            "quiz_taken",
            {
                "role_name": attempt['role_name'],
                "score": score,
                "correct_answers": correct_count,
                "total_questions": len(correct_answers),
                "attempt_id": request.attempt_id
            }
        )
        
        # Update user profile quiz count
        if request.user_id in user_profiles:
            user_profiles[request.user_id]['total_quizzes'] = user_profiles[request.user_id].get('total_quizzes', 0) + 1
        
        return {
            "success": True,
            "attempt_id": request.attempt_id,
            "score": round(score, 1),
            "correct_answers": correct_count,
            "total_questions": len(correct_answers),
            "passed": score >= 70,
            "improvement_suggestions": generate_quiz_improvements(attempt['role_name'], score, correct_count, len(correct_answers)),
            "detailed_results": [
                {
                    "question_index": i,
                    "user_answer": user_answers[i] if i < len(user_answers) else -1,
                    "correct_answer": correct_answers[i],
                    "is_correct": i < len(user_answers) and user_answers[i] == correct_answers[i]
                }
                for i in range(len(correct_answers))
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit quiz: {str(e)}")

def generate_quiz_improvements(role_name: str, score: float, correct_answers: int, total_questions: int) -> List[Dict]:
    """Generate improvement suggestions based on quiz performance."""
    improvements = []
    
    if score < 70:
        improvements.append({
            "type": "overall_performance",
            "title": "Focus on Fundamentals",
            "description": f"You scored {score}% on the {role_name} quiz. Focus on strengthening core concepts.",
            "priority": "high",
            "action": "Review basic concepts and practice more"
        })
    
    if score < 50:
        improvements.append({
            "type": "knowledge_gap",
            "title": "Significant Knowledge Gap",
            "description": "Consider taking a structured course or bootcamp to build foundational knowledge.",
            "priority": "critical",
            "action": "Enroll in comprehensive training program"
        })
    elif score < 70:
        improvements.append({
            "type": "skill_building",
            "title": "Skill Enhancement Needed",
            "description": "You have basic knowledge but need to strengthen specific areas.",
            "priority": "high",
            "action": "Focus on hands-on practice and projects"
        })
    elif score < 85:
        improvements.append({
            "type": "fine_tuning",
            "title": "Good Foundation, Room for Growth",
            "description": "You have solid knowledge. Focus on advanced topics and real-world applications.",
            "priority": "medium",
            "action": "Work on advanced projects and certifications"
        })
    else:
        improvements.append({
            "type": "excellence",
            "title": "Excellent Performance!",
            "description": "You demonstrate strong knowledge in this area. Consider mentoring others or specializing further.",
            "priority": "low",
            "action": "Share knowledge and explore advanced specializations"
        })
    
    # Role-specific improvements
    role_lower = role_name.lower()
    if "frontend" in role_lower or "react" in role_lower:
        if score < 80:
            improvements.append({
                "type": "technical_skill",
                "title": "Frontend Development Skills",
                "description": "Focus on modern JavaScript, React hooks, and responsive design principles.",
                "priority": "high",
                "action": "Build portfolio projects with React and modern CSS"
            })
    elif "backend" in role_lower or "api" in role_lower:
        if score < 80:
            improvements.append({
                "type": "technical_skill",
                "title": "Backend Development Skills",
                "description": "Strengthen your knowledge of APIs, databases, and server-side programming.",
                "priority": "high",
                "action": "Build REST APIs and work with databases"
            })
    elif "data" in role_lower or "ml" in role_lower:
        if score < 80:
            improvements.append({
                "type": "technical_skill",
                "title": "Data Science & ML Skills",
                "description": "Focus on statistics, machine learning algorithms, and data visualization.",
                "priority": "high",
                "action": "Complete data science projects and learn ML frameworks"
            })
    
    return improvements

def generate_default_questions(role_name: str) -> List[Dict]:
    """Generate default questions for a role."""
    role_lower = role_name.lower()
    
    # Default questions based on role
    if "frontend" in role_lower or "react" in role_lower:
        questions_data = [
            {
                "question_text": "What is the virtual DOM in React?",
                "options": [
                    "A copy of the real DOM kept in memory",
                    "A database for storing component state",
                    "A CSS framework for styling",
                    "A testing library for React"
                ],
                "correct_answer": 0
            },
            {
                "question_text": "Which CSS property is used for responsive design?",
                "options": ["display", "position", "media queries", "flex"],
                "correct_answer": 2
            },
            {
                "question_text": "What does JSX stand for?",
                "options": ["JavaScript XML", "Java Syntax Extension", "JSON XML", "JavaScript Extension"],
                "correct_answer": 0
            },
            {
                "question_text": "Which hook is used for side effects in React?",
                "options": ["useState", "useEffect", "useContext", "useReducer"],
                "correct_answer": 1
            },
            {
                "question_text": "What is the purpose of CSS Grid?",
                "options": ["Animation", "2D layout system", "Color management", "Font loading"],
                "correct_answer": 1
            }
        ]
    elif "backend" in role_lower or "api" in role_lower:
        questions_data = [
            {
                "question_text": "What is REST API?",
                "options": [
                    "A database management system",
                    "An architectural style for web services",
                    "A programming language",
                    "A testing framework"
                ],
                "correct_answer": 1
            },
            {
                "question_text": "Which HTTP method is used to update data?",
                "options": ["GET", "POST", "PUT", "DELETE"],
                "correct_answer": 2
            },
            {
                "question_text": "What is SQL injection?",
                "options": [
                    "A type of database",
                    "A security vulnerability",
                    "A query optimization technique",
                    "A data type"
                ],
                "correct_answer": 1
            },
            {
                "question_text": "What does CRUD stand for?",
                "options": [
                    "Create, Read, Update, Delete",
                    "Connect, Retrieve, Upload, Download",
                    "Copy, Remove, Undo, Duplicate",
                    "Cache, Render, Update, Display"
                ],
                "correct_answer": 0
            },
            {
                "question_text": "Which status code indicates successful creation?",
                "options": ["200", "201", "400", "500"],
                "correct_answer": 1
            }
        ]
    elif "data" in role_lower or "ml" in role_lower or "ai" in role_lower:
        questions_data = [
            {
                "question_text": "What is supervised learning?",
                "options": [
                    "Learning with labeled data",
                    "Learning without any data",
                    "Learning with unlabeled data",
                    "Learning with partial data"
                ],
                "correct_answer": 0
            },
            {
                "question_text": "Which library is commonly used for data manipulation in Python?",
                "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"],
                "correct_answer": 1
            },
            {
                "question_text": "What is overfitting in machine learning?",
                "options": [
                    "Model performs well on training data but poorly on test data",
                    "Model performs poorly on all data",
                    "Model is too simple",
                    "Model has too few parameters"
                ],
                "correct_answer": 0
            },
            {
                "question_text": "What does SQL stand for?",
                "options": [
                    "Structured Query Language",
                    "Simple Query Language",
                    "Standard Query Language",
                    "Sequential Query Language"
                ],
                "correct_answer": 0
            },
            {
                "question_text": "Which algorithm is used for classification?",
                "options": ["Linear Regression", "K-Means", "Random Forest", "PCA"],
                "correct_answer": 2
            }
        ]
    else:
        # General programming questions
        questions_data = [
            {
                "question_text": "What is version control?",
                "options": [
                    "A system to track changes in code",
                    "A type of database",
                    "A programming language",
                    "A testing method"
                ],
                "correct_answer": 0
            },
            {
                "question_text": "What does API stand for?",
                "options": [
                    "Application Programming Interface",
                    "Advanced Programming Interface",
                    "Automated Programming Interface",
                    "Application Process Interface"
                ],
                "correct_answer": 0
            },
            {
                "question_text": "What is debugging?",
                "options": [
                    "Writing new code",
                    "Finding and fixing errors in code",
                    "Deleting old code",
                    "Optimizing performance"
                ],
                "correct_answer": 1
            },
            {
                "question_text": "What is the purpose of comments in code?",
                "options": [
                    "To make code run faster",
                    "To explain what the code does",
                    "To hide code from users",
                    "To create variables"
                ],
                "correct_answer": 1
            },
            {
                "question_text": "What is a function?",
                "options": [
                    "A type of variable",
                    "A reusable block of code",
                    "A database table",
                    "A user interface element"
                ],
                "correct_answer": 1
            }
        ]
    
    # Convert to proper format
    questions = []
    for i, q_data in enumerate(questions_data[:10]):  # Limit to 10 questions
        question_id = f"{role_name}_{i}_{uuid.uuid4().hex[:8]}"
        question = {
            "question_id": question_id,
            "role_name": role_name,
            "question_text": q_data["question_text"],
            "options": q_data["options"],
            "correct_answer": q_data["correct_answer"],
            "difficulty_level": "medium",
            "category": "general"
        }
        questions.append(question)
    
    return questions

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Enhanced Skill Gap Analyzer",
        "version": "2.0.0",
        "ml_models_trained": ml_skill_matcher.models_trained,
        "total_skills": len(ml_skill_matcher.all_skills),
        "total_roles": len(ml_skill_matcher.job_data),
        "active_users": len(user_profiles),
        "total_activities": sum(len(activities) for activities in user_activities.values())
    }

if __name__ == "__main__":
    print("🚀 Starting CareerBoost AI - Enhanced Skill Gap Analyzer")
    print("🤖 ML-powered skill analysis with activity tracking")
    print("🔗 API Documentation: http://localhost:8006/docs")
    print("🏥 Health Check: http://localhost:8006/health")
    print("=" * 60)
    
    uvicorn.run(
        "simple_enhanced_skill_server:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )