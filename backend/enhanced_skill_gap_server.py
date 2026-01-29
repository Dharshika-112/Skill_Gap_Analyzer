"""
CareerBoost AI - Enhanced Skill Gap Analyzer Server
Complete ML-based skill analysis with user activity tracking and quiz system
"""

from fastapi import FastAPI, HTTPException, Depends
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

# Import services and models
from app.services.ml_skill_matcher import ml_skill_matcher
from app.models.user_activity import (
    UserActivity, SkillAnalysisActivity, QuizQuestion, QuizAttempt, 
    UserSkillProfile, RoleQuizConfig, ActivityType
)

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

# In-memory storage (replace with MongoDB in production)
user_activities = {}
user_profiles = {}
quiz_questions = {}
quiz_attempts = {}
role_quiz_configs = {}

# Request/Response models
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

class QuizQuestionRequest(BaseModel):
    role_name: str
    question_text: str
    options: List[str]
    correct_answer: int
    difficulty_level: str = "medium"
    category: str = "general"
    created_by: str

# Helper functions
def log_user_activity(user_id: str, activity_type: ActivityType, activity_data: Dict):
    """Log user activity to database."""
    activity_id = str(uuid.uuid4())
    activity = UserActivity(
        activity_id=activity_id,
        user_id=user_id,
        activity_type=activity_type,
        activity_data=activity_data,
        timestamp=datetime.now()
    )
    
    if user_id not in user_activities:
        user_activities[user_id] = []
    
    user_activities[user_id].append(activity.dict())
    
    # Update user profile
    if user_id not in user_profiles:
        user_profiles[user_id] = UserSkillProfile(user_id=user_id).dict()
    
    user_profiles[user_id]['total_activities'] += 1
    user_profiles[user_id]['last_analysis_date'] = datetime.now().isoformat()

def get_user_profile(user_id: str) -> Dict:
    """Get or create user profile."""
    if user_id not in user_profiles:
        user_profiles[user_id] = UserSkillProfile(user_id=user_id).dict()
    return user_profiles[user_id]

# API Endpoints

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
            "🧠 Intelligent Quiz System",
            "👑 Admin Quiz Management"
        ],
        "endpoints": {
            "skills": "/api/skills/all",
            "role_suggestions": "/api/analysis/role-suggestions",
            "specific_analysis": "/api/analysis/specific-role",
            "user_activities": "/api/user/{user_id}/activities",
            "quiz": "/api/quiz/{role_name}",
            "admin_quiz": "/api/admin/quiz"
        }
    }

