"""
Role Models for CareerBoost AI
MongoDB schema and Pydantic models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RoleBase(BaseModel):
    """Base role model"""
    roleId: str = Field(..., description="Unique role identifier for URLs")
    title: str = Field(..., description="Role title (e.g., Frontend Developer)")
    cardSubtitle: str = Field(..., description="Short description for dashboard card")
    isActive: bool = Field(default=True, description="Whether role is active/visible")
    order: int = Field(..., description="Display order on dashboard")
    overview: str = Field(..., description="Detailed role explanation")
    responsibilities: List[str] = Field(..., description="List of key responsibilities")
    mustHaveSkills: List[str] = Field(..., description="Required skills")
    goodToHaveSkills: List[str] = Field(..., description="Nice-to-have skills")
    tools: List[str] = Field(..., description="Tools and technologies")

class RoleCreate(RoleBase):
    """Model for creating new roles"""
    pass

class RoleUpdate(BaseModel):
    """Model for updating roles (all fields optional)"""
    title: Optional[str] = None
    cardSubtitle: Optional[str] = None
    isActive: Optional[bool] = None
    order: Optional[int] = None
    overview: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    mustHaveSkills: Optional[List[str]] = None
    goodToHaveSkills: Optional[List[str]] = None
    tools: Optional[List[str]] = None

class RoleResponse(RoleBase):
    """Model for role responses"""
    id: str = Field(..., description="MongoDB ObjectId as string")
    createdAt: str = Field(..., description="Creation timestamp")
    updatedAt: str = Field(..., description="Last update timestamp")

class RoleCardResponse(BaseModel):
    """Simplified model for dashboard cards"""
    roleId: str
    title: str
    cardSubtitle: str
    topSkills: List[str] = Field(..., description="Top 3-4 skills for card display")
    order: int

# Admin Models
class AdminUser(BaseModel):
    """Admin user model"""
    email: str
    password_hash: str
    created_at: str
    is_active: bool = True

class AdminLogin(BaseModel):
    """Admin login request"""
    email: str
    password: str

class AdminResponse(BaseModel):
    """Admin response model"""
    id: str
    email: str
    is_active: bool