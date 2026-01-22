#!/usr/bin/env python3
"""
Initialize dataset in MongoDB
Run this script after placing your Kaggle dataset

Usage:
    python init_dataset.py --dataset /path/to/dataset.csv
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from pymongo import MongoClient
from app.core.config import MONGODB_URL, MONGODB_DB_NAME, COLLECTIONS
from app.services.dataset_normalizer import DatasetNormalizer

def init_dataset(dataset_path: str):
    """Initialize dataset in MongoDB"""
    
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset file not found: {dataset_path}")
        return False
    
    try:
        # Connect to MongoDB
        print("[*] Connecting to MongoDB...")
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("[OK] MongoDB connected")
        
        db = client[MONGODB_DB_NAME]
        
        # Load and normalize dataset
        print("[*] Loading and normalizing dataset...")
        normalizer = DatasetNormalizer()
        
        if not normalizer.load_kaggle_dataset(dataset_path):
            return False
        
        skills = normalizer.normalize_skills()
        roles = normalizer.extract_roles()
        
        # Store skills in MongoDB
        print("[*] Storing skills in MongoDB...")
        skills_collection = db[COLLECTIONS['dataset_skills']]
        skills_collection.delete_many({})  # Clear existing
        
        skills_docs = [{'skill': skill, '_id': skill.lower()} for skill in skills]
        if skills_docs:
            skills_collection.insert_many(skills_docs)
        
        print(f"[OK] Stored {len(skills)} skills")
        
        # Store roles in MongoDB
        print("[*] Storing roles in MongoDB...")
        roles_collection = db[COLLECTIONS['dataset_roles']]
        roles_collection.delete_many({})  # Clear existing
        
        roles_docs = []
        for level, role_list in roles.items():
            for role in role_list:
                role_skills = normalizer.get_role_skills(role)
                roles_docs.append({
                    'title': role,
                    'level': level,
                    'skills': role_skills,
                    '_id': f"{role}_{level}"
                })
        
        if roles_docs:
            roles_collection.insert_many(roles_docs)
        
        print(f"[OK] Stored {len(roles_docs)} roles")
        
        # Create indexes for faster queries
        print("[*] Creating indexes...")
        skills_collection.create_index([("skill", 1)])
        roles_collection.create_index([("title", 1)])
        roles_collection.create_index([("level", 1)])
        
        # Store dataset statistics
        print("[*] Storing dataset statistics...")
        stats_collection = db['dataset_stats']
        stats_collection.delete_one({'_id': 'main'})
        
        stats = {
            '_id': 'main',
            'total_skills': len(skills),
            'total_roles': len(roles_docs),
            'common_skills': [item['skill'] for item in normalizer.get_most_common_skills(50)],
            'roles_by_level': {level: len(role_list) for level, role_list in roles.items()}
        }
        stats_collection.insert_one(stats)
        
        print("[OK] Dataset initialization complete!")
        print(f"\n[SUMMARY]")
        print(f"  Total Skills: {len(skills)}")
        print(f"  Total Roles: {len(roles_docs)}")
        print(f"  Database: {MONGODB_DB_NAME}")
        print(f"  MongoDB: {MONGODB_URL}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Initialize dataset in MongoDB')
    parser.add_argument('--dataset', type=str, help='Path to Kaggle dataset CSV', 
                       default='../data/raw/jobs_dataset.csv')
    
    args = parser.parse_args()
    
    dataset_path = args.dataset
    
    # Try to find dataset if path is relative
    if not os.path.isabs(dataset_path):
        # Try from scripts directory
        scripts_dir = Path(__file__).parent
        candidate_path = scripts_dir / dataset_path
        if candidate_path.exists():
            dataset_path = str(candidate_path)
        else:
            # Try from backend directory
            backend_dir = Path(__file__).parent.parent
            candidate_path = backend_dir / dataset_path
            if candidate_path.exists():
                dataset_path = str(candidate_path)
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║       SKILL GAP ANALYZER - DATASET INITIALIZATION             ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"[*] Dataset file: {dataset_path}")
    
    if init_dataset(dataset_path):
        print("\n[✓] SUCCESS: Dataset initialized in MongoDB!")
        sys.exit(0)
    else:
        print("\n[✗] FAILED: Dataset initialization failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
