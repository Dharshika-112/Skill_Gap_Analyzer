#!/usr/bin/env python3
"""
Comprehensive API Test Suite
Tests all endpoints, authentication, and MongoDB connection
"""

import requests
import json
import time
import sys
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.test_email = f"test_{int(time.time())}@example.com"
        self.test_password = "test123"
        self.results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_server_health(self):
        """Test if server is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Server Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def test_api_info(self):
        """Test API info endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Info", True, f"Version: {data.get('version')}")
                return True
            else:
                self.log_test("API Info", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Info", False, f"Error: {str(e)}")
            return False
            
    def test_signup(self):
        """Test user signup"""
        try:
            payload = {
                "name": "Test User",
                "email": self.test_email,
                "password": self.test_password
            }
            response = requests.post(f"{self.base_url}/api/auth/signup", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.log_test("User Signup", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("User Signup", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Signup", False, f"Error: {str(e)}")
            return False
            
    def test_login(self):
        """Test user login"""
        try:
            payload = {
                "email": self.test_email,
                "password": self.test_password
            }
            response = requests.post(f"{self.base_url}/api/auth/login", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.log_test("User Login", True, f"Token received: {bool(self.token)}")
                return True
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")
            return False
            
    def test_profile_access(self):
        """Test authenticated profile access"""
        if not self.token:
            self.log_test("Profile Access", False, "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/api/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Profile Access", True, f"Email: {data.get('email')}")
                return True
            else:
                self.log_test("Profile Access", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Profile Access", False, f"Error: {str(e)}")
            return False
            
    def test_profile_update(self):
        """Test profile update"""
        if not self.token:
            self.log_test("Profile Update", False, "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "name": "Updated Test User",
                "experience": {"type": "fresher", "years": 0.5}
            }
            response = requests.put(f"{self.base_url}/api/auth/me", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Profile Update", True, f"Updated: {data.get('status')}")
                return True
            else:
                self.log_test("Profile Update", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Profile Update", False, f"Error: {str(e)}")
            return False
            
    def test_resume_upload(self):
        """Test resume upload"""
        if not self.token:
            self.log_test("Resume Upload", False, "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            files = {
                'file': ('test_resume.txt', 
                        'Skills: Python, JavaScript, SQL, Machine Learning\nExperience: 2 years in software development\nEducation: Computer Science', 
                        'text/plain')
            }
            response = requests.post(f"{self.base_url}/api/data/upload-resume", files=files, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Resume Upload", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Resume Upload", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Resume Upload", False, f"Error: {str(e)}")
            return False
            
    def test_skills_endpoints(self):
        """Test skills-related endpoints"""
        if not self.token:
            self.log_test("Skills Endpoints", False, "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test get user skills
            response = requests.get(f"{self.base_url}/api/skills/user-skills", headers=headers, timeout=10)
            if response.status_code == 200:
                self.log_test("Get User Skills", True, "Skills retrieved")
            else:
                self.log_test("Get User Skills", False, f"Status: {response.status_code}")
                
            # Test skill gap analysis
            gap_data = {
                "user_skills": ["Python", "JavaScript", "SQL"],
                "role_skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB"],
                "role_name": "Full Stack Developer"
            }
            response = requests.post(f"{self.base_url}/api/data/skill-gap", json=gap_data, headers=headers, timeout=15)
            if response.status_code == 200:
                self.log_test("Skill Gap Analysis", True, "Analysis completed")
            else:
                self.log_test("Skill Gap Analysis", False, f"Status: {response.status_code}")
                
            return True
        except Exception as e:
            self.log_test("Skills Endpoints", False, f"Error: {str(e)}")
            return False
            
    def test_data_endpoints(self):
        """Test data-related endpoints"""
        try:
            # Test dataset info (public endpoint)
            response = requests.get(f"{self.base_url}/api/data/dataset-info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Dataset Info", True, f"Roles: {data.get('total_roles', 0)}")
            else:
                self.log_test("Dataset Info", False, f"Status: {response.status_code}")
                
            return True
        except Exception as e:
            self.log_test("Data Endpoints", False, f"Error: {str(e)}")
            return False
            
    def test_mongodb_connection(self):
        """Test MongoDB connection indirectly through API"""
        try:
            # If we can signup/login, MongoDB is working
            if self.user_id and self.token:
                self.log_test("MongoDB Connection", True, "Database operations successful")
                return True
            else:
                self.log_test("MongoDB Connection", False, "No successful database operations")
                return False
        except Exception as e:
            self.log_test("MongoDB Connection", False, f"Error: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive API Test Suite")
        print(f"📍 Testing server at: {self.base_url}")
        print(f"📧 Test email: {self.test_email}")
        print("=" * 60)
        
        # Basic connectivity tests
        if not self.test_server_health():
            print("❌ Server is not running. Please start the backend first.")
            return False
            
        self.test_api_info()
        
        # Authentication tests
        signup_success = self.test_signup()
        if not signup_success:
            # Try login if signup fails (user might already exist)
            login_success = self.test_login()
            if not login_success:
                print("❌ Authentication failed. Cannot continue with authenticated tests.")
                return False
        
        # Authenticated tests
        self.test_profile_access()
        self.test_profile_update()
        self.test_resume_upload()
        self.test_skills_endpoints()
        
        # Data tests
        self.test_data_endpoints()
        
        # Database test
        self.test_mongodb_connection()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if total - passed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 Overall Success Rate: {(passed/total)*100:.1f}%")
        
        return passed == total

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive API Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API (default: http://localhost:8000)")
    args = parser.parse_args()
    
    tester = APITester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()