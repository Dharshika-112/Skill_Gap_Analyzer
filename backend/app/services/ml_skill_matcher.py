"""
CareerBoost AI - Machine Learning Skill Matcher
Advanced ML/DL algorithms for accurate skill matching and role prediction
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import json
import os
from typing import List, Dict, Tuple
import logging

class MLSkillMatcher:
    def __init__(self):
        """Initialize ML-based skill matcher with trained models."""
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        self.role_classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        
        self.skill_neural_network = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.001,
            batch_size='auto',
            learning_rate='constant',
            learning_rate_init=0.001,
            max_iter=500,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Load and prepare data
        self.job_data = self.load_job_data()
        self.all_skills = self.extract_all_skills()
        self.models_trained = False
        
        # Train models on initialization
        if self.job_data:  # Only train if data is loaded
            self.train_models()
    
    def load_job_data(self) -> Dict:
        """Load job data from the processed dataset."""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '../../data/processed/skill_gap_reference.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading job data: {e}")
            return {}
    
    def extract_all_skills(self) -> List[str]:
        """Extract all unique skills from the dataset."""
        all_skills = set()
        
        for role_data in self.job_data.values():
            skills = role_data.get('required_skills', [])
            all_skills.update([skill.lower().strip() for skill in skills])
        
        return sorted(list(all_skills))
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare training data for ML models."""
        roles = []
        skill_vectors = []
        role_names = []
        
        for role_name, role_data in self.job_data.items():
            skills = role_data.get('required_skills', [])
            skill_text = ' '.join(skills)
            
            roles.append(role_name)
            skill_vectors.append(skill_text)
            role_names.append(role_name)
        
        # Create TF-IDF vectors
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(skill_vectors)
        
        return tfidf_matrix.toarray(), roles, role_names
    
    def train_models(self):
        """Train ML models for skill matching and role prediction."""
        try:
            print("🤖 Training ML models for skill matching...")
            
            # Prepare training data
            X, y, role_names = self.prepare_training_data()
            
            if len(X) == 0:
                print("⚠️ No training data available")
                return
            
            # Since we have only one sample per role, we'll use a different approach
            # Train on the full dataset without splitting
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Random Forest for role classification (no test split needed for single samples)
            self.role_classifier.fit(X, y_encoded)
            
            # Train Neural Network for advanced matching
            self.skill_neural_network.fit(X_scaled, y_encoded)
            
            self.models_trained = True
            
            print(f"✅ Models trained successfully")
            print(f"📊 Trained on {len(role_names)} job roles")
            print(f"🎯 Total skills: {len(self.all_skills)}")
            
        except Exception as e:
            logging.error(f"Error training models: {e}")
            print(f"❌ Model training failed: {e}")
            # Set a fallback mode
            self.models_trained = False
    
    def predict_suitable_roles(self, user_skills: List[str], top_k: int = 10) -> List[Dict]:
        """
        Predict most suitable roles for user skills using ML algorithms.
        
        Args:
            user_skills: List of user's skills
            top_k: Number of top roles to return
            
        Returns:
            List of role predictions with confidence scores
        """
        if not self.models_trained:
            return []
        
        try:
            # Prepare user skill vector
            user_skill_text = ' '.join([skill.lower().strip() for skill in user_skills])
            user_vector = self.tfidf_vectorizer.transform([user_skill_text]).toarray()
            
            # Get predictions from both models
            rf_probabilities = self.role_classifier.predict_proba(user_vector)[0]
            
            user_vector_scaled = self.scaler.transform(user_vector)
            nn_probabilities = self.skill_neural_network.predict_proba(user_vector_scaled)[0]
            
            # Combine predictions (ensemble approach)
            combined_probabilities = (rf_probabilities + nn_probabilities) / 2
            
            # Get role names and scores
            role_predictions = []
            for i, prob in enumerate(combined_probabilities):
                role_name = self.label_encoder.inverse_transform([i])[0]
                
                # Calculate detailed match information
                role_data = self.job_data.get(role_name, {})
                required_skills = role_data.get('required_skills', [])
                
                matched_skills, missing_skills = self.calculate_skill_match(
                    user_skills, required_skills
                )
                
                match_percentage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0
                
                role_predictions.append({
                    'role_name': role_name,
                    'ml_confidence': float(prob),
                    'match_percentage': round(match_percentage, 1),
                    'matched_skills': matched_skills,
                    'missing_skills': missing_skills,
                    'total_required_skills': len(required_skills),
                    'experience_level': role_data.get('experience_level', 'fresher'),
                    'job_count': role_data.get('job_count', 1)
                })
            
            # Sort by combined score (ML confidence + match percentage)
            role_predictions.sort(
                key=lambda x: (x['ml_confidence'] * 0.6 + x['match_percentage'] * 0.004), 
                reverse=True
            )
            
            return role_predictions[:top_k]
            
        except Exception as e:
            logging.error(f"Error predicting roles: {e}")
            return []
    
    def calculate_skill_match(self, user_skills: List[str], required_skills: List[str]) -> Tuple[List[str], List[str]]:
        """Calculate matched and missing skills using advanced similarity."""
        user_skills_lower = [skill.lower().strip() for skill in user_skills]
        required_skills_lower = [skill.lower().strip() for skill in required_skills]
        
        matched_skills = []
        missing_skills = []
        
        for req_skill in required_skills_lower:
            # Check for exact match
            if req_skill in user_skills_lower:
                matched_skills.append(req_skill)
            else:
                # Check for semantic similarity using TF-IDF
                similarity_found = False
                req_vector = self.tfidf_vectorizer.transform([req_skill])
                
                for user_skill in user_skills_lower:
                    user_vector = self.tfidf_vectorizer.transform([user_skill])
                    similarity = cosine_similarity(req_vector, user_vector)[0][0]
                    
                    if similarity > 0.7:  # High similarity threshold
                        matched_skills.append(req_skill)
                        similarity_found = True
                        break
                
                if not similarity_found:
                    missing_skills.append(req_skill)
        
        return matched_skills, missing_skills
    
    def analyze_specific_role(self, user_skills: List[str], target_role: str) -> Dict:
        """
        Perform detailed analysis for a specific role using ML algorithms.
        
        Args:
            user_skills: List of user's skills
            target_role: Target role name
            
        Returns:
            Detailed analysis with ML-based insights
        """
        if target_role not in self.job_data:
            return {'error': 'Role not found in database'}
        
        role_data = self.job_data[target_role]
        required_skills = role_data.get('required_skills', [])
        
        # Calculate skill match
        matched_skills, missing_skills = self.calculate_skill_match(user_skills, required_skills)
        
        # ML-based role suitability prediction
        user_skill_text = ' '.join([skill.lower().strip() for skill in user_skills])
        user_vector = self.tfidf_vectorizer.transform([user_skill_text]).toarray()
        
        # Get ML confidence for this specific role
        if self.models_trained:
            try:
                role_index = list(self.label_encoder.classes_).index(target_role)
                rf_prob = self.role_classifier.predict_proba(user_vector)[0][role_index]
                
                user_vector_scaled = self.scaler.transform(user_vector)
                nn_prob = self.skill_neural_network.predict_proba(user_vector_scaled)[0][role_index]
                
                ml_confidence = (rf_prob + nn_prob) / 2
            except:
                ml_confidence = 0.5
        else:
            ml_confidence = 0.5
        
        # Calculate metrics
        match_percentage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0
        
        # Generate ML-based improvement suggestions
        improvement_suggestions = self.generate_ml_suggestions(
            missing_skills, user_skills, target_role
        )
        
        return {
            'role_name': target_role,
            'match_percentage': round(match_percentage, 1),
            'ml_confidence': round(ml_confidence * 100, 1),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'total_required_skills': len(required_skills),
            'experience_level': role_data.get('experience_level', 'fresher'),
            'job_count': role_data.get('job_count', 1),
            'improvement_suggestions': improvement_suggestions,
            'readiness_level': self.determine_readiness_level(match_percentage, ml_confidence)
        }
    
    def generate_ml_suggestions(self, missing_skills: List[str], user_skills: List[str], target_role: str) -> List[Dict]:
        """Generate ML-based improvement suggestions."""
        suggestions = []
        
        # Priority-based suggestions using ML insights
        skill_priorities = self.calculate_skill_priorities(missing_skills, target_role)
        
        for skill, priority in skill_priorities.items():
            difficulty = self.estimate_learning_difficulty(skill, user_skills)
            
            suggestions.append({
                'skill': skill,
                'priority': priority,
                'difficulty': difficulty,
                'estimated_time': self.estimate_learning_time(skill, difficulty),
                'learning_path': self.suggest_learning_path(skill),
                'related_skills': self.find_related_skills(skill, user_skills)
            })
        
        return sorted(suggestions, key=lambda x: x['priority'], reverse=True)
    
    def calculate_skill_priorities(self, missing_skills: List[str], target_role: str) -> Dict[str, float]:
        """Calculate priority scores for missing skills using ML."""
        priorities = {}
        
        # Use feature importance from trained models
        if self.models_trained and hasattr(self.role_classifier, 'feature_importances_'):
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            feature_importance = self.role_classifier.feature_importances_
            
            for skill in missing_skills:
                skill_lower = skill.lower().strip()
                priority = 0.5  # Default priority
                
                # Find skill in TF-IDF features
                for i, feature in enumerate(feature_names):
                    if skill_lower in feature or feature in skill_lower:
                        priority = max(priority, feature_importance[i])
                
                priorities[skill] = priority
        else:
            # Fallback: equal priority
            for skill in missing_skills:
                priorities[skill] = 0.5
        
        return priorities
    
    def estimate_learning_difficulty(self, skill: str, user_skills: List[str]) -> str:
        """Estimate learning difficulty based on user's current skills."""
        # Check for related skills
        related_count = 0
        for user_skill in user_skills:
            if self.calculate_skill_similarity(skill, user_skill) > 0.3:
                related_count += 1
        
        if related_count >= 3:
            return "Easy"
        elif related_count >= 1:
            return "Medium"
        else:
            return "Hard"
    
    def calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills using TF-IDF."""
        try:
            vectors = self.tfidf_vectorizer.transform([skill1.lower(), skill2.lower()])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return similarity
        except:
            return 0.0
    
    def estimate_learning_time(self, skill: str, difficulty: str) -> str:
        """Estimate learning time based on skill and difficulty."""
        time_mapping = {
            "Easy": "1-2 weeks",
            "Medium": "2-4 weeks", 
            "Hard": "4-8 weeks"
        }
        return time_mapping.get(difficulty, "2-4 weeks")
    
    def suggest_learning_path(self, skill: str) -> List[str]:
        """Suggest learning path for a skill."""
        # Basic learning path suggestions
        paths = {
            'python': ['Python Basics', 'Data Structures', 'OOP Concepts', 'Libraries & Frameworks'],
            'javascript': ['JS Fundamentals', 'DOM Manipulation', 'ES6+ Features', 'Async Programming'],
            'react': ['Component Basics', 'State Management', 'Hooks', 'Advanced Patterns'],
            'sql': ['Basic Queries', 'Joins & Relations', 'Advanced Functions', 'Database Design']
        }
        
        skill_lower = skill.lower()
        for key, path in paths.items():
            if key in skill_lower:
                return path
        
        return ['Fundamentals', 'Practice', 'Advanced Topics', 'Real Projects']
    
    def find_related_skills(self, skill: str, user_skills: List[str]) -> List[str]:
        """Find related skills from user's current skills."""
        related = []
        for user_skill in user_skills:
            if self.calculate_skill_similarity(skill, user_skill) > 0.3:
                related.append(user_skill)
        return related[:3]  # Top 3 related skills
    
    def determine_readiness_level(self, match_percentage: float, ml_confidence: float) -> str:
        """Determine readiness level using ML confidence and match percentage."""
        combined_score = (match_percentage + ml_confidence * 100) / 2
        
        if combined_score >= 80:
            return "Job Ready"
        elif combined_score >= 60:
            return "Interview Ready"
        elif combined_score >= 40:
            return "Learning Phase"
        else:
            return "Beginner"
    
    def get_skill_recommendations(self, user_skills: List[str], limit: int = 20) -> List[str]:
        """Get skill recommendations based on ML analysis."""
        if not self.models_trained:
            return self.all_skills[:limit]
        
        try:
            # Find skills that frequently appear with user's skills
            user_skill_text = ' '.join([skill.lower().strip() for skill in user_skills])
            user_vector = self.tfidf_vectorizer.transform([user_skill_text])
            
            # Calculate similarity with all job roles
            role_similarities = []
            for role_name, role_data in self.job_data.items():
                role_skills = role_data.get('required_skills', [])
                role_text = ' '.join(role_skills)
                role_vector = self.tfidf_vectorizer.transform([role_text])
                
                similarity = cosine_similarity(user_vector, role_vector)[0][0]
                role_similarities.append((role_name, similarity, role_skills))
            
            # Get skills from most similar roles
            role_similarities.sort(key=lambda x: x[1], reverse=True)
            recommended_skills = set()
            
            for role_name, similarity, role_skills in role_similarities[:5]:
                for skill in role_skills:
                    if skill.lower() not in [us.lower() for us in user_skills]:
                        recommended_skills.add(skill)
            
            return list(recommended_skills)[:limit]
            
        except Exception as e:
            logging.error(f"Error getting skill recommendations: {e}")
            return self.all_skills[:limit]

# Global instance
ml_skill_matcher = MLSkillMatcher()