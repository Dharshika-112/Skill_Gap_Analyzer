"""
Skill Gap Analyzer - Complete Integration
CareerBoost AI - Main Skill Gap Analysis Service

This module integrates all 8 steps of the skill gap analysis process:
1. Skill Normalization Layer
2. Skill Taxonomy Classification  
3. Intelligent Skill Matching
4. Weighted Gap Scoring System
5. Gap Analysis Output
6. Learning Roadmap Generator
7. Project Recommendation Engine
8. Interview Readiness Layer
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

# Import all the analysis components
from .skill_normalizer import skill_normalizer
from .skill_taxonomy import skill_taxonomy, SkillCategory
from .intelligent_skill_matcher import intelligent_skill_matcher, MatchType
from .weighted_gap_scorer import weighted_gap_scorer, ReadinessLevel
from .learning_roadmap_generator import learning_roadmap_generator

class SkillGapAnalyzer:
    def __init__(self):
        """Initialize the complete skill gap analyzer."""
        self.job_roles_data = self.load_job_roles_data()
        
        # Project recommendations by skill category
        self.project_recommendations = {
            SkillCategory.FRONTEND: [
                {
                    "title": "Responsive Portfolio Website",
                    "description": "Build a personal portfolio showcasing your projects",
                    "skills_gained": ["HTML", "CSS", "JavaScript", "Responsive Design"],
                    "difficulty": "Beginner",
                    "duration": "1-2 weeks",
                    "resume_value": "High - Shows personal branding and web skills"
                },
                {
                    "title": "E-commerce Product Catalog",
                    "description": "Create a product listing with search and filter functionality",
                    "skills_gained": ["React/Vue", "API Integration", "State Management"],
                    "difficulty": "Intermediate",
                    "duration": "2-3 weeks",
                    "resume_value": "High - Demonstrates real-world application skills"
                }
            ],
            SkillCategory.CORE_PROGRAMMING: [
                {
                    "title": "REST API with Authentication",
                    "description": "Build a secure API with user authentication and CRUD operations",
                    "skills_gained": ["API Design", "Database Integration", "Security"],
                    "difficulty": "Intermediate",
                    "duration": "2-3 weeks",
                    "resume_value": "Very High - Core backend development skill"
                },
                {
                    "title": "Microservices Architecture",
                    "description": "Design and implement a microservices-based system",
                    "skills_gained": ["Microservices", "Docker", "API Gateway"],
                    "difficulty": "Advanced",
                    "duration": "3-4 weeks",
                    "resume_value": "Very High - Shows architectural thinking"
                }
            ],
            SkillCategory.AI_ML_CORE: [
                {
                    "title": "Predictive Analytics Dashboard",
                    "description": "Build a machine learning model with visualization dashboard",
                    "skills_gained": ["ML Algorithms", "Data Visualization", "Model Deployment"],
                    "difficulty": "Intermediate",
                    "duration": "3-4 weeks",
                    "resume_value": "Very High - Shows end-to-end ML skills"
                },
                {
                    "title": "Recommendation System",
                    "description": "Create a recommendation engine for products or content",
                    "skills_gained": ["Collaborative Filtering", "Content-Based Filtering", "ML Pipeline"],
                    "difficulty": "Advanced",
                    "duration": "4-5 weeks",
                    "resume_value": "Very High - Highly sought-after skill"
                }
            ],
            SkillCategory.MOBILE: [
                {
                    "title": "Cross-Platform Mobile App",
                    "description": "Build a mobile app that works on both iOS and Android",
                    "skills_gained": ["React Native/Flutter", "Mobile UI/UX", "App Store Deployment"],
                    "difficulty": "Intermediate",
                    "duration": "3-4 weeks",
                    "resume_value": "High - Shows mobile development capability"
                }
            ],
            SkillCategory.DEVOPS_CLOUD: [
                {
                    "title": "CI/CD Pipeline with Cloud Deployment",
                    "description": "Set up automated deployment pipeline to cloud platform",
                    "skills_gained": ["CI/CD", "Docker", "Cloud Platforms", "Infrastructure as Code"],
                    "difficulty": "Intermediate",
                    "duration": "2-3 weeks",
                    "resume_value": "Very High - Essential for modern development"
                }
            ]
        }
        
        # Interview questions by skill level and category
        self.interview_questions = {
            "beginner": {
                SkillCategory.CORE_PROGRAMMING: [
                    "What is the difference between a variable and a constant?",
                    "Explain the concept of loops and when to use them",
                    "What is object-oriented programming?",
                    "How do you handle errors in your code?"
                ],
                SkillCategory.WEB_TECHNOLOGIES: [
                    "What is the difference between HTML and CSS?",
                    "Explain the box model in CSS",
                    "What is responsive design?",
                    "How do you make a website accessible?"
                ]
            },
            "intermediate": {
                SkillCategory.CORE_PROGRAMMING: [
                    "Explain the difference between synchronous and asynchronous programming",
                    "What are design patterns and why are they useful?",
                    "How do you optimize code performance?",
                    "Explain the concept of recursion with an example"
                ],
                SkillCategory.DATABASES: [
                    "What is database normalization and why is it important?",
                    "Explain the difference between SQL and NoSQL databases",
                    "How do you optimize database queries?",
                    "What are database indexes and how do they work?"
                ]
            },
            "advanced": {
                SkillCategory.ARCHITECTURE_DESIGN: [
                    "How would you design a scalable system for millions of users?",
                    "Explain microservices architecture and its trade-offs",
                    "How do you handle distributed system failures?",
                    "What are the principles of clean architecture?"
                ],
                SkillCategory.AI_ML_CORE: [
                    "How do you prevent overfitting in machine learning models?",
                    "Explain the bias-variance tradeoff",
                    "How do you handle imbalanced datasets?",
                    "What are the different types of machine learning algorithms?"
                ]
            }
        }
    
    def load_job_roles_data(self) -> Dict:
        """Load job roles data from the processed dataset."""
        try:
            data_path = Path(__file__).parent.parent.parent / "data" / "processed" / "skill_gap_reference.json"
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load job roles data: {e}")
            return {}
    
    def find_matching_roles(self, target_role: str) -> List[Dict]:
        """
        Find job roles that match the target role query.
        
        Args:
            target_role: User's target role query
            
        Returns:
            List of matching job roles with their data
        """
        if not self.job_roles_data:
            return []
        
        target_lower = target_role.lower().strip()
        matching_roles = []
        
        for role_name, role_data in self.job_roles_data.items():
            role_name_lower = role_name.lower()
            
            # Direct match or partial match
            if (target_lower in role_name_lower or 
                role_name_lower in target_lower or
                any(word in role_name_lower for word in target_lower.split() if len(word) > 2)):
                
                matching_roles.append({
                    "role_name": role_name,
                    "required_skills": role_data.get("required_skills", []),
                    "experience_level": role_data.get("experience_level", "fresher"),
                    "job_count": role_data.get("job_count", 1),
                    "match_score": self.calculate_role_match_score(target_lower, role_name_lower)
                })
        
        # Sort by match score and job count
        matching_roles.sort(key=lambda x: (x["match_score"], x["job_count"]), reverse=True)
        return matching_roles[:5]  # Return top 5 matches
    
    def calculate_role_match_score(self, target: str, role_name: str) -> float:
        """Calculate how well a role name matches the target."""
        if target == role_name:
            return 1.0
        elif target in role_name or role_name in target:
            return 0.8
        else:
            # Word-based matching
            target_words = set(target.split())
            role_words = set(role_name.split())
            if target_words and role_words:
                intersection = len(target_words & role_words)
                union = len(target_words | role_words)
                return intersection / union if union > 0 else 0
            return 0
    
    def analyze_skill_gap(self, user_skills: List[str], target_role: str) -> Dict:
        """
        Perform complete skill gap analysis following the 8-step process.
        
        Args:
            user_skills: List of user's current skills
            target_role: Target job role
            
        Returns:
            Comprehensive skill gap analysis
        """
        # Step 1: Skill Normalization
        normalized_user_skills = skill_normalizer.normalize_skills_list(user_skills)
        
        # Find matching job roles
        matching_roles = self.find_matching_roles(target_role)
        
        if not matching_roles:
            return {
                "success": False,
                "error": f"No matching roles found for '{target_role}'. Please try a different role name.",
                "suggestions": ["Software Engineer", "Data Scientist", "Frontend Developer", "Backend Developer"]
            }
        
        # Use the best matching role
        best_role = matching_roles[0]
        required_skills = best_role["required_skills"]
        experience_level = best_role["experience_level"]
        
        # Normalize required skills
        normalized_required_skills = skill_normalizer.normalize_skills_list(required_skills)
        
        # Step 2: Skill Taxonomy Classification
        user_categorized = skill_taxonomy.classify_skills_list(normalized_user_skills)
        required_categorized = skill_taxonomy.classify_skills_list(normalized_required_skills)
        
        # Step 3: Intelligent Skill Matching
        matching_analysis = intelligent_skill_matcher.match_skills_comprehensive(
            normalized_user_skills, normalized_required_skills
        )
        
        # Step 4: Weighted Gap Scoring
        role_type = self.determine_role_type(target_role)
        scoring_analysis = weighted_gap_scorer.calculate_weighted_score(
            normalized_user_skills, normalized_required_skills, role_type, experience_level
        )
        
        # Step 5: Gap Analysis Output
        gap_analysis = self.create_gap_analysis_output(
            matching_analysis, scoring_analysis, best_role
        )
        
        # Step 6: Learning Roadmap Generation
        missing_skills = matching_analysis["unmatched_required_skills"]
        roadmap = learning_roadmap_generator.generate_comprehensive_roadmap(
            missing_skills, normalized_user_skills
        )
        
        # Step 7: Project Recommendation Engine
        project_recommendations = self.generate_project_recommendations(
            missing_skills, normalized_user_skills, role_type
        )
        
        # Step 8: Interview Readiness Layer
        interview_readiness = self.assess_interview_readiness(
            scoring_analysis, missing_skills, experience_level
        )
        
        return {
            "success": True,
            "analysis_timestamp": "2024-01-28T10:00:00Z",
            "target_role": best_role["role_name"],
            "role_match_confidence": best_role["match_score"],
            "alternative_roles": [role["role_name"] for role in matching_roles[1:4]],
            
            # Core Analysis Results
            "skill_gap_analysis": gap_analysis,
            "scoring_analysis": scoring_analysis,
            "learning_roadmap": roadmap,
            "project_recommendations": project_recommendations,
            "interview_readiness": interview_readiness,
            
            # Detailed Breakdowns
            "skill_matching": matching_analysis,
            "skill_categorization": {
                "user_skills": {cat.value: skills for cat, skills in user_categorized.items()},
                "required_skills": {cat.value: skills for cat, skills in required_categorized.items()}
            },
            
            # Metadata
            "analysis_metadata": {
                "total_user_skills": len(normalized_user_skills),
                "total_required_skills": len(normalized_required_skills),
                "role_experience_level": experience_level,
                "role_type": role_type,
                "job_market_data": {
                    "job_count": best_role["job_count"],
                    "demand_level": "High" if best_role["job_count"] > 10 else "Medium"
                }
            }
        }
    
    def determine_role_type(self, target_role: str) -> str:
        """Determine the type of role for weight adjustments."""
        role_lower = target_role.lower()
        
        if any(keyword in role_lower for keyword in ["frontend", "ui", "ux", "react", "angular", "vue"]):
            return "frontend"
        elif any(keyword in role_lower for keyword in ["backend", "api", "server", "database"]):
            return "backend"
        elif any(keyword in role_lower for keyword in ["mobile", "android", "ios", "app"]):
            return "mobile"
        elif any(keyword in role_lower for keyword in ["data", "scientist", "analyst", "ml", "ai"]):
            return "data"
        elif any(keyword in role_lower for keyword in ["devops", "cloud", "infrastructure", "sre"]):
            return "devops"
        elif any(keyword in role_lower for keyword in ["ai", "machine learning", "deep learning", "nlp"]):
            return "ai"
        else:
            return "general"
    
    def create_gap_analysis_output(self, matching_analysis: Dict, scoring_analysis: Dict, 
                                 role_data: Dict) -> Dict:
        """Create structured gap analysis output."""
        total_required = matching_analysis["total_required_skills"]
        total_matched = matching_analysis["total_matched_skills"]
        match_percentage = matching_analysis["match_percentage"]
        
        # Determine gap severity
        if match_percentage >= 80:
            severity = {"level": "low", "color": "#10b981"}
        elif match_percentage >= 60:
            severity = {"level": "medium", "color": "#f59e0b"}
        elif match_percentage >= 40:
            severity = {"level": "high", "color": "#f97316"}
        else:
            severity = {"level": "critical", "color": "#ef4444"}
        
        # Gap severity descriptions
        severity_descriptions = {
            "low": "Excellent skill alignment! You're very close to the job requirements.",
            "medium": "Good foundation with some skill gaps to address.",
            "high": "Significant gaps exist but achievable with focused learning.",
            "critical": "Major skill development needed to meet job requirements."
        }
        
        severity_recommendations = {
            "low": "Focus on advanced topics and start applying for positions.",
            "medium": "Dedicate 2-3 months to learning missing skills.",
            "high": "Plan a 4-6 month intensive learning program.",
            "critical": "Consider a comprehensive 6-12 month skill development plan."
        }
        
        return {
            "target_role": role_data["role_name"],
            "match_percentage": match_percentage,
            "matched_count": total_matched,
            "total_required": total_required,
            "gap_count": total_required - total_matched,
            "job_count": role_data["job_count"],
            
            "gap_severity": {
                "level": severity["level"],
                "color": severity["color"],
                "description": severity_descriptions[severity["level"]],
                "recommendation": severity_recommendations[severity["level"]]
            },
            
            "matched_skills": [
                match["required_skill"] for matches in matching_analysis["matches"].values()
                for match in matches if match["required_skill"]
            ],
            
            "missing_skills": matching_analysis["unmatched_required_skills"],
            
            "additional_skills": [
                skill for skill in matching_analysis["matches"]["no_match"]
                if skill["user_skill"] not in [m["user_skill"] for matches in matching_analysis["matches"].values() 
                                             for m in matches if m["match_type"] != "no_match"]
            ],
            
            "readiness_level": scoring_analysis["readiness_level"]
        }
    
    def generate_project_recommendations(self, missing_skills: List[str], user_skills: List[str], 
                                       role_type: str) -> List[Dict]:
        """Generate project recommendations based on missing skills."""
        recommendations = []
        
        # Categorize missing skills
        missing_categorized = skill_taxonomy.classify_skills_list(missing_skills)
        
        # Get project recommendations for each category with missing skills
        for category, skills in missing_categorized.items():
            if category in self.project_recommendations:
                category_projects = self.project_recommendations[category]
                
                for project in category_projects:
                    # Check if project skills overlap with missing skills
                    project_skills_lower = [skill.lower() for skill in project["skills_gained"]]
                    missing_skills_lower = [skill.lower() for skill in skills]
                    
                    overlap = any(
                        any(missing in project_skill or project_skill in missing 
                            for project_skill in project_skills_lower)
                        for missing in missing_skills_lower
                    )
                    
                    if overlap:
                        recommendations.append({
                            **project,
                            "category": category.value,
                            "relevant_missing_skills": [
                                skill for skill in skills 
                                if any(skill.lower() in pg.lower() or pg.lower() in skill.lower() 
                                      for pg in project["skills_gained"])
                            ]
                        })
        
        # Sort by relevance and difficulty
        difficulty_order = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
        recommendations.sort(key=lambda x: (
            len(x["relevant_missing_skills"]),  # More relevant skills first
            difficulty_order.get(x["difficulty"], 2)  # Easier projects first
        ), reverse=True)
        
        return recommendations[:6]  # Return top 6 recommendations
    
    def assess_interview_readiness(self, scoring_analysis: Dict, missing_skills: List[str], 
                                 experience_level: str) -> Dict:
        """Assess interview readiness and generate relevant questions."""
        readiness_level = scoring_analysis["readiness_level"]
        overall_score = scoring_analysis["overall_score"]
        
        # Determine interview readiness
        if readiness_level == "Job-Ready":
            readiness_status = "Ready"
            readiness_description = "You're well-prepared for technical interviews!"
        elif readiness_level == "Interview-Ready":
            readiness_status = "Mostly Ready"
            readiness_description = "You can handle most interview questions with some preparation."
        else:
            readiness_status = "Needs Preparation"
            readiness_description = "Focus on building core skills before interviewing."
        
        # Generate relevant interview questions
        questions = []
        
        # Categorize missing skills to determine question difficulty
        missing_categorized = skill_taxonomy.classify_skills_list(missing_skills)
        
        # Determine question level based on experience and readiness
        if experience_level in ["fresher", "junior"] or overall_score < 50:
            question_level = "beginner"
        elif overall_score < 75:
            question_level = "intermediate"
        else:
            question_level = "advanced"
        
        # Get questions for categories with missing skills
        for category in missing_categorized.keys():
            if category in self.interview_questions.get(question_level, {}):
                category_questions = self.interview_questions[question_level][category]
                questions.extend([
                    {
                        "question": q,
                        "category": category.value,
                        "difficulty": question_level,
                        "focus_area": "Missing skill area"
                    }
                    for q in category_questions[:2]  # 2 questions per category
                ])
        
        # Add general questions if not enough specific ones
        if len(questions) < 4:
            general_questions = [
                {
                    "question": "Tell me about a challenging project you worked on",
                    "category": "General",
                    "difficulty": "general",
                    "focus_area": "Experience and problem-solving"
                },
                {
                    "question": "How do you stay updated with new technologies?",
                    "category": "General", 
                    "difficulty": "general",
                    "focus_area": "Learning and growth mindset"
                }
            ]
            questions.extend(general_questions)
        
        return {
            "readiness_status": readiness_status,
            "readiness_description": readiness_description,
            "overall_score": overall_score,
            "readiness_level": readiness_level,
            
            "interview_questions": questions[:8],  # Top 8 questions
            
            "preparation_tips": [
                "Practice coding problems on platforms like LeetCode or HackerRank",
                "Review fundamental concepts in your missing skill areas",
                "Prepare examples of projects that demonstrate your skills",
                "Practice explaining technical concepts in simple terms",
                "Research the company and role-specific requirements"
            ],
            
            "confidence_boosters": [
                f"You have {len(scoring_analysis.get('skill_scores', {}))} relevant skills",
                f"Your {readiness_level.lower()} status shows good progress",
                "Focus on your strengths while addressing gaps",
                "Every interview is a learning opportunity"
            ]
        }

# Global instance for easy import
skill_gap_analyzer = SkillGapAnalyzer()