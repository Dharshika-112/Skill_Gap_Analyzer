"""
Data routes - provides skills, roles, and analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.extended_dataset import (
    get_extended_skills, 
    get_extended_roles,
    get_role_requirements,
    get_dataset_summary
)
from services.advanced_ml import get_skill_gap_analysis, get_learning_path

router = APIRouter()

class SkillGapRequest(BaseModel):
    user_skills: List[str]
    role_skills: List[str]
    role_name: str = ""

class LearningPathRequest(BaseModel):
    user_skills: List[str]
    role_skills: List[str]
    gap_analysis: dict = {}

@router.get("/skills")
async def get_skills():
    """Get all available skills from extended dataset"""
    try:
        skills = get_extended_skills()
        return {
            "skills": skills,
            "total": len(skills),
            "dataset_info": "Extended dataset with 1000+ skills across multiple categories"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roles")
async def get_roles():
    """Get all available job roles from extended dataset"""
    try:
        roles = get_extended_roles()
        return {
            "roles": roles,
            "total": len(roles),
            "dataset_info": "Extended dataset with 100+ roles across multiple categories"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dataset-info")
async def dataset_info():
    """Get information about the dataset"""
    try:
        return get_dataset_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skill-gap")
async def analyze_skill_gap(request: SkillGapRequest):
    """
    Analyze skill gap using advanced ML algorithms:
    - TF-IDF Similarity
    - Cosine Similarity
    - Jaccard Index
    - Deep Learning Predictions (if available)
    """
    try:
        if not request.user_skills or not request.role_skills:
            raise HTTPException(status_code=400, detail="User skills and role skills are required")
        
        # Perform analysis
        analysis = get_skill_gap_analysis(
            request.user_skills,
            request.role_skills,
            request.role_name
        )
        
        return {
            "status": "success",
            "analysis": analysis,
            "algorithms_used": [
                "Jaccard Similarity",
                "TF-IDF Cosine Similarity",
                "Vector Cosine Similarity",
                "Deep Learning Ensemble" if analysis.get('deep_learning_score') else "Classic ML"
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning-path")
async def generate_learning_path(request: LearningPathRequest):
    """Generate personalized learning path based on skill gaps"""
    try:
        if not request.user_skills or not request.role_skills:
            raise HTTPException(status_code=400, detail="User skills and role skills are required")
        
        # First, perform gap analysis if not provided
        if not request.gap_analysis:
            request.gap_analysis = get_skill_gap_analysis(
                request.user_skills,
                request.role_skills
            )
        
        # Generate learning path
        learning_path = get_learning_path(
            request.user_skills,
            request.role_skills,
            request.gap_analysis
        )
        
        return {
            "status": "success",
            "learning_path": learning_path,
            "total_skills_to_learn": len(learning_path),
            "estimated_total_hours": sum([item["estimated_hours"] for item in learning_path])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/role-requirements/{role_name}")
async def get_role_reqs(role_name: str):
    """Get required skills for a specific role"""
    try:
        skills = get_role_requirements(role_name)
        return {
            "role": role_name,
            "required_skills": skills,
            "total_skills": len(skills)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend-roles")
async def recommend_roles(user_skills_req: dict):
    """Recommend roles based on user skills"""
    try:
        user_skills = user_skills_req.get("skills", [])
        if not user_skills:
            raise HTTPException(status_code=400, detail="Skills are required")
        
        roles = get_extended_roles()
        recommendations = []
        
        for role in roles[:20]:  # Top 20 recommendations
            role_reqs = get_role_requirements(role)
            gap = get_skill_gap_analysis(user_skills, role_reqs, role)
            
            if gap['match_percentage'] > 0:
                recommendations.append({
                    "role": role,
                    "match_percentage": gap['match_percentage'],
                    "matching_skills": len(gap['matching_skills']),
                    "missing_skills": len(gap['missing_skills'])
                })
        
        # Sort by match percentage
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return {
            "status": "success",
            "recommendations": recommendations[:10],  # Top 10
            "total_evaluated": len(roles)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
