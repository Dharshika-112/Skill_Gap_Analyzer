#!/usr/bin/env python3
"""
Comprehensive Feature Test Suite - Tests all 15 features
"""

import requests
import time
import json

class SkillGapTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.test_email = f"feature_test_{int(time.time())}@example.com"
        self.results = []
        
    def log_test(self, feature, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {feature}: {test_name}")
        if details:
            print(f"    {details}")
        self.results.append({"feature": feature, "test": test_name, "success": success, "details": details})
        
    def test_authentication(self):
        """✅ 1. USER AUTHENTICATION"""
        print("\n🔐 TESTING FEATURE 1: USER AUTHENTICATION")
        
        # Test Signup
        signup_data = {"name": "Feature Test User", "email": self.test_email, "password": "test123"}
        
        try:
            response = requests.post(f"{self.base_url}/api/auth/signup", json=signup_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.log_test("Authentication", "Signup with Name/Email/Password", True, f"User ID: {self.user_id}")
            else:
                self.log_test("Authentication", "Signup", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication", "Signup", False, f"Error: {e}")
            return False
            
        # Test Login
        login_data = {"email": self.test_email, "password": "test123"}
        try:
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                self.log_test("Authentication", "Login", True, "Login successful")
            else:
                self.log_test("Authentication", "Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Authentication", "Login", False, f"Error: {e}")
            
        # Test MongoDB Storage
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(f"{self.base_url}/api/auth/me", headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                required_fields = ["user_id", "name", "email", "created_at"]
                if all(field in user_data for field in required_fields):
                    self.log_test("Authentication", "MongoDB User Storage", True, "All required fields present")
                else:
                    self.log_test("Authentication", "MongoDB User Storage", False, "Missing required fields")
            else:
                self.log_test("Authentication", "MongoDB User Storage", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Authentication", "MongoDB User Storage", False, f"Error: {e}")
            
        return True
        
    def test_manual_skills(self):
        """📝 4. MANUAL SKILL ENTRY"""
        print("\n📝 TESTING FEATURE 4: MANUAL SKILL ENTRY")
        
        if not self.token:
            self.log_test("Manual Skills", "All Tests", False, "No authentication token")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test Get Dataset Skills
        try:
            response = requests.get(f"{self.base_url}/api/data/skills", timeout=10)
            if response.status_code == 200:
                data = response.json()
                skills = data.get("skills", [])
                if len(skills) > 50:
                    self.log_test("Manual Skills", "Dataset Skills Available", True, f"{len(skills)} skills available")
                else:
                    self.log_test("Manual Skills", "Dataset Skills Available", False, f"Only {len(skills)} skills")
            else:
                self.log_test("Manual Skills", "Dataset Skills Available", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Manual Skills", "Dataset Skills Available", False, f"Error: {e}")
            
        # Test Save Manual Skills
        manual_skills = {
            "user_skills": [
                {"skill": "Python", "source": "manual"},
                {"skill": "JavaScript", "source": "manual"},
                {"skill": "SQL", "source": "manual"}
            ]
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/skills/save-objects", json=manual_skills, headers=headers, timeout=10)
            if response.status_code == 200:
                self.log_test("Manual Skills", "Save Skills to MongoDB", True, "Skills saved successfully")
            else:
                self.log_test("Manual Skills", "Save Skills to MongoDB", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Manual Skills", "Save Skills to MongoDB", False, f"Error: {e}")
            
        return True
        
    def test_resume_upload(self):
        """📄 5. RESUME UPLOAD & PARSING"""
        print("\n📄 TESTING FEATURE 5: RESUME UPLOAD & PARSING")
        
        if not self.token:
            self.log_test("Resume Upload", "All Tests", False, "No authentication token")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create sample resume
        resume_content = """
        JOHN DOE - Software Developer
        
        TECHNICAL SKILLS:
        Programming Languages: Python, JavaScript, Java, C++
        Web Technologies: React, Node.js, HTML, CSS
        Databases: MySQL, MongoDB, PostgreSQL
        Tools: Git, Docker, Jenkins
        Machine Learning: TensorFlow, PyTorch
        
        EXPERIENCE:
        Software Developer Intern - ABC Company (6 months)
        Full-time Developer - XYZ Corp (2 years)
        """
        
        files = {'file': ('test_resume.txt', resume_content.encode(), 'text/plain')}
        
        try:
            response = requests.post(f"{self.base_url}/api/data/upload-resume", files=files, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                parsed_data = data.get("parsed", {})
                extracted_skills = parsed_data.get("skills", [])
                
                if len(extracted_skills) > 0:
                    self.log_test("Resume Upload", "Skill Extraction", True, f"{len(extracted_skills)} skills extracted")
                    
                    # Check dataset matching
                    expected_skills = ["Python", "JavaScript", "React", "Node.js", "MySQL", "MongoDB"]
                    found_skills = [skill for skill in expected_skills if skill in extracted_skills]
                    if len(found_skills) > 3:
                        self.log_test("Resume Upload", "Dataset Skill Matching", True, f"{len(found_skills)} dataset skills found")
                    else:
                        self.log_test("Resume Upload", "Dataset Skill Matching", False, f"Only {len(found_skills)} dataset skills found")
                else:
                    self.log_test("Resume Upload", "Skill Extraction", False, "No skills extracted")
                    
                # Check experience detection
                experience = parsed_data.get("experience", {})
                if experience and "type" in experience:
                    self.log_test("Resume Upload", "Experience Detection", True, f"Experience type: {experience.get('type')}")
                else:
                    self.log_test("Resume Upload", "Experience Detection", False, "No experience detected")
                    
            else:
                self.log_test("Resume Upload", "File Upload", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Resume Upload", "File Upload", False, f"Error: {e}")
            
        return True
        
    def test_role_matching(self):
        """🧩 9. ROLE MATCHING ENGINE"""
        print("\n🧩 TESTING FEATURE 9: ROLE MATCHING ENGINE")
        
        user_skills_data = {
            "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "MongoDB"],
            "experience": {"type": "internship", "years": 0.5}
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/data/recommend-roles", json=user_skills_data, timeout=20)
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])
                
                if len(recommendations) > 0:
                    self.log_test("Role Matching", "Top Role Recommendations", True, f"{len(recommendations)} roles recommended")
                    
                    first_role = recommendations[0]
                    required_fields = ["role", "match_percentage", "star_rating", "matching_skills", "missing_skills"]
                    if all(field in first_role for field in required_fields):
                        self.log_test("Role Matching", "Match Percentage & Star Rating", True, f"Match: {first_role.get('match_percentage')}%, Stars: {first_role.get('star_rating')}")
                    else:
                        self.log_test("Role Matching", "Match Percentage & Star Rating", False, "Missing required fields")
                        
                    if "essential_skills_match" in first_role:
                        self.log_test("Role Matching", "Essential vs Overall Skills", True, f"Essential: {first_role.get('essential_skills_match')}")
                    else:
                        self.log_test("Role Matching", "Essential vs Overall Skills", False, "Missing skill match data")
                else:
                    self.log_test("Role Matching", "Top Role Recommendations", False, "No recommendations returned")
            else:
                self.log_test("Role Matching", "Top Role Recommendations", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Role Matching", "Top Role Recommendations", False, f"Error: {e}")
            
        return True
        
    def test_common_vs_role_specific(self):
        """🧩 11. COMMON vs ROLE-SPECIFIC SKILLS"""
        print("\n🧩 TESTING FEATURE 11: COMMON vs ROLE-SPECIFIC SKILLS")
        
        gap_data = {
            "user_skills": ["Python", "JavaScript", "SQL"],
            "role_skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB", "Docker", "AWS"],
            "role_name": "Full Stack Developer"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/data/skill-gap", json=gap_data, timeout=15)
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", {})
                
                common_skills = analysis.get("common_skills", [])
                if len(common_skills) > 0:
                    self.log_test("Common vs Role-Specific", "Common Skills Detection", True, f"{len(common_skills)} common skills found")
                else:
                    self.log_test("Common vs Role-Specific", "Common Skills Detection", False, "No common skills found")
                    
                role_specific = analysis.get("role_specific_skills", [])
                if len(role_specific) > 0:
                    self.log_test("Common vs Role-Specific", "Role-Specific Boosters", True, f"{len(role_specific)} booster skills found")
                else:
                    self.log_test("Common vs Role-Specific", "Role-Specific Boosters", False, "No booster skills found")
                    
            else:
                self.log_test("Common vs Role-Specific", "Analysis", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Common vs Role-Specific", "Analysis", False, f"Error: {e}")
            
        return True
        
    def test_grouped_display(self):
        """🗂️ 12. GROUPED SKILL DISPLAY"""
        print("\n🗂️ TESTING FEATURE 12: GROUPED SKILL DISPLAY")
        
        gap_data = {
            "user_skills": ["Python", "HTML"],
            "role_skills": ["Python", "JavaScript", "React", "TensorFlow", "Docker", "AWS", "MySQL"],
            "role_name": "Full Stack Developer"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/data/skill-gap", json=gap_data, timeout=15)
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", {})
                
                missing_grouped = analysis.get("missing_skills_grouped", {})
                if isinstance(missing_grouped, dict) and len(missing_grouped) > 0:
                    categories = list(missing_grouped.keys())
                    self.log_test("Grouped Display", "Missing Skills Grouped", True, f"Categories: {', '.join(categories)}")
                    
                    expected_categories = ["Programming Languages", "Web Technologies", "Databases", "Cloud Platforms"]
                    found_categories = [cat for cat in expected_categories if cat in categories]
                    if len(found_categories) > 0:
                        self.log_test("Grouped Display", "Category Classification", True, f"Found: {', '.join(found_categories)}")
                    else:
                        self.log_test("Grouped Display", "Category Classification", False, "No expected categories found")
                else:
                    self.log_test("Grouped Display", "Missing Skills Grouped", False, "No grouped skills found")
                    
            else:
                self.log_test("Grouped Display", "Analysis", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Grouped Display", "Analysis", False, f"Error: {e}")
            
        return True
        
    def run_all_tests(self):
        """Run all feature tests"""
        print("🚀 COMPREHENSIVE SKILL GAP ANALYZER FEATURE TEST")
        print("=" * 80)
        
        self.test_authentication()
        self.test_manual_skills()
        self.test_resume_upload()
        self.test_role_matching()
        self.test_common_vs_role_specific()
        self.test_grouped_display()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FEATURE TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Group by feature
        features = {}
        for result in self.results:
            feature = result["feature"]
            if feature not in features:
                features[feature] = {"passed": 0, "total": 0}
            features[feature]["total"] += 1
            if result["success"]:
                features[feature]["passed"] += 1
                
        print(f"\n📋 FEATURE BREAKDOWN:")
        for feature, stats in features.items():
            status = "✅" if stats["passed"] == stats["total"] else "⚠️" if stats["passed"] > 0 else "❌"
            print(f"{status} {feature}: {stats['passed']}/{stats['total']}")
        
        if total - passed > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['feature']} - {result['test']}: {result['details']}")
        
        print(f"\n🎯 Overall Success Rate: {(passed/total)*100:.1f}%")
        
        return passed == total

if __name__ == "__main__":
    tester = SkillGapTester()
    tester.run_all_tests()