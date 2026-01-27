"""
Resume Analysis Routes - AI-Powered ATS System
Combines ML-based ATS scoring with skill gap analysis
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Header, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ...core.database import get_collection
from ...core.security import decode_token
from ...services.resume_parser import parse_resume
from ...services.ats_system import (
    predict_ats_score,
    analyze_skill_gap,
    score_resume_for_roles,
    calculate_resume_jd_similarity,
    get_improvement_suggestions
)
from ...services.dataset_loader import (
    get_all_skills_from_dataset,
    get_all_roles_from_dataset,
    get_role_requirements_from_dataset,
    find_matching_roles_from_dataset,
    calculate_resume_score_from_dataset
)
from ...services.intelligent_role_matcher import (
    find_intelligent_matches,
    get_skill_recommendations,
    get_skill_importance
)
from datetime import datetime

router = APIRouter()

class ATSAnalysisRequest(BaseModel):
    user_skills: List[str]
    experience_years: Optional[float] = 0
    education: Optional[str] = "Bachelor's"
    certifications: Optional[List[str]] = []
    target_role: Optional[str] = None
    projects_count: Optional[int] = 0

class ResumeAnalysisRequest(BaseModel):
    user_skills: List[str]
    experience: Optional[Dict] = None

class RoleAnalysisRequest(BaseModel):
    role_title: str
    user_skills: List[str]

class ResumeRankingRequest(BaseModel):
    job_description: str
    target_role: str

def _get_user_from_token(authorization: Optional[str]):
    """Extract user info from authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    try:
        payload = decode_token(parts[1])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/ats-analysis")
