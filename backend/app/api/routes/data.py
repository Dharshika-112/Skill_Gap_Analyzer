"""
Data routes - provides skills, roles, and analysis
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from pydantic import BaseModel
from typing import List
from ...services.extended_dataset import (
    get_dataset_skills,
    get_dataset_roles,
    get_role_requirements,
    get_dataset_summary,
)
from ...services.advanced_ml import get_skill_gap_analysis, get_learning_path
from ...services.resume_parser import parse_resume, save_parsed_resume
from ...services.skill_categorizer import categorize_skills, get_star_rating
from ...services.common_role_skills import compute_common_and_role_specific_skills, get_essential_vs_overall_skills
from ...services.skill_matcher import rank_matching_roles
from ...core.security import decode_token
from typing import Optional
from ...core.database import get_collection

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
        skills = get_dataset_skills()
        return {
            "skills": skills,
            "total": len(skills),
            "dataset_info": "Skills from MongoDB dataset (fallback to built-in list if Mongo not initialized)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roles")
async def get_roles():
    """Get all available job roles from extended dataset"""
    try:
        roles = get_dataset_roles()
        return {
            "roles": roles,
            "total": len(roles),
            "dataset_info": "Roles from MongoDB dataset (fallback to built-in list if Mongo not initialized)"
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
    Analyze skill gap using advanced ML algorithms with enhanced features:
    - TF-IDF Similarity
    - Cosine Similarity
    - Jaccard Index
    - Deep Learning Predictions (if available)
    - Common vs Role-Specific Skills
    - Essential vs Overall Skills
    - Grouped Skill Display
    - Star Rating
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
        
        # Enhance with common vs role-specific
        common_role = {}
        if request.role_name:
            try:
                common_role = compute_common_and_role_specific_skills(request.role_name)
            except:
                pass
        
        # Essential vs overall
        essential_overall = get_essential_vs_overall_skills(request.role_skills, request.user_skills)
        
        # Categorize missing skills
        missing_categorized = categorize_skills(analysis.get('missing_skills', []))
        matching_categorized = categorize_skills(analysis.get('matching_skills', []))
        
        # Star rating
        star_rating = get_star_rating(analysis.get('match_percentage', 0))
        
        # Enhanced analysis
        enhanced_analysis = {
            **analysis,
            "star_rating": star_rating,
            "missing_skills_grouped": missing_categorized,
            "matching_skills_grouped": matching_categorized,
            "common_skills": common_role.get('common_skills', []),
            "role_specific_skills": common_role.get('role_specific_skills', []),
            "essential_skills": essential_overall.get('essential_skills', []),
            "overall_skills": essential_overall.get('overall_skills', []),
            "essential_match_count": essential_overall.get('essential_match_count', 0),
            "essential_total": essential_overall.get('total_essential', 0),
            "overall_match_count": essential_overall.get('overall_match_count', 0),
            "overall_total": essential_overall.get('total_overall', 0)
        }
        
        return {
            "status": "success",
            "analysis": enhanced_analysis,
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


@router.post('/save-analysis')
async def save_analysis(authorization: Optional[str] = Header(None), payload: dict = {}):
    """Save an analysis result into user's history. Requires Bearer token and payload containing role and analysis."""
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
    if not token:
        raise HTTPException(status_code=401, detail='Missing token')
    try:
        user = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')

    user_id = user.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail='Invalid token payload')

    col = get_collection('user_skill_gaps')
    doc = {
        'user_id': user_id,
        'role': payload.get('role'),
        'analysis': payload.get('analysis'),
        'created_at': __import__('datetime').datetime.utcnow()
    }
    res = col.insert_one(doc)
    return {'status': 'success', 'id': str(res.inserted_id)}


@router.get('/history')
async def get_history(authorization: Optional[str] = Header(None)):
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
    if not token:
        raise HTTPException(status_code=401, detail='Missing token')
    try:
        user = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')

    user_id = user.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail='Invalid token payload')

    col = get_collection('user_skill_gaps')
    items = list(col.find({'user_id': user_id}).sort('created_at', -1))
    # Convert ObjectId and datetimes
    from bson import ObjectId
    for it in items:
        it['id'] = str(it.get('_id'))
        it.pop('_id', None)
        if isinstance(it.get('created_at'), __import__('datetime').datetime):
            it['created_at'] = it['created_at'].isoformat()
    return {'status': 'success', 'history': items}

