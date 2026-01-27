"""
User-related data models for MongoDB documents.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from enum import Enum


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    FRESHER = "fresher"
    INTERNSHIP = "internship"
    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    EXPERT = "expert"


class SkillSource(str, Enum):
    """Source of skill information."""
    MANUAL = "manual"
    RESUME_EXTRACTED = "resume_extracted"


class UserModel(BaseModel):
    """User document model for MongoDB."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resume_path: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "experience_level": "junior",
                "resume_path": "/uploads/resume_123.pdf"
            }
        }


class UserSkillModel(BaseModel):
    """User skill relationship model for MongoDB."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    skill_name: str
    source: SkillSource
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "skill_name": "Python",
                "source": "manual",
                "confidence": 0.95
            }
        }


class UserCreate(BaseModel):
    """Model for user creation requests."""
    
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "name": "John Doe"
            }
        }


class UserUpdate(BaseModel):
    """Model for user profile updates."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    resume_path: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "John Smith",
                "experience_level": "mid_level",
                "resume_path": "/uploads/new_resume.pdf"
            }
        }


class UserResponse(BaseModel):
    """Model for user data responses."""
    
    id: str
    email: EmailStr
    name: str
    created_at: datetime
    updated_at: datetime
    resume_path: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "experience_level": "junior"
            }
        }