async def comprehensive_ats_analysis(
    request: ATSAnalysisRequest,
    authorization: Optional[str] = Header(None)
):
    """
    🚀 COMPREHENSIVE ATS ANALYSIS
    Combines ML-based ATS scoring with skill gap analysis
    """
    user = _get_user_from_token(authorization)
    user_id = user.get('user_id')
    
    try:
        # Prepare resume data for ATS scoring
        resume_data = {
            'skills': request.user_skills,
            'experience_years': request.experience_years,
            'education': request.education,
            'certifications': request.certifications,
            'target_role': request.target_role or 'Software Developer',
            'projects_count': request.projects_count
        }
        
        # 1. ATS Score Prediction (ML Model)
        ats_result = predict_ats_score(resume_data)
        
        # 2. Role-based Scoring (Multiple Roles)
        role_scoring = score_resume_for_roles(resume_data)
        
        # 3. Skill Gap Analysis (if target role specified)
        skill_gap = None
        if request.target_role:
            skill_gap = analyze_skill_gap(request.user_skills, request.target_role)
        else:
            # Use best matching role for skill gap analysis
            if 'error' not in role_scoring and role_scoring.get('best_match'):
                best_role = role_scoring['best_match']['role']
                skill_gap = analyze_skill_gap(request.user_skills, best_role)
        
        # 4. Improvement Suggestions
        suggestions = []
        if skill_gap and 'error' not in skill_gap:
            suggestions = get_improvement_suggestions(skill_gap, ats_result.get('ats_score', 0))
        else:
            # Generate basic suggestions based on ATS score
            ats_score = ats_result.get('ats_score', 0)
            if ats_score < 70:
                suggestions.append("🎯 Consider adding more relevant technical skills to improve your ATS score")
                suggestions.append("📝 Enhance your resume with quantifiable achievements and project details")
            if ats_score < 50:
                suggestions.append("🎓 Consider obtaining relevant certifications in your field")
                suggestions.append("💼 Gain more hands-on experience through projects or internships")
        
        # 5. Intelligent Role Matches (Deep Learning)
        intelligent_matches = find_intelligent_matches(request.user_skills, top_n=5)
        
        # 6. Skill Importance Analysis
        skill_importance = []
        for skill in request.user_skills:
            importance = get_skill_importance(skill)
            skill_importance.append({
                "skill": skill,
                "importance": round(importance, 3),
                "priority": "High" if importance > 0.5 else "Medium" if importance > 0.2 else "Low"
            })
        
        skill_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        # Save analysis to database
        try:
            analyses_col = get_collection('ats_analyses')
            analysis_doc = {
                'user_id': user_id,
                'resume_data': resume_data,
                'ats_result': ats_result,
                'role_scoring': role_scoring,
                'skill_gap': skill_gap,
                'suggestions': suggestions,
                'intelligent_matches': intelligent_matches,
                'skill_importance': skill_importance,
                'analyzed_at': datetime.utcnow()
            }
            analyses_col.insert_one(analysis_doc)
        except Exception as e:
            print(f"Database save error: {e}")
        
        return {
            "status": "success",
            "analysis_type": "comprehensive_ats",
            "ats_scoring": ats_result,
            "role_based_scoring": role_scoring,
            "skill_gap_analysis": skill_gap,
            "improvement_suggestions": suggestions,
            "intelligent_role_matches": intelligent_matches,
            "skill_importance_ranking": skill_importance,
            "summary": {
                "ats_score": ats_result.get('ats_score', 0),
                "best_role_match": role_scoring.get('best_match', {}).get('role', 'Unknown') if 'error' not in role_scoring else 'Unknown',
                "skill_gaps": len(skill_gap.get('missing_skills', [])) if skill_gap and 'error' not in skill_gap else 0,
                "high_priority_skills": len([s for s in skill_importance if s['priority'] == 'High'])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ATS analysis failed: {str(e)}")

@router.post("/upload-and-analyze")
async def upload_and_analyze_resume(
    file: UploadFile = File(...), 
    authorization: Optional[str] = Header(None)
):
    """
    📄 UPLOAD RESUME + ANALYSIS (Legacy endpoint for compatibility)
    Parse resume and run analysis
    """
    # Redirect to the comprehensive ATS analysis
    return await upload_resume_and_ats_analyze(file, authorization)

@router.post("/upload-and-ats-analyze")
async def upload_resume_and_ats_analyze(
    file: UploadFile = File(...), 
    authorization: Optional[str] = Header(None)
):
    """
    📄 UPLOAD RESUME + COMPREHENSIVE ATS ANALYSIS
    Parse resume and run full ATS analysis
    """
    user = _get_user_from_token(authorization)
    user_id = user.get('user_id')
    
    # Parse resume
    try:
        contents = await file.read()
        parsed = parse_resume(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")
    
    extracted_skills = parsed.get('skills', [])
    experience = parsed.get('experience', {})
    
    if not extracted_skills or len(extracted_skills) < 3:
        # Resume parsing failed - return manual selection option
        return {
            "status": "parsing_failed",
            "message": f"Only {len(extracted_skills)} skills extracted from resume",
            "extracted_skills": extracted_skills,
            "fallback_action": "manual_selection",
            "suggestions": [
                "Use manual skill selection for better accuracy",
                "Ensure your resume has a clear 'Technical Skills' section",
                "List skills with bullet points or clear separators"
            ]
        }
    
    # Run comprehensive ATS analysis
    try:
        ats_request = ATSAnalysisRequest(
            user_skills=extracted_skills,
            experience_years=experience.get('years', 0),
            education="Bachelor's",  # Default, can be enhanced
            certifications=[],  # Can be extracted from resume
            target_role=None,  # Will analyze multiple roles
            projects_count=0  # Can be extracted from resume
        )
        
        # Get comprehensive analysis
        analysis_result = await comprehensive_ats_analysis(ats_request, authorization)
        
        # Add resume-specific data
        analysis_result['resume_info'] = {
            'filename': file.filename,
            'extracted_skills': extracted_skills,
            'experience': experience,
            'parsing_success': True
        }
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ATS analysis failed: {str(e)}")

@router.post("/resume-jd-similarity")
async def calculate_resume_job_similarity(
    request: dict,
    authorization: Optional[str] = Header(None)
):
    """
    📊 RESUME-JD SIMILARITY ANALYSIS
    Calculate similarity between resume and job description
    """
    user = _get_user_from_token(authorization)
    
    try:
        resume_text = request.get('resume_text', '')
        job_description = request.get('job_description', '')
        
        if not resume_text or not job_description:
            raise HTTPException(status_code=400, detail="Both resume_text and job_description are required")
        
        similarity_result = calculate_resume_jd_similarity(resume_text, job_description)
        
        return {
            "status": "success",
            "similarity_analysis": similarity_result,
            "recommendations": _generate_similarity_recommendations(similarity_result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity analysis failed: {str(e)}")

@router.post("/rank-resumes")
async def rank_multiple_resumes(
    request: ResumeRankingRequest,
    authorization: Optional[str] = Header(None)
):
    """
    🏆 RESUME RANKING SYSTEM
    Rank multiple resumes for a job role
    """
    user = _get_user_from_token(authorization)
    
    try:
        # Get all user resumes from database
        resumes_col = get_collection('resumes')
        user_id = user.get('user_id')
        
        # Try different user_id formats
        user_resumes = list(resumes_col.find({'user_id': user_id}))
        if not user_resumes:
            # Try with string conversion
            user_resumes = list(resumes_col.find({'user_id': str(user_id)}))
        
        if not user_resumes:
            # Return empty result instead of error for better UX
            return {
                "status": "success",
                "target_role": request.target_role,
                "total_resumes": 0,
                "ranked_resumes": [],
                "top_resume": None,
                "message": "No resumes found for ranking. Upload resumes first."
            }
        
        ranked_resumes = []
        
        for resume_doc in user_resumes:
            try:
                # Prepare resume data
                resume_data = {
                    'skills': resume_doc.get('skills', []),
                    'experience_years': resume_doc.get('experience', {}).get('years', 0) if resume_doc.get('experience') else 0,
                    'education': 'Bachelor\'s',
                    'certifications': [],
                    'target_role': request.target_role,
                    'projects_count': 0
                }
                
                # Get ATS score
                ats_result = predict_ats_score(resume_data)
                
                # Get skill gap analysis
                gap_analysis = analyze_skill_gap(resume_data['skills'], request.target_role)
                
                if 'error' not in ats_result and 'error' not in gap_analysis:
                    ranked_resumes.append({
                        'resume_id': str(resume_doc['_id']),
                        'filename': resume_doc.get('filename', 'Unknown'),
                        'ats_score': ats_result['ats_score'],
                        'match_percentage': gap_analysis['match_percentage'],
                        'combined_score': (ats_result['ats_score'] + gap_analysis['match_percentage']) / 2,
                        'readiness': gap_analysis['readiness_level']['level'],
                        'skills_count': len(resume_data['skills'])
                    })
            except Exception as resume_error:
                print(f"Error processing resume {resume_doc.get('_id')}: {resume_error}")
                continue
        
        # Sort by combined score
        ranked_resumes.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Add rankings
        for i, resume in enumerate(ranked_resumes, 1):
            resume['rank'] = i
        
        return {
            "status": "success",
            "target_role": request.target_role,
            "total_resumes": len(ranked_resumes),
            "ranked_resumes": ranked_resumes,
            "top_resume": ranked_resumes[0] if ranked_resumes else None
        }
        
    except Exception as e:
        print(f"Resume ranking error: {e}")
        return {
            "status": "error",
            "target_role": request.target_role,
            "total_resumes": 0,
            "ranked_resumes": [],
            "top_resume": None,
            "error": f"Resume ranking failed: {str(e)}"
        }

@router.get("/ats-insights")
async def get_ats_insights(authorization: Optional[str] = Header(None)):
    """
    📈 ATS SYSTEM INSIGHTS
    Get insights about the ATS system and market trends
    """
    user = _get_user_from_token(authorization)
    
    try:
        # Get dataset statistics
        roles = get_all_roles_from_dataset()
        skills = get_all_skills_from_dataset()
        
        # Calculate market insights
        top_roles = sorted(roles, key=lambda x: x['job_count'], reverse=True)[:10]
        
        # Skill frequency analysis
        skill_frequency = {}
        for role in roles:
            for skill in role['skills']:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + role['job_count']
        
        top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Experience level distribution
        exp_levels = {}
        for role in roles:
            for level in role['experience_levels']:
                exp_levels[level] = exp_levels.get(level, 0) + role['job_count']
        
        return {
            "status": "success",
            "market_insights": {
                "total_jobs": sum(role['job_count'] for role in roles),
                "total_roles": len(roles),
                "total_skills": len(skills),
                "top_roles": [{"role": role['title'], "job_count": role['job_count']} for role in top_roles],
                "top_skills": [{"skill": skill, "frequency": freq} for skill, freq in top_skills],
                "experience_distribution": exp_levels
            },
            "ats_system_info": {
                "model_type": "Random Forest Regressor",
                "features_used": ["Skills", "Experience", "Education", "Certifications", "Projects"],
                "accuracy_metrics": "R² Score: 0.85+ (Training), Cross-validation: 0.80+",
                "training_data": "AI Resume Screening Dataset (1000+ resumes)"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

def _generate_similarity_recommendations(similarity_result: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on similarity analysis"""
    recommendations = []
    overall_sim = similarity_result.get('overall_similarity', 0)
    
    if overall_sim < 40:
        recommendations.append("🎯 Low similarity detected - Tailor your resume more closely to the job description")
        recommendations.append("📝 Include more keywords from the job posting")
    elif overall_sim < 60:
        recommendations.append("📈 Moderate similarity - Add more relevant keywords and skills")
        recommendations.append("🔧 Highlight experience that matches job requirements")
    else:
        recommendations.append("✅ Good similarity score - Your resume aligns well with the job")
        recommendations.append("🚀 Consider applying - you meet most requirements")
    
    # Section-specific recommendations
    section_sims = similarity_result.get('section_similarities', {})
    for section, sim_score in section_sims.items():
        if sim_score < 50:
            recommendations.append(f"📚 Improve {section} section - current similarity: {sim_score}%")
    
    return recommendations

# Keep existing endpoints for backward compatibility
@router.get("/all-skills")
async def get_all_skills():
    """Get all available skills from dataset for manual selection"""
    try:
        skills = get_all_skills_from_dataset()
        
        # Group skills by category for better UX
        categorized_skills = {}
        
        for skill in skills:
            category = _get_skill_category(skill)
            if category not in categorized_skills:
                categorized_skills[category] = []
            categorized_skills[category].append(skill)
        
        # Sort skills within each category
        for category in categorized_skills:
            categorized_skills[category].sort()
        
        return {
            "status": "success",
            "total_skills": len(skills),
            "skills": skills,
            "categorized_skills": categorized_skills,
            "categories": list(categorized_skills.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load skills: {str(e)}")

@router.post("/manual-skill-analysis")
async def manual_skill_analysis(
    request: ResumeAnalysisRequest,
    authorization: Optional[str] = Header(None)
):
    """Analyze manually selected skills using ATS system"""
    user = _get_user_from_token(authorization)
    
    if not request.user_skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    
    try:
        # Convert to ATS analysis request
        ats_request = ATSAnalysisRequest(
            user_skills=request.user_skills,
            experience_years=request.experience.get('years', 0) if request.experience else 0,
            education="Bachelor's",
            certifications=[],
            target_role=None,
            projects_count=0
        )
        
        # Run comprehensive ATS analysis
        analysis_result = await comprehensive_ats_analysis(ats_request, authorization)
        
        # Add manual selection flag
        analysis_result['selection_method'] = 'manual'
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def _get_skill_category(skill: str) -> str:
    """Get category for a single skill"""
    skill_lower = skill.lower()
    
    if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'c#', 'c++', 'php', 'ruby']):
        return "Programming Languages"
    elif any(tech in skill_lower for tech in ['react', 'angular', 'vue', 'node', 'express', 'django']):
        return "Web Technologies"
    elif any(db in skill_lower for db in ['mysql', 'postgresql', 'mongodb', 'redis', 'sql']):
        return "Databases"
    elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'docker', 'kubernetes']):
        return "Cloud & DevOps"
    elif any(ml in skill_lower for ml in ['tensorflow', 'pytorch', 'machine learning', 'deep learning']):
        return "Machine Learning"
    else:
        return "Other"
async def upload_and_analyze_resume(
    file: UploadFile = File(...), 
    authorization: Optional[str] = Header(None)
):
    """
    Step 1: Upload resume and extract skills with immediate analysis
    Returns: extracted skills, experience, resume score, and initial role matches
    """
    user = _get_user_from_token(authorization)
    user_id = user.get('user_id')
    
    # Parse resume
    try:
        contents = await file.read()
        parsed = parse_resume(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")
    
    extracted_skills = parsed.get('skills', [])
    experience = parsed.get('experience', {})
    
    if not extracted_skills:
        return {
            "status": "warning",
            "message": "No skills were extracted from your resume. Please check if your resume has a 'Technical Skills' or 'Skills' section.",
            "extracted_skills": [],
            "suggestions": [
                "Make sure your resume has a clear 'Technical Skills' or 'Skills' section",
                "List your skills separated by commas or semicolons",
                "Include programming languages, frameworks, databases, and tools you know"
            ]
        }
    
    # Calculate resume score
    score_data = calculate_resume_score_from_dataset(extracted_skills)
    
    # Find intelligent role matches using Deep Learning
    intelligent_matches = find_intelligent_matches(extracted_skills, top_n=5)
    
    # Get skill recommendations
    skill_recommendations = get_skill_recommendations(extracted_skills)
    
    # Also get basic role matches for comparison
    basic_role_matches = find_matching_roles_from_dataset(extracted_skills, top_n=5)
    
    # Save to database
    try:
        resumes_col = get_collection('resumes')
        resume_doc = {
            'user_id': user_id,
            'filename': file.filename,
            'extracted_skills': extracted_skills,
            'experience': experience,
            'score_data': score_data,
            'parsed_at': datetime.utcnow()
        }
        result = resumes_col.insert_one(resume_doc)
        
        # Update user profile with resume skills
        users_col = get_collection('users')
        users_col.update_one(
            {'_id': user_id}, 
            {'$set': {'resume_skills': extracted_skills, 'experience': experience}}
        )
        
    except Exception as e:
        print(f"Database save error: {e}")
    
    return {
        "status": "success",
        "extracted_skills": extracted_skills,
        "skills_count": len(extracted_skills),
        "experience": experience,
        "resume_score": score_data,
        "intelligent_role_matches": intelligent_matches,
        "skill_recommendations": skill_recommendations,
        "skill_importance_scores": [
            {"skill": skill, "importance": get_skill_importance(skill)}
            for skill in extracted_skills
        ],
        "basic_role_matches": basic_role_matches,  # For comparison
        "next_steps": [
            "Review your skill importance scores - higher scores indicate more valuable skills",
            "Check intelligent role matches that prioritize important skills",
            "Focus on high-priority missing skills from recommendations",
            "Select a specific role for detailed gap analysis"
        ]
    }

@router.get("/dataset-roles")
async def get_dataset_roles():
    """
    Step 2: Get all available roles from the job dataset for dropdown
    """
    try:
        roles = get_all_roles_from_dataset()
        
        # Format for dropdown
        role_options = []
        for role in roles:
            role_options.append({
                'title': role['title'],
                'job_count': role['job_count'],
                'experience_levels': role['experience_levels'],
                'skills_count': len(role['skills'])
            })
        
        return {
            "status": "success",
            "roles": role_options,
            "total_roles": len(role_options)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load roles: {str(e)}")

@router.post("/analyze-role-gap")
async def analyze_role_gap(
    request: RoleAnalysisRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Step 3: Analyze gap for a specific role selected by user
    """
    user = _get_user_from_token(authorization)
    
    try:
        # Get role requirements
        role_requirements = get_role_requirements_from_dataset(request.role_title)
        
        if not role_requirements:
            raise HTTPException(status_code=404, detail=f"Role '{request.role_title}' not found in dataset")
        
        required_skills = role_requirements['required_skills']
        user_skills_lower = [s.lower().strip() for s in request.user_skills]
        required_skills_lower = [s.lower().strip() for s in required_skills]
        
        # Calculate matches and gaps
        matching_skills = []
        missing_skills = []
        
        for skill in required_skills:
            if skill.lower().strip() in user_skills_lower:
                matching_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        # Calculate match percentage
        match_percentage = (len(matching_skills) / len(required_skills) * 100) if required_skills else 0
        
        # Categorize missing skills
        missing_categorized = _categorize_skills(missing_skills)
        matching_categorized = _categorize_skills(matching_skills)
        
        # Determine readiness level
        if match_percentage >= 80:
            readiness = "Ready to Apply"
            readiness_color = "green"
        elif match_percentage >= 60:
            readiness = "Almost Ready"
            readiness_color = "orange"
        elif match_percentage >= 40:
            readiness = "Needs Preparation"
            readiness_color = "yellow"
        else:
            readiness = "Significant Gap"
            readiness_color = "red"
        
        analysis_result = {
            "role_title": request.role_title,
            "match_percentage": round(match_percentage, 2),
            "readiness": readiness,
            "readiness_color": readiness_color,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "matching_skills_categorized": matching_categorized,
            "missing_skills_categorized": missing_categorized,
            "total_required_skills": len(required_skills),
            "total_matching_skills": len(matching_skills),
            "total_missing_skills": len(missing_skills),
            "role_details": role_requirements,
            "recommendations": _generate_recommendations(missing_skills, match_percentage)
        }
        
        # Save analysis to history
        try:
            analyses_col = get_collection('analyses')
            analysis_doc = {
                'user_id': user.get('user_id'),
                'role_title': request.role_title,
                'user_skills': request.user_skills,
                'analysis_result': analysis_result,
                'analyzed_at': datetime.utcnow()
            }
            analyses_col.insert_one(analysis_doc)
        except Exception as e:
            print(f"Failed to save analysis: {e}")
        
        return {
            "status": "success",
            "analysis": analysis_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/intelligent-role-analysis")
async def intelligent_role_analysis(
    request: RoleAnalysisRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Enhanced role analysis using Deep Learning and skill importance
    """
    user = _get_user_from_token(authorization)
    
    try:
        # Get intelligent role matches for comparison
        intelligent_matches = find_intelligent_matches(request.user_skills, top_n=10)
        
        # Find the specific role in intelligent matches
        target_role_match = None
        for match in intelligent_matches:
            if match['role'].lower() == request.role_title.lower():
                target_role_match = match
                break
        
        # Get role requirements from dataset
        role_requirements = get_role_requirements_from_dataset(request.role_title)
        
        if not role_requirements:
            raise HTTPException(status_code=404, detail=f"Role '{request.role_title}' not found in dataset")
        
        # Get skill importance scores for user skills
        user_skill_importance = []
        for skill in request.user_skills:
            importance = get_skill_importance(skill)
            user_skill_importance.append({
                "skill": skill,
                "importance_score": round(importance, 3),
                "priority": "High" if importance > 0.5 else "Medium" if importance > 0.2 else "Low"
            })
        
        # Sort by importance
        user_skill_importance.sort(key=lambda x: x['importance_score'], reverse=True)
        
        # Get skill recommendations
        skill_recommendations = get_skill_recommendations(request.user_skills, request.role_title)
        
        # Enhanced analysis result
        analysis_result = {
            "role_title": request.role_title,
            "intelligent_match_data": target_role_match,
            "user_skill_importance": user_skill_importance,
            "skill_recommendations": skill_recommendations,
            "role_requirements": role_requirements,
            "market_insights": {
                "role_demand": role_requirements.get('job_count', 0),
                "experience_levels": role_requirements.get('experience_levels', []),
                "skill_categories": _categorize_skills(role_requirements.get('required_skills', []))
            }
        }
        
        # Save enhanced analysis
        try:
            analyses_col = get_collection('analyses')
            analysis_doc = {
                'user_id': user.get('user_id'),
                'role_title': request.role_title,
                'user_skills': request.user_skills,
                'analysis_type': 'intelligent',
                'analysis_result': analysis_result,
                'analyzed_at': datetime.utcnow()
            }
            analyses_col.insert_one(analysis_doc)
        except Exception as e:
            print(f"Failed to save intelligent analysis: {e}")
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "insights": [
                f"Your top skill by importance: {user_skill_importance[0]['skill']}" if user_skill_importance else "No skills analyzed",
                f"Intelligent match score: {target_role_match['intelligent_score']}%" if target_role_match else "Role not in top matches",
                f"High priority skills you have: {len([s for s in user_skill_importance if s['priority'] == 'High'])}",
                f"Recommended skills to learn: {len(skill_recommendations.get('high_priority_skills', []))}"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligent analysis failed: {str(e)}")

@router.get("/skill-market-analysis")
async def get_skill_market_analysis(authorization: Optional[str] = Header(None)):
    """
    Get comprehensive skill market analysis using Deep Learning insights
    """
    user = _get_user_from_token(authorization)
    
    try:
        # Get user's skills from database
        users_col = get_collection('users')
        user_doc = users_col.find_one({'_id': user.get('user_id')})
        
        user_skills = []
        if user_doc:
            user_skills = user_doc.get('resume_skills', []) or user_doc.get('skills', [])
        
        if not user_skills:
            return {
                "status": "warning",
                "message": "No skills found. Please upload a resume or add skills manually first.",
                "market_analysis": None
            }
        
        # Get comprehensive skill recommendations
        recommendations = get_skill_recommendations(user_skills)
        
        # Get intelligent role matches
        role_matches = find_intelligent_matches(user_skills, top_n=10)
        
        # Analyze user's skill portfolio
        skill_portfolio = []
        for skill in user_skills:
            importance = get_skill_importance(skill)
            skill_portfolio.append({
                "skill": skill,
                "market_importance": round(importance, 3),
                "category": _get_skill_category(skill),
                "demand_level": "High" if importance > 0.5 else "Medium" if importance > 0.2 else "Low"
            })
        
        skill_portfolio.sort(key=lambda x: x['market_importance'], reverse=True)
        
        return {
            "status": "success",
            "user_skills_analysis": {
                "total_skills": len(user_skills),
                "high_value_skills": len([s for s in skill_portfolio if s['demand_level'] == 'High']),
                "skill_portfolio": skill_portfolio
            },
            "market_recommendations": recommendations,
            "intelligent_role_matches": role_matches,
            "career_insights": {
                "strongest_skill_category": _get_dominant_category(skill_portfolio),
                "recommended_focus_areas": [skill['skill'] for skill in recommendations.get('high_priority_skills', [])[:5]],
                "career_readiness": _assess_career_readiness(skill_portfolio, role_matches)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")

def _get_skill_category(skill: str) -> str:
    """Get category for a single skill"""
    skill_lower = skill.lower()
    
    if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'c#', 'c++', 'php', 'ruby']):
        return "Programming Languages"
    elif any(tech in skill_lower for tech in ['react', 'angular', 'vue', 'node', 'express', 'django']):
        return "Web Technologies"
    elif any(db in skill_lower for db in ['mysql', 'postgresql', 'mongodb', 'redis', 'sql']):
        return "Databases"
    elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'docker', 'kubernetes']):
        return "Cloud & DevOps"
    elif any(ml in skill_lower for ml in ['tensorflow', 'pytorch', 'machine learning', 'deep learning']):
        return "Machine Learning"
    else:
        return "Other"

def _get_dominant_category(skill_portfolio: List[Dict]) -> str:
    """Find the dominant skill category"""
    categories = {}
    for skill in skill_portfolio:
        cat = skill['category']
        categories[cat] = categories.get(cat, 0) + skill['market_importance']
    
    if categories:
        return max(categories.items(), key=lambda x: x[1])[0]
    return "Unknown"

def _assess_career_readiness(skill_portfolio: List[Dict], role_matches: List[Dict]) -> str:
    """Assess overall career readiness"""
    high_value_count = len([s for s in skill_portfolio if s['demand_level'] == 'High'])
    avg_match_score = sum(match['intelligent_score'] for match in role_matches[:5]) / 5 if role_matches else 0
    
    if high_value_count >= 5 and avg_match_score >= 70:
        return "Excellent - Ready for senior roles"
    elif high_value_count >= 3 and avg_match_score >= 50:
        return "Good - Ready for mid-level roles"
    elif high_value_count >= 1 and avg_match_score >= 30:
        return "Developing - Focus on building core skills"
    else:
        return "Entry Level - Build foundational skills"

@router.get("/user-analysis-history")
async def get_user_analysis_history(authorization: Optional[str] = Header(None)):
    """Get user's analysis history"""
    user = _get_user_from_token(authorization)
    user_id = user.get('user_id')
    
    try:
        analyses_col = get_collection('analyses')
        history = list(analyses_col.find({'user_id': user_id}).sort('analyzed_at', -1).limit(20))
        
        # Convert ObjectId to string
        for item in history:
            item['_id'] = str(item['_id'])
            if 'analyzed_at' in item:
                item['analyzed_at'] = item['analyzed_at'].isoformat()
        
        return {
            "status": "success",
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.get("/dataset-stats")
async def get_dataset_statistics():
    """Get statistics about the job dataset"""
    try:
        roles = get_all_roles_from_dataset()
        skills = get_all_skills_from_dataset()
        
        # Experience level distribution
        exp_levels = {}
        for role in roles:
            for level in role['experience_levels']:
                exp_levels[level] = exp_levels.get(level, 0) + role['job_count']
        
        # Top skills
        skill_frequency = {}
        for role in roles:
            for skill in role['skills']:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + role['job_count']
        
        top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "status": "success",
            "total_roles": len(roles),
            "total_skills": len(skills),
            "total_jobs": sum(role['job_count'] for role in roles),
            "experience_levels": exp_levels,
            "top_skills": [{"skill": skill, "frequency": freq} for skill, freq in top_skills],
            "top_roles": [{"title": role['title'], "job_count": role['job_count']} for role in roles[:10]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

def _categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize skills into groups"""
    categories = {
        "Programming Languages": [],
        "Web Technologies": [],
        "Databases": [],
        "Cloud Platforms": [],
        "DevOps Tools": [],
        "Machine Learning": [],
        "Mobile Development": [],
        "Other": []
    }
    
    # Define skill categories
    prog_langs = ['python', 'java', 'javascript', 'c#', 'c++', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift', 'typescript', 'scala', 'r']
    web_tech = ['react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'asp.net', 'html', 'css', 'bootstrap']
    databases = ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server', 'sqlite', 'cassandra', 'elasticsearch']
    cloud = ['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean']
    devops = ['docker', 'kubernetes', 'jenkins', 'git', 'gitlab', 'github', 'terraform', 'ansible']
    ml = ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'keras', 'opencv']
    mobile = ['android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic']
    
    for skill in skills:
        skill_lower = skill.lower()
        categorized = False
        
        if any(lang in skill_lower for lang in prog_langs):
            categories["Programming Languages"].append(skill)
            categorized = True
        elif any(tech in skill_lower for tech in web_tech):
            categories["Web Technologies"].append(skill)
            categorized = True
        elif any(db in skill_lower for db in databases):
            categories["Databases"].append(skill)
            categorized = True
        elif any(cloud_tech in skill_lower for cloud_tech in cloud):
            categories["Cloud Platforms"].append(skill)
            categorized = True
        elif any(devops_tool in skill_lower for devops_tool in devops):
            categories["DevOps Tools"].append(skill)
            categorized = True
        elif any(ml_tool in skill_lower for ml_tool in ml):
            categories["Machine Learning"].append(skill)
            categorized = True
        elif any(mobile_tech in skill_lower for mobile_tech in mobile):
            categories["Mobile Development"].append(skill)
            categorized = True
        
        if not categorized:
            categories["Other"].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

def _generate_recommendations(missing_skills: List[str], match_percentage: float) -> List[str]:
    """Generate recommendations based on missing skills and match percentage"""
    recommendations = []
    
    if match_percentage >= 80:
        recommendations.append("🎉 Excellent match! You're ready to apply for this role.")
        recommendations.append("Consider highlighting your matching skills prominently in your resume.")
    elif match_percentage >= 60:
        recommendations.append("👍 Good match! Focus on learning the missing skills to strengthen your profile.")
        recommendations.append("Consider applying while mentioning your willingness to learn the missing skills.")
    elif match_percentage >= 40:
        recommendations.append("📚 Moderate match. Invest time in learning key missing skills before applying.")
        recommendations.append("Focus on the most common missing skills first.")
    else:
        recommendations.append("🎯 Significant skill gap. Consider this role as a long-term goal.")
        recommendations.append("Start with roles that better match your current skills.")
    
    if missing_skills:
        # Prioritize missing skills
        high_priority = []
        medium_priority = []
        
        for skill in missing_skills[:10]:  # Top 10 missing skills
            skill_lower = skill.lower()
            if any(important in skill_lower for important in ['python', 'java', 'javascript', 'sql', 'react', 'node']):
                high_priority.append(skill)
            else:
                medium_priority.append(skill)
        
        if high_priority:
            recommendations.append(f"🔥 High Priority Skills: {', '.join(high_priority[:3])}")
        if medium_priority:
            recommendations.append(f"📖 Medium Priority Skills: {', '.join(medium_priority[:3])}")
    
    return recommendations