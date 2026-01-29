#!/usr/bin/env python3
"""
Simple Role Management Server
Standalone FastAPI server for role management without complex dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import hashlib
from typing import List, Dict, Any

# Create FastAPI app
app = FastAPI(
    title="CareerBoost AI - Role Management API",
    description="Simple role management system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "skillgap"

def get_db():
    """Get database connection"""
    client = MongoClient(MONGODB_URL)
    return client[DATABASE_NAME]

# Health check
@app.get("/")
async def root():
    return {
        "message": "CareerBoost AI - Role Management API v1.0",
        "status": "running",
        "features": ["Role Management", "Admin Panel", "User Dashboard"]
    }

# USER ENDPOINTS
@app.get("/api/roles")
async def get_active_roles():
    """Get all active roles for user dashboard"""
    try:
        db = get_db()
        roles_collection = db['roles']
        
        cursor = roles_collection.find({"isActive": True}).sort("order", 1)
        roles = []
        
        for doc in cursor:
            roles.append({
                "roleId": doc.get("roleId"),
                "title": doc.get("title"),
                "cardSubtitle": doc.get("cardSubtitle"),
                "topSkills": doc.get("mustHaveSkills", [])[:4],
                "order": doc.get("order", 0)
            })
        
        return roles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch roles: {str(e)}")

@app.get("/api/roles/{role_id}")
async def get_role_details(role_id: str):
    """Get detailed role information by roleId"""
    try:
        db = get_db()
        roles_collection = db['roles']
        
        role_doc = roles_collection.find_one({"roleId": role_id})
        
        if not role_doc:
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
        
        if not role_doc.get('isActive', False):
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' is not available")
        
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
            "extraQuestions": role_doc.get("extraQuestions", []),
            "dropdownOptions": role_doc.get("dropdownOptions", {}),
            "faqs": role_doc.get("faqs", []),
            "interviewTopics": role_doc.get("interviewTopics", []),
            "projectIdeas": role_doc.get("projectIdeas", []),
            "learningResources": role_doc.get("learningResources", []),
            "salaryRange": role_doc.get("salaryRange", {}),
            "experienceLevel": role_doc.get("experienceLevel", ""),
            "remoteWork": role_doc.get("remoteWork", False),
            "industryDemand": role_doc.get("industryDemand", "Medium"),
            "createdAt": str(role_doc["createdAt"]),
            "updatedAt": str(role_doc["updatedAt"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch role details: {str(e)}")

# ADMIN ENDPOINTS
@app.post("/api/admin/auth/login")
async def admin_login(request: dict):
    """Admin login endpoint"""
    try:
        email = request.get('email')
        password = request.get('password')
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        db = get_db()
        admin_collection = db['admin_users']
        
        admin_doc = admin_collection.find_one({"email": email})
        if not admin_doc:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Simple password verification
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if admin_doc['password_hash'] != password_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not admin_doc.get('is_active', False):
            raise HTTPException(status_code=401, detail="Admin account is deactivated")
        
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
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/admin/roles")
async def get_all_roles_admin():
    """Get all roles for admin (including inactive)"""
    try:
        db = get_db()
        roles_collection = db['roles']
        
        cursor = roles_collection.find({}).sort("order", 1)
        roles = []
        
        for doc in cursor:
            roles.append({
                "id": str(doc["_id"]),
                "roleId": doc["roleId"],
                "title": doc["title"],
                "cardSubtitle": doc["cardSubtitle"],
                "isActive": doc["isActive"],
                "order": doc["order"],
                "overview": doc["overview"],
                "responsibilities": doc["responsibilities"],
                "mustHaveSkills": doc["mustHaveSkills"],
                "goodToHaveSkills": doc["goodToHaveSkills"],
                "tools": doc["tools"],
                "extraQuestions": doc.get("extraQuestions", []),
                "dropdownOptions": doc.get("dropdownOptions", {}),
                "faqs": doc.get("faqs", []),
                "interviewTopics": doc.get("interviewTopics", []),
                "projectIdeas": doc.get("projectIdeas", []),
                "learningResources": doc.get("learningResources", []),
                "salaryRange": doc.get("salaryRange", {}),
                "experienceLevel": doc.get("experienceLevel", ""),
                "remoteWork": doc.get("remoteWork", False),
                "industryDemand": doc.get("industryDemand", "Medium"),
                "createdAt": str(doc["createdAt"]),
                "updatedAt": str(doc["updatedAt"])
            })
        
        return roles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch admin roles: {str(e)}")

@app.patch("/api/admin/roles/{role_id}/toggle")
async def toggle_role_status(role_id: str):
    """Toggle role active/inactive status"""
    try:
        db = get_db()
        roles_collection = db['roles']
        
        role_doc = roles_collection.find_one({"roleId": role_id})
        if not role_doc:
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
        
        # Toggle isActive status
        new_status = not role_doc.get('isActive', True)
        
        # Update role
        from datetime import datetime
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
        raise HTTPException(status_code=500, detail=f"Failed to toggle role status: {str(e)}")

@app.post("/api/admin/roles")
async def create_role(request: dict):
    """Create a new role"""
    try:
        db = get_db()
        roles_collection = db['roles']
        
        # Validate required fields
        required_fields = ['roleId', 'title', 'cardSubtitle', 'order', 'overview']
        for field in required_fields:
            if not request.get(field):
                raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
        
        # Check if roleId already exists
        existing_role = roles_collection.find_one({"roleId": request['roleId']})
        if existing_role:
            raise HTTPException(status_code=400, detail=f"Role ID '{request['roleId']}' already exists")
        
        # Prepare role document
        from datetime import datetime
        role_doc = {
            "roleId": request['roleId'],
            "title": request['title'],
            "cardSubtitle": request['cardSubtitle'],
            "isActive": request.get('isActive', True),
            "order": int(request['order']),
            "overview": request['overview'],
            "responsibilities": request.get('responsibilities', []),
            "mustHaveSkills": request.get('mustHaveSkills', []),
            "goodToHaveSkills": request.get('goodToHaveSkills', []),
            "tools": request.get('tools', []),
            # New fields for enhanced features
            "extraQuestions": request.get('extraQuestions', []),
            "dropdownOptions": request.get('dropdownOptions', {}),
            "faqs": request.get('faqs', []),
            "interviewTopics": request.get('interviewTopics', []),
            "projectIdeas": request.get('projectIdeas', []),
            "learningResources": request.get('learningResources', []),
            "salaryRange": request.get('salaryRange', {}),
            "experienceLevel": request.get('experienceLevel', ''),
            "remoteWork": request.get('remoteWork', False),
            "industryDemand": request.get('industryDemand', 'Medium'),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert role
        result = roles_collection.insert_one(role_doc)
        
        # Return created role
        created_role = roles_collection.find_one({"_id": result.inserted_id})
        return {
            "id": str(created_role["_id"]),
            "roleId": created_role["roleId"],
            "title": created_role["title"],
            "cardSubtitle": created_role["cardSubtitle"],
            "isActive": created_role["isActive"],
            "order": created_role["order"],
            "overview": created_role["overview"],
            "responsibilities": created_role["responsibilities"],
            "mustHaveSkills": created_role["mustHaveSkills"],
            "goodToHaveSkills": created_role["goodToHaveSkills"],
            "tools": created_role["tools"],
            "extraQuestions": created_role.get("extraQuestions", []),
            "dropdownOptions": created_role.get("dropdownOptions", {}),
            "faqs": created_role.get("faqs", []),
            "interviewTopics": created_role.get("interviewTopics", []),
            "projectIdeas": created_role.get("projectIdeas", []),
            "learningResources": created_role.get("learningResources", []),
            "salaryRange": created_role.get("salaryRange", {}),
            "experienceLevel": created_role.get("experienceLevel", ""),
            "remoteWork": created_role.get("remoteWork", False),
            "industryDemand": created_role.get("industryDemand", "Medium"),
            "createdAt": str(created_role["createdAt"]),
            "updatedAt": str(created_role["updatedAt"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create role: {str(e)}")

@app.put("/api/admin/roles/{role_id}")
async def update_role(role_id: str, request: dict):
    """Update an existing role"""
    try:
        db = get_db()
        roles_collection = db['roles']
        
        # Check if role exists
        existing_role = roles_collection.find_one({"roleId": role_id})
        if not existing_role:
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
        
        # Prepare update data
        from datetime import datetime
        update_data = {
            "updatedAt": datetime.utcnow()
        }
        
        # Update allowed fields
        allowed_fields = ['title', 'cardSubtitle', 'order', 'overview', 'responsibilities', 
                         'mustHaveSkills', 'goodToHaveSkills', 'tools', 'extraQuestions',
                         'dropdownOptions', 'faqs', 'interviewTopics', 'projectIdeas',
                         'learningResources', 'salaryRange', 'experienceLevel', 'remoteWork',
                         'industryDemand']
        
        for field in allowed_fields:
            if field in request:
                if field == 'order':
                    update_data[field] = int(request[field])
                else:
                    update_data[field] = request[field]
        
        # Update role
        roles_collection.update_one(
            {"roleId": role_id},
            {"$set": update_data}
        )
        
        # Return updated role
        updated_role = roles_collection.find_one({"roleId": role_id})
        return {
            "id": str(updated_role["_id"]),
            "roleId": updated_role["roleId"],
            "title": updated_role["title"],
            "cardSubtitle": updated_role["cardSubtitle"],
            "isActive": updated_role["isActive"],
            "order": updated_role["order"],
            "overview": updated_role["overview"],
            "responsibilities": updated_role["responsibilities"],
            "mustHaveSkills": updated_role["mustHaveSkills"],
            "goodToHaveSkills": updated_role["goodToHaveSkills"],
            "tools": updated_role["tools"],
            "extraQuestions": updated_role.get("extraQuestions", []),
            "dropdownOptions": updated_role.get("dropdownOptions", {}),
            "faqs": updated_role.get("faqs", []),
            "interviewTopics": updated_role.get("interviewTopics", []),
            "projectIdeas": updated_role.get("projectIdeas", []),
            "learningResources": updated_role.get("learningResources", []),
            "salaryRange": updated_role.get("salaryRange", {}),
            "experienceLevel": updated_role.get("experienceLevel", ""),
            "remoteWork": updated_role.get("remoteWork", False),
            "industryDemand": updated_role.get("industryDemand", "Medium"),
            "createdAt": str(updated_role["createdAt"]),
            "updatedAt": str(updated_role["updatedAt"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")

@app.delete("/api/admin/roles/{role_id}")
async def delete_role(role_id: str):
    """Delete a role"""
    try:
        db = get_db()
        roles_collection = db['roles']
        
        result = roles_collection.delete_one({"roleId": role_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' not found")
        
        return JSONResponse({
            "success": True,
            "message": f"Role '{role_id}' deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete role: {str(e)}")

# Database info endpoint
@app.get("/api/database/info")
async def get_database_info():
    """Get database information"""
    try:
        db = get_db()
        roles_count = db['roles'].count_documents({})
        active_roles = db['roles'].count_documents({"isActive": True})
        admin_count = db['admin_users'].count_documents({})
        
        return {
            "database": DATABASE_NAME,
            "collections": {
                "roles": {
                    "total": roles_count,
                    "active": active_roles,
                    "inactive": roles_count - active_roles
                },
                "admin_users": admin_count
            },
            "status": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CareerBoost AI Role Management Server")
    print("=" * 50)
    print("📊 Database: skillgap")
    print("🌐 Server: http://localhost:8004")
    print("📖 API Docs: http://localhost:8004/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        reload=False,
        log_level="info"
    )

# FAQ Management Endpoints
@app.get("/api/admin/faqs")
async def get_all_faqs():
    """Get all FAQs for admin management"""
    try:
        db = get_db()
        faqs_collection = db['faqs']
        
        cursor = faqs_collection.find({}).sort("order", 1)
        faqs = []
        
        for doc in cursor:
            faqs.append({
                "id": str(doc["_id"]),
                "question": doc["question"],
                "answer": doc["answer"],
                "category": doc.get("category", "General"),
                "isActive": doc.get("isActive", True),
                "order": doc.get("order", 0),
                "relatedRoles": doc.get("relatedRoles", []),
                "createdAt": str(doc["createdAt"]),
                "updatedAt": str(doc["updatedAt"])
            })
        
        return faqs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch FAQs: {str(e)}")

@app.post("/api/admin/faqs")
async def create_faq(request: dict):
    """Create a new FAQ"""
    try:
        db = get_db()
        faqs_collection = db['faqs']
        
        # Validate required fields
        if not request.get('question') or not request.get('answer'):
            raise HTTPException(status_code=400, detail="Question and answer are required")
        
        # Prepare FAQ document
        from datetime import datetime
        faq_doc = {
            "question": request['question'],
            "answer": request['answer'],
            "category": request.get('category', 'General'),
            "isActive": request.get('isActive', True),
            "order": request.get('order', 0),
            "relatedRoles": request.get('relatedRoles', []),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert FAQ
        result = faqs_collection.insert_one(faq_doc)
        
        # Return created FAQ
        created_faq = faqs_collection.find_one({"_id": result.inserted_id})
        return {
            "id": str(created_faq["_id"]),
            "question": created_faq["question"],
            "answer": created_faq["answer"],
            "category": created_faq["category"],
            "isActive": created_faq["isActive"],
            "order": created_faq["order"],
            "relatedRoles": created_faq["relatedRoles"],
            "createdAt": str(created_faq["createdAt"]),
            "updatedAt": str(created_faq["updatedAt"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create FAQ: {str(e)}")

@app.put("/api/admin/faqs/{faq_id}")
async def update_faq(faq_id: str, request: dict):
    """Update an existing FAQ"""
    try:
        db = get_db()
        faqs_collection = db['faqs']
        
        # Check if FAQ exists
        from bson import ObjectId
        existing_faq = faqs_collection.find_one({"_id": ObjectId(faq_id)})
        if not existing_faq:
            raise HTTPException(status_code=404, detail=f"FAQ '{faq_id}' not found")
        
        # Prepare update data
        from datetime import datetime
        update_data = {
            "updatedAt": datetime.utcnow()
        }
        
        # Update allowed fields
        allowed_fields = ['question', 'answer', 'category', 'isActive', 'order', 'relatedRoles']
        
        for field in allowed_fields:
            if field in request:
                update_data[field] = request[field]
        
        # Update FAQ
        faqs_collection.update_one(
            {"_id": ObjectId(faq_id)},
            {"$set": update_data}
        )
        
        # Return updated FAQ
        updated_faq = faqs_collection.find_one({"_id": ObjectId(faq_id)})
        return {
            "id": str(updated_faq["_id"]),
            "question": updated_faq["question"],
            "answer": updated_faq["answer"],
            "category": updated_faq["category"],
            "isActive": updated_faq["isActive"],
            "order": updated_faq["order"],
            "relatedRoles": updated_faq["relatedRoles"],
            "createdAt": str(updated_faq["createdAt"]),
            "updatedAt": str(updated_faq["updatedAt"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update FAQ: {str(e)}")

@app.delete("/api/admin/faqs/{faq_id}")
async def delete_faq(faq_id: str):
    """Delete a FAQ"""
    try:
        db = get_db()
        faqs_collection = db['faqs']
        
        from bson import ObjectId
        result = faqs_collection.delete_one({"_id": ObjectId(faq_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"FAQ '{faq_id}' not found")
        
        return JSONResponse({
            "success": True,
            "message": f"FAQ deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete FAQ: {str(e)}")

# User FAQ endpoint
@app.get("/api/faqs")
async def get_active_faqs():
    """Get active FAQs for users"""
    try:
        db = get_db()
        faqs_collection = db['faqs']
        
        cursor = faqs_collection.find({"isActive": True}).sort("order", 1)
        faqs = []
        
        for doc in cursor:
            faqs.append({
                "id": str(doc["_id"]),
                "question": doc["question"],
                "answer": doc["answer"],
                "category": doc.get("category", "General"),
                "relatedRoles": doc.get("relatedRoles", [])
            })
        
        return faqs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch FAQs: {str(e)}")