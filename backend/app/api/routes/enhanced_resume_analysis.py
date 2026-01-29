"""
Enhanced Resume Analysis API Routes
Handles resume upload, parsing, and scoring with deep learning
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ...services.deep_learning_parser import parse_resume_with_deep_learning
from ...services.role_based_ml_scorer import (
    score_resume_general, 
    score_resume_role_based, 
    get_available_scoring_roles
)
from ...services.enhanced_skill_matcher import (
    analyze_skill_gap,
    generate_improvement_suggestions
)
from ...core.database import get_collection

router = APIRouter()

# Pydantic models
class GeneralScoringRequest(BaseModel):
    resume_data: Dict[str, Any]

class RoleBasedScoringRequest(BaseModel):
    resume_data: Dict[str, Any]
    target_role: str

class SkillGapRequest(BaseModel):
    user_skills: list[str]
    target_role: str

# Upload directory
UPLOAD_DIR = Path(__file__).parents[3] / 'data' / 'raw' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse resume using deep learning techniques"""
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    if file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    try:
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4()).replace('-', '')[:16]
        filename = f"{timestamp}_{unique_id}.pdf"
        file_path = UPLOAD_DIR / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse resume with deep learning
        def progress_callback(step: str, progress: int):
            # In a real implementation, you might use WebSockets or Server-Sent Events
            # to send progress updates to the frontend
            print(f"[PROGRESS] {step}: {progress}%")
        
        parsed_data = parse_resume_with_deep_learning(str(file_path), progress_callback)
        
        # Store in database for future reference
        collection = get_collection("resume_uploads")
        upload_record = {
            "filename": filename,
            "original_name": file.filename,
            "file_path": str(file_path),
            "upload_time": datetime.utcnow(),
            "parsed_data": parsed_data,
            "file_size": file.size
        }
        
        result = collection.insert_one(upload_record)
        upload_record["_id"] = str(result.inserted_id)
        
        return JSONResponse({
            "success": True,
            "message": "Resume uploaded and parsed successfully",
            "upload_id": str(result.inserted_id),
            "parsed_data": parsed_data,
            "processing_info": {
                "pdf_type": parsed_data.get("pdf_type", "unknown"),
                "extraction_method": parsed_data.get("extraction_method", "unknown"),
                "confidence": parsed_data.get("confidence", 0.0),
                "skills_extracted": len(parsed_data.get("skills", [])),
                "deep_learning_enabled": parsed_data.get("metadata", {}).get("deep_learning_enabled", False)
            }
        })
        
    except Exception as e:
        # Clean up file if parsing failed
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process resume: {str(e)}"
        )

