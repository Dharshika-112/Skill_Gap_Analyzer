"""
File-based Database for CareerBoost AI
Works when MongoDB is not available
"""

import json
import os
from datetime import datetime
from pathlib import Path
import hashlib

class FileDatabase:
    """File-based database implementation"""
    
    def __init__(self):
        self.db_dir = Path(__file__).parents[2] / 'data' / 'database'
        self.db_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize collection files
        self.collections = {
            'users': self.db_dir / 'users.json',
            'user_profiles': self.db_dir / 'user_profiles.json',
            'user_skills': self.db_dir / 'user_skills.json',
            'analysis_history': self.db_dir / 'analysis_history.json',
            'resume_uploads': self.db_dir / 'resume_uploads.json',
            'skill_gap_results': self.db_dir / 'skill_gap_results.json',
            'resume_scores': self.db_dir / 'resume_scores.json'
        }
        
        # Initialize empty collections
        for collection_name, file_path in self.collections.items():
            if not file_path.exists():
                self._save_collection(collection_name, [])
    
    def _load_collection(self, collection_name):
        """Load collection from file"""
        try:
            with open(self.collections[collection_name], 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_collection(self, collection_name, data):
        """Save collection to file"""
        try:
            with open(self.collections[collection_name], 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving {collection_name}: {e}")
            return False
    
    def _generate_id(self):
        """Generate unique ID"""
        return hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()[:12]
    
    def insert_one(self, collection_name, document):
        """Insert one document"""
        data = self._load_collection(collection_name)
        
        # Add ID and timestamp
        document['_id'] = self._generate_id()
        document['created_at'] = datetime.utcnow().isoformat()
        
        data.append(document)
        
        if self._save_collection(collection_name, data):
            class InsertResult:
                def __init__(self, inserted_id):
                    self.inserted_id = inserted_id
            return InsertResult(document['_id'])
        return None
    
    def find_one(self, collection_name, query=None):
        """Find one document"""
        data = self._load_collection(collection_name)
        
        if not query:
            return data[0] if data else None
        
        for doc in data:
            if self._matches_query(doc, query):
                return doc
        return None
    
    def find(self, collection_name, query=None):
        """Find multiple documents"""
        data = self._load_collection(collection_name)
        
        if not query:
            return data
        
        return [doc for doc in data if self._matches_query(doc, query)]
    
    def update_one(self, collection_name, query, update):
        """Update one document"""
        data = self._load_collection(collection_name)
        
        for i, doc in enumerate(data):
            if self._matches_query(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                doc['updated_at'] = datetime.utcnow().isoformat()
                data[i] = doc
                return self._save_collection(collection_name, data)
        return False
    
    def delete_one(self, collection_name, query):
        """Delete one document"""
        data = self._load_collection(collection_name)
        
        for i, doc in enumerate(data):
            if self._matches_query(doc, query):
                del data[i]
                return self._save_collection(collection_name, data)
        return False
    
    def count_documents(self, collection_name, query=None):
        """Count documents"""
        data = self._load_collection(collection_name)
        
        if not query:
            return len(data)
        
        return len([doc for doc in data if self._matches_query(doc, query)])
    
    def _matches_query(self, document, query):
        """Check if document matches query"""
        for key, value in query.items():
            if key not in document or document[key] != value:
                return False
        return True

# Global file database instance
file_db = FileDatabase()

class FileCollection:
    """File-based collection wrapper"""
    
    def __init__(self, collection_name):
        self.collection_name = collection_name
    
    def find_one(self, query=None):
        return file_db.find_one(self.collection_name, query)
    
    def find(self, query=None):
        return file_db.find(self.collection_name, query)
    
    def insert_one(self, document):
        return file_db.insert_one(self.collection_name, document)
    
    def update_one(self, query, update):
        return file_db.update_one(self.collection_name, query, update)
    
    def delete_one(self, query):
        return file_db.delete_one(self.collection_name, query)
    
    def count_documents(self, query=None):
        return file_db.count_documents(self.collection_name, query)
    
    def create_index(self, field, unique=False):
        # Mock index creation for file database
        pass

def get_file_collection(collection_name):
    """Get file-based collection"""
    return FileCollection(collection_name)