@router.post("/export-report")
async def export_report(authorization: Optional[str] = Header(None), payload: dict = {}):
    """Export skill gap report as TXT, PDF, or CSV"""
    from fastapi.responses import Response
    import csv
    import io
    from datetime import datetime
    
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
    if not token:
        raise HTTPException(status_code=401, detail='Missing token')
    
    try:
        user = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')
    
    export_type = payload.get('type', 'txt')  # txt, pdf, csv
    analysis = payload.get('analysis', {})
    role_name = payload.get('role', 'Unknown Role')
    
    if export_type == 'csv':
        # CSV export for missing skills
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Skill', 'Category', 'Priority'])
        
        missing_grouped = analysis.get('missing_skills_grouped', {})
        for category, skills in missing_grouped.items():
            for skill in skills:
                writer.writerow([skill, category, 'High' if category in ['Programming Languages', 'Web Technologies'] else 'Medium'])
        
        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename=skill_gap_{role_name.replace(" ", "_")}.csv'}
        )
    
    elif export_type == 'txt':
        # TXT report
        report_lines = [
            f"SKILL GAP ANALYSIS REPORT",
            f"{'='*50}",
            f"Role: {role_name}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"MATCH SUMMARY",
            f"{'-'*50}",
            f"Match Percentage: {analysis.get('match_percentage', 0)}%",
            f"Star Rating: {'⭐' * analysis.get('star_rating', 0)}",
            f"Matching Skills: {analysis.get('matching_count', 0)}",
            f"Missing Skills: {analysis.get('missing_count', 0)}",
            f"",
            f"MATCHING SKILLS",
            f"{'-'*50}",
        ]
        
        matching_grouped = analysis.get('matching_skills_grouped', {})
        for category, skills in matching_grouped.items():
            report_lines.append(f"\n{category}:")
            for skill in skills:
                report_lines.append(f"  ✓ {skill}")
        
        report_lines.extend([
            f"",
            f"MISSING SKILLS",
            f"{'-'*50}",
        ])
        
        missing_grouped = analysis.get('missing_skills_grouped', {})
        for category, skills in missing_grouped.items():
            report_lines.append(f"\n{category}:")
            for skill in skills:
                report_lines.append(f"  ✗ {skill}")
        
        report_lines.extend([
            f"",
            f"COMMON SKILLS (Must Know)",
            f"{'-'*50}",
        ])
        
        for skill in analysis.get('common_skills', [])[:10]:
            report_lines.append(f"  • {skill}")
        
        report_lines.extend([
            f"",
            f"ROLE-SPECIFIC BOOSTERS",
            f"{'-'*50}",
        ])
        
        for skill in analysis.get('role_specific_skills', [])[:10]:
            report_lines.append(f"  • {skill}")
        
        txt_content = '\n'.join(report_lines)
        return Response(
            content=txt_content,
            media_type='text/plain',
            headers={'Content-Disposition': f'attachment; filename=skill_gap_report_{role_name.replace(" ", "_")}.txt'}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid export type. Use 'txt', 'csv', or 'pdf'")

@router.get("/role-requirements/{role_name}")
async def get_role_reqs(role_name: str):
    """Get required skills for a specific role"""
    try:
        skills = get_role_requirements(role_name)
        return {
            "role_ref": role_name,
            "required_skills": skills,
            "total_skills": len(skills)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend-roles")
async def recommend_roles(user_skills_req: dict):
    """Recommend top 5 roles based on user skills with star ratings"""
    try:
        user_skills = user_skills_req.get("skills", [])
        experience = user_skills_req.get("experience", {})
        if not user_skills:
            raise HTTPException(status_code=400, detail="Skills are required")
        
        roles = get_dataset_roles()
        roles_dict = {}
        
        # Build roles dictionary
        eval_roles = roles if roles and isinstance(roles[0], dict) else [{"id": r, "title": r, "level": "unknown"} for r in roles]
        for role in eval_roles[:200]:  # safety cap
            role_ref = role.get("id") or role.get("title")
            role_title = role.get("title") or role_ref
            try:
                role_reqs = get_role_requirements(role_ref)
                roles_dict[role_title] = role_reqs
            except:
                continue
        
        # Rank roles using skill matcher
        rankings = rank_matching_roles(user_skills, roles_dict)
        
        # Take top 5
        rankings = rankings[:5]
        
        # Enhance with star ratings, essential vs overall, common vs role-specific
        enhanced_recommendations = []
        for rank in rankings:
            role_name = rank['role']
            role_reqs = roles_dict.get(role_name, [])
            
            # Get common vs role-specific
            common_role = {}
            try:
                common_role = compute_common_and_role_specific_skills(role_name)
            except:
                pass
            
            # Get essential vs overall
            essential_overall = get_essential_vs_overall_skills(role_reqs, user_skills)
            
            # Calculate star rating
            star_rating = get_star_rating(rank['match_percentage'])
            
            # Categorize missing skills
            missing_categorized = categorize_skills(rank['missing_skills'])
            
            enhanced_recommendations.append({
                "role": role_name,
                "match_percentage": rank['match_percentage'],
                "star_rating": star_rating,
                "matching_skills": rank['matching_skills'],
                "missing_skills": rank['missing_skills'],
                "missing_skills_grouped": missing_categorized,
                "essential_skills_match": essential_overall['essential_match_count'],
                "essential_skills_total": essential_overall['total_essential'],
                "overall_skills_match": essential_overall['overall_match_count'],
                "overall_skills_total": essential_overall['total_overall'],
                "common_skills": common_role.get('common_skills', []),
                "role_specific_skills": common_role.get('role_specific_skills', []),
                "algorithms": rank.get('algorithms', {})
            })
        
        return {
            "status": "success",
            "recommendations": enhanced_recommendations,
            "total_evaluated": len(roles_dict)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), authorization: Optional[str] = Header(None)):
    """Upload and parse resume (PDF/DOCX/TXT). Requires Bearer token."""
    # Extract bearer token
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # validate token
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Read file bytes
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {e}")

    # Parse resume
    try:
        parsed = parse_resume(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {e}")

    # Persist parsed resume
    try:
        resume_id = save_parsed_resume(user_id, parsed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save parsed resume: {e}")

    # Return parsed summary
    # Convert datetime to isoformat for JSON
    parsed_summary = {
        'resume_id': resume_id,
        'filename': parsed.get('filename'),
        'skills': parsed.get('skills', []),
        'experience': parsed.get('experience', {}),
        'parsed_at': parsed.get('parsed_at').isoformat() if parsed.get('parsed_at') else None
    }

    return {"status": "success", "parsed": parsed_summary}
