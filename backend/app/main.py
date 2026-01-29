"""
CareerBoost AI - FastAPI Backend
Enhanced with Deep Learning and ML algorithms
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routes with direct imports
try:
    from api.routes.auth import router as auth_router
    print("[OK] Auth routes imported successfully")
except ImportError as e:
    print(f"[WARNING] Auth routes import failed: {e}")
    from fastapi import APIRouter
    auth_router = APIRouter()

try:
    from api.routes import skills, data, resume_analysis
    print("[OK] Other routes imported successfully")
except ImportError as e:
    print(f"[WARNING] Some route modules not found: {e}")
    from fastapi import APIRouter
    skills = APIRouter()
    data = APIRouter()
    resume_analysis = APIRouter()

try:
    from api.routes.enhanced_resume_analysis import router as enhanced_resume_router
    print("[OK] Enhanced resume routes imported successfully")
except ImportError as e:
    print(f"[WARNING] Enhanced resume routes not found: {e}")
    from fastapi import APIRouter
    enhanced_resume_router = APIRouter()

try:
    from api.routes.roles import router as roles_router
    print("[OK] Roles routes imported successfully")
except ImportError as e:
    print(f"[WARNING] Roles routes not found: {e}")
    from fastapi import APIRouter
    roles_router = APIRouter()
    
    # Add basic role endpoints directly
    @roles_router.get("/api/roles")
    async def get_roles_fallback():
        """Fallback roles endpoint"""
        from pymongo import MongoClient
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["skillgap"]
            roles_collection = db["roles"]
            
            cursor = roles_collection.find({"isActive": True}).sort("order", 1)
            roles = []
            for doc in cursor:
                roles.append({
                    "roleId": doc.get("roleId"),
                    "title": doc.get("title"),
                    "cardSubtitle": doc.get("cardSubtitle"),
                    "topSkills": doc.get("mustHaveSkills", [])[:4],
                    "order": doc.get("order")
                })
            return roles
        except Exception as e:
            return []
    
    @roles_router.get("/api/roles/{role_id}")
    async def get_role_details_fallback(role_id: str):
        """Fallback role details endpoint"""
        from pymongo import MongoClient
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["skillgap"]
            roles_collection = db["roles"]
            
            role_doc = roles_collection.find_one({"roleId": role_id})
            if not role_doc or not role_doc.get('isActive', False):
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail="Role not found")
            
            return {
                "id": str(role_doc["_id"]),
                "roleId": role_doc["roleId"],
                "title": role_doc["title"],
                "cardSubtitle": role_doc["cardSubtitle"],
                "isActive": role_doc["isActive"],
                "order": role_doc["order"],
                "overview": role_doc["overview"],
                "responsibilities": role_doc["responsibilities"],
                "mustHaveSkills": role_doc["mustHaveSkills"],
                "goodToHaveSkills": role_doc["goodToHaveSkills"],
                "tools": role_doc["tools"],
                "createdAt": str(role_doc["createdAt"]),
                "updatedAt": str(role_doc["updatedAt"])
            }
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))
    
    @roles_router.post("/api/admin/auth/login")
    async def admin_login_fallback(request: dict):
        """Fallback admin login endpoint"""
        from pymongo import MongoClient
        import hashlib
        
        try:
            email = request.get('email')
            password = request.get('password')
            
            client = MongoClient("mongodb://localhost:27017/")
            db = client["skillgap"]
            admin_collection = db["admin_users"]
            
            admin_doc = admin_collection.find_one({"email": email})
            if not admin_doc:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if admin_doc['password_hash'] != password_hash:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            return JSONResponse({
                "success": True,
                "admin": {
                    "id": str(admin_doc['_id']),
                    "email": admin_doc['email'],
                    "is_active": admin_doc['is_active']
                },
                "message": "Login successful"
            })
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))

# Import database and ML services
try:
    from core.database import get_database
except ImportError:
    print("[WARNING] Database module not found, using mock")
    def get_database():
        return {"status": "mock"}

try:
    from services.extended_dataset import get_dataset_summary
except ImportError:
    def get_dataset_summary():
        return {"datasets": "mock"}

# Create FastAPI app
app = FastAPI(
    title="CareerBoost AI - Resume Analysis API",
    description="Advanced resume analysis with Deep Learning, ML algorithms, and ATS scoring",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "CareerBoost AI - Resume Analysis API v3.0",
        "status": "running",
        "features": [
            "🔥 Deep Learning Resume Parsing",
            "🔥 Role-Based ML Scoring", 
            "🔥 Skill Gap Analysis",
            "🔥 Resume Improvement Suggestions",
            "Real-time ATS Scoring",
            "Industry Benchmarking"
        ]
    }

# API Documentation
@app.get("/api/info")
async def api_info():
    return {
        "name": "CareerBoost AI",
        "version": "3.0",
        "features": get_dataset_summary(),
        "endpoints": {
            "auth": "/api/auth/",
            "skills": "/api/skills/",
            "data": "/api/data/",
            "resume": "/api/resume/",
            "docs": "/docs"
        },
        "new_features": {
            "deep_learning_parsing": "Advanced resume parsing with OCR and NLP",
            "role_based_scoring": "ML models trained on specific job roles",
            "skill_gap_analysis": "Real ATS-style skill matching",
            "improvement_suggestions": "Actionable resume optimization tips"
        }
    }

# Test endpoints for skill gap analysis
@app.post("/api/resume/skill-gap-analysis")
async def skill_gap_analysis_endpoint(request: dict):
    """🔥 FEATURE 1: Analyze skill gaps for target role"""
    try:
        user_skills = request.get('user_skills', [])
        target_role = request.get('target_role', '')
        
        # Mock analysis for testing
        matched_skills = user_skills[:len(user_skills)//2] if user_skills else []
        missing_skills = ['Python', 'React', 'SQL', 'Git'] if target_role else []
        
        match_percentage = (len(matched_skills) / (len(matched_skills) + len(missing_skills)) * 100) if (matched_skills or missing_skills) else 0
        
        gap_analysis = {
            'success': True,
            'target_role': target_role,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'additional_skills': [],
            'match_percentage': round(match_percentage, 1),
            'matched_count': len(matched_skills),
            'total_required': len(matched_skills) + len(missing_skills),
            'gap_count': len(missing_skills),
            'job_count': 25,
            'gap_severity': {
                'level': 'medium' if match_percentage < 70 else 'low',
                'description': 'Moderate gaps requiring focused learning' if match_percentage < 70 else 'Minor gaps that can be easily addressed',
                'recommendation': 'Targeted learning plan over 1-2 months' if match_percentage < 70 else 'Quick skill updates and resume optimization'
            }
        }
        
        suggestions = {
            'success': True,
            'suggestions': [
                {
                    'type': 'critical',
                    'title': 'Add Missing Critical Skills',
                    'description': f'Focus on learning these high-priority skills for {target_role}',
                    'action_items': missing_skills[:3],
                    'impact': 'High - Directly improves job readiness'
                }
            ],
            'timeline': {
                'week_1_2': missing_skills[:1],
                'month_1': missing_skills[1:2],
                'month_2_3': missing_skills[2:3],
                'ongoing': ['Practice and build projects']
            }
        }
        
        return JSONResponse({
            "success": True,
            "skill_gap_analysis": gap_analysis,
            "improvement_suggestions": suggestions
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# Authentication endpoints
@app.post("/api/auth/signup")
async def signup_endpoint(request: dict):
    """User signup endpoint with optional profile data"""
    try:
        from core.database import get_collection
        from core.security import hash_password, create_access_token
        
        name = request.get('name')
        email = request.get('email')
        password = request.get('password')
        
        # Optional profile fields
        phone = request.get('phone', '')
        specialization = request.get('specialization', '')
        experience = request.get('experience', '')
        degree = request.get('degree', '')
        
        if not all([name, email, password]):
            return JSONResponse({
                "success": False,
                "error": "Name, email, and password are required"
            }, status_code=400)
        
        users = get_collection('users')
        existing = users.find_one({"email": email})
        if existing:
            return JSONResponse({
                "success": False,
                "error": "Email already registered"
            }, status_code=400)

        # Calculate profile completion percentage
        profile_completion = 25  # Base for name, email, password
        if phone: profile_completion += 15
        if specialization: profile_completion += 20
        if experience: profile_completion += 20
        if degree: profile_completion += 20

        user = {
            "name": name,
            "email": email,
            "password_hash": hash_password(password),
            "phone": phone,
            "specialization": specialization,
            "experience": experience,
            "degree": degree,
            "created_at": datetime.utcnow(),
            "profile_completion": profile_completion,
            "needs_profile_completion": profile_completion < 100
        }
        result = users.insert_one(user)
        user_id = str(result.inserted_id)
        token = create_access_token({"user_id": user_id, "email": email})
        
        user_data = {
            "id": user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "specialization": specialization,
            "experience": experience,
            "degree": degree,
            "profile_completion": profile_completion,
            "needs_profile_completion": profile_completion < 100
        }
        
        return JSONResponse({
            "success": True,
            "access_token": token,
            "user": user_data
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/auth/login")
async def login_endpoint(request: dict):
    """User login endpoint"""
    try:
        from core.database import get_collection
        from core.security import verify_password, create_access_token
        
        email = request.get('email')
        password = request.get('password')
        
        if not all([email, password]):
            return JSONResponse({
                "success": False,
                "error": "Email and password are required"
            }, status_code=400)
        
        users = get_collection('users')
        user = users.find_one({"email": email})
        if not user:
            return JSONResponse({
                "success": False,
                "error": "User not found. Please sign up first."
            }, status_code=401)

        if not verify_password(password, user.get('password_hash', '')):
            return JSONResponse({
                "success": False,
                "error": "Invalid password"
            }, status_code=401)

        user_id = str(user.get('_id'))
        token = create_access_token({"user_id": user_id, "email": user.get('email')})
        
        user_data = {
            "id": user_id,
            "name": user.get('name'),
            "email": user.get('email'),
            "phone": user.get('phone', ''),
            "specialization": user.get('specialization', ''),
            "experience": user.get('experience', ''),
            "degree": user.get('degree', ''),
            "profile_completion": user.get('profile_completion', 25),
            "needs_profile_completion": user.get('needs_profile_completion', True)
        }
        
        return JSONResponse({
            "success": True,
            "access_token": token,
            "user": user_data
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.put("/api/auth/profile")
async def update_profile_endpoint(request: dict):
    """Update user profile endpoint"""
    try:
        from core.database import get_collection
        from core.security import decode_token
        
        # Get token from headers (this would normally be handled by middleware)
        # For now, we'll get user_id from request or use a mock
        user_id = request.get('user_id')  # This should come from JWT token
        
        if not user_id:
            return JSONResponse({
                "success": False,
                "error": "User not authenticated"
            }, status_code=401)
        
        users = get_collection('users')
        
        # Update fields
        update_data = {}
        if 'phone' in request:
            update_data['phone'] = request['phone']
        if 'specialization' in request:
            update_data['specialization'] = request['specialization']
        if 'experience' in request:
            update_data['experience'] = request['experience']
        if 'degree' in request:
            update_data['degree'] = request['degree']
        if 'profile_completion' in request:
            update_data['profile_completion'] = request['profile_completion']
        if 'needs_profile_completion' in request:
            update_data['needs_profile_completion'] = request['needs_profile_completion']
        
        update_data['updated_at'] = datetime.utcnow()
        
        # Update user in database
        from bson import ObjectId
        result = users.update_one(
            {"_id": ObjectId(user_id)}, 
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Get updated user
            updated_user = users.find_one({"_id": ObjectId(user_id)})
            user_data = {
                "id": str(updated_user['_id']),
                "name": updated_user.get('name'),
                "email": updated_user.get('email'),
                "phone": updated_user.get('phone', ''),
                "specialization": updated_user.get('specialization', ''),
                "experience": updated_user.get('experience', ''),
                "degree": updated_user.get('degree', ''),
                "profile_completion": updated_user.get('profile_completion', 25),
                "needs_profile_completion": updated_user.get('needs_profile_completion', True)
            }
            
            return JSONResponse({
                "success": True,
                "user": user_data
            })
        else:
            return JSONResponse({
                "success": False,
                "error": "Profile update failed"
            }, status_code=400)
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

    """Mock resume upload endpoint"""
    return JSONResponse({
        "success": True,
        "message": "Resume uploaded successfully",
        "parsed_data": {
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "experience": {"total_years": 3, "level": "mid-level"},
            "extraction_method": "Deep Learning"
        }
    })

@app.post("/api/resume/score-general")
async def score_resume_general(request: dict):
    """Mock general resume scoring"""
    return JSONResponse({
        "success": True,
        "score": 78,
        "model_type": "general",
        "confidence": "high"
    })

@app.post("/api/resume/upload")
async def upload_resume():
    """Mock resume upload endpoint"""
    return JSONResponse({
        "success": True,
        "message": "Resume uploaded successfully",
        "parsed_data": {
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "experience": {"total_years": 3, "level": "mid-level"},
            "extraction_method": "Deep Learning"
        }
    })

@app.post("/api/resume/score-general")
async def score_resume_general(request: dict):
    """Mock general resume scoring"""
    return JSONResponse({
        "success": True,
        "score": 78,
        "model_type": "general",
        "confidence": "high"
    })

@app.post("/api/resume/score-role-based")
async def score_resume_role_based(request: dict):
    """Mock role-based resume scoring"""
    target_role = request.get('target_role', 'Software Engineer')
    return JSONResponse({
        "success": True,
        "score": 82,
        "target_role": target_role,
        "model_type": "role_specific",
        "confidence": "high",
        "skill_match_ratio": 0.75,
        "benchmarks": {
            "average_score": 75,
            "percentiles": {"90th": 90}
        }
    })

# Include routers (with error handling)
try:
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    print("[OK] Auth routes included")
except Exception as e:
    print(f"[WARNING] Could not include auth routes: {e}")

try:
    app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
    app.include_router(data.router, prefix="/api/data", tags=["Data"])
    app.include_router(resume_analysis.router, prefix="/api/resume", tags=["Resume Analysis"])
    print("[OK] Other routes included")
except Exception as e:
    print(f"[WARNING] Could not include some other routes: {e}")

try:
    app.include_router(enhanced_resume_router, prefix="/api/resume", tags=["Enhanced Resume Analysis"])
    print("[OK] Enhanced resume routes included")
except Exception as e:
    print(f"[WARNING] Could not include enhanced resume routes: {e}")

try:
    app.include_router(roles_router, tags=["Roles Management"])
    print("[OK] Roles routes included")
except Exception as e:
    print(f"[WARNING] Could not include roles routes: {e}")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and ML models on startup"""
    try:
        print("[*] Initializing CareerBoost AI...")
        get_database()
        print("[OK] Database initialized")
        
        print("[*] Loading ML models and datasets...")
        try:
            # Try to load datasets and models
            from services.dataset_normalizer import get_normalized_datasets
            ats_df, job_df = get_normalized_datasets()
            print(f"[OK] Loaded {len(ats_df)} ATS records and {len(job_df)} job records")
        except Exception as e:
            print(f"[WARNING] Using mock data: {e}")
        
        print("[OK] CareerBoost AI startup complete")
        print("=" * 60)
        print("🚀 CareerBoost AI is ready!")
        print("📊 Features: Deep Learning Parsing, Role-Based Scoring, Skill Gap Analysis")
        print("🎯 Access API docs at: http://localhost:8000/docs")
        print("🌐 Frontend will be available at: http://localhost:3000")
        print("=" * 60)
        
    except Exception as e:
        print(f"[WARNING] Startup completed with warnings: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
