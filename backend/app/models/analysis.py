"""
Analysis and matching result data models for MongoDB documents.
"""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

from .user import PyObjectId


class RoleMatchModel(BaseModel):
    """Role matching result model."""
    
    role_id: PyObjectId
    role_title: str
    company: str
    match_percentage: float = Field(ge=0.0, le=100.0)
    essential_match_percentage: float = Field(ge=0.0, le=100.0)
    star_rating: int = Field(ge=1, le=5)
    missing_skills: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "role_id": "507f1f77bcf86cd799439011",
                "role_title": "Software Engineer",
                "company": "Tech Corp",
                "match_percentage": 75.5,
                "essential_match_percentage": 80.0,
                "star_rating": 4,
                "missing_skills": ["Docker", "Kubernetes"],
                "matched_skills": ["Python", "JavaScript", "SQL"]
            }
        }


class SkillGapModel(BaseModel):
    """Skill gap analysis result model."""
    
    role_id: PyObjectId
    role_title: str
    missing_skills_by_category: Dict[str, List[str]] = Field(default_factory=dict)
    common_skills: List[str] = Field(default_factory=list)
    role_specific_skills: List[str] = Field(default_factory=list)
    skill_importance_scores: Dict[str, float] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "role_id": "507f1f77bcf86cd799439011",
                "role_title": "Software Engineer",
                "missing_skills_by_category": {
                    "programming": ["Go", "Rust"],
                    "devops": ["Docker", "Kubernetes"],
                    "cloud": ["AWS", "Azure"]
                },
                "common_skills": ["Python", "SQL"],
                "role_specific_skills": ["React", "Node.js"],
                "skill_importance_scores": {
                    "Python": 0.95,
                    "Docker": 0.75,
                    "AWS": 0.60
                }
            }
        }


class AnalysisModel(BaseModel):
    """Analysis history document model for MongoDB."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    role_matches: List[RoleMatchModel] = Field(default_factory=list)
    skill_gaps: Dict[str, SkillGapModel] = Field(default_factory=dict)
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    user_skills_snapshot: List[str] = Field(default_factory=list)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "analysis_date": "2024-01-01T00:00:00Z",
                "user_skills_snapshot": ["Python", "JavaScript", "SQL"],
                "role_matches": [],
                "skill_gaps": {}
            }
        }


class LearningPathModel(BaseModel):
    """Learning path recommendation model."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    target_role_id: PyObjectId
    recommended_skills: List[str] = Field(default_factory=list)
    skill_priorities: Dict[str, float] = Field(default_factory=dict)
    estimated_learning_time: Dict[str, int] = Field(default_factory=dict)  # in hours
    learning_resources: Dict[str, List[str]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "target_role_id": "507f1f77bcf86cd799439012",
                "recommended_skills": ["Docker", "Kubernetes", "AWS"],
                "skill_priorities": {
                    "Docker": 0.9,
                    "Kubernetes": 0.7,
                    "AWS": 0.6
                },
                "estimated_learning_time": {
                    "Docker": 40,
                    "Kubernetes": 60,
                    "AWS": 80
                },
                "learning_resources": {
                    "Docker": ["Docker Official Tutorial", "Docker Deep Dive Course"],
                    "Kubernetes": ["Kubernetes Documentation", "K8s Hands-on Lab"]
                }
            }
        }