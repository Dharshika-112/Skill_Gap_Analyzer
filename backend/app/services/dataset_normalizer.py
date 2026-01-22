"""
Dataset Loader and Normalizer
Processes Kaggle dataset and normalizes skills/roles for ML
"""

import pandas as pd
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import re
from collections import Counter

class DatasetNormalizer:
    """Load, normalize, and process Kaggle dataset"""
    
    def __init__(self):
        self.jobs_df = None
        self.skills_vocabulary = set()
        self.role_mapping = {}
        self.skill_normalization_map = {}
        
    def load_kaggle_dataset(self, file_path: str):
        """
        Load CSV dataset from Kaggle
        Expected columns: JobID, Title, ExperienceLevel, YearsOfExperience, Skills, Responsibilities, Keywords
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dataset not found at {file_path}")
            
            print(f"[*] Loading dataset from {file_path}...")
            self.jobs_df = pd.read_csv(file_path)
            
            print(f"[OK] Loaded {len(self.jobs_df)} job records")
            print(f"[OK] Columns: {list(self.jobs_df.columns)}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load dataset: {e}")
            return False
    
    def normalize_skills(self):
        """Extract and normalize all skills from dataset"""
        try:
            print("[*] Normalizing skills...")
            
            if self.jobs_df is None:
                raise ValueError("Dataset not loaded")
            
            # Extract skills from various columns
            all_skills = []
            
            # From 'Skills' column (main source)
            if 'Skills' in self.jobs_df.columns:
                for skills_str in self.jobs_df['Skills'].dropna():
                    if isinstance(skills_str, str):
                        # Handle different formats: "python, java, sql" or "[python, java]"
                        skills = self._parse_skills_string(skills_str)
                        all_skills.extend(skills)
            
            # From 'Keywords' column
            if 'Keywords' in self.jobs_df.columns:
                for keywords_str in self.jobs_df['Keywords'].dropna():
                    if isinstance(keywords_str, str):
                        keywords = self._parse_skills_string(keywords_str)
                        all_skills.extend(keywords)
            
            # From 'Responsibilities' (extract skill-like words)
            if 'Responsibilities' in self.jobs_df.columns:
                for resp_str in self.jobs_df['Responsibilities'].dropna():
                    if isinstance(resp_str, str):
                        skills = self._extract_tech_skills(resp_str)
                        all_skills.extend(skills)
            
            # Normalize and deduplicate
            normalized_skills = set()
            for skill in all_skills:
                normalized = self._normalize_skill_name(skill)
                if len(normalized) > 2:  # Skip very short strings
                    normalized_skills.add(normalized)
            
            self.skills_vocabulary = normalized_skills
            print(f"[OK] Found and normalized {len(normalized_skills)} unique skills")
            
            return list(normalized_skills)
        except Exception as e:
            print(f"[ERROR] Skill normalization failed: {e}")
            return []
    
    def _parse_skills_string(self, skills_str: str) -> List[str]:
        """Parse skills from various string formats"""
        # Remove brackets and quotes
        skills_str = skills_str.strip("[]'\"")
        
        # Split by common delimiters
        skills = re.split(r'[,;/\|]', skills_str)
        
        # Clean and filter
        cleaned = []
        for skill in skills:
            skill = skill.strip().lower()
            if skill and len(skill) > 1:
                cleaned.append(skill)
        
        return cleaned
    
    def _extract_tech_skills(self, text: str) -> List[str]:
        """Extract technology-related keywords from text"""
        # Common tech keywords
        tech_keywords = [
            'python', 'java', 'javascript', 'sql', 'nosql', 'mongodb', 'postgresql',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'cloud', 'react', 'angular',
            'node', 'express', 'django', 'flask', 'spring', 'git', 'api', 'rest',
            'graphql', 'machine learning', 'deep learning', 'ai', 'ml', 'nlp', 'cv',
            'data', 'analytics', 'hadoop', 'spark', 'kafka', 'redis', 'elasticsearch',
            'ci/cd', 'devops', 'agile', 'scrum', 'linux', 'windows', 'terraform',
            'ansible', 'jenkins', 'gitlab', 'github', 'tfs', 'jira'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                found_skills.append(keyword)
        
        return found_skills
    
    def _normalize_skill_name(self, skill: str) -> str:
        """Normalize skill name (js→javascript, sql→SQL, etc)"""
        skill = skill.strip().lower()
        
        # Common mappings
        mapping = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'cpp': 'c++',
            'c#': 'csharp',
            'obj-c': 'objective-c',
            'asp': 'asp.net',
            'mssql': 'sql server',
            'mysql': 'mysql',
            'pg': 'postgresql',
            'mongo': 'mongodb',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'cv': 'computer vision',
            'nlp': 'natural language processing',
            'rnn': 'recurrent neural network',
            'cnn': 'convolutional neural network',
            'dl': 'deep learning',
            'dsa': 'data structures',
            'oop': 'object oriented programming',
            'ci/cd': 'continuous integration/deployment',
            'etl': 'extract transform load'
        }
        
        return mapping.get(skill, skill)
    
    def extract_roles(self) -> Dict[str, List[str]]:
        """Extract and categorize roles from dataset"""
        try:
            print("[*] Extracting roles...")
            
            if self.jobs_df is None:
                raise ValueError("Dataset not loaded")
            
            roles_by_level = {
                'fresher': [],
                'junior': [],
                'mid-level': [],
                'senior': [],
                'lead': []
            }
            
            experience_mapping = {
                'fresher': 'fresher',
                'intern': 'fresher',
                '0-1': 'fresher',
                'junior': 'junior',
                '1-3': 'junior',
                'mid': 'mid-level',
                'middle': 'mid-level',
                '3-5': 'mid-level',
                'senior': 'senior',
                '5-10': 'senior',
                'experienced': 'senior',
                'lead': 'lead',
                'principal': 'lead',
                '10+': 'lead'
            }
            
            # Extract from Title and ExperienceLevel
            for idx, row in self.jobs_df.iterrows():
                title = str(row.get('Title', ''))
                exp_level = str(row.get('ExperienceLevel', '')).lower()
                
                # Determine experience level
                determined_level = 'mid-level'  # Default
                for key, level in experience_mapping.items():
                    if key in exp_level:
                        determined_level = level
                        break
                
                # Add role
                if title:
                    roles_by_level[determined_level].append(title)
            
            # Deduplicate
            for level in roles_by_level:
                roles_by_level[level] = list(set(roles_by_level[level]))
            
            self.role_mapping = roles_by_level
            
            total_roles = sum(len(roles) for roles in roles_by_level.values())
            print(f"[OK] Found {total_roles} roles across {len(roles_by_level)} experience levels")
            
            return roles_by_level
        except Exception as e:
            print(f"[ERROR] Role extraction failed: {e}")
            return {}
    
    def get_role_skills(self, role_title: str) -> List[str]:
        """Get skills required for a specific role"""
        try:
            if self.jobs_df is None:
                return []
            
            # Find matching role in dataset
            role_rows = self.jobs_df[self.jobs_df['Title'].str.contains(role_title, case=False, na=False)]
            
            if role_rows.empty:
                return []
            
            # Aggregate skills from all matching roles
            all_skills = []
            for idx, row in role_rows.iterrows():
                if 'Skills' in row and pd.notna(row['Skills']):
                    skills = self._parse_skills_string(str(row['Skills']))
                    all_skills.extend(skills)
            
            # Normalize and count frequency
            skill_freq = Counter()
            for skill in all_skills:
                normalized = self._normalize_skill_name(skill)
                skill_freq[normalized] += 1
            
            # Return top 20 most common skills for this role
            return [skill for skill, _ in skill_freq.most_common(20)]
        except Exception as e:
            print(f"[ERROR] Failed to get role skills: {e}")
            return []
    
    def get_most_common_skills(self, top_n: int = 50) -> List[Dict[str, Any]]:
        """Get most commonly required skills across all roles"""
        try:
            if self.jobs_df is None:
                return []
            
            skill_freq = Counter()
            
            # Count skill frequency
            if 'Skills' in self.jobs_df.columns:
                for skills_str in self.jobs_df['Skills'].dropna():
                    if isinstance(skills_str, str):
                        skills = self._parse_skills_string(skills_str)
                        for skill in skills:
                            normalized = self._normalize_skill_name(skill)
                            skill_freq[normalized] += 1
            
            # Return top skills with frequency
            result = []
            for skill, freq in skill_freq.most_common(top_n):
                result.append({
                    'skill': skill,
                    'frequency': freq,
                    'percentage': round((freq / len(self.jobs_df)) * 100, 2)
                })
            
            return result
        except Exception as e:
            print(f"[ERROR] Failed to get common skills: {e}")
            return []
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        try:
            if self.jobs_df is None:
                return {}
            
            return {
                'total_jobs': len(self.jobs_df),
                'total_unique_skills': len(self.skills_vocabulary),
                'total_roles': sum(len(roles) for roles in self.role_mapping.values()),
                'experience_levels': list(self.role_mapping.keys()),
                'jobs_per_level': {level: len(roles) for level, roles in self.role_mapping.items()}
            }
        except Exception as e:
            print(f"[ERROR] Failed to get stats: {e}")
            return {}
    
    def save_normalized_dataset(self, output_dir: str):
        """Save normalized dataset as JSON for easy access"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save skills vocabulary
            with open(os.path.join(output_dir, 'skills_vocabulary.json'), 'w') as f:
                json.dump(list(self.skills_vocabulary), f, indent=2)
            
            # Save role mapping
            with open(os.path.join(output_dir, 'role_mapping.json'), 'w') as f:
                json.dump(self.role_mapping, f, indent=2)
            
            # Save common skills
            common_skills = self.get_most_common_skills(100)
            with open(os.path.join(output_dir, 'common_skills.json'), 'w') as f:
                json.dump(common_skills, f, indent=2)
            
            # Save stats
            stats = self.get_dataset_stats()
            with open(os.path.join(output_dir, 'dataset_stats.json'), 'w') as f:
                json.dump(stats, f, indent=2)
            
            print(f"[OK] Normalized dataset saved to {output_dir}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save dataset: {e}")
            return False

# Global normalizer instance
normalizer = DatasetNormalizer()

def load_and_normalize_dataset(csv_path: str):
    """Load Kaggle dataset and normalize it"""
    if normalizer.load_kaggle_dataset(csv_path):
        normalizer.normalize_skills()
        normalizer.extract_roles()
        return True
    return False

def get_skills_vocabulary():
    """Get all normalized skills"""
    return list(normalizer.skills_vocabulary)

def get_roles_by_experience():
    """Get roles grouped by experience level"""
    return normalizer.role_mapping