@router.post("/score-general")
async def score_resume_general_endpoint(request: GeneralScoringRequest):
    """Score resume using general ATS model"""
    
    try:
        result = score_resume_general(request.resume_data)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to score resume")
            )
        
        # Store scoring result
        collection = get_collection("scoring_results")
        scoring_record = {
            "scoring_type": "general",
            "score": result.get("score", 0),
            "model_type": result.get("model_type", "general"),
            "confidence": result.get("confidence", "medium"),
            "timestamp": datetime.utcnow(),
            "resume_data": request.resume_data
        }
        
        collection.insert_one(scoring_record)
        
        return JSONResponse({
            "success": True,
            "score": result.get("score", 0),
            "model_type": result.get("model_type", "general"),
            "confidence": result.get("confidence", "medium"),
            "features_used": result.get("features_used", 0),
            "analysis": {
                "score_interpretation": _interpret_general_score(result.get("score", 0)),
                "recommendations": _get_general_recommendations(result.get("score", 0))
            }
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to score resume: {str(e)}"
        )

@router.post("/score-role-based")
async def score_resume_role_based_endpoint(request: RoleBasedScoringRequest):
    """🔥 FEATURE 3: Score resume for specific role using ML models"""
    
    try:
        result = score_resume_role_based(request.resume_data, request.target_role)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to score resume for target role")
            )
        
        # Store scoring result
        collection = get_collection("scoring_results")
        scoring_record = {
            "scoring_type": "role_based",
            "target_role": request.target_role,
            "score": result.get("score", 0),
            "model_type": result.get("model_type", "role_specific"),
            "confidence": result.get("confidence", "medium"),
            "skill_match_ratio": result.get("skill_match_ratio", 0),
            "timestamp": datetime.utcnow(),
            "resume_data": request.resume_data
        }
        
        collection.insert_one(scoring_record)
        
        return JSONResponse({
            "success": True,
            "score": result.get("score", 0),
            "target_role": request.target_role,
            "matched_role": result.get("matched_role", request.target_role),
            "model_type": result.get("model_type", "role_specific"),
            "confidence": result.get("confidence", "medium"),
            "skill_match_ratio": result.get("skill_match_ratio", 0),
            "features_used": result.get("features_used", 0),
            "benchmarks": result.get("benchmarks", {}),
            "interpretation": result.get("interpretation", {}),
            "analysis": {
                "percentile_rank": result.get("interpretation", {}).get("percentile_rank", 50),
                "performance_level": result.get("interpretation", {}).get("level", "average"),
                "recommendations": _get_role_based_recommendations(
                    result.get("score", 0), 
                    request.target_role,
                    result.get("skill_match_ratio", 0)
                )
            }
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to score resume for role: {str(e)}"
        )

@router.get("/available-roles")
async def get_available_roles():
    """Get available roles for scoring"""
    
    try:
        roles = get_available_scoring_roles()
        
        return JSONResponse({
            "success": True,
            "roles": roles,
            "total_roles": len(roles)
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available roles: {str(e)}"
        )

@router.post("/skill-gap-analysis")
async def skill_gap_analysis_endpoint(request: SkillGapRequest):
    """🔥 FEATURE 1: Analyze skill gaps for target role"""
    
    try:
        # Perform skill gap analysis
        gap_analysis = analyze_skill_gap(request.user_skills, request.target_role)
        
        if not gap_analysis.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=gap_analysis.get("error", "Failed to analyze skill gaps")
            )
        
        # Generate improvement suggestions
        suggestions = generate_improvement_suggestions(gap_analysis)
        
        # Store analysis result
        collection = get_collection("skill_gap_analyses")
        analysis_record = {
            "user_skills": request.user_skills,
            "target_role": request.target_role,
            "match_percentage": gap_analysis.get("match_percentage", 0),
            "gap_count": gap_analysis.get("gap_count", 0),
            "timestamp": datetime.utcnow(),
            "analysis_result": gap_analysis,
            "suggestions": suggestions
        }
        
        collection.insert_one(analysis_record)
        
        return JSONResponse({
            "success": True,
            "skill_gap_analysis": gap_analysis,
            "improvement_suggestions": suggestions,
            "summary": {
                "match_percentage": gap_analysis.get("match_percentage", 0),
                "matched_skills": len(gap_analysis.get("matched_skills", [])),
                "missing_skills": len(gap_analysis.get("missing_skills", [])),
                "gap_severity": gap_analysis.get("gap_severity", {}).get("level", "unknown"),
                "priority_actions": suggestions.get("priority_actions", [])
            }
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze skill gaps: {str(e)}"
        )

@router.get("/user-history")
async def get_user_history():
    """Get user's analysis and scoring history"""
    
    try:
        # Get recent uploads
        uploads_collection = get_collection("resume_uploads")
        recent_uploads = list(uploads_collection.find(
            {},
            {"filename": 1, "original_name": 1, "upload_time": 1, "parsed_data.skills": 1}
        ).sort("upload_time", -1).limit(10))
        
        # Get recent scoring results
        scoring_collection = get_collection("scoring_results")
        recent_scores = list(scoring_collection.find(
            {},
            {"scoring_type": 1, "target_role": 1, "score": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(10))
        
        # Get recent skill gap analyses
        gap_collection = get_collection("skill_gap_analyses")
        recent_analyses = list(gap_collection.find(
            {},
            {"target_role": 1, "match_percentage": 1, "gap_count": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(10))
        
        return JSONResponse({
            "success": True,
            "history": {
                "recent_uploads": [
                    {
                        "id": str(item["_id"]),
                        "filename": item.get("original_name", "Unknown"),
                        "upload_time": item.get("upload_time").isoformat() if item.get("upload_time") else None,
                        "skills_count": len(item.get("parsed_data", {}).get("skills", []))
                    }
                    for item in recent_uploads
                ],
                "recent_scores": [
                    {
                        "id": str(item["_id"]),
                        "type": item.get("scoring_type", "general"),
                        "role": item.get("target_role", "General"),
                        "score": item.get("score", 0),
                        "timestamp": item.get("timestamp").isoformat() if item.get("timestamp") else None
                    }
                    for item in recent_scores
                ],
                "recent_analyses": [
                    {
                        "id": str(item["_id"]),
                        "role": item.get("target_role", "Unknown"),
                        "match_percentage": item.get("match_percentage", 0),
                        "gap_count": item.get("gap_count", 0),
                        "timestamp": item.get("timestamp").isoformat() if item.get("timestamp") else None
                    }
                    for item in recent_analyses
                ]
            }
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user history: {str(e)}"
        )

# Helper functions
def _interpret_general_score(score: float) -> Dict[str, Any]:
    """Interpret general ATS score"""
    if score >= 90:
        return {
            "level": "excellent",
            "description": "Your resume is highly optimized for ATS systems",
            "color": "#10b981"
        }
    elif score >= 80:
        return {
            "level": "very_good",
            "description": "Your resume performs well with ATS systems",
            "color": "#3b82f6"
        }
    elif score >= 70:
        return {
            "level": "good",
            "description": "Your resume has good ATS compatibility",
            "color": "#f59e0b"
        }
    elif score >= 60:
        return {
            "level": "average",
            "description": "Your resume needs some optimization for ATS",
            "color": "#f97316"
        }
    else:
        return {
            "level": "needs_improvement",
            "description": "Your resume requires significant ATS optimization",
            "color": "#ef4444"
        }

def _get_general_recommendations(score: float) -> list[str]:
    """Get general recommendations based on score"""
    recommendations = []
    
    if score < 70:
        recommendations.extend([
            "Add more relevant keywords throughout your resume",
            "Use standard section headings (Experience, Education, Skills)",
            "Ensure consistent formatting and font usage",
            "Include quantifiable achievements with numbers and percentages"
        ])
    
    if score < 80:
        recommendations.extend([
            "Optimize your resume for specific job descriptions",
            "Include industry-specific terminology and buzzwords",
            "Add a professional summary section"
        ])
    
    if score < 90:
        recommendations.extend([
            "Fine-tune keyword density for better matching",
            "Consider adding relevant certifications or training"
        ])
    
    return recommendations[:5]  # Return top 5 recommendations

def _get_role_based_recommendations(score: float, role: str, skill_match_ratio: float) -> list[str]:
    """Get role-specific recommendations"""
    recommendations = []
    
    if skill_match_ratio < 0.6:
        recommendations.append(f"Focus on acquiring key skills for {role} positions")
    
    if score < 70:
        recommendations.extend([
            f"Study job descriptions for {role} to identify missing keywords",
            f"Highlight relevant projects and experience for {role}",
            f"Consider getting certifications relevant to {role}"
        ])
    
    if score < 80:
        recommendations.extend([
            f"Quantify your achievements in {role}-related tasks",
            f"Use industry-specific terminology for {role}"
        ])
    
    return recommendations[:5]