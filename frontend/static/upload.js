// Better API URL detection
function getAPIUrl() {
    // If opened as file://, always use localhost:8000
    if (window.location.protocol === 'file:') {
        console.error('❌ File opened directly! Use http://localhost:3000/app.html');
        return 'http://localhost:8000';
    }
    
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '') {
        return 'http://localhost:8000';
    }
    
    return window.location.origin.replace(':3000', ':8000');
}

const API_URL = getAPIUrl();
console.log('🌐 API URL:', API_URL);

document.getElementById('upload').addEventListener('click', async () => {
  const fileInput = document.getElementById('resume');
  const tokenInput = document.getElementById('token');
  const status = document.getElementById('status');
  const result = document.getElementById('result');
  const rSkills = document.getElementById('r-skills');
  const rExp = document.getElementById('r-experience');
  const rFilename = document.getElementById('r-filename');

  if (!fileInput.files.length) {
    status.textContent = 'Please choose a resume file to upload.';
    return;
  }

  const file = fileInput.files[0];
  status.textContent = 'Uploading...';
  result.classList.add('hidden');
  rSkills.innerHTML = '';

  const fd = new FormData();
  fd.append('file', file, file.name);

  try {
    const headers = {};
    if (tokenInput.value && tokenInput.value.trim()) {
      headers['Authorization'] = tokenInput.value.trim();
    }

    const resp = await fetch(`${API_URL}/api/data/upload-resume`, {
      method: 'POST',
      body: fd,
      headers
    });

    if (!resp.ok) {
      const err = await resp.json().catch(()=>({detail:resp.statusText}));
      status.textContent = 'Upload failed: ' + (err.detail || resp.statusText);
      return;
    }

    const data = await resp.json();
    if (data.status !== 'success') {
      status.textContent = 'Parsing failed';
      return;
    }

    const parsed = data.parsed;
    status.textContent = 'Parsed successfully';
    rFilename.textContent = parsed.filename || file.name;
    rExp.textContent = (parsed.experience && parsed.experience.type) ? `${parsed.experience.type} (${parsed.experience.years || 'N/A'} yrs)` : 'N/A';

    (parsed.skills || []).forEach(s => {
      const li = document.createElement('li');
      li.textContent = s;
      rSkills.appendChild(li);
    });

    result.classList.remove('hidden');
  } catch (e) {
    status.textContent = 'Upload error: ' + e.message;
  }
});
