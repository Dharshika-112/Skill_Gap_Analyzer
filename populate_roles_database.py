#!/usr/bin/env python3
"""
Populate roles database with sample career roles for dashboard
"""

import requests
import json
from datetime import datetime

def populate_roles():
    """Populate the roles database with sample data."""
    
    # Sample roles data for dashboard
    roles_data = [
        {
            "roleId": "data-scientist",
            "title": "Data Scientist",
            "cardSubtitle": "Analyze data to extract insights and build predictive models",
            "topSkills": ["Python", "Machine Learning", "SQL", "Statistics", "Pandas"],
            "order": 1,
            "description": "Data Scientists analyze complex data to help organizations make informed decisions.",
            "requirements": ["Bachelor's degree in related field", "3+ years experience", "Strong analytical skills"],
            "salary_range": "$80,000 - $150,000",
            "growth_rate": "22%",
            "job_count": 245
        },
        {
            "roleId": "software-engineer",
            "title": "Software Engineer",
            "cardSubtitle": "Design and develop software applications and systems",
            "topSkills": ["JavaScript", "Python", "React", "Node.js", "Git"],
            "order": 2,
            "description": "Software Engineers create and maintain software applications.",
            "requirements": ["Bachelor's degree in Computer Science", "2+ years experience", "Problem-solving skills"],
            "salary_range": "$70,000 - $140,000",
            "growth_rate": "18%",
            "job_count": 312
        },
        {
            "roleId": "frontend-developer",
            "title": "Frontend Developer",
            "cardSubtitle": "Create user interfaces and enhance user experience",
            "topSkills": ["HTML", "CSS", "JavaScript", "React", "Vue.js"],
            "order": 3,
            "description": "Frontend Developers build the visual and interactive parts of websites.",
            "requirements": ["Portfolio of projects", "2+ years experience", "Design sense"],
            "salary_range": "$60,000 - $120,000",
            "growth_rate": "15%",
            "job_count": 189
        },
        {
            "roleId": "devops-engineer",
            "title": "DevOps Engineer",
            "cardSubtitle": "Bridge development and operations for efficient deployment",
            "topSkills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
            "order": 4,
            "description": "DevOps Engineers streamline software development and deployment processes.",
            "requirements": ["Experience with cloud platforms", "3+ years experience", "Automation skills"],
            "salary_range": "$85,000 - $160,000",
            "growth_rate": "25%",
            "job_count": 156
        },
        {
            "roleId": "cybersecurity-analyst",
            "title": "Cybersecurity Analyst",
            "cardSubtitle": "Protect organizations from cyber threats and vulnerabilities",
            "topSkills": ["Network Security", "Incident Response", "Risk Assessment", "SIEM", "Compliance"],
            "order": 5,
            "description": "Cybersecurity Analysts protect organizations from digital threats.",
            "requirements": ["Security certifications", "2+ years experience", "Analytical mindset"],
            "salary_range": "$75,000 - $135,000",
            "growth_rate": "28%",
            "job_count": 134
        },
        {
            "roleId": "product-manager",
            "title": "Product Manager",
            "cardSubtitle": "Guide product development from conception to launch",
            "topSkills": ["Product Strategy", "Market Research", "Agile", "Analytics", "Communication"],
            "order": 6,
            "description": "Product Managers oversee the development and success of products.",
            "requirements": ["MBA or equivalent experience", "3+ years experience", "Leadership skills"],
            "salary_range": "$90,000 - $170,000",
            "growth_rate": "20%",
            "job_count": 98
        }
    ]
    
    print("🚀 Populating Roles Database...")
    print("=" * 50)
    
    success_count = 0
    
    for role in roles_data:
        try:
            response = requests.post(
                "http://localhost:8004/api/roles",
                json=role,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Added: {role['title']}")
                success_count += 1
            else:
                print(f"❌ Failed to add {role['title']}: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error adding {role['title']}: {e}")
    
    print("=" * 50)
    print(f"📊 Results: {success_count}/{len(roles_data)} roles added successfully")
    
    # Test the roles endpoint
    try:
        response = requests.get("http://localhost:8004/api/roles", timeout=10)
        if response.status_code == 200:
            roles = response.json()
            print(f"✅ Verification: {len(roles)} roles now available in database")
        else:
            print(f"❌ Verification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    populate_roles()