@app.get("/api/skills/all")
async def get_all_skills():
    """Get all available skills from dataset for dropdown."""
    try:
        all_skills = ml_skill_matcher.all_skills
        
        # Get skill recommendations based on popularity
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
            ActivityType.SKILL_ANALYSIS,
            {
                "user_skills": request.selected_skills,
                "analysis_type": "role_suggestions"
            }
        )
        
        # Get ML-based role predictions
        role_suggestions = ml_skill_matcher.predict_suitable_roles(
            request.selected_skills, top_k=15
        )
        
        # Update user profile
        profile = get_user_profile(request.user_id)
        profile['current_skills'] = request.selected_skills
        profile['ml_recommendations'] = ml_skill_matcher.get_skill_recommendations(
            request.selected_skills, limit=10
        )
        
        return {
            "success": True,
            "user_id": request.user_id,
            "user_skills": request.selected_skills,
            "total_suggestions": len(role_suggestions),
            "role_suggestions": role_suggestions,
            "skill_recommendations": profile['ml_recommendations'],
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
        
        # Log activity
        activity_data = SkillAnalysisActivity(
            user_skills=request.user_skills,
            target_role=request.target_role,
            match_percentage=analysis_result['match_percentage'],
            matched_skills=analysis_result['matched_skills'],
            missing_skills=analysis_result['missing_skills'],
            ml_confidence=analysis_result['ml_confidence'],
            readiness_level=analysis_result['readiness_level']
        ).dict()
        
        log_user_activity(
            request.user_id,
            ActivityType.ROLE_SEARCH,
            activity_data
        )
        
        # Update user profile
        profile = get_user_profile(request.user_id)
        if request.target_role not in profile['target_roles']:
            profile['target_roles'].append(request.target_role)
        
        return {
            "success": True,
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
        profile = get_user_profile(user_id)
        
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

@app.get("/api/quiz/{role_name}")
async def get_role_quiz(role_name: str, user_id: str):
    """Get quiz questions for a specific role."""
    try:
        # Get quiz configuration
        quiz_config = role_quiz_configs.get(role_name)
        if not quiz_config:
            # Create default quiz config
            quiz_config = RoleQuizConfig(
                role_name=role_name,
                created_by="system"
            ).dict()
            role_quiz_configs[role_name] = quiz_config
        
        # Get questions for this role
        role_questions = [
            q for q in quiz_questions.values() 
            if q['role_name'] == role_name and q['is_active']
        ]
        
        if len(role_questions) < quiz_config['total_questions']:
            # Generate default questions if not enough exist
            default_questions = generate_default_questions(role_name)
            role_questions.extend(default_questions)
        
        # Select questions based on difficulty distribution
        selected_questions = select_quiz_questions(
            role_questions, quiz_config['difficulty_distribution']
        )
        
        # Create quiz attempt
        attempt_id = str(uuid.uuid4())
        quiz_attempt = QuizAttempt(
            attempt_id=attempt_id,
            user_id=user_id,
            role_name=role_name,
            questions=[q['question_id'] for q in selected_questions],
            user_answers=[],
            correct_answers=[q['correct_answer'] for q in selected_questions],
            score=0.0,
            time_taken=0,
            started_at=datetime.now(),
            completed_at=datetime.now()
        ).dict()
        
        quiz_attempts[attempt_id] = quiz_attempt
        
        # Remove correct answers from questions sent to frontend
        quiz_questions_for_user = []
        for q in selected_questions:
            question_copy = q.copy()
            del question_copy['correct_answer']
            quiz_questions_for_user.append(question_copy)
        
        return {
            "success": True,
            "attempt_id": attempt_id,
            "role_name": role_name,
            "total_questions": len(selected_questions),
            "time_limit": quiz_config['time_limit'],
            "passing_score": quiz_config['passing_score'],
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
            ActivityType.QUIZ_TAKEN,
            {
                "role_name": attempt['role_name'],
                "score": score,
                "correct_answers": correct_count,
                "total_questions": len(correct_answers)
            }
        )
        
        # Update user profile
        profile = get_user_profile(request.user_id)
        if request.attempt_id not in profile['completed_quizzes']:
            profile['completed_quizzes'].append(request.attempt_id)
        
        return {
            "success": True,
            "attempt_id": request.attempt_id,
            "score": round(score, 1),
            "correct_answers": correct_count,
            "total_questions": len(correct_answers),
            "passed": score >= role_quiz_configs.get(attempt['role_name'], {}).get('passing_score', 70),
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

# Admin endpoints for quiz management
@app.post("/api/admin/quiz/question")
async def add_quiz_question(request: QuizQuestionRequest):
    """Add a new quiz question (Admin only)."""
    try:
        question_id = str(uuid.uuid4())
        question = QuizQuestion(
            question_id=question_id,
            role_name=request.role_name,
            question_text=request.question_text,
            options=request.options,
            correct_answer=request.correct_answer,
            difficulty_level=request.difficulty_level,
            category=request.category,
            created_by=request.created_by
        ).dict()
        
        quiz_questions[question_id] = question
        
        return {
            "success": True,
            "question_id": question_id,
            "message": "Question added successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add question: {str(e)}")

@app.get("/api/admin/quiz/questions/{role_name}")
async def get_role_questions(role_name: str):
    """Get all questions for a role (Admin only)."""
    try:
        role_questions = [
            q for q in quiz_questions.values() 
            if q['role_name'] == role_name
        ]
        
        return {
            "success": True,
            "role_name": role_name,
            "total_questions": len(role_questions),
            "questions": role_questions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get questions: {str(e)}")

@app.delete("/api/admin/quiz/question/{question_id}")
async def delete_quiz_question(question_id: str):
    """Delete a quiz question (Admin only)."""
    try:
        if question_id not in quiz_questions:
            raise HTTPException(status_code=404, detail="Question not found")
        
        del quiz_questions[question_id]
        
        return {
            "success": True,
            "message": "Question deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete question: {str(e)}")

# Helper functions
def generate_default_questions(role_name: str) -> List[Dict]:
    """Generate default questions for a role."""
    default_questions_data = {
        "frontend developer": [
            {
                "question_text": "What is the virtual DOM in React?",
                "options": [
                    "A copy of the real DOM kept in memory",
                    "A database for storing component state",
                    "A CSS framework for styling",
                    "A testing library for React"
                ],
                "correct_answer": 0,
                "difficulty_level": "medium"
            },
            {
                "question_text": "Which CSS property is used for responsive design?",
                "options": ["display", "position", "media-query", "flex"],
                "correct_answer": 2,
                "difficulty_level": "easy"
            }
        ],
        "backend developer": [
            {
                "question_text": "What is REST API?",
                "options": [
                    "A database management system",
                    "An architectural style for web services",
                    "A programming language",
                    "A testing framework"
                ],
                "correct_answer": 1,
                "difficulty_level": "medium"
            }
        ]
    }
    
    questions = []
    role_lower = role_name.lower()
    
    for key, question_list in default_questions_data.items():
        if key in role_lower:
            for i, q_data in enumerate(question_list):
                question_id = f"default_{role_name}_{i}_{uuid.uuid4().hex[:8]}"
                question = QuizQuestion(
                    question_id=question_id,
                    role_name=role_name,
                    question_text=q_data["question_text"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    difficulty_level=q_data["difficulty_level"],
                    category="general",
                    created_by="system"
                ).dict()
                
                quiz_questions[question_id] = question
                questions.append(question)
    
    return questions

def select_quiz_questions(available_questions: List[Dict], difficulty_distribution: Dict[str, int]) -> List[Dict]:
    """Select questions based on difficulty distribution."""
    selected = []
    
    # Group questions by difficulty
    by_difficulty = {}
    for q in available_questions:
        diff = q['difficulty_level']
        if diff not in by_difficulty:
            by_difficulty[diff] = []
        by_difficulty[diff].append(q)
    
    # Select questions according to distribution
    for difficulty, count in difficulty_distribution.items():
        available = by_difficulty.get(difficulty, [])
        selected.extend(available[:count])
    
    # Fill remaining slots if needed
    total_needed = sum(difficulty_distribution.values())
    if len(selected) < total_needed:
        remaining = [q for q in available_questions if q not in selected]
        selected.extend(remaining[:total_needed - len(selected)])
    
    return selected[:total_needed]

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
        "total_activities": sum(len(activities) for activities in user_activities.values()),
        "total_quiz_questions": len(quiz_questions)
    }

if __name__ == "__main__":
    print("🚀 Starting CareerBoost AI - Enhanced Skill Gap Analyzer")
    print("🤖 ML-powered skill analysis with activity tracking")
    print("🔗 API Documentation: http://localhost:8006/docs")
    print("🏥 Health Check: http://localhost:8006/health")
    print("=" * 60)
    
    uvicorn.run(
        "enhanced_skill_gap_server:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )