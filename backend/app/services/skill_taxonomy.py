"""
Skill Gap Analyzer - Step 2: Skill Taxonomy Classification
CareerBoost AI - Professional Skill Categorization System

This module implements the second step of the 8-step skill gap analysis process:
- Groups skills into professional categories
- Provides hierarchical skill classification
- Supports weighted analysis by category importance
"""

from typing import Dict, List, Set
from enum import Enum

class SkillCategory(Enum):
    """Professional skill categories for classification."""
    CORE_PROGRAMMING = "Core Programming"
    FRAMEWORKS = "Frameworks"
    DATABASES = "Databases"
    TESTING = "Testing"
    DEVOPS_CLOUD = "DevOps & Cloud"
    ARCHITECTURE_DESIGN = "Architecture & Design"
    FRONTEND = "Frontend"
    AI_ML_CORE = "AI/ML Core"
    NLP_CV = "NLP / Computer Vision"
    SOFT_COGNITIVE = "Soft & Cognitive Skills"
    MOBILE = "Mobile Development"
    WEB_TECHNOLOGIES = "Web Technologies"
    DATA_ANALYTICS = "Data & Analytics"
    SECURITY = "Security"
    METHODOLOGIES = "Methodologies"

class SkillTaxonomy:
    def __init__(self):
        """Initialize skill taxonomy with comprehensive categorization."""
        self.skill_categories = {
            SkillCategory.CORE_PROGRAMMING: {
                "skills": [
                    "python", "java", "javascript", "c#", "c++", "c", "go", "rust",
                    "typescript", "php", "ruby", "scala", "kotlin", "swift",
                    "r", "matlab", "perl", "shell scripting", "bash", "powershell"
                ],
                "weight": 0.25,  # 25% importance
                "description": "Fundamental programming languages and scripting"
            },
            
            SkillCategory.FRAMEWORKS: {
                "skills": [
                    "react", "angular", "vue", "django", "flask", "fastapi",
                    "spring boot", "asp.net", ".net core", ".net framework",
                    "express.js", "node.js", "laravel", "rails", "hibernate",
                    "tensorflow", "pytorch", "scikit-learn", "keras"
                ],
                "weight": 0.20,  # 20% importance
                "description": "Application frameworks and libraries"
            },
            
            SkillCategory.DATABASES: {
                "skills": [
                    "sql", "mysql", "postgresql", "mongodb", "redis", "cassandra",
                    "elasticsearch", "oracle", "sql server", "sqlite", "nosql",
                    "dynamodb", "neo4j", "influxdb", "bigquery", "snowflake"
                ],
                "weight": 0.15,  # 15% importance
                "description": "Database systems and data storage"
            },
            
            SkillCategory.TESTING: {
                "skills": [
                    "unit testing", "integration testing", "selenium", "jest",
                    "pytest", "junit", "testng", "cypress", "mocha", "jasmine",
                    "postman", "api testing", "automation testing", "tdd", "bdd"
                ],
                "weight": 0.10,  # 10% importance
                "description": "Testing frameworks and methodologies"
            },
            
            SkillCategory.DEVOPS_CLOUD: {
                "skills": [
                    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
                    "terraform", "ansible", "chef", "puppet", "gitlab ci",
                    "github actions", "circleci", "helm", "prometheus", "grafana",
                    "elk stack", "cicd", "cloudformation"
                ],
                "weight": 0.15,  # 15% importance
                "description": "Cloud platforms and DevOps tools"
            },
            
            SkillCategory.ARCHITECTURE_DESIGN: {
                "skills": [
                    "microservices", "design patterns", "system design", "api design",
                    "rest api", "graphql", "solid principles", "clean architecture",
                    "distributed systems", "scalability", "performance optimization",
                    "load balancing", "caching", "message queues"
                ],
                "weight": 0.12,  # 12% importance
                "description": "System architecture and design principles"
            },
            
            SkillCategory.FRONTEND: {
                "skills": [
                    "html", "css", "javascript", "react", "angular", "vue",
                    "bootstrap", "tailwind css", "sass", "less", "webpack",
                    "responsive design", "ui/ux", "figma", "adobe xd"
                ],
                "weight": 0.10,  # 10% importance (varies by role)
                "description": "Frontend technologies and UI/UX design"
            },
            
            SkillCategory.AI_ML_CORE: {
                "skills": [
                    "machine learning", "deep learning", "neural networks",
                    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
                    "data science", "statistics", "linear algebra", "calculus",
                    "feature engineering", "model training", "hyperparameter tuning"
                ],
                "weight": 0.20,  # 20% importance for AI roles
                "description": "Core AI/ML technologies and concepts"
            },
            
            SkillCategory.NLP_CV: {
                "skills": [
                    "natural language processing", "computer vision", "opencv",
                    "nltk", "spacy", "transformers", "bert", "gpt", "llm",
                    "image processing", "text mining", "sentiment analysis",
                    "object detection", "image classification"
                ],
                "weight": 0.15,  # 15% importance for specialized AI roles
                "description": "Specialized AI domains: NLP and Computer Vision"
            },
            
            SkillCategory.SOFT_COGNITIVE: {
                "skills": [
                    "communication", "leadership", "teamwork", "problem solving",
                    "critical thinking", "project management", "time management",
                    "adaptability", "creativity", "analytical thinking",
                    "collaboration", "mentoring", "presentation skills"
                ],
                "weight": 0.08,  # 8% importance
                "description": "Soft skills and cognitive abilities"
            },
            
            SkillCategory.MOBILE: {
                "skills": [
                    "android", "ios", "react native", "flutter", "xamarin",
                    "swift", "kotlin", "objective-c", "mobile ui/ux",
                    "app store optimization", "mobile testing"
                ],
                "weight": 0.15,  # 15% importance for mobile roles
                "description": "Mobile development platforms and tools"
            },
            
            SkillCategory.WEB_TECHNOLOGIES: {
                "skills": [
                    "html", "css", "javascript", "rest api", "graphql",
                    "websockets", "ajax", "json", "xml", "http/https",
                    "oauth", "jwt", "cors", "web security"
                ],
                "weight": 0.12,  # 12% importance
                "description": "Web protocols and technologies"
            },
            
            SkillCategory.DATA_ANALYTICS: {
                "skills": [
                    "data analysis", "tableau", "power bi", "excel", "r",
                    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
                    "data visualization", "statistics", "etl", "data warehousing",
                    "business intelligence", "reporting"
                ],
                "weight": 0.18,  # 18% importance for data roles
                "description": "Data analysis and visualization tools"
            },
            
            SkillCategory.SECURITY: {
                "skills": [
                    "cybersecurity", "penetration testing", "ethical hacking",
                    "encryption", "ssl/tls", "oauth", "jwt", "firewall",
                    "vulnerability assessment", "security auditing",
                    "compliance", "gdpr", "hipaa", "pci dss"
                ],
                "weight": 0.12,  # 12% importance
                "description": "Security and compliance technologies"
            },
            
            SkillCategory.METHODOLOGIES: {
                "skills": [
                    "agile", "scrum", "kanban", "waterfall", "devops",
                    "lean", "six sigma", "design thinking", "user research",
                    "a/b testing", "continuous integration", "continuous deployment"
                ],
                "weight": 0.08,  # 8% importance
                "description": "Development and project methodologies"
            }
        }
        
        # Create reverse mapping for quick lookup
        self.skill_to_category = {}
        for category, data in self.skill_categories.items():
            for skill in data["skills"]:
                if skill not in self.skill_to_category:
                    self.skill_to_category[skill] = []
                self.skill_to_category[skill].append(category)
    
    def classify_skill(self, skill: str) -> List[SkillCategory]:
        """
        Classify a skill into one or more categories.
        
        Args:
            skill: Normalized skill name
            
        Returns:
            List of categories this skill belongs to
        """
        skill_lower = skill.lower().strip()
        categories = self.skill_to_category.get(skill_lower, [])
        
        # If no direct match, try partial matching
        if not categories:
            for category, data in self.skill_categories.items():
                for category_skill in data["skills"]:
                    if (skill_lower in category_skill.lower() or 
                        category_skill.lower() in skill_lower):
                        categories.append(category)
                        break
        
        return categories if categories else [SkillCategory.CORE_PROGRAMMING]  # Default category
    
    def classify_skills_list(self, skills: List[str]) -> Dict[SkillCategory, List[str]]:
        """
        Classify a list of skills into categories.
        
        Args:
            skills: List of normalized skill names
            
        Returns:
            Dictionary mapping categories to skills
        """
        categorized = {category: [] for category in SkillCategory}
        
        for skill in skills:
            categories = self.classify_skill(skill)
            for category in categories:
                if skill not in categorized[category]:
                    categorized[category].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def get_category_weight(self, category: SkillCategory, role_type: str = "general") -> float:
        """
        Get the weight/importance of a category for a specific role type.
        
        Args:
            category: Skill category
            role_type: Type of role (e.g., "ai", "frontend", "backend", "mobile")
            
        Returns:
            Weight value between 0 and 1
        """
        base_weight = self.skill_categories[category]["weight"]
        
        # Adjust weights based on role type
        role_adjustments = {
            "ai": {
                SkillCategory.AI_ML_CORE: 1.5,
                SkillCategory.NLP_CV: 1.3,
                SkillCategory.DATA_ANALYTICS: 1.2,
                SkillCategory.FRONTEND: 0.5
            },
            "frontend": {
                SkillCategory.FRONTEND: 1.8,
                SkillCategory.WEB_TECHNOLOGIES: 1.5,
                SkillCategory.FRAMEWORKS: 1.3,
                SkillCategory.AI_ML_CORE: 0.3
            },
            "backend": {
                SkillCategory.CORE_PROGRAMMING: 1.4,
                SkillCategory.DATABASES: 1.5,
                SkillCategory.ARCHITECTURE_DESIGN: 1.3,
                SkillCategory.FRONTEND: 0.4
            },
            "mobile": {
                SkillCategory.MOBILE: 2.0,
                SkillCategory.FRONTEND: 1.2,
                SkillCategory.DATABASES: 0.8
            },
            "devops": {
                SkillCategory.DEVOPS_CLOUD: 2.0,
                SkillCategory.SECURITY: 1.3,
                SkillCategory.FRONTEND: 0.3
            },
            "data": {
                SkillCategory.DATA_ANALYTICS: 1.8,
                SkillCategory.AI_ML_CORE: 1.4,
                SkillCategory.DATABASES: 1.3
            }
        }
        
        adjustment = role_adjustments.get(role_type, {}).get(category, 1.0)
        return min(base_weight * adjustment, 1.0)  # Cap at 1.0
    
    def get_category_coverage(self, user_skills: List[str], required_skills: List[str]) -> Dict:
        """
        Calculate category-wise skill coverage.
        
        Args:
            user_skills: List of user's skills
            required_skills: List of required skills
            
        Returns:
            Dictionary with category coverage analysis
        """
        user_categorized = self.classify_skills_list(user_skills)
        required_categorized = self.classify_skills_list(required_skills)
        
        coverage = {}
        
        for category in SkillCategory:
            user_cat_skills = set(user_categorized.get(category, []))
            required_cat_skills = set(required_categorized.get(category, []))
            
            if required_cat_skills:
                matched = user_cat_skills & required_cat_skills
                coverage_percentage = len(matched) / len(required_cat_skills) * 100
                
                coverage[category.value] = {
                    "required_count": len(required_cat_skills),
                    "matched_count": len(matched),
                    "coverage_percentage": round(coverage_percentage, 1),
                    "matched_skills": list(matched),
                    "missing_skills": list(required_cat_skills - user_cat_skills),
                    "weight": self.skill_categories[category]["weight"]
                }
        
        return coverage
    
    def get_skill_hierarchy(self, skill: str) -> Dict:
        """
        Get hierarchical information about a skill.
        
        Args:
            skill: Skill name
            
        Returns:
            Dictionary with hierarchy information
        """
        categories = self.classify_skill(skill)
        
        return {
            "skill": skill,
            "categories": [cat.value for cat in categories],
            "primary_category": categories[0].value if categories else "Unknown",
            "importance_weight": self.skill_categories[categories[0]]["weight"] if categories else 0.1
        }

# Global instance for easy import
skill_taxonomy = SkillTaxonomy()