"""Authentication routes: signup, login, profile"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from ...core.database import get_collection
from ...core.security import hash_password, verify_password, create_access_token, decode_token, get_user_by_email
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel

router = APIRouter()

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    resume_path: Optional[str] = None
    # Stored experience structure:
    # { "type": "internship" | "training" | "fresher" | "experienced" | "unknown", "years": 0.5 }
    experience: Optional[dict] = None

@router.post("/signup")
async def signup(req: SignupRequest):
    users = get_collection('users')
    existing = users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "name": req.name,
        "email": req.email,
        "password_hash": hash_password(req.password),
        "created_at": datetime.utcnow()
    }
    result = users.insert_one(user)
    user_id = str(result.inserted_id)
    token = create_access_token({"user_id": user_id, "email": req.email})
    return {"status": "success", "user_id": user_id, "access_token": token}

@router.post("/login")
async def login(req: LoginRequest):
    users = get_collection('users')
    user = users.find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(req.password, user.get('password_hash', '')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(user.get('_id'))
    token = create_access_token({"user_id": user_id, "email": user.get('email')})
    return {"status": "success", "access_token": token, "user_id": user_id}

def _get_token_from_header(authorization: Optional[str]):
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    return None

@router.get("/me")
async def me(authorization: Optional[str] = Header(None)):
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_email(payload.get('email'))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": str(user.get('_id')),
        "name": user.get('name'),
        "email": user.get('email'),
        "created_at": user.get('created_at'),
        "resume_path": user.get("resume_path"),
        "experience": user.get("experience", {})
    }

@router.put("/me")
async def update_me(payload: ProfileUpdateRequest, authorization: Optional[str] = Header(None)):
    """Update basic profile fields (name/resume_path/experience)."""
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        tok = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = tok.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    users = get_collection("users")
    user = users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update = {}
    if payload.name is not None:
        update["name"] = payload.name.strip()
    if payload.resume_path is not None:
        update["resume_path"] = payload.resume_path
    if payload.experience is not None:
        update["experience"] = payload.experience

    if not update:
        return {"status": "success", "updated": False}

    update["updated_at"] = datetime.utcnow()
    users.update_one({"_id": user["_id"]}, {"$set": update})

    # Return fresh profile
    user2 = users.find_one({"_id": user["_id"]})
    return {
        "status": "success",
        "user": {
            "user_id": str(user2.get("_id")),
            "name": user2.get("name"),
            "email": user2.get("email"),
            "created_at": user2.get("created_at"),
            "resume_path": user2.get("resume_path"),
            "experience": user2.get("experience", {}),
        },
    }

@router.post("/update-profile")
async def update_profile_post(payload: ProfileUpdateRequest, authorization: Optional[str] = Header(None)):
    """POST version for frontend compatibility"""
    return await update_me(payload, authorization)
