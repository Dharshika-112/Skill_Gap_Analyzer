"""
Real Job Dataset Loader
Loads and processes the actual job dataset CSV file
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Set
import re
from ..core.database import get_collection
from datetime import datetime

# Path to the job dataset
DATASET_PATH = Path(__file__).parents[2] / 'data' / 'raw' / 'job_dataset.csv'

class JobDatasetLoader:
    def __init__(self):
        self.df = None
        self.skills_cache = None
        self.roles_cache = None
        self.load_dataset()
    
    def load_dataset(self):
        """Load the job dataset from CSV"""
        try:
            if DATASET_PATH.exists():
                self.df = pd.read_csv(DATASET_PATH)
                print(f"[INFO] Loaded job dataset: {len(self.df)} jobs, {self.df['Title'].nunique()} unique roles")
            else:
                print(f"[WARNING] Job dataset not found at {DATASET_PATH}")
                self.df = None
        except Exception as e:
            print(f"[ERROR] Failed to load job dataset: {e}")
            self.df = None
    
    def get_all_skills(self) -> List[str]:
        """Extract all unique skills from the dataset"""
        if self.skills_cache:
            return self.skills_cache
            
        if self.df is None:
            return []
        
        all_skills = set()
        
        # Extract from Skills column
        for skills_str in self.df['Skills'].dropna():
            if pd.isna(skills_str) or not isinstance(skills_str, str):
                continue
            # Split by semicolon and clean
            skills = [s.strip() for s in str(skills_str).split(';') if s.strip()]
            all_skills.update(skills)
        
        # Extract from Keywords column
        for keywords_str in self.df['Keywords'].dropna():
            if pd.isna(keywords_str) or not isinstance(keywords_str, str):
                continue
            # Split by semicolon and clean
            keywords = [k.strip() for k in str(keywords_str).split(';') if k.strip()]
            all_skills.update(keywords)
        
        # Clean and filter skills
        cleaned_skills = []
        for skill in all_skills:
            if skill and len(skill.strip()) > 1:
                # Remove common non-technical words
                skill_lower = skill.lower().strip()
                if not any(word in skill_lower for word in ['basics', 'fundamentals', 'under guidance', 'with mentors']):
                    cleaned_skills.append(skill.strip())
        
        self.skills_cache = sorted(list(set(cleaned_skills)))
        return self.skills_cache
    
    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Get all unique job roles with their details"""
        if self.roles_cache:
            return self.roles_cache
            
        if self.df is None:
            return []
        
        # Group by Title and get representative data
        roles = []
        for title in self.df['Title'].dropna().unique():
            if pd.isna(title) or title == 'nan':
                continue
                
            role_data = self.df[self.df['Title'] == title].iloc[0]
            
            roles.append({
                'title': str(title).strip(),
                'experience_levels': list(self.df[self.df['Title'] == title]['ExperienceLevel'].dropna().unique()),
                'skills': self._extract_skills_for_role(title),
                'sample_responsibilities': str(role_data.get('Responsibilities', '')),
                'job_count': len(self.df[self.df['Title'] == title])
            })
        
        self.roles_cache = sorted(roles, key=lambda x: x['job_count'], reverse=True)
        return self.roles_cache
    
    def _extract_skills_for_role(self, role_title: str) -> List[str]:
        """Extract all skills required for a specific role"""
        role_jobs = self.df[self.df['Title'] == role_title]
        all_skills = set()
        
        for _, job in role_jobs.iterrows():
            # From Skills column
            if pd.notna(job['Skills']):
                skills = [s.strip() for s in str(job['Skills']).split(';') if s.strip()]
                all_skills.update(skills)
            
            # From Keywords column
            if pd.notna(job['Keywords']):
                keywords = [k.strip() for k in str(job['Keywords']).split(';') if k.strip()]
                all_skills.update(keywords)
        
        # Clean skills
        cleaned_skills = []
        for skill in all_skills:
            if skill and len(skill.strip()) > 1:
                skill_lower = skill.lower().strip()
                if not any(word in skill_lower for word in ['basics', 'fundamentals', 'under guidance']):
                    cleaned_skills.append(skill.strip())
        
        return sorted(list(set(cleaned_skills)))
    
    def get_role_requirements(self, role_title: str) -> Dict[str, Any]:
        """Get detailed requirements for a specific role"""
        if self.df is None:
            return {}
        
        role_jobs = self.df[self.df['Title'] == role_title]
        if role_jobs.empty:
            return {}
        
        skills = self._extract_skills_for_role(role_title)
        experience_levels = list(role_jobs['ExperienceLevel'].dropna().unique())
        
        # Get years of experience range
        years_data = []
        for years_str in role_jobs['YearsOfExperience'].dropna():
            if pd.notna(years_str):
                # Extract numbers from strings like "0-1", "2-4", "5+"
                numbers = re.findall(r'\d+', str(years_str))
                if numbers:
                    years_data.extend([int(n) for n in numbers])
        
        return {
            'title': role_title,
            'required_skills': skills,
            'experience_levels': experience_levels,
            'years_range': {
                'min': min(years_data) if years_data else 0,
                'max': max(years_data) if years_data else 0
            },
            'total_jobs': len(role_jobs),
            'sample_responsibilities': role_jobs.iloc[0]['Responsibilities'] if not role_jobs.empty else ''
        }
    
    def find_matching_roles(self, user_skills: List[str], top_n: int = 10) -> List[Dict[str, Any]]:
        """Find roles that best match user skills"""
        if self.df is None:
            return []
        
        user_skills_lower = [s.lower().strip() for s in user_skills]
        role_matches = []
        
        for role in self.get_all_roles():
            role_skills = [s.lower().strip() for s in role['skills']]
            
            # Calculate match metrics
            matching_skills = [s for s in user_skills_lower if s in role_skills]
            match_count = len(matching_skills)
            total_role_skills = len(role_skills)
            
            if total_role_skills > 0:
                match_percentage = (match_count / total_role_skills) * 100
                
                role_matches.append({
                    'role': role['title'],
                    'match_percentage': round(match_percentage, 2),
                    'matching_skills_count': match_count,
                    'total_required_skills': total_role_skills,
                    'matching_skills': [s for s in user_skills if s.lower() in [ms.lower() for ms in matching_skills]],
                    'missing_skills': [s for s in role['skills'] if s.lower() not in user_skills_lower],
                    'experience_levels': role['experience_levels'],
                    'job_count': role['job_count']
                })
        
        # Sort by match percentage and job count
        role_matches.sort(key=lambda x: (x['match_percentage'], x['job_count']), reverse=True)
        return role_matches[:top_n]
    
    def calculate_resume_score(self, user_skills: List[str]) -> Dict[str, Any]:
        """Calculate overall resume score based on dataset"""
        if self.df is None or not user_skills:
            return {'score': 0, 'details': 'No data available'}
        
        all_dataset_skills = self.get_all_skills()
        user_skills_lower = [s.lower().strip() for s in user_skills]
        dataset_skills_lower = [s.lower().strip() for s in all_dataset_skills]
        
        # Calculate coverage
        matching_skills = [s for s in user_skills_lower if s in dataset_skills_lower]
        skill_coverage = len(matching_skills) / len(all_dataset_skills) * 100 if all_dataset_skills else 0
        
        # Calculate relevance (how many of user's skills are in dataset)
        skill_relevance = len(matching_skills) / len(user_skills) * 100 if user_skills else 0
        
        # Overall score (weighted average)
        overall_score = (skill_coverage * 0.3 + skill_relevance * 0.7)
        
        # Determine score category
        if overall_score >= 80:
            category = "Excellent"
        elif overall_score >= 60:
            category = "Good"
        elif overall_score >= 40:
            category = "Average"
        elif overall_score >= 20:
            category = "Below Average"
        else:
            category = "Needs Improvement"
        
        return {
            'overall_score': round(overall_score, 2),
            'category': category,
            'skill_coverage': round(skill_coverage, 2),
            'skill_relevance': round(skill_relevance, 2),
            'total_skills_in_resume': len(user_skills),
            'matching_skills_count': len(matching_skills),
            'total_dataset_skills': len(all_dataset_skills),
            'matching_skills': [s for s in user_skills if s.lower() in [ms.lower() for ms in matching_skills]]
        }

# Global instance
dataset_loader = JobDatasetLoader()

# Convenience functions
def get_all_skills_from_dataset() -> List[str]:
    """Get all skills from the job dataset"""
    return dataset_loader.get_all_skills()

def get_all_roles_from_dataset() -> List[Dict[str, Any]]:
    """Get all roles from the job dataset"""
    return dataset_loader.get_all_roles()

def get_role_requirements_from_dataset(role_title: str) -> Dict[str, Any]:
    """Get requirements for a specific role"""
    return dataset_loader.get_role_requirements(role_title)

def find_matching_roles_from_dataset(user_skills: List[str], top_n: int = 10) -> List[Dict[str, Any]]:
    """Find matching roles from dataset"""
    return dataset_loader.find_matching_roles(user_skills, top_n)

def calculate_resume_score_from_dataset(user_skills: List[str]) -> Dict[str, Any]:
    """Calculate resume score based on dataset"""
    return dataset_loader.calculate_resume_score(user_skills)