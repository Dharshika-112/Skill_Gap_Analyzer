"""
CareerBoost AI - User Activity Models
Database models for tracking user activities and quiz system
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class ActivityType(str, Enum):
    """Types of user activities."""
    SKILL_ANALYSIS = "skill_analysis"
    ROLE_SEARCH = "role_search"
    QUIZ_TAKEN = "quiz_taken"
    PROFILE_UPDATE = "profile_update"
    LEARNING_ROADMAP = "learning_roadmap"

class UserActivity(BaseModel):
    """Model for user activity tracking."""
    activity_id: str = Field(..., description="Unique activity ID")
    user_id: str = Field(..., description="User ID")
    activity_type: ActivityType = Field(..., description="Type of activity")
    activity_data: Dict = Field(default_factory=dict, description="Activity specific data")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Activity timestamp")
    session_id: Optional[str] = Field(None, description="Session ID")

class SkillAnalysisActivity(BaseModel):
    """Specific model for skill analysis activities."""
    user_skills: List[str] = Field(..., description="User's skills")
    target_role: Optional[str] = Field(None, description="Target role analyzed")
    match_percentage: Optional[float] = Field(None, description="Match percentage")
    matched_skills: List[str] = Field(default_factory=list, description="Matched skills")
    missing_skills: List[str] = Field(default_factory=list, description="Missing skills")
    ml_confidence: Optional[float] = Field(None, description="ML confidence score")
    readiness_level: Optional[str] = Field(None, description="Readiness level")

class QuizQuestion(BaseModel):
    """Model for quiz questions."""
    question_id: str = Field(..., description="Unique question ID")
    role_name: str = Field(..., description="Associated role")
    question_text: str = Field(..., description="Question text")
    options: List[str] = Field(..., description="Answer options")
    correct_answer: int = Field(..., description="Index of correct answer")
    difficulty_level: str = Field(default="medium", description="Question difficulty")
    category: str = Field(default="general", description="Question category")
    created_by: str = Field(..., description="Admin who created the question")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    is_active: bool = Field(default=True, description="Whether question is active")

class QuizAttempt(BaseModel):
    """Model for quiz attempts."""
    attempt_id: str = Field(..., description="Unique attempt ID")
    user_id: str = Field(..., description="User ID")
    role_name: str = Field(..., description="Role for which quiz was taken")
    questions: List[str] = Field(..., description="List of question IDs")
    user_answers: List[int] = Field(..., description="User's answers")
    correct_answers: List[int] = Field(..., description="Correct answers")
    score: float = Field(..., description="Quiz score percentage")
    time_taken: int = Field(..., description="Time taken in seconds")
    started_at: str = Field(..., description="Quiz start time")
    completed_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Quiz completion time")

class UserSkillProfile(BaseModel):
    """Enhanced user skill profile with ML insights."""
    user_id: str = Field(..., description="User ID")
    current_skills: List[str] = Field(default_factory=list, description="Current skills")
    skill_levels: Dict[str, str] = Field(default_factory=dict, description="Skill proficiency levels")
    target_roles: List[str] = Field(default_factory=list, description="Target roles")
    completed_quizzes: List[str] = Field(default_factory=list, description="Completed quiz IDs")
    learning_progress: Dict[str, float] = Field(default_factory=dict, description="Learning progress per skill")
    ml_recommendations: List[str] = Field(default_factory=list, description="ML-based skill recommendations")
    last_analysis_date: Optional[str] = Field(None, description="Last skill analysis date")
    total_activities: int = Field(default=0, description="Total number of activities")

class RoleQuizConfig(BaseModel):
    """Configuration for role-based quizzes."""
    role_name: str = Field(..., description="Role name")
    total_questions: int = Field(default=10, description="Total questions in quiz")
    time_limit: int = Field(default=600, description="Time limit in seconds")
    passing_score: float = Field(default=70.0, description="Minimum passing score")
    difficulty_distribution: Dict[str, int] = Field(
        default_factory=lambda: {"easy": 3, "medium": 5, "hard": 2},
        description="Distribution of question difficulties"
    )
    is_active: bool = Field(default=True, description="Whether quiz is active")
    created_by: str = Field(..., description="Admin who created the config")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")