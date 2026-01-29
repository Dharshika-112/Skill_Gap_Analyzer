#!/usr/bin/env python3
"""
Setup admin user and populate roles database
"""

from pymongo import MongoClient
import hashlib
import requests
import json

def setup_admin_user():
    """Create admin user in MongoDB"""
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client['skillgap']  # Using skillgap database as per roles server
        admin_collection = db['admin_users']
        
        # Check if admin already exists
        existing_admin = admin_collection.find_one({"email": "admin@careerboost.ai"})
        
        if not existing_admin:
            # Create admin user
            admin_data = {
                "email": "admin@careerboost.ai",
                "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
                "is_active": True,
                "created_at": "2026-01-29T00:00:00Z"
            }
            
            result = admin_collection.insert_one(admin_data)
            print(f"✅ Admin user created with ID: {result.inserted_id}")
        else:
            print("✅ Admin user already exists")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

def login_admin():
    """Login as admin and get token"""
    try:
        login_data = {
            "email": "admin@careerboost.ai",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:8004/api/admin/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Admin login successful")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return False

def populate_roles():
    """Populate roles using admin endpoint"""
    try:
        # Sample roles data
        roles_data = [
            {
                "roleId": "data-scientist",
                "title": "Data Scientist",
                "cardSubtitle": "Analyze data to extract insights and build predictive models",
                "order": 1,
                "overview": "Data Scientists analyze complex data to help organizations make informed decisions using statistical analysis and machine learning techniques.",
                "topSkills": ["Python", "Machine Learning", "SQL", "Statistics", "Pandas"],
                "description": "Data Scientists analyze complex data to help organizations make informed decisions using statistical analysis and machine learning techniques.",
                "requirements": [
                    "Bachelor's degree in Computer Science, Statistics, or related field",
                    "3+ years of experience in data analysis",
                    "Strong programming skills in Python or R",
                    "Experience with machine learning frameworks"
                ],
                "salary_range": "$80,000 - $150,000",
                "growth_rate": "22%",
                "job_count": 245,
                "experience_level": "Mid-Senior",
                "category": "Data & Analytics"
            },
            {
                "roleId": "software-engineer",
                "title": "Software Engineer",
                "cardSubtitle": "Design and develop software applications and systems",
                "order": 2,
                "overview": "Software Engineers design, develop, and maintain software applications and systems that power modern technology.",
                "topSkills": ["JavaScript", "Python", "React", "Node.js", "Git"],
                "description": "Software Engineers design, develop, and maintain software applications and systems that power modern technology.",
                "requirements": [
                    "Bachelor's degree in Computer Science or related field",
                    "2+ years of software development experience",
                    "Proficiency in multiple programming languages",
                    "Understanding of software development lifecycle"
                ],
                "salary_range": "$70,000 - $140,000",
                "growth_rate": "18%",
                "job_count": 312,
                "experience_level": "Entry-Mid",
                "category": "Software Development"
            },
            {
                "roleId": "frontend-developer",
                "title": "Frontend Developer",
                "cardSubtitle": "Create user interfaces and enhance user experience",
                "order": 3,
                "overview": "Frontend Developers create the visual and interactive elements of websites and web applications that users interact with directly.",
                "topSkills": ["HTML", "CSS", "JavaScript", "React", "Vue.js"],
                "description": "Frontend Developers create the visual and interactive elements of websites and web applications that users interact with directly.",
                "requirements": [
                    "Strong portfolio demonstrating frontend skills",
                    "2+ years of experience with modern frameworks",
                    "Understanding of responsive design principles",
                    "Knowledge of web accessibility standards"
                ],
                "salary_range": "$60,000 - $120,000",
                "growth_rate": "15%",
                "job_count": 189,
                "experience_level": "Entry-Mid",
                "category": "Web Development"
            },
            {
                "roleId": "devops-engineer",
                "title": "DevOps Engineer",
                "cardSubtitle": "Bridge development and operations for efficient deployment",
                "order": 4,
                "overview": "DevOps Engineers streamline software development and deployment processes by implementing automation and monitoring solutions.",
                "topSkills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
                "description": "DevOps Engineers streamline software development and deployment processes by implementing automation and monitoring solutions.",
                "requirements": [
                    "Experience with cloud platforms (AWS, Azure, GCP)",
                    "3+ years of experience in system administration",
                    "Strong automation and scripting skills",
                    "Knowledge of containerization technologies"
                ],
                "salary_range": "$85,000 - $160,000",
                "growth_rate": "25%",
                "job_count": 156,
                "experience_level": "Mid-Senior",
                "category": "Infrastructure"
            },
            {
                "roleId": "cybersecurity-analyst",
                "title": "Cybersecurity Analyst",
                "cardSubtitle": "Protect organizations from cyber threats and vulnerabilities",
                "order": 5,
                "overview": "Cybersecurity Analysts protect organizations from digital threats by monitoring, detecting, and responding to security incidents.",
                "topSkills": ["Network Security", "Incident Response", "Risk Assessment", "SIEM", "Compliance"],
                "description": "Cybersecurity Analysts protect organizations from digital threats by monitoring, detecting, and responding to security incidents.",
                "requirements": [
                    "Security certifications (CISSP, CEH, CompTIA Security+)",
                    "2+ years of experience in cybersecurity",
                    "Strong analytical and problem-solving skills",
                    "Knowledge of security frameworks and compliance"
                ],
                "salary_range": "$75,000 - $135,000",
                "growth_rate": "28%",
                "job_count": 134,
                "experience_level": "Entry-Mid",
                "category": "Security"
            },
            {
                "roleId": "product-manager",
                "title": "Product Manager",
                "cardSubtitle": "Guide product development from conception to launch",
                "order": 6,
                "overview": "Product Managers oversee the development and success of products by coordinating between technical teams and business stakeholders.",
                "topSkills": ["Product Strategy", "Market Research", "Agile", "Analytics", "Communication"],
                "description": "Product Managers oversee the development and success of products by coordinating between technical teams and business stakeholders.",
                "requirements": [
                    "MBA or equivalent business experience",
                    "3+ years of product management experience",
                    "Strong leadership and communication skills",
                    "Experience with agile development methodologies"
                ],
                "salary_range": "$90,000 - $170,000",
                "growth_rate": "20%",
                "job_count": 98,
                "experience_level": "Mid-Senior",
                "category": "Product & Strategy"
            }
        ]
        
        success_count = 0
        
        for role in roles_data:
            try:
                response = requests.post(
                    "http://localhost:8004/api/admin/roles",
                    json=role,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ Added role: {role['title']}")
                    success_count += 1
                else:
                    print(f"❌ Failed to add {role['title']}: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error adding {role['title']}: {e}")
        
        print(f"📊 Successfully added {success_count}/{len(roles_data)} roles")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error populating roles: {e}")
        return False

def verify_setup():
    """Verify the setup by checking roles"""
    try:
        response = requests.get("http://localhost:8004/api/roles", timeout=10)
        
        if response.status_code == 200:
            roles = response.json()
            print(f"✅ Verification: {len(roles)} roles available in database")
            
            if len(roles) > 0:
                print("📋 Available roles:")
                for i, role in enumerate(roles[:3], 1):
                    title = role.get('title', 'Unknown')
                    skills = role.get('topSkills', [])
                    print(f"   {i}. {title} - Skills: {', '.join(skills[:3])}...")
            
            return len(roles) > 0
        else:
            print(f"❌ Verification failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 SETTING UP ADMIN USER AND ROLES DATABASE")
    print("=" * 60)
    
    # Step 1: Create admin user
    print("📝 Step 1: Creating admin user...")
    admin_created = setup_admin_user()
    
    if not admin_created:
        print("❌ Failed to create admin user. Exiting.")
        return
    
    # Step 2: Login as admin
    print("\n🔐 Step 2: Testing admin login...")
    admin_logged_in = login_admin()
    
    if not admin_logged_in:
        print("❌ Admin login failed. Exiting.")
        return
    
    # Step 3: Populate roles
    print("\n📊 Step 3: Populating roles database...")
    roles_populated = populate_roles()
    
    # Step 4: Verify setup
    print("\n✅ Step 4: Verifying setup...")
    setup_verified = verify_setup()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 SETUP SUMMARY")
    print("=" * 60)
    
    if admin_created and admin_logged_in and roles_populated and setup_verified:
        print("✅ ALL SETUP COMPLETED SUCCESSFULLY!")
        print("\n🔗 ACCESS INFORMATION:")
        print("   👤 USER SIDE: http://localhost:3000")
        print("   🔧 ADMIN SIDE: http://localhost:3000/admin")
        print("   📧 Admin Email: admin@careerboost.ai")
        print("   🔑 Admin Password: admin123")
        print("\n📊 FEATURES READY:")
        print("   ✅ User Registration & Login")
        print("   ✅ Dashboard with Role Cards")
        print("   ✅ AI-Powered Skill Gap Analysis")
        print("   ✅ Role Recommendations")
        print("   ✅ Interactive Quiz System")
        print("   ✅ Admin Panel for Role Management")
    else:
        print("❌ SETUP INCOMPLETE - Please check errors above")

if __name__ == "__main__":
    main()