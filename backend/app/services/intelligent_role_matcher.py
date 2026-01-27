"""
Intelligent Role Matching using Deep Learning and Skill Importance Analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
import re
from pathlib import Path

# ML/DL imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from .dataset_loader import JobDatasetLoader

class IntelligentRoleMatcher:
    def __init__(self):
        self.dataset_loader = JobDatasetLoader()
        self.skill_importance_model = None
        self.role_embedding_model = None
        self.skill_frequency_map = {}
        self.role_skill_importance = {}
        self._analyze_skill_importance()
        if ML_AVAILABLE:
            self._build_deep_learning_models()
    
    def _analyze_skill_importance(self):
        """Analyze skill importance across all job roles in the dataset"""
        print("[INFO] Analyzing skill importance across job dataset...")
        
        if self.dataset_loader.df is None:
            print("[WARNING] No dataset available for skill analysis")
            return
        
        # Count skill frequency across all jobs
        skill_counts = Counter()
        role_skill_counts = {}
        
        for _, job in self.dataset_loader.df.iterrows():
            role_title = job.get('Title', '')
            if pd.isna(role_title) or role_title == 'nan':
                continue
                
            # Extract skills from this job
            job_skills = set()
            
            # From Skills column
            if pd.notna(job.get('Skills')):
                skills = [s.strip().lower() for s in str(job['Skills']).split(';') if s.strip()]
                job_skills.update(skills)
            
            # From Keywords column
            if pd.notna(job.get('Keywords')):
                keywords = [k.strip().lower() for k in str(job['Keywords']).split(';') if k.strip()]
                job_skills.update(keywords)
            
            # Update global skill counts
            for skill in job_skills:
                if len(skill) > 2:  # Filter out very short skills
                    skill_counts[skill] += 1
            
            # Update role-specific skill counts
            if role_title not in role_skill_counts:
                role_skill_counts[role_title] = Counter()
            
            for skill in job_skills:
                if len(skill) > 2:
                    role_skill_counts[role_title][skill] += 1
        
        # Calculate skill importance scores
        total_jobs = len(self.dataset_loader.df)
        
        for skill, count in skill_counts.items():
            # Importance = frequency * inverse document frequency
            frequency = count / total_jobs
            # Skills that appear in 10-80% of jobs are most important
            if 0.1 <= frequency <= 0.8:
                importance = frequency * (1 - frequency)  # Peak at 50%
            else:
                importance = frequency * 0.5  # Lower importance for very rare or very common
            
            self.skill_frequency_map[skill] = {
                'count': count,
                'frequency': frequency,
                'importance': importance
            }
        
        # Calculate role-specific skill importance
        for role_title, skill_counter in role_skill_counts.items():
            role_total = sum(skill_counter.values())
            self.role_skill_importance[role_title] = {}
            
            for skill, count in skill_counter.items():
                role_frequency = count / role_total if role_total > 0 else 0
                global_importance = self.skill_frequency_map.get(skill, {}).get('importance', 0)
                
                # Combined importance: role frequency + global importance
                combined_importance = (role_frequency * 0.7) + (global_importance * 0.3)
                
                self.role_skill_importance[role_title][skill] = {
                    'role_frequency': role_frequency,
                    'global_importance': global_importance,
                    'combined_importance': combined_importance
                }
        
        print(f"[INFO] Analyzed {len(skill_counts)} unique skills across {total_jobs} jobs")
        
        # Get top important skills
        top_skills = sorted(self.skill_frequency_map.items(), 
                          key=lambda x: x[1]['importance'], reverse=True)[:20]
        print(f"[INFO] Top important skills: {[skill for skill, _ in top_skills[:10]]}")
    
    def _build_deep_learning_models(self):
        """Build deep learning models for skill importance and role matching"""
        if not ML_AVAILABLE:
            print("[WARNING] ML libraries not available, using fallback methods")
            return
        
        try:
            print("[INFO] Building deep learning models for role matching...")
            
            # Prepare training data
            X_skills = []
            y_importance = []
            
            for skill, data in self.skill_frequency_map.items():
                # Feature vector: [frequency, count, skill_length, has_programming_keywords]
                features = [
                    data['frequency'],
                    min(data['count'] / 100, 1.0),  # Normalized count
                    len(skill) / 20,  # Normalized skill length
                    1.0 if any(kw in skill for kw in ['python', 'java', 'javascript', 'react', 'sql']) else 0.0
                ]
                X_skills.append(features)
                y_importance.append(data['importance'])
            
            if len(X_skills) > 10:  # Need minimum data for training
                X_skills = np.array(X_skills)
                y_importance = np.array(y_importance)
                
                # Build skill importance prediction model
                self.skill_importance_model = keras.Sequential([
                    layers.Dense(64, activation='relu', input_shape=(4,)),
                    layers.Dropout(0.3),
                    layers.Dense(32, activation='relu'),
                    layers.Dropout(0.2),
                    layers.Dense(16, activation='relu'),
                    layers.Dense(1, activation='sigmoid')
                ])
                
                self.skill_importance_model.compile(
                    optimizer='adam',
                    loss='mse',
                    metrics=['mae']
                )
                
                # Train the model
                self.skill_importance_model.fit(
                    X_skills, y_importance,
                    epochs=50,
                    batch_size=32,
                    verbose=0,
                    validation_split=0.2
                )
                
                print("[INFO] Deep learning skill importance model trained successfully")
            
        except Exception as e:
            print(f"[WARNING] Failed to build DL models: {e}")
            self.skill_importance_model = None
    
    def get_skill_importance_score(self, skill: str) -> float:
        """Get importance score for a skill using DL model or fallback"""
        skill_lower = skill.lower().strip()
        
        # Try to get from pre-calculated importance
        if skill_lower in self.skill_frequency_map:
            return self.skill_frequency_map[skill_lower]['importance']
        
        # Use DL model if available
        if self.skill_importance_model and ML_AVAILABLE:
            try:
                features = np.array([[
                    0.1,  # Default frequency
                    0.1,  # Default normalized count
                    len(skill) / 20,  # Normalized skill length
                    1.0 if any(kw in skill_lower for kw in ['python', 'java', 'javascript', 'react', 'sql']) else 0.0
                ]])
                
                importance = self.skill_importance_model.predict(features, verbose=0)[0][0]
                return float(importance)
            except Exception as e:
                print(f"[WARNING] DL prediction failed: {e}")
        
        # Fallback: rule-based importance
        high_value_skills = ['python', 'java', 'javascript', 'react', 'sql', 'machine learning', 'deep learning', 'aws', 'docker', 'kubernetes']
        if any(hvs in skill_lower for hvs in high_value_skills):
            return 0.8
        elif len(skill) >= 3:
            return 0.3
        else:
            return 0.1
    
    def find_intelligent_role_matches(self, user_skills: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """Find role matches using intelligent skill importance analysis"""
        print(f"[INFO] Finding intelligent role matches for {len(user_skills)} user skills...")
        
        user_skills_lower = [s.lower().strip() for s in user_skills]
        role_matches = []
        
        # Get user skill importance scores
        user_skill_scores = {}
        for skill in user_skills_lower:
            user_skill_scores[skill] = self.get_skill_importance_score(skill)
        
        # Analyze each role
        for role_title, role_skill_data in self.role_skill_importance.items():
            if not role_skill_data:
                continue
            
            # Calculate intelligent match score
            total_role_importance = 0
            matched_importance = 0
            high_priority_matches = 0
            high_priority_total = 0
            
            matching_skills = []
            missing_skills = []
            
            for role_skill, skill_data in role_skill_data.items():
                skill_importance = skill_data['combined_importance']
                total_role_importance += skill_importance
                
                # Check if it's a high priority skill (top 30% importance)
                if skill_importance > 0.3:
                    high_priority_total += 1
                
                # Check if user has this skill
                user_has_skill = False
                for user_skill in user_skills_lower:
                    if (user_skill == role_skill or 
                        user_skill in role_skill or 
                        role_skill in user_skill or
                        self._are_similar_skills(user_skill, role_skill)):
                        user_has_skill = True
                        matching_skills.append(role_skill)
                        break
                
                if user_has_skill:
                    matched_importance += skill_importance
                    if skill_importance > 0.3:
                        high_priority_matches += 1
                else:
                    missing_skills.append(role_skill)
            
            # Calculate match percentage based on importance weighting
            if total_role_importance > 0:
                importance_match_percentage = (matched_importance / total_role_importance) * 100
            else:
                importance_match_percentage = 0
            
            # Calculate high priority match percentage
            if high_priority_total > 0:
                high_priority_percentage = (high_priority_matches / high_priority_total) * 100
            else:
                high_priority_percentage = 100 if len(matching_skills) > 0 else 0
            
            # Combined intelligent score (weighted)
            intelligent_score = (importance_match_percentage * 0.7) + (high_priority_percentage * 0.3)
            
            # Only include roles with reasonable matches
            if len(matching_skills) > 0 and intelligent_score > 5:
                # Sort missing skills by importance
                missing_with_importance = []
                for skill in missing_skills:
                    importance = role_skill_data.get(skill, {}).get('combined_importance', 0)
                    missing_with_importance.append((skill, importance))
                
                missing_with_importance.sort(key=lambda x: x[1], reverse=True)
                prioritized_missing = [skill for skill, _ in missing_with_importance[:10]]
                
                role_matches.append({
                    'role': role_title,
                    'intelligent_score': round(intelligent_score, 2),
                    'importance_match_percentage': round(importance_match_percentage, 2),
                    'high_priority_match_percentage': round(high_priority_percentage, 2),
                    'matching_skills': matching_skills[:10],  # Top 10
                    'missing_skills': prioritized_missing,  # Top 10 by importance
                    'high_priority_matches': high_priority_matches,
                    'high_priority_total': high_priority_total,
                    'total_matching_skills': len(matching_skills),
                    'total_missing_skills': len(missing_skills)
                })
        
        # Sort by intelligent score
        role_matches.sort(key=lambda x: x['intelligent_score'], reverse=True)
        
        print(f"[INFO] Found {len(role_matches)} role matches, returning top {top_n}")
        return role_matches[:top_n]
    
    def _are_similar_skills(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are similar using various methods"""
        # Exact match
        if skill1 == skill2:
            return True
        
        # Common variations
        variations = {
            'js': 'javascript', 'javascript': 'js',
            'ts': 'typescript', 'typescript': 'ts',
            'py': 'python', 'python': 'py',
            'react': 'reactjs', 'reactjs': 'react',
            'node': 'nodejs', 'nodejs': 'node',
            'ml': 'machine learning', 'machine learning': 'ml',
            'ai': 'artificial intelligence', 'artificial intelligence': 'ai',
            'dl': 'deep learning', 'deep learning': 'dl'
        }
        
        if skill1 in variations and variations[skill1] == skill2:
            return True
        if skill2 in variations and variations[skill2] == skill1:
            return True
        
        # Substring matching for longer skills
        if len(skill1) > 4 and len(skill2) > 4:
            if skill1 in skill2 or skill2 in skill1:
                return True
        
        return False
    
    def get_skill_recommendations(self, user_skills: List[str], target_role: str = None) -> Dict[str, Any]:
        """Get intelligent skill recommendations based on market demand"""
        user_skills_lower = [s.lower().strip() for s in user_skills]
        
        # Get top important skills that user doesn't have
        missing_important_skills = []
        
        for skill, data in self.skill_frequency_map.items():
            if data['importance'] > 0.2:  # Only high importance skills
                user_has_skill = any(
                    us == skill or us in skill or skill in us 
                    for us in user_skills_lower
                )
                
                if not user_has_skill:
                    missing_important_skills.append({
                        'skill': skill,
                        'importance': data['importance'],
                        'frequency': data['frequency'],
                        'job_count': data['count']
                    })
        
        # Sort by importance
        missing_important_skills.sort(key=lambda x: x['importance'], reverse=True)
        
        recommendations = {
            'high_priority_skills': missing_important_skills[:10],
            'user_skill_scores': [
                {
                    'skill': skill,
                    'importance_score': self.get_skill_importance_score(skill)
                }
                for skill in user_skills
            ],
            'market_trends': self._get_market_trends()
        }
        
        return recommendations
    
    def _get_market_trends(self) -> Dict[str, Any]:
        """Analyze market trends from the dataset"""
        # Get top skills by frequency
        top_skills = sorted(
            self.skill_frequency_map.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:20]
        
        # Categorize skills
        categories = {
            'Programming Languages': [],
            'Web Technologies': [],
            'Cloud & DevOps': [],
            'Data & AI': [],
            'Databases': []
        }
        
        for skill, data in top_skills:
            if any(lang in skill for lang in ['python', 'java', 'javascript', 'c++', 'c#']):
                categories['Programming Languages'].append({'skill': skill, 'count': data['count']})
            elif any(web in skill for web in ['react', 'angular', 'vue', 'html', 'css', 'node']):
                categories['Web Technologies'].append({'skill': skill, 'count': data['count']})
            elif any(cloud in skill for cloud in ['aws', 'azure', 'docker', 'kubernetes', 'git']):
                categories['Cloud & DevOps'].append({'skill': skill, 'count': data['count']})
            elif any(data_skill in skill for data_skill in ['machine learning', 'deep learning', 'tensorflow', 'pandas']):
                categories['Data & AI'].append({'skill': skill, 'count': data['count']})
            elif any(db in skill for db in ['sql', 'mongodb', 'mysql', 'postgresql']):
                categories['Databases'].append({'skill': skill, 'count': data['count']})
        
        return {
            'top_skills_by_demand': [{'skill': skill, 'job_count': data['count']} for skill, data in top_skills[:10]],
            'skill_categories': categories
        }

# Global instance
intelligent_matcher = IntelligentRoleMatcher()

# Convenience functions
def find_intelligent_matches(user_skills: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
    """Find intelligent role matches"""
    return intelligent_matcher.find_intelligent_role_matches(user_skills, top_n)

def get_skill_recommendations(user_skills: List[str], target_role: str = None) -> Dict[str, Any]:
    """Get skill recommendations"""
    return intelligent_matcher.get_skill_recommendations(user_skills, target_role)

def get_skill_importance(skill: str) -> float:
    """Get importance score for a skill"""
    return intelligent_matcher.get_skill_importance_score(skill)