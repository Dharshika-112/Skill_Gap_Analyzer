"""Database helper: MongoDB or file-based database"""
from pymongo import MongoClient
from .config import MONGODB_URL, MONGODB_DB_NAME, COLLECTIONS
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None
_use_file_db = False

def get_database():
    """Return a singleton database connection or file database"""
    global _client, _db, _use_file_db
    
    # Try MongoDB connection first
    try:
        if _db is not None and not _use_file_db:
            return _db

        _client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=3000)
        # Test connection
        _client.server_info()
        _db = _client[MONGODB_DB_NAME]

        # Ensure basic collections exist
        for name in COLLECTIONS.values():
            if name not in _db.list_collection_names():
                _db.create_collection(name)

        # Basic indexes
        try:
            _db[COLLECTIONS['users']].create_index('email', unique=True)
            _db[COLLECTIONS['user_skills']].create_index('user_id')
        except Exception:
            pass

        logger.info("✅ Connected to MongoDB successfully")
        print("✅ Using MongoDB database")
        return _db
        
    except Exception as e:
        logger.warning(f"⚠️  MongoDB not available: {e}")
        print("⚠️  MongoDB not available, using file-based database")
        
        # Use file database
        _use_file_db = True
        from .file_database import FileDatabase
        return FileDatabase()

class FileCollectionWrapper:
    """Wrapper to make file collections compatible with MongoDB interface"""
    
    def __init__(self, collection_name):
        from .file_database import get_file_collection
        self.collection = get_file_collection(collection_name)
        self.collection_name = collection_name
    
    def find_one(self, query=None):
        return self.collection.find_one(query)
    
    def find(self, query=None):
        return self.collection.find(query)
    
    def insert_one(self, document):
        return self.collection.insert_one(document)
    
    def update_one(self, query, update):
        return self.collection.update_one(query, update)
    
    def delete_one(self, query):
        return self.collection.delete_one(query)
    
    def count_documents(self, query=None):
        return self.collection.count_documents(query)
    
    def create_index(self, field, unique=False):
        return self.collection.create_index(field, unique)
    
    def delete_many(self, query):
        # For file database, delete all matching documents
        data = self.collection.find(query)
        count = 0
        for doc in data:
            if self.collection.delete_one({'_id': doc['_id']}):
                count += 1
        return count
    
    def insert_many(self, documents):
        results = []
        for doc in documents:
            result = self.collection.insert_one(doc)
            if result:
                results.append(result)
        return results

def get_collection(key: str):
    """Get collection (MongoDB or file-based)"""
    global _use_file_db
    
    col_name = COLLECTIONS.get(key)
    if not col_name:
        raise KeyError(f"Unknown collection key: {key}")
    
    if _use_file_db:
        return FileCollectionWrapper(col_name)
    else:
        db = get_database()
        return db[col_name]