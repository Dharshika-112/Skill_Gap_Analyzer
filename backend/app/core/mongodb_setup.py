"""
MongoDB Database Setup for CareerBoost AI
Complete database schema and initialization
"""

from pymongo import MongoClient
from datetime import datetime
import json
import os
from pathlib import Path

# MongoDB Configuration
MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "careerboost_ai"

class CareerBoostDatabase:
    """Complete MongoDB setup for CareerBoost AI"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collections = {}
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(MONGODB_URL)
            # Test connection
            self.client.server_info()
            self.db = self.client[DATABASE_NAME]
            print(f"✅ Connected to MongoDB: {MONGODB_URL}")
            print(f"📊 Database: {DATABASE_NAME}")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("💡 Please ensure MongoDB is running on localhost:27017")
            return False
    
    def create_collections(self):
        """Create all required collections with proper schema"""
        
        # Collection definitions
        collections_schema = {
            'users': {
                'description': 'User accounts and profiles',
                'indexes': ['email'],
                'unique_indexes': ['email']
            },
            'user_profiles': {
                'description': 'Detailed user profile information',
                'indexes': ['user_id'],
                'unique_indexes': ['user_id']
            },
            'user_skills': {
                'description': 'User skills and competencies',
                'indexes': ['user_id', 'skill_name']
            },
            'analysis_history': {
                'description': 'User analysis history and results',
                'indexes': ['user_id', 'analysis_type', 'created_at']
            },
            'resume_uploads': {
                'description': 'Uploaded resumes and parsed data',
                'indexes': ['user_id', 'upload_date']
            },
            'job_roles': {
                'description': 'Job roles from dataset',
                'indexes': ['title', 'category', 'experience_level']
            },
            'job_skills': {
                'description': 'Skills required for job roles',
                'indexes': ['job_role_id', 'skill_name', 'importance']
            },
            'ats_training_data': {
                'description': 'ATS training dataset',
                'indexes': ['job_role', 'ats_score']
            },
            'skill_gap_results': {
                'description': 'Skill gap analysis results',
                'indexes': ['user_id', 'target_role', 'analysis_date']
            },
            'resume_scores': {
                'description': 'Resume scoring results',
                'indexes': ['user_id', 'score_type', 'score_date']
            }
        }
        
        print("\n🏗️  Creating collections and indexes...")
        
        for collection_name, schema in collections_schema.items():
            # Create collection
            if collection_name not in self.db.list_collection_names():
                self.db.create_collection(collection_name)
                print(f"   ✅ Created collection: {collection_name}")
            else:
                print(f"   ℹ️  Collection exists: {collection_name}")
            
            # Store collection reference
            self.collections[collection_name] = self.db[collection_name]
            
            # Create indexes
            try:
                for index_field in schema.get('indexes', []):
                    self.collections[collection_name].create_index(index_field)
                
                for unique_index in schema.get('unique_indexes', []):
                    self.collections[collection_name].create_index(unique_index, unique=True)
                    
            except Exception as e:
                print(f"   ⚠️  Index creation warning for {collection_name}: {e}")
        
        print("✅ All collections created successfully!")
    
    def insert_sample_data(self):
        """Insert sample data for testing"""
        print("\n📝 Inserting sample data...")
        
        # Sample user
        sample_user = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password_hash": "hashed_password_here",
            "created_at": datetime.utcnow(),
            "profile_completion": 75,
            "is_active": True
        }
        
        try:
            user_result = self.collections['users'].insert_one(sample_user)
            user_id = user_result.inserted_id
            print(f"   ✅ Sample user created: {user_id}")
            
            # Sample user profile
            sample_profile = {
                "user_id": user_id,
                "full_name": "John Doe",
                "phone": "+1234567890",
                "location": "New York, NY",
                "education": {
                    "degree": "Bachelor's",
                    "field": "Computer Science",
                    "university": "Tech University",
                    "graduation_year": 2020
                },
                "experience": {
                    "total_years": 3,
                    "level": "mid-level",
                    "current_role": "Software Developer",
                    "current_company": "Tech Corp"
                },
                "profile_picture": None,
                "bio": "Passionate software developer with 3 years of experience",
                "updated_at": datetime.utcnow()
            }
            
            self.collections['user_profiles'].insert_one(sample_profile)
            print("   ✅ Sample profile created")
            
            # Sample skills
            sample_skills = [
                {
                    "user_id": user_id,
                    "skill_name": "Python",
                    "proficiency_level": "Advanced",
                    "years_experience": 3,
                    "verified": True,
                    "added_at": datetime.utcnow()
                },
                {
                    "user_id": user_id,
                    "skill_name": "JavaScript",
                    "proficiency_level": "Intermediate",
                    "years_experience": 2,
                    "verified": True,
                    "added_at": datetime.utcnow()
                }
            ]
            
            self.collections['user_skills'].insert_many(sample_skills)
            print("   ✅ Sample skills created")
            
        except Exception as e:
            print(f"   ⚠️  Sample data insertion warning: {e}")
    
    def load_datasets(self):
        """Load job dataset and ATS training data into MongoDB"""
        print("\n📊 Loading datasets into MongoDB...")
        
        try:
            # Load job dataset
            job_dataset_path = Path(__file__).parents[2] / 'data' / 'raw' / 'job_dataset.csv'
            if job_dataset_path.exists():
                import pandas as pd
                
                job_df = pd.read_csv(job_dataset_path)
                print(f"   📁 Loading {len(job_df)} job records...")
                
                job_records = []
                for _, row in job_df.iterrows():
                    job_record = {
                        "job_id": row.get('JobID'),
                        "title": row.get('Title'),
                        "experience_level": row.get('ExperienceLevel'),
                        "years_of_experience": row.get('YearsOfExperience'),
                        "skills": row.get('Skills', '').split(';') if pd.notna(row.get('Skills')) else [],
                        "responsibilities": row.get('Responsibilities', ''),
                        "keywords": row.get('Keywords', '').split(';') if pd.notna(row.get('Keywords')) else [],
                        "category": self._categorize_job(row.get('Title', '')),
                        "loaded_at": datetime.utcnow()
                    }
                    job_records.append(job_record)
                
                # Clear existing data and insert new
                self.collections['job_roles'].delete_many({})
                self.collections['job_roles'].insert_many(job_records)
                print(f"   ✅ Loaded {len(job_records)} job roles")
            
            # Load ATS training dataset
            ats_dataset_path = Path(__file__).parents[2] / 'data' / 'raw' / 'AI_Resume_Screening.csv'
            if ats_dataset_path.exists():
                ats_df = pd.read_csv(ats_dataset_path)
                print(f"   📁 Loading {len(ats_df)} ATS training records...")
                
                ats_records = []
                for _, row in ats_df.iterrows():
                    ats_record = {
                        "resume_id": row.get('Resume_ID'),
                        "name": row.get('Name'),
                        "skills": row.get('Skills', '').split(',') if pd.notna(row.get('Skills')) else [],
                        "experience_years": row.get('Experience (Years)', 0),
                        "education": row.get('Education'),
                        "certifications": row.get('Certifications'),
                        "job_role": row.get('Job Role'),
                        "recruiter_decision": row.get('Recruiter Decision'),
                        "salary_expectation": row.get('Salary Expectation ($)', 0),
                        "projects_count": row.get('Projects Count', 0),
                        "ats_score": row.get('AI Score (0-100)', 0),
                        "loaded_at": datetime.utcnow()
                    }
                    ats_records.append(ats_record)
                
                # Clear existing data and insert new
                self.collections['ats_training_data'].delete_many({})
                self.collections['ats_training_data'].insert_many(ats_records)
                print(f"   ✅ Loaded {len(ats_records)} ATS training records")
                
        except Exception as e:
            print(f"   ❌ Dataset loading error: {e}")
    
    def _categorize_job(self, title):
        """Categorize job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['software', 'developer', 'engineer', 'programmer']):
            return 'software_development'
        elif any(word in title_lower for word in ['data', 'scientist', 'analyst', 'ml', 'ai']):
            return 'data_science'
        elif any(word in title_lower for word in ['security', 'cyber', 'penetration']):
            return 'cybersecurity'
        elif any(word in title_lower for word in ['devops', 'cloud', 'infrastructure']):
            return 'devops'
        else:
            return 'other'
    
    def get_database_stats(self):
        """Get database statistics"""
        print("\n📊 Database Statistics:")
        print("=" * 40)
        
        for collection_name in self.collections:
            count = self.collections[collection_name].count_documents({})
            print(f"   {collection_name}: {count} documents")
        
        print("=" * 40)
    
    def setup_complete_database(self):
        """Complete database setup process"""
        print("🚀 CareerBoost AI - MongoDB Setup")
        print("=" * 50)
        
        # Step 1: Connect
        if not self.connect():
            return False
        
        # Step 2: Create collections
        self.create_collections()
        
        # Step 3: Load datasets
        self.load_datasets()
        
        # Step 4: Insert sample data
        self.insert_sample_data()
        
        # Step 5: Show stats
        self.get_database_stats()
        
        print("\n🎉 Database setup completed successfully!")
        print(f"📍 MongoDB URL: {MONGODB_URL}")
        print(f"📊 Database: {DATABASE_NAME}")
        print("\n✅ Ready for CareerBoost AI application!")
        
        return True

def main():
    """Main setup function"""
    db_setup = CareerBoostDatabase()
    success = db_setup.setup_complete_database()
    
    if success:
        print("\n🔗 Connection String: mongodb://localhost:27017/")
        print("🗄️  Database Name: careerboost_ai")
        print("\n📱 You can now start the application:")
        print("   Backend: python backend/app/main.py")
        print("   Frontend: cd frontend-react && npm start")
    else:
        print("\n❌ Setup failed. Please ensure MongoDB is running.")
        print("💡 To start MongoDB:")
        print("   - Windows: net start MongoDB")
        print("   - macOS/Linux: sudo systemctl start mongod")
        print("   - Docker: docker run -d -p 27017:27017 mongo")

if __name__ == "__main__":
    main()