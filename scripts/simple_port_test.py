#!/usr/bin/env python3
"""
Super simple test - just test if backend responds
"""
import socket
import time

def is_port_open(port, host='localhost', timeout=1):
    """Check if port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

print("Checking if port 8000 is open...")
time.sleep(1)

if is_port_open(8000):
    print("✅ Port 8000 is OPEN - Backend is listening!")
    
    # Try simple HTTP GET
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8000))
    request = b'GET / HTTP/1.1\r\nHost: localhost:8000\r\nConnection: close\r\n\r\n'
    sock.sendall(request)
    response = b''
    while True:
        data = sock.recv(4096)
        if not data:
            break
        response += data
    sock.close()
    
    print("\nHTTP Response:")
    print(response.decode('utf-8', errors='ignore')[:500])
else:
    print("❌ Port 8000 is NOT open - Backend is not listening")
    print("The backend appears to have crashed or not started")
