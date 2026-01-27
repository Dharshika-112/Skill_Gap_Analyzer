"""Skills routes: list dataset skills, save user's manual skills"""
from fastapi import APIRouter, HTTPException, Header
from typing import List, Optional
from pydantic import BaseModel
from ...core.database import get_collection
from ...services.extended_dataset import get_dataset_skills
from ...core.security import decode_token

router = APIRouter()

class SaveSkillsRequest(BaseModel):
    skills: List[str]

class SaveSkillObjectsRequest(BaseModel):
    # Example:
    # [{"skill":"python","source":"manual"}, {"skill":"sql","source":"resume"}]
    user_skills: List[dict]

def _get_user_id_from_auth(header_auth: Optional[str]):
    if not header_auth:
        return None
    parts = header_auth.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        token = parts[1]
        try:
            payload = decode_token(token)
            return payload.get('user_id')
        except Exception:
            return None
    return None

@router.get("/")
async def list_skills():
    try:
        skills = get_dataset_skills()
        return {"skills": skills, "total": len(skills)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_user_skills(payload: SaveSkillsRequest, authorization: Optional[str] = Header(None)):
    user_id = _get_user_id_from_auth(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Normalize and dedupe
    normalized = []
    seen = set()
    for s in payload.skills:
        s_norm = s.strip()
        if not s_norm:
            continue
        key = s_norm.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append({"skill": s_norm, "source": "manual"})

    col = get_collection('user_skills')
    col.update_one({"user_id": user_id}, {"$set": {"skills": normalized, "updated_at": __import__('datetime').datetime.utcnow()}}, upsert=True)
    return {"status": "success", "saved": len(normalized)}

@router.get("/user-skills")
async def get_user_skills(authorization: Optional[str] = Header(None)):
    user_id = _get_user_id_from_auth(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    col = get_collection('user_skills')
    doc = col.find_one({"user_id": user_id})
    if doc:
        skills = [s.get('skill') if isinstance(s, dict) else s for s in doc.get('skills', [])]
        return {"skills": skills}
    return {"skills": []}

@router.get("/me")
async def get_my_skills(authorization: Optional[str] = Header(None)):
    user_id = _get_user_id_from_auth(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    col = get_collection("user_skills")
    doc = col.find_one({"user_id": user_id}) or {}
    skills = doc.get("skills", [])
    return {"status": "success", "user_id": user_id, "user_skills": skills}

@router.post("/save-objects")
async def save_user_skill_objects(payload: SaveSkillObjectsRequest, authorization: Optional[str] = Header(None)):
    """
    Save skill objects including `source` (manual/resume).
    This supports the requirement:
      "user_skills": [{"skill":"python","source":"manual"}, ...]
    """
    user_id = _get_user_id_from_auth(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Normalize/dedupe by skill name
    seen = set()
    out = []
    for obj in payload.user_skills:
        if not isinstance(obj, dict):
            continue
        skill = str(obj.get("skill") or "").strip()
        if not skill:
            continue
        key = skill.lower()
        if key in seen:
            continue
        seen.add(key)
        source = str(obj.get("source") or "manual").strip().lower()
        if source not in ("manual", "resume"):
            source = "manual"
        out.append({"skill": skill, "source": source})

    col = get_collection("user_skills")
    col.update_one(
        {"user_id": user_id},
        {"$set": {"skills": out, "updated_at": __import__("datetime").datetime.utcnow()}},
        upsert=True,
    )
    return {"status": "success", "saved": len(out)}
