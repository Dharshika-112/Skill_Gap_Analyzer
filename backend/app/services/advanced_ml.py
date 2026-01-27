"""
Advanced Machine Learning Service for Skill Gap Analysis
Uses Deep Learning and ML algorithms for better predictions
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from .role_matcher import enhanced_match_score
from .skill_cleaner import clean_skill_list
from .experience_weighting import get_experience_weight
import json
import os
from pathlib import Path

try:
    from tensorflow.keras.models import Sequential  # type: ignore
    from tensorflow.keras.layers import Dense, Dropout, Input  # type: ignore
    from tensorflow.keras.optimizers import Adam  # type: ignore
    import tensorflow as tf  # type: ignore
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

class AdvancedSkillGapAnalyzer:
    """Advanced skill gap analyzer with Deep Learning capabilities"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        self.scaler = StandardScaler()
        self.neural_model = None
        self.role_embeddings = None
        self.skill_embeddings = None
        self.is_trained = False
        
    def train_deep_learning_model(self, training_data):
        """Train a neural network for skill prediction"""
        if not TF_AVAILABLE:
            return False
            
        try:
            X = training_data['X']
            y = training_data['y']
            
            # Build neural network
            self.neural_model = Sequential([
                Input(shape=(X.shape[1],)),
                Dense(128, activation='relu'),
                Dropout(0.3),
                Dense(64, activation='relu'),
                Dropout(0.2),
                Dense(32, activation='relu'),
                Dense(y.shape[1], activation='sigmoid')
            ])
            
            self.neural_model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Train with reduced epochs for quick response
            self.neural_model.fit(X, y, epochs=5, batch_size=32, verbose=0)
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error training neural model: {e}")
            return False
    
    def calculate_skill_gap(self, user_skills, role_skills, role_name=""):
        """
        Calculate skill gap using multiple algorithms
        Returns: gap analysis with multiple scoring methods
        """
        user_skills_set = set([s.lower() for s in user_skills])
        role_skills_set = set([s.lower() for s in role_skills])
        
        # Use role_matcher enhanced score
        cleaned_user = clean_skill_list(list(user_skills_set))
        cleaned_role = clean_skill_list(list(role_skills_set))

        enhanced = enhanced_match_score(cleaned_user, cleaned_role, {})

        dl_score = self._calculate_deep_learning_score(user_skills, role_skills) if self.is_trained else None

        # Build response, include legacy metrics
        matching_skills = list(user_skills_set & role_skills_set)
        missing_skills = list(role_skills_set - user_skills_set)
        extra_skills = list(user_skills_set - role_skills_set)

        return {
            'match_percentage': enhanced['score'],
            'jaccard_score': round(enhanced['jaccard'] * 100, 2),
            'tfidf_score': round(enhanced['cosine'] * 100, 2),
            'cosine_score': round(enhanced['cosine'] * 100, 2),
            'deep_learning_score': round(dl_score, 2) if dl_score else None,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'extra_skills': extra_skills,
            'matching_count': len(matching_skills),
            'missing_count': len(missing_skills),
            'total_required': len(role_skills_set)
        }
    
    def _calculate_tfidf_similarity(self, user_skills, role_skills):
        """Calculate TF-IDF similarity"""
        try:
            all_skills = list(set(user_skills + role_skills))
            if len(all_skills) < 2:
                return 100.0 if len(user_skills) > 0 and user_skills == role_skills else 0.0
            
            # Create documents
            user_doc = ' '.join(user_skills)
            role_doc = ' '.join(role_skills)
            
            # Fit and transform
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([user_doc, role_doc])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100
        except:
            return 0.0
    
    def _calculate_cosine_similarity(self, user_skills, role_skills):
        """Calculate Cosine similarity using simple vectors"""
        try:
            all_skills = list(set(user_skills + role_skills))
            
            # Create binary vectors
            user_vector = np.array([1 if skill in user_skills else 0 for skill in all_skills])
            role_vector = np.array([1 if skill in role_skills else 0 for skill in all_skills])
            
            # Calculate cosine similarity
            dot_product = np.dot(user_vector, role_vector)
            norm_user = np.linalg.norm(user_vector)
            norm_role = np.linalg.norm(role_vector)
            
            if norm_user == 0 or norm_role == 0:
                return 0.0
            
            similarity = dot_product / (norm_user * norm_role)
            return similarity * 100
        except:
            return 0.0
    
    def _calculate_deep_learning_score(self, user_skills, role_skills):
        """Calculate score using trained neural network"""
        if not self.neural_model or not self.is_trained:
            return None
        
        try:
            # Create feature vector
            all_skills = list(set(user_skills + role_skills))
            feature_vector = np.array([1 if skill in user_skills else 0 for skill in all_skills])
            feature_vector = feature_vector.reshape(1, -1)
            
            # Predict
            prediction = self.neural_model.predict(feature_vector, verbose=0)
            return float(np.mean(prediction) * 100)
        except:
            return None
    
    def find_optimal_learning_path(self, user_skills, role_skills, gap_analysis):
        """Generate learning path based on skill gaps"""
        missing_skills = gap_analysis['missing_skills']
        
        # Prioritize skills by frequency and importance
        skill_priority = self._calculate_skill_priority(missing_skills, role_skills)
        
        learning_path = []
        for i, skill in enumerate(skill_priority[:10], 1):  # Top 10 skills
            learning_path.append({
                'priority': i,
                'skill': skill,
                'importance': 'High' if i <= 3 else 'Medium' if i <= 7 else 'Low',
                'estimated_hours': 20 + (i * 5)
            })
        
        return learning_path
    
    def _calculate_skill_priority(self, missing_skills, role_skills):
        """Calculate priority of skills to learn"""
        # Skills appearing in role description get higher priority
        skill_frequency = {}
        for skill in missing_skills:
            freq = sum(1 for rs in role_skills if skill.lower() in rs.lower())
            skill_frequency[skill] = freq
        
        # Sort by frequency
        sorted_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, _ in sorted_skills]

# Global analyzer instance
analyzer = AdvancedSkillGapAnalyzer()

def get_skill_gap_analysis(user_skills, role_skills, role_name=""):
    """Wrapper function for skill gap analysis"""
    return analyzer.calculate_skill_gap(user_skills, role_skills, role_name)

def get_learning_path(user_skills, role_skills, gap_analysis):
    """Wrapper function for learning path generation"""
    return analyzer.find_optimal_learning_path(user_skills, role_skills, gap_analysis)
