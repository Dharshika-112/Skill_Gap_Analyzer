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
    'mongodb://localhost:27017'  # Default local
)

MONGODB_DB_NAME = os.getenv(
    'MONGODB_DB_NAME',
    'skill_gap_analyzer'
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
    'user_skills': 'user_skills',
    'user_skill_gaps': 'user_skill_gaps',
    'resumes': 'resumes',
    'dataset_roles': 'dataset_roles',
    'dataset_skills': 'dataset_skills',
    'ml_models': 'ml_models'
}
