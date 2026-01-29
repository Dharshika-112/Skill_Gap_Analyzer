"""
Skill Gap Analyzer - Step 1: Skill Normalization Layer
CareerBoost AI - Advanced Skill Normalization Service

This module implements the first step of the 8-step skill gap analysis process:
- Converts skills to lowercase
- Trims spaces and removes duplicates
- Standardizes variants using synonym mapping
- Applies normalization to both job requirements and user input
"""

import re
import json
from typing import List, Dict, Set
from pathlib import Path

class SkillNormalizer:
    def __init__(self):
        """Initialize the skill normalizer with synonym mappings."""
        self.skill_synonyms = {
            # .NET Technologies
            ".net": [".net", "dot net", ".net framework", "dotnet"],
            ".net core": [".net core", "asp.net core", "dotnet core"],
            "asp.net": ["asp.net", "aspnet", "asp net"],
            "c#": ["c#", "csharp", "c sharp"],
            
            # JavaScript & Frameworks
            "javascript": ["javascript", "js", "ecmascript"],
            "typescript": ["typescript", "ts"],
            "react": ["react", "reactjs", "react.js"],
            "angular": ["angular", "angularjs", "angular.js"],
            "vue": ["vue", "vuejs", "vue.js"],
            "node.js": ["node.js", "nodejs", "node js"],
            
            # Python & Frameworks
            "python": ["python", "py"],
            "django": ["django", "django framework"],
            "flask": ["flask", "flask framework"],
            "fastapi": ["fastapi", "fast api"],
            
            # Databases
            "sql": ["sql", "structured query language"],
            "mysql": ["mysql", "my sql"],
            "postgresql": ["postgresql", "postgres", "postgre sql"],
            "mongodb": ["mongodb", "mongo db", "mongo"],
            "nosql": ["nosql", "no sql", "non-sql"],
            
            # Cloud Platforms
            "aws": ["aws", "amazon web services", "amazon aws"],
            "azure": ["azure", "microsoft azure", "ms azure"],
            "gcp": ["gcp", "google cloud platform", "google cloud"],
            
            # DevOps & Tools
            "docker": ["docker", "containerization"],
            "kubernetes": ["kubernetes", "k8s", "kube"],
            "jenkins": ["jenkins", "jenkins ci/cd"],
            "git": ["git", "version control"],
            "github": ["github", "git hub"],
            "gitlab": ["gitlab", "git lab"],
            
            # Testing
            "unit testing": ["unit testing", "unit tests", "testing"],
            "selenium": ["selenium", "selenium webdriver"],
            "jest": ["jest", "jest testing"],
            "pytest": ["pytest", "py test"],
            
            # Machine Learning & AI
            "machine learning": ["machine learning", "ml", "artificial intelligence", "ai"],
            "tensorflow": ["tensorflow", "tensor flow"],
            "pytorch": ["pytorch", "torch"],
            "scikit-learn": ["scikit-learn", "sklearn", "scikitlearn"],
            "pandas": ["pandas", "python pandas"],
            "numpy": ["numpy", "numerical python"],
            
            # Web Technologies
            "html": ["html", "html5", "hypertext markup language"],
            "css": ["css", "css3", "cascading style sheets"],
            "rest api": ["rest api", "restful api", "rest apis", "api"],
            "graphql": ["graphql", "graph ql"],
            
            # Mobile Development
            "android": ["android", "android development"],
            "ios": ["ios", "ios development"],
            "react native": ["react native", "react-native"],
            "flutter": ["flutter", "dart flutter"],
            
            # Data & Analytics
            "data analysis": ["data analysis", "data analytics"],
            "tableau": ["tableau", "tableau desktop"],
            "power bi": ["power bi", "powerbi", "microsoft power bi"],
            "excel": ["excel", "microsoft excel", "ms excel"],
            
            # Soft Skills
            "communication": ["communication", "communication skills"],
            "leadership": ["leadership", "team leadership"],
            "problem solving": ["problem solving", "problem-solving", "problemsolving"],
            "teamwork": ["teamwork", "team work", "collaboration"],
            "project management": ["project management", "pm", "project planning"],
            
            # Methodologies
            "agile": ["agile", "agile methodology", "agile development"],
            "scrum": ["scrum", "scrum methodology"],
            "devops": ["devops", "dev ops", "development operations"],
            "cicd": ["cicd", "ci/cd", "continuous integration", "continuous deployment"],
        }
        
        # Create reverse mapping for faster lookup
        self.normalized_mapping = {}
        for normalized, variants in self.skill_synonyms.items():
            for variant in variants:
                self.normalized_mapping[variant.lower().strip()] = normalized
    
    def normalize_skill(self, skill: str) -> str:
        """
        Normalize a single skill string.
        
        Args:
            skill: Raw skill string
            
        Returns:
            Normalized skill string
        """
        if not skill or not isinstance(skill, str):
            return ""
        
        # Step 1: Convert to lowercase and trim spaces
        cleaned = skill.lower().strip()
        
        # Step 2: Remove extra whitespace and special characters
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'[^\w\s\.\-\+\#]', '', cleaned)
        
        # Step 3: Apply synonym mapping
        if cleaned in self.normalized_mapping:
            return self.normalized_mapping[cleaned]
        
        # Step 4: Handle partial matches for compound skills
        for normalized, variants in self.skill_synonyms.items():
            for variant in variants:
                if variant.lower() in cleaned or cleaned in variant.lower():
                    return normalized
        
        return cleaned
    
    def normalize_skills_list(self, skills: List[str]) -> List[str]:
        """
        Normalize a list of skills and remove duplicates.
        
        Args:
            skills: List of raw skill strings
            
        Returns:
            List of normalized, deduplicated skills
        """
        if not skills:
            return []
        
        normalized_skills = []
        seen_skills = set()
        
        for skill in skills:
            normalized = self.normalize_skill(skill)
            if normalized and normalized not in seen_skills:
                normalized_skills.append(normalized)
                seen_skills.add(normalized)
        
        return sorted(normalized_skills)
    
    def normalize_job_requirements(self, job_data: Dict) -> Dict:
        """
        Normalize skills in job requirement data.
        
        Args:
            job_data: Dictionary containing job information with required_skills
            
        Returns:
            Updated job data with normalized skills
        """
        if "required_skills" in job_data:
            job_data["required_skills_normalized"] = self.normalize_skills_list(
                job_data["required_skills"]
            )
        
        return job_data
    
    def get_skill_variants(self, normalized_skill: str) -> List[str]:
        """
        Get all variants of a normalized skill.
        
        Args:
            normalized_skill: The normalized skill name
            
        Returns:
            List of all variants for this skill
        """
        return self.skill_synonyms.get(normalized_skill, [normalized_skill])
    
    def is_skill_match(self, user_skill: str, required_skill: str, threshold: float = 0.85) -> bool:
        """
        Check if user skill matches required skill using normalization.
        
        Args:
            user_skill: User's skill
            required_skill: Required skill from job
            threshold: Similarity threshold for fuzzy matching
            
        Returns:
            True if skills match
        """
        user_normalized = self.normalize_skill(user_skill)
        required_normalized = self.normalize_skill(required_skill)
        
        # Exact match
        if user_normalized == required_normalized:
            return True
        
        # Check if they're variants of the same skill
        user_variants = self.get_skill_variants(user_normalized)
        required_variants = self.get_skill_variants(required_normalized)
        
        return bool(set(user_variants) & set(required_variants))
    
    def get_normalization_stats(self, skills: List[str]) -> Dict:
        """
        Get statistics about skill normalization.
        
        Args:
            skills: List of raw skills
            
        Returns:
            Dictionary with normalization statistics
        """
        original_count = len(skills)
        normalized = self.normalize_skills_list(skills)
        normalized_count = len(normalized)
        
        return {
            "original_count": original_count,
            "normalized_count": normalized_count,
            "duplicates_removed": original_count - normalized_count,
            "normalization_rate": (original_count - normalized_count) / original_count if original_count > 0 else 0
        }

# Global instance for easy import
skill_normalizer = SkillNormalizer()