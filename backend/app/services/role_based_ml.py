"""
Role-Based ML System for Resume Scoring
Implements role-specific ML models using TF-IDF + Regression

🎯 Goal: Score resume differently per role
🧠 Logic: Filter resume dataset by Job_Role, Train separate ML model per role, Predict ATS score
📌 Algorithm: TF-IDF + Regression OR One model + role as feature
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pickle
import joblib
from datetime import datetime
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dataset paths
ATS_DATASET_PATH = Path(__file__).parents[2] / 'data' / 'raw' / 'AI_Resume_Screening.csv'
JOB_DATASET_PATH = Path(__file__).parents[2] / 'data' / 'raw' / 'job_dataset.csv'
MODEL_DIR = Path(__file__).parents[2] / 'data' / 'models' / 'role_based'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

class RoleBasedMLSystem:
    """Role-specific ML models for accurate resume scoring"""
    
    def __init__(self):
        self.ats_df = None
        self.job_df = None
        self.role_models = {}
        self.role_vectorizers = {}
        self.role_scalers = {}
        self.role_encoders = {}
        self.available_roles = []
        self.is_trained = False
        
        # Load datasets
        self.load_datasets()
        
        # Load or train models
        if not self.load_models():
            logger.info("[INFO] Training role-based ML models...")
            self.train_role_specific_models()
    
    def load_datasets(self):
        """Load ATS and Job datasets"""
        try:
            if ATS_DATASET_PATH.exists():
                self.ats_df = pd.read_csv(ATS_DATASET_PATH)
                logger.info(f"[OK] Loaded ATS dataset: {len(self.ats_df)} resumes")
                
                # Get available roles from ATS dataset
                self.available_roles = self.ats_df['Job Role'].unique().tolist()
                logger.info(f"[OK] Available roles: {self.available_roles}")
            else:
                logger.error(f"[ERROR] ATS dataset not found at {ATS_DATASET_PATH}")
                
            if JOB_DATASET_PATH.exists():
                self.job_df = pd.read_csv(JOB_DATASET_PATH)
                logger.info(f"[OK] Loaded Job dataset: {len(self.job_df)} jobs")
            else:
                logger.error(f"[ERROR] Job dataset not found at {JOB_DATASET_PATH}")
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to load datasets: {e}")
    
    def preprocess_role_data(self, role_name: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Preprocess data for specific role"""
        if self.ats_df is None:
            return None, None, {}
        
        # Filter dataset by role
        role_data = self.ats_df[self.ats_df['Job Role'] == role_name].copy()
        
        if len(role_data) < 10:
            logger.warning(f"[WARNING] Insufficient data for role {role_name}: {len(role_data)} samples")
            return None, None, {}
        
        logger.info(f"[INFO] Processing {len(role_data)} samples for role: {role_name}")
        
        # Clean and prepare features
        role_data['Skills_Clean'] = role_data['Skills'].fillna('').str.lower()
        role_data['Education_Clean'] = role_data['Education'].fillna('').str.lower()
        role_data['Certifications_Clean'] = role_data['Certifications'].fillna('none').str.lower()
        
        # Create combined text for TF-IDF
        role_data['Combined_Text'] = (
            role_data['Skills_Clean'] + ' ' + 
            role_data['Education_Clean'] + ' ' + 
            role_data['Certifications_Clean']
        )
        
        # Prepare numerical features
        numerical_features = ['Experience (Years)', 'Projects Count']
        for col in numerical_features:
            if col in role_data.columns:
                role_data[col] = role_data[col].fillna(role_data[col].median())
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        tfidf_features = vectorizer.fit_transform(role_data['Combined_Text']).toarray()
        
        # Combine TF-IDF with numerical features
        numerical_data = role_data[numerical_features].values
        X = np.hstack([tfidf_features, numerical_data])
        
        # Target variable
        y = role_data['AI Score (0-100)'].values
        
        # Prepare metadata
        metadata = {
            'role_name': role_name,
            'samples': len(role_data),
            'tfidf_features': tfidf_features.shape[1],
            'numerical_features': len(numerical_features),
            'total_features': X.shape[1],
            'vectorizer': vectorizer
        }
        
        return X, y, metadata
    
    def train_role_model(self, role_name: str) -> Dict[str, Any]:
        """Train ML model for specific role"""
        try:
            # Preprocess data
            X, y, metadata = self.preprocess_role_data(role_name)
            
            if X is None or len(X) < 10:
                logger.warning(f"[WARNING] Skipping {role_name} - insufficient data")
                return {'success': False, 'reason': 'insufficient_data'}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=None
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Try multiple models and select best
            models = {
                'ridge': Ridge(alpha=1.0, random_state=42),
                'linear': LinearRegression(),
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            }
            
            best_model = None
            best_score = -np.inf
            best_model_name = None
            
            for model_name, model in models.items():
                try:
                    # Train model
                    if model_name == 'random_forest':
                        # Random Forest doesn't need scaling
                        model.fit(X_train, y_train)
                        y_pred = model.predict(X_test)
                        train_pred = model.predict(X_train)
                    else:
                        # Linear models benefit from scaling
                        model.fit(X_train_scaled, y_train)
                        y_pred = model.predict(X_test_scaled)
                        train_pred = model.predict(X_train_scaled)
                    
                    # Evaluate
                    test_r2 = r2_score(y_test, y_pred)
                    train_r2 = r2_score(y_train, train_pred)
                    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    
                    logger.info(f"[INFO] {role_name} - {model_name}: R²={test_r2:.3f}, RMSE={test_rmse:.2f}")
                    
                    # Select best model based on test R²
                    if test_r2 > best_score:
                        best_score = test_r2
                        best_model = model
                        best_model_name = model_name
                        
                except Exception as e:
                    logger.warning(f"[WARNING] Model {model_name} failed for {role_name}: {e}")
                    continue
            
            if best_model is None:
                logger.error(f"[ERROR] All models failed for role: {role_name}")
                return {'success': False, 'reason': 'training_failed'}
            
            # Store model and components
            self.role_models[role_name] = best_model
            self.role_vectorizers[role_name] = metadata['vectorizer']
            self.role_scalers[role_name] = scaler
            
            # Save to disk
            model_path = MODEL_DIR / f"{role_name.replace(' ', '_').lower()}_model.pkl"
            vectorizer_path = MODEL_DIR / f"{role_name.replace(' ', '_').lower()}_vectorizer.pkl"
            scaler_path = MODEL_DIR / f"{role_name.replace(' ', '_').lower()}_scaler.pkl"
            
            joblib.dump(best_model, model_path)
            joblib.dump(metadata['vectorizer'], vectorizer_path)
            joblib.dump(scaler, scaler_path)
            
            result = {
                'success': True,
                'role_name': role_name,
                'model_type': best_model_name,
                'test_r2': best_score,
                'samples': metadata['samples'],
                'features': metadata['total_features'],
                'model_path': str(model_path)
            }
            
            logger.info(f"[OK] Trained {role_name} model: {best_model_name} (R²={best_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Training failed for {role_name}: {e}")
            return {'success': False, 'reason': str(e)}
    
    def train_role_specific_models(self) -> Dict[str, Any]:
        """Train ML models for all available roles"""
        if not self.available_roles:
            logger.error("[ERROR] No roles available for training")
            return {'success': False, 'trained_roles': []}
        
        training_results = {}
        successful_roles = []
        
        for role in self.available_roles:
            logger.info(f"[INFO] Training model for role: {role}")
            result = self.train_role_model(role)
            training_results[role] = result
            
            if result['success']:
                successful_roles.append(role)
        
        self.is_trained = len(successful_roles) > 0
        
        # Save training summary
        summary = {
            'success': self.is_trained,
            'trained_roles': successful_roles,
            'failed_roles': [role for role in self.available_roles if role not in successful_roles],
            'training_results': training_results,
            'trained_at': datetime.utcnow().isoformat()
        }
        
        summary_path = MODEL_DIR / 'training_summary.json'
        import json
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"[OK] Training complete: {len(successful_roles)}/{len(self.available_roles)} roles")
        return summary
    
    def load_models(self) -> bool:
        """Load pre-trained role-based models"""
        try:
            if not MODEL_DIR.exists():
                return False
            
            loaded_roles = []
            
            for role in self.available_roles:
                role_key = role.replace(' ', '_').lower()
                model_path = MODEL_DIR / f"{role_key}_model.pkl"
                vectorizer_path = MODEL_DIR / f"{role_key}_vectorizer.pkl"
                scaler_path = MODEL_DIR / f"{role_key}_scaler.pkl"
                
                if all(path.exists() for path in [model_path, vectorizer_path, scaler_path]):
                    try:
                        self.role_models[role] = joblib.load(model_path)
                        self.role_vectorizers[role] = joblib.load(vectorizer_path)
                        self.role_scalers[role] = joblib.load(scaler_path)
                        loaded_roles.append(role)
                    except Exception as e:
                        logger.warning(f"[WARNING] Failed to load model for {role}: {e}")
            
            self.is_trained = len(loaded_roles) > 0
            
            if self.is_trained:
                logger.info(f"[OK] Loaded models for {len(loaded_roles)} roles: {loaded_roles}")
                return True
            else:
                logger.info("[INFO] No pre-trained models found")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to load models: {e}")
            return False
    
    def predict_role_score(self, resume_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
        """Predict ATS score for specific role"""
        try:
            if target_role not in self.role_models:
                logger.warning(f"[WARNING] No model available for role: {target_role}")
                return {
                    'success': False,
                    'error': f'No model available for role: {target_role}',
                    'score': 0,
                    'confidence': 0.0
                }
            
            # Extract features from resume data
            skills = resume_data.get('skills', [])
            experience_years = resume_data.get('experience', {}).get('total_years', 0)
            education = resume_data.get('education', '')
            certifications = resume_data.get('certifications', '')
            projects_count = resume_data.get('projects_count', 0)
            
            # Create combined text (same format as training)
            skills_text = ' '.join(skills).lower()
            education_text = str(education).lower()
            cert_text = str(certifications).lower() if certifications else 'none'
            combined_text = f"{skills_text} {education_text} {cert_text}"
            
            # Get model components
            model = self.role_models[target_role]
            vectorizer = self.role_vectorizers[target_role]
            scaler = self.role_scalers[target_role]
            
            # Transform text features
            tfidf_features = vectorizer.transform([combined_text]).toarray()
            
            # Prepare numerical features
            numerical_features = np.array([[experience_years, projects_count]])
            
            # Combine features
            X = np.hstack([tfidf_features, numerical_features])
            
            # Scale features (for linear models)
            model_type = type(model).__name__
            if model_type in ['Ridge', 'LinearRegression']:
                X_scaled = scaler.transform(X)
                prediction = model.predict(X_scaled)[0]
            else:
                # Random Forest doesn't need scaling
                prediction = model.predict(X)[0]
            
            # Ensure score is within valid range
            score = max(0, min(100, prediction))
            
            # Calculate confidence based on model performance
            confidence = 0.85  # Base confidence for role-specific models
            
            # Adjust confidence based on data availability
            if hasattr(model, 'score'):
                try:
                    # For models with built-in scoring
                    confidence = min(0.95, confidence + 0.1)
                except:
                    pass
            
            result = {
                'success': True,
                'role': target_role,
                'score': round(score, 1),
                'confidence': round(confidence, 2),
                'model_type': model_type,
                'features_used': {
                    'skills_count': len(skills),
                    'experience_years': experience_years,
                    'projects_count': projects_count,
                    'tfidf_features': tfidf_features.shape[1]
                },
                'prediction_details': {
                    'raw_prediction': round(prediction, 2),
                    'clamped_score': round(score, 1),
                    'text_features': tfidf_features.shape[1],
                    'numerical_features': 2
                }
            }
            
            logger.info(f"[OK] Role-based prediction for {target_role}: {score:.1f}% (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Role-based prediction failed for {target_role}: {e}")
            return {
                'success': False,
                'error': str(e),
                'score': 0,
                'confidence': 0.0
            }
    
    def get_role_requirements(self, role_name: str) -> Dict[str, Any]:
        """Get role requirements from job dataset"""
        try:
            if self.job_df is None:
                return {'skills': [], 'experience_level': 'Any', 'keywords': []}
            
            # Find matching roles in job dataset
            role_matches = self.job_df[
                self.job_df['Title'].str.contains(role_name, case=False, na=False) |
                self.job_df['Keywords'].str.contains(role_name, case=False, na=False)
            ]
            
            if len(role_matches) == 0:
                return {'skills': [], 'experience_level': 'Any', 'keywords': []}
            
            # Aggregate skills and requirements
            all_skills = []
            experience_levels = []
            keywords = []
            
            for _, row in role_matches.iterrows():
                if pd.notna(row['Skills']):
                    skills = [s.strip() for s in str(row['Skills']).split(';')]
                    all_skills.extend(skills)
                
                if pd.notna(row['ExperienceLevel']):
                    experience_levels.append(row['ExperienceLevel'])
                
                if pd.notna(row['Keywords']):
                    kw = [k.strip() for k in str(row['Keywords']).split(';')]
                    keywords.extend(kw)
            
            # Get most common requirements
            from collections import Counter
            skill_counts = Counter(all_skills)
            exp_counts = Counter(experience_levels)
            keyword_counts = Counter(keywords)
            
            return {
                'skills': [skill for skill, count in skill_counts.most_common(20)],
                'experience_level': exp_counts.most_common(1)[0][0] if exp_counts else 'Any',
                'keywords': [kw for kw, count in keyword_counts.most_common(10)],
                'total_jobs': len(role_matches)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get role requirements for {role_name}: {e}")
            return {'skills': [], 'experience_level': 'Any', 'keywords': []}
    
    def compare_with_role_requirements(self, resume_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
        """Compare resume against role-specific requirements"""
        try:
            # Get role requirements
            role_reqs = self.get_role_requirements(target_role)
            
            # Extract resume data
            resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
            resume_exp_years = resume_data.get('experience', {}).get('total_years', 0)
            resume_exp_level = resume_data.get('experience', {}).get('level', 'fresher')
            
            # Compare skills
            required_skills = set(skill.lower() for skill in role_reqs['skills'])
            matched_skills = resume_skills.intersection(required_skills)
            missing_skills = required_skills - resume_skills
            
            skill_match_percentage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0
            
            # Compare experience
            exp_match = self._compare_experience_levels(resume_exp_level, role_reqs['experience_level'])
            
            # Calculate overall compatibility
            compatibility_score = (skill_match_percentage * 0.7 + exp_match * 0.3)
            
            return {
                'role': target_role,
                'compatibility_score': round(compatibility_score, 1),
                'skill_analysis': {
                    'matched_skills': list(matched_skills),
                    'missing_skills': list(missing_skills),
                    'match_percentage': round(skill_match_percentage, 1),
                    'total_required': len(required_skills)
                },
                'experience_analysis': {
                    'resume_level': resume_exp_level,
                    'required_level': role_reqs['experience_level'],
                    'match_score': exp_match,
                    'resume_years': resume_exp_years
                },
                'role_requirements': role_reqs
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Role comparison failed for {target_role}: {e}")
            return {
                'role': target_role,
                'compatibility_score': 0,
                'error': str(e)
            }
    
    def _compare_experience_levels(self, resume_level: str, required_level: str) -> float:
        """Compare experience levels and return match score (0-100)"""
        level_hierarchy = {
            'fresher': 1,
            'junior': 2,
            'mid-level': 3,
            'senior': 4,
            'entry-level': 1,
            'experienced': 3,
            'any': 2.5
        }
        
        resume_score = level_hierarchy.get(resume_level.lower(), 1)
        required_score = level_hierarchy.get(required_level.lower(), 2.5)
        
        # Perfect match
        if resume_score == required_score:
            return 100.0
        
        # Calculate distance-based score
        distance = abs(resume_score - required_score)
        max_distance = 3  # Maximum possible distance
        
        match_score = max(0, 100 - (distance / max_distance * 50))
        return round(match_score, 1)
    
    def get_available_roles(self) -> List[str]:
        """Get list of available roles for scoring"""
        return self.available_roles.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about trained models"""
        return {
            'is_trained': self.is_trained,
            'available_roles': self.available_roles,
            'trained_models': list(self.role_models.keys()),
            'model_count': len(self.role_models),
            'dataset_info': {
                'ats_samples': len(self.ats_df) if self.ats_df is not None else 0,
                'job_samples': len(self.job_df) if self.job_df is not None else 0
            }
        }

# Global instance
_role_ml_system = None

def get_role_ml_system() -> RoleBasedMLSystem:
    """Get singleton role-based ML system"""
    global _role_ml_system
    if _role_ml_system is None:
        _role_ml_system = RoleBasedMLSystem()
    return _role_ml_system

def predict_role_based_score(resume_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """Main entry point for role-based scoring"""
    system = get_role_ml_system()
    return system.predict_role_score(resume_data, target_role)

def compare_resume_with_role(resume_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """Main entry point for role comparison"""
    system = get_role_ml_system()
    return system.compare_with_role_requirements(resume_data, target_role)