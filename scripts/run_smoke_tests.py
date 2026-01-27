import sys
import traceback
from pprint import pprint
from pathlib import Path

ROOT = Path(__file__).parents[1].resolve()
# Ensure backend package is importable
root_path = str(ROOT)
if root_path not in sys.path:
    sys.path.insert(0, root_path)
backend_app = str(ROOT / 'backend' / 'app')
if backend_app not in sys.path:
    sys.path.insert(0, backend_app)

print('Running smoke tests for Skill Gap Analyzer')

sample_text = b"""John Doe
Experience: 2 years
Skills: Python, SQL, TensorFlow, leadership
Internship at ABC Corp"""

try:
    from backend.app.core import config as cfg
    print('MongoDB URL from config:', cfg.MONGODB_URL)
except Exception as e:
    print('Failed to import config:', e)

db = None
try:
    from backend.app.core.database import get_database
    db = get_database()
    print('Connected to MongoDB, collections:', db.list_collection_names())
    try:
        ping = db.command('ping')
        print('Mongo ping:', ping)
    except Exception as e:
        print('Mongo ping failed:', e)
except Exception as e:
    print('Database connection failed:', e)

print('\nTesting resume parser...')
try:
    from backend.app.services.resume_parser import parse_resume, save_parsed_resume
    parsed = parse_resume(sample_text, 'sample_resume.txt')
    print('Parsed resume summary:')
    pprint({k: parsed.get(k) for k in ('filename', 'skills', 'experience', 'stored_path')})

    if db is not None:
        print('Saving parsed resume to DB as user_id test_user_1')
        rid = save_parsed_resume('test_user_1', parsed)
        print('Inserted resume id:', rid)
    else:
        print('Skipping DB save (no DB)')
except Exception as e:
    print('Resume parser test failed:')
    traceback.print_exc()

print('\nTesting API upload endpoint if backend running...')
try:
    import requests, os
    url = os.getenv('API_URL', 'http://localhost:8000')
    files = {'file': ('sample_resume.txt', sample_text, 'text/plain')}
    resp = requests.post(f'{url}/api/data/upload-resume', files=files, timeout=5)
    print('API response status:', resp.status_code)
    try:
        print('API response:', resp.json())
    except Exception:
        print('API response text:', resp.text[:400])
except Exception as e:
    print('API upload test skipped or failed (backend not running?):', e)

print('\nSmoke tests complete')
