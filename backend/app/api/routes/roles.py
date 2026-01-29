"""
Role Management API Routes
Handles both user and admin role operations
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient

from models.role import (
    RoleCreate, RoleUpdate, RoleResponse, RoleCardResponse,
    AdminLogin, AdminResponse
)

router = APIRouter()

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017/"
SKILLGAP_DB = "skillgap"

def get_skillgap_db():
    """Get skillgap database connection"""
    client = MongoClient(MONGODB_URL)
    return client[SKILLGAP_DB]

def get_roles_collection():
    """Get roles collection"""
    db = get_skillgap_db()
    return db['roles']

def get_admin_collection():
    """Get admin users collection"""
    db = get_skillgap_db()
    return db['admin_users']

# Helper functions
def role_doc_to_response(doc) -> RoleResponse:
    """Convert MongoDB document to RoleResponse"""
    return RoleResponse(
        id=str(doc['_id']),
        roleId=doc['roleId'],
        title=doc['title'],
        cardSubtitle=doc['cardSubtitle'],
        isActive=doc['isActive'],
        order=doc['order'],
        overview=doc['overview'],
        responsibilities=doc['responsibilities'],
        mustHaveSkills=doc['mustHaveSkills'],
        goodToHaveSkills=doc['goodToHaveSkills'],
        tools=doc['tools'],
        createdAt=str(doc['createdAt']),
        updatedAt=str(doc['updatedAt'])
    )

def role_doc_to_card(doc) -> RoleCardResponse:
    """Convert MongoDB document to RoleCardResponse for dashboard"""
    # Get top 4 must-have skills for card display
    top_skills = doc['mustHaveSkills'][:4] if doc['mustHaveSkills'] else []
    
    return RoleCardResponse(
        roleId=doc['roleId'],
        title=doc['title'],
        cardSubtitle=doc['cardSubtitle'],
        topSkills=top_skills,
        order=doc['order']
    )

# USER APIs (Public)
@router.get("/api/roles", response_model=List[RoleCardResponse])
async def get_active_roles():
    """Get all active roles for user dashboard"""
    try:
        roles_collection = get_roles_collection()
        
        # Find active roles, sorted by order
        cursor = roles_collection.find(
            {"isActive": True}
        ).sort("order", 1)
        
        roles = []
        for doc in cursor:
            roles.append(role_doc_to_card(doc))
        
        return roles
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch roles: {str(e)}"
        )

@router.get("/api/roles/{role_id}", response_model=RoleResponse)
async def get_role_details(role_id: str):
    """Get detailed role information by roleId"""
    try:
        roles_collection = get_roles_collection()
        
        # Find role by roleId
        role_doc = roles_collection.find_one({"roleId": role_id})
        
        if not role_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Role '{role_id}' not found"
            )
        
        if not role_doc.get('isActive', False):
            raise HTTPException(
                status_code=404,
                detail=f"Role '{role_id}' is not available"
            )
        
        return role_doc_to_response(role_doc)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch role details: {str(e)}"
        )

# ADMIN APIs (Protected)
@router.post("/api/admin/auth/login")
async def admin_login(login_data: AdminLogin):
    """Admin login endpoint"""
    try:
        import hashlib
        
        admin_collection = get_admin_collection()
        
        # Find admin by email
        admin_doc = admin_collection.find_one({"email": login_data.email})
        
        if not admin_doc:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Verify password (simple hash for now)
        password_hash = hashlib.sha256(login_data.password.encode()).hexdigest()
        
        if admin_doc['password_hash'] != password_hash:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        if not admin_doc.get('is_active', False):
            raise HTTPException(
                status_code=401,
                detail="Admin account is deactivated"
            )
        
        # Return admin info (in real app, would return JWT token)
        return JSONResponse({
            "success": True,
            "admin": {
                "id": str(admin_doc['_id']),
                "email": admin_doc['email'],
                "is_active": admin_doc['is_active']
            },
            "message": "Login successful"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/api/admin/roles", response_model=List[RoleResponse])
async def get_all_roles_admin():
    """Get all roles for admin (including inactive)"""
    try:
        roles_collection = get_roles_collection()
        
        # Get all roles, sorted by order
        cursor = roles_collection.find({}).sort("order", 1)
        
        roles = []
        for doc in cursor:
            roles.append(role_doc_to_response(doc))
        
        return roles
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch admin roles: {str(e)}"
        )

@router.post("/api/admin/roles", response_model=RoleResponse)
async def create_role(role_data: RoleCreate):
    """Create a new role"""
    try:
        roles_collection = get_roles_collection()
        
        # Check if roleId already exists
        existing = roles_collection.find_one({"roleId": role_data.roleId})
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Role with ID '{role_data.roleId}' already exists"
            )
        
        # Create role document
        now = datetime.utcnow()
        role_doc = {
            **role_data.dict(),
            "createdAt": now,
            "updatedAt": now
        }
        
        # Insert role
        result = roles_collection.insert_one(role_doc)
        
        # Get created role
        created_role = roles_collection.find_one({"_id": result.inserted_id})
        
        return role_doc_to_response(created_role)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create role: {str(e)}"
        )

@router.put("/api/admin/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: str, role_data: RoleUpdate):
    """Update an existing role"""
    try:
        roles_collection = get_roles_collection()
        
        # Find role by roleId
        existing_role = roles_collection.find_one({"roleId": role_id})
        if not existing_role:
            raise HTTPException(
                status_code=404,
                detail=f"Role '{role_id}' not found"
            )
        
        # Prepare update data (only include non-None fields)
        update_data = {k: v for k, v in role_data.dict().items() if v is not None}
        update_data["updatedAt"] = datetime.utcnow()
        
        # Update role
        roles_collection.update_one(
            {"roleId": role_id},
            {"$set": update_data}
        )
        
        # Get updated role
        updated_role = roles_collection.find_one({"roleId": role_id})
        
        return role_doc_to_response(updated_role)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update role: {str(e)}"
        )

@router.delete("/api/admin/roles/{role_id}")
async def delete_role(role_id: str):
    """Delete a role"""
    try:
        roles_collection = get_roles_collection()
        
        # Find and delete role
        result = roles_collection.delete_one({"roleId": role_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Role '{role_id}' not found"
            )
        
        return JSONResponse({
            "success": True,
            "message": f"Role '{role_id}' deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete role: {str(e)}"
        )

@router.patch("/api/admin/roles/{role_id}/toggle")
async def toggle_role_status(role_id: str):
    """Toggle role active/inactive status"""
    try:
        roles_collection = get_roles_collection()
        
        # Find role
        role_doc = roles_collection.find_one({"roleId": role_id})
        if not role_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Role '{role_id}' not found"
            )
        
        # Toggle isActive status
        new_status = not role_doc.get('isActive', True)
        
        # Update role
        roles_collection.update_one(
            {"roleId": role_id},
            {
                "$set": {
                    "isActive": new_status,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return JSONResponse({
            "success": True,
            "roleId": role_id,
            "isActive": new_status,
            "message": f"Role '{role_id}' {'activated' if new_status else 'deactivated'}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to toggle role status: {str(e)}"
        )