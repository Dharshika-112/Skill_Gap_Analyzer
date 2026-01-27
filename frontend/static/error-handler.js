// Global error handler for better debugging
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    if (e.message && e.message.includes('file://')) {
        console.error('❌ File protocol detected! Use http://localhost:3000/index.html');
    }
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    if (e.reason && e.reason.message && e.reason.message.includes('file://')) {
        console.error('❌ File protocol detected! Use http://localhost:3000/index.html');
        alert('⚠️ Please open http://localhost:3000/index.html instead of opening the file directly!');
    }
});

// Test backend connection on page load
async function testBackendConnection() {
    // Check if file:// protocol
    if (window.location.protocol === 'file:') {
        console.error('❌ ERROR: File opened with file:// protocol!');
        console.error('✅ SOLUTION: Open http://localhost:3000/index.html');
        document.body.innerHTML = `
            <div style="padding: 40px; text-align: center; font-family: Arial;">
                <h1 style="color: red;">❌ Wrong Way to Open Application</h1>
                <p style="font-size: 18px; margin: 20px 0;">
                    You opened the HTML file directly from your file system.<br>
                    This won't work because of browser security restrictions.
                </p>
                <h2 style="color: green;">✅ Correct Way:</h2>
                <ol style="text-align: left; display: inline-block; font-size: 16px;">
                    <li>Make sure frontend server is running: <code>cd frontend && python server.py</code></li>
                    <li>Open in browser: <a href="http://localhost:3000/index.html" style="color: blue;">http://localhost:3000/index.html</a></li>
                </ol>
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Or click here: <a href="http://localhost:3000/index.html" style="color: blue; font-size: 18px;">http://localhost:3000/index.html</a>
                </p>
            </div>
        `;
        return false;
    }
    
    if (typeof API_URL === 'undefined') {
        console.error('❌ API_URL not defined');
        return false;
    }
    
    try {
        const res = await fetch(`${API_URL}/`);
        if (res.ok) {
            console.log('✅ Backend connection successful');
            return true;
        } else {
            console.warn('⚠️ Backend responded but with error:', res.status);
            return false;
        }
    } catch (e) {
        console.error('❌ Backend connection failed:', e.message);
        console.error('Make sure backend is running at:', API_URL);
        console.error('Start backend with: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000');
        return false;
    }
}

// Run test when page loads
if (typeof API_URL !== 'undefined') {
    // Wait a bit for page to load
    setTimeout(() => {
        testBackendConnection();
    }, 100);
}
