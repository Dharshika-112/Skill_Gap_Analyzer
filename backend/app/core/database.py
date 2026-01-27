"""MongoDB helper: connection and collection access"""
from pymongo import MongoClient
from .config import MONGODB_URL, MONGODB_DB_NAME, COLLECTIONS
from datetime import datetime

_client = None
_db = None

def get_database():
    """Return a singleton database connection"""
    global _client, _db
    if _db is not None:
        return _db

    _client = MongoClient(MONGODB_URL)
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

    return _db

def get_collection(key: str):
    db = get_database()
    col_name = COLLECTIONS.get(key)
    if not col_name:
        raise KeyError(f"Unknown collection key: {key}")
    return db[col_name]
