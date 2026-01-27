"""
MongoDB Configuration - Supports local and remote connections
"""

import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection Configuration
# Can be local or campus/cloud URL

MONGODB_URL = os.getenv(
    'MONGODB_URL',
    'mongodb://localhost:27017/'  # Your database URL
)

MONGODB_DB_NAME = os.getenv(
    'MONGODB_DB_NAME',
    'skill_gap_analyzer'
)

# JWT Secret Key for token generation
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'your-secret-key-change-this-in-production-use-random-string-here'
)

# Example URLs for different scenarios:
# Local: mongodb://localhost:27017
# Atlas Cloud: mongodb+srv://user:password@cluster.mongodb.net/dbname
# Campus/Custom: mongodb+srv://user:password@campus-mongodb-server.com/dbname

print(f"""
[*] MongoDB Configuration
    URL: {MONGODB_URL}
    Database: {MONGODB_DB_NAME}
    
If using campus MongoDB:
    1. Get connection URL from campus admin
    2. Set environment variable: MONGODB_URL=<your_url>
    3. Or update this file: core/config.py
""")

# Collections
COLLECTIONS = {
    'users': 'users',
    'skills': 'user_skills',  # Add this for backward compatibility
    'user_skills': 'user_skills',
    'user_skill_gaps': 'user_skill_gaps',
    'resumes': 'resumes',
    'analyses': 'analyses',  # Add this for analysis storage
    'ats_analyses': 'ats_analyses',  # Add this for ATS analysis storage
    'dataset_roles': 'dataset_roles',
    'dataset_skills': 'dataset_skills',
    'ml_models': 'ml_models'
}
