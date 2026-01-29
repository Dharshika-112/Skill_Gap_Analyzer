"""
MongoDB Configuration for CareerBoost AI
Complete database setup with structured collections
"""

import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection Configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'careerboost_ai')

# JWT Secret Key for token generation
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'careerboost-ai-secret-key-change-in-production-2026'
)

print(f"""
[*] CareerBoost AI - Database Configuration
    MongoDB URL: {MONGODB_URL}
    Database: {MONGODB_DB_NAME}
    
💡 Database Structure:
    ✅ users - User accounts and authentication
    ✅ user_profiles - Detailed profile information
    ✅ user_skills - User skills and competencies
    ✅ analysis_history - Analysis results and history
    ✅ resume_uploads - Resume files and parsed data
    ✅ job_roles - Job dataset from CSV
    ✅ ats_training_data - ATS training dataset
    ✅ skill_gap_results - Skill gap analysis results
    ✅ resume_scores - Resume scoring results
    
🚀 To setup database: python backend/app/core/mongodb_setup.py
""")

# Collections mapping for the application
COLLECTIONS = {
    'users': 'users',
    'user_profiles': 'user_profiles', 
    'user_skills': 'user_skills',
    'analysis_history': 'analysis_history',
    'resume_uploads': 'resume_uploads',
    'job_roles': 'job_roles',
    'job_skills': 'job_skills',
    'ats_training_data': 'ats_training_data',
    'skill_gap_results': 'skill_gap_results',
    'resume_scores': 'resume_scores',
    
    # Legacy mappings for compatibility
    'skills': 'user_skills',
    'analyses': 'analysis_history',
    'resumes': 'resume_uploads',
    'ats_analyses': 'resume_scores',
    'dataset_roles': 'job_roles',
    'dataset_skills': 'job_skills',
    'ml_models': 'ml_models'
}