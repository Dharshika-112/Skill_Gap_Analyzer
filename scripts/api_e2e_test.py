import requests, time

base='http://localhost:8000'
email=f'testuser_{int(time.time())}@example.com'
print('Signup', email)
resp = requests.post(base+'/api/auth/signup', json={'name':'Test User','email':email,'password':'test123'})
print('signup', resp.status_code, resp.text)
token = None
if resp.ok:
    token = resp.json().get('access_token')
else:
    resp2 = requests.post(base+'/api/auth/login', json={'email':email,'password':'test123'})
    print('login attempt', resp2.status_code, resp2.text)
    if resp2.ok:
        token = resp2.json().get('access_token')

print('token present:', bool(token))

files={'file':('sample.txt', b"Skills: Python, SQL, TensorFlow\nExperience: 1 year", 'text/plain')}
headers = {'Authorization': f'Bearer {token}'} if token else {}
up = requests.post(base+'/api/data/upload-resume', files=files, headers=headers)
print('upload', up.status_code)
try:
    print('upload json:', up.json())
except Exception:
    print('upload text:', up.text)
