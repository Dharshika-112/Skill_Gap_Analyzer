"""
Skill and job role data models for MongoDB documents.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum

from .user import PyObjectId, ExperienceLevel


class SkillCategory(str, Enum):
    """Skill category enumeration."""
    PROGRAMMING = "programming"
    DEVOPS = "devops"
    MACHINE_LEARNING = "machine_learning"
    DATA_SCIENCE = "data_science"
    WEB_DEVELOPMENT = "web_development"
    MOBILE_DEVELOPMENT = "mobile_development"
    DATABASE = "database"
    CLOUD = "cloud"
    SECURITY = "security"
    SOFT_SKILLS = "soft_skills"
    TOOLS = "tools"
    FRAMEWORKS = "frameworks"
    OTHER = "other"


class SkillModel(BaseModel):
    """Skill document model for MongoDB."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    category: SkillCategory
    aliases: List[str] = Field(default_factory=list)
    is_technical: bool = True
    description: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Python",
                "category": "programming",
                "aliases": ["python3", "py"],
                "is_technical": True,
                "description": "Python programming language"
            }
        }


class JobRoleModel(BaseModel):
    """Job role document model for MongoDB."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: ExperienceLevel
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "required_skills": ["Python", "JavaScript", "SQL"],
                "preferred_skills": ["React", "Docker", "AWS"],
                "experience_level": "junior",
                "category": "Software Development",
                "description": "Full-stack software engineer position"
            }
        }


class SkillNormalizationRule(BaseModel):
    """Skill normalization mapping model."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    from_skill: str = Field(..., min_length=1)
    to_skill: str = Field(..., min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "from_skill": "js",
                "to_skill": "JavaScript",
                "confidence": 0.95
            }
        }