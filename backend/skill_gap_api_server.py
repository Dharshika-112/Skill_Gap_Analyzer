"""
CareerBoost AI - Skill Gap Analyzer API Server
Complete 8-Step Skill Gap Analysis System

This server provides the comprehensive skill gap analysis API following the exact
8-step process specified in the requirements.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import the skill gap analyzer
from app.services.skill_gap_analyzer import skill_gap_analyzer

app = FastAPI(
    title="CareerBoost AI - Skill Gap Analyzer",
    description="Advanced 8-Step Skill Gap Analysis System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class SkillGapAnalysisRequest(BaseModel):
    user_skills: List[str]
    target_role: str
    experience_preference: Optional[str] = "fresher"  # fresher, junior, mid-level, senior

class SkillNormalizationRequest(BaseModel):
    skills: List[str]

class SkillMatchingRequest(BaseModel):
    user_skills: List[str]
    required_skills: List[str]

# Response models
class SkillGapAnalysisResponse(BaseModel):
    success: bool
    analysis_timestamp: str
    target_role: str
    role_match_confidence: float
    alternative_roles: List[str]
    skill_gap_analysis: dict
    scoring_analysis: dict
    learning_roadmap: dict
    project_recommendations: List[dict]
    interview_readiness: dict
    skill_matching: dict
    skill_categorization: dict
    analysis_metadata: dict

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "CareerBoost AI - Skill Gap Analyzer",
        "version": "1.0.0",
        "description": "Advanced 8-Step Skill Gap Analysis System",
        "endpoints": {
            "skill_gap_analysis": "/api/skill-gap-analysis",
            "skill_normalization": "/api/skill-normalization",
            "skill_matching": "/api/skill-matching",
            "available_roles": "/api/available-roles",
            "health": "/health"
        },
        "features": [
            "Step 1: Skill Normalization Layer",
            "Step 2: Skill Taxonomy Classification",
            "Step 3: Intelligent Skill Matching",
            "Step 4: Weighted Gap Scoring System",
            "Step 5: Gap Analysis Output",
            "Step 6: Learning Roadmap Generator",
            "Step 7: Project Recommendation Engine",
            "Step 8: Interview Readiness Layer"
        ]
    }

@app.post("/api/skill-gap-analysis")
async def analyze_skill_gap(request: SkillGapAnalysisRequest):
    """
    Perform comprehensive skill gap analysis using the 8-step process.
    
    This endpoint implements the complete skill gap analysis system:
    1. Normalizes user skills and job requirements
    2. Classifies skills into professional categories
    3. Performs intelligent matching (exact, fuzzy, hierarchical)
    4. Calculates weighted gap scores
    5. Generates structured gap analysis
    6. Creates personalized learning roadmap
    7. Recommends relevant projects
    8. Assesses interview readiness
    """
    try:
        if not request.user_skills:
            raise HTTPException(status_code=400, detail="User skills cannot be empty")
        
        if not request.target_role.strip():
            raise HTTPException(status_code=400, detail="Target role cannot be empty")
        
        # Perform the complete 8-step analysis
        analysis_result = skill_gap_analyzer.analyze_skill_gap(
            user_skills=request.user_skills,
            target_role=request.target_role
        )
        
        if not analysis_result.get("success", False):
            raise HTTPException(
                status_code=404, 
                detail=analysis_result.get("error", "Analysis failed")
            )
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/skill-normalization")
async def normalize_skills(request: SkillNormalizationRequest):
    """
    Normalize a list of skills using the skill normalization layer.
    
    This endpoint demonstrates Step 1 of the analysis process:
    - Converts skills to lowercase
    - Trims spaces and removes duplicates
    - Standardizes variants using synonym mapping
    """
    try:
        from app.services.skill_normalizer import skill_normalizer
        
        normalized_skills = skill_normalizer.normalize_skills_list(request.skills)
        stats = skill_normalizer.get_normalization_stats(request.skills)
        
        return {
            "success": True,
            "original_skills": request.skills,
            "normalized_skills": normalized_skills,
            "normalization_stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")

@app.post("/api/skill-matching")
async def match_skills(request: SkillMatchingRequest):
    """
    Perform intelligent skill matching between user skills and requirements.
    
    This endpoint demonstrates Step 3 of the analysis process:
    - Exact matching for perfect alignment
    - Fuzzy matching for typos and variants
    - Hierarchical matching for advanced skills covering basics
    """
    try:
        from app.services.intelligent_skill_matcher import intelligent_skill_matcher
        
        matching_result = intelligent_skill_matcher.match_skills_comprehensive(
            request.user_skills, request.required_skills
        )
        
        return {
            "success": True,
            "matching_analysis": matching_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill matching failed: {str(e)}")

@app.get("/api/available-roles")
async def get_available_roles():
    """
    Get list of available job roles in the system.
    
    Returns a list of job roles that can be used for skill gap analysis,
    along with their basic information.
    """
    try:
        if not skill_gap_analyzer.job_roles_data:
            return {
                "success": False,
                "message": "Job roles data not available",
                "sample_roles": [
                    ".NET Developer", "AI Engineer - Fresher", "AI Engineer - Experienced",
                    "Frontend Developer", "Backend Developer", "Full Stack Developer",
                    "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
                    "Mobile Developer", "Cybersecurity Analyst", "Cloud Architect"
                ]
            }
        
        # Get role statistics
        roles_info = []
        for role_name, role_data in list(skill_gap_analyzer.job_roles_data.items())[:50]:  # Limit to 50 for performance
            roles_info.append({
                "role_name": role_name,
                "experience_level": role_data.get("experience_level", "fresher"),
                "skill_count": len(role_data.get("required_skills", [])),
                "job_count": role_data.get("job_count", 1)
            })
        
        # Sort by job count (popularity)
        roles_info.sort(key=lambda x: x["job_count"], reverse=True)
        
        return {
            "success": True,
            "total_roles": len(skill_gap_analyzer.job_roles_data),
            "sample_roles": roles_info[:20],  # Return top 20
            "experience_levels": ["fresher", "junior", "mid-level", "senior"],
            "popular_categories": [
                "Software Engineer", "Data Scientist", "Frontend Developer",
                "Backend Developer", "AI Engineer", "DevOps Engineer",
                "Mobile Developer", "Cybersecurity Analyst"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get roles: {str(e)}")

@app.get("/api/skill-categories")
async def get_skill_categories():
    """
    Get information about skill categories used in the taxonomy.
    
    Returns the skill categorization system used in Step 2 of the analysis.
    """
    try:
        from app.services.skill_taxonomy import skill_taxonomy, SkillCategory
        
        categories_info = {}
        for category in SkillCategory:
            category_data = skill_taxonomy.skill_categories[category]
            categories_info[category.value] = {
                "description": category_data["description"],
                "weight": category_data["weight"],
                "sample_skills": category_data["skills"][:10]  # First 10 skills as samples
            }
        
        return {
            "success": True,
            "categories": categories_info,
            "total_categories": len(SkillCategory)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test if the analyzer can load data
        has_job_data = bool(skill_gap_analyzer.job_roles_data)
        
        return {
            "status": "healthy",
            "service": "CareerBoost AI - Skill Gap Analyzer",
            "version": "1.0.0",
            "components": {
                "skill_normalizer": "operational",
                "skill_taxonomy": "operational", 
                "intelligent_matcher": "operational",
                "gap_scorer": "operational",
                "roadmap_generator": "operational",
                "job_data": "loaded" if has_job_data else "not_loaded"
            },
            "data_status": {
                "job_roles_count": len(skill_gap_analyzer.job_roles_data),
                "has_job_data": has_job_data
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": [
            "/api/skill-gap-analysis",
            "/api/skill-normalization", 
            "/api/skill-matching",
            "/api/available-roles",
            "/health"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "success": False,
        "error": "Internal server error",
        "message": "Please check your request and try again"
    }

if __name__ == "__main__":
    print("🚀 Starting CareerBoost AI - Skill Gap Analyzer API Server")
    print("📊 8-Step Skill Gap Analysis System")
    print("🔗 API Documentation: http://localhost:8005/docs")
    print("🏥 Health Check: http://localhost:8005/health")
    print("=" * 60)
    
    uvicorn.run(
        "skill_gap_api_server:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )