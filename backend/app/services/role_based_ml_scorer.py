"""
Role-Based ML Resume Scorer
🔥 FEATURE 3: Role-Based Resume Scoring using ML models trained on ATS data
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import logging

from .dataset_normalizer import get_normalized_datasets
from .enhanced_skill_matcher import get_skill_gap_analyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoleBasedMLScorer:
    """Role-based resume scoring using ML models trained on ATS data"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parents[2] / 'data'
        self.models_dir = self.data_dir / 'models' / 'role_based'
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Load normalized datasets
        self.ats_df, self.job_df = get_normalized_datasets()
        
        # Initialize models storage
        self.role_models = {}
        self.role_scalers = {}
        self.role_vectorizers = {}
        self.general_model = None
        self.general_scaler = None
        
        # Feature columns for ML
        self.feature_columns = [
            'experience_years', 'experience_level_numeric', 'education_level', 
            'skills_count', 'projects_count'
        ]
        
        # Initialize or load models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load existing ML models"""
        try:
            # Try to load existing models
            self._load_existing_models()
            logger.info("[OK] Loaded existing ML models")
        except Exception as e:
            logger.info(f"[INFO] No existing models found: {e}")
            logger.info("[*] Training new ML models...")
            self._train_all_models()
    
    def _load_existing_models(self):
        """Load existing trained models"""
        model_files = list(self.models_dir.glob("*.pkl"))
        
        if not model_files:
            raise FileNotFoundError("No model files found")
        
        for model_file in model_files:
            model_name = model_file.stem
            
            if model_name == 'general_model':
                self.general_model = joblib.load(model_file)
            elif model_name == 'general_scaler':
                self.general_scaler = joblib.load(model_file)
            elif model_name.endswith('_model'):
                role = model_name.replace('_model', '')
                self.role_models[role] = joblib.load(model_file)
            elif model_name.endswith('_scaler'):
                role = model_name.replace('_scaler', '')
                self.role_scalers[role] = joblib.load(model_file)
            elif model_name.endswith('_vectorizer'):
                role = model_name.replace('_vectorizer', '')
                self.role_vectorizers[role] = joblib.load(model_file)
    
    def _train_all_models(self):
        """Train ML models for all roles with sufficient data"""
        
        # Prepare base features
        self._prepare_base_features()
        
        # Train general model (fallback)
        self._train_general_model()
        
        # Train role-specific models
        role_counts = self.ats_df['job_role_normalized'].value_counts()
        
        for role, count in role_counts.items():
            if pd.isna(role) or count < 10:  # Need at least 10 samples
                continue
            
            try:
                self._train_role_specific_model(role)
                logger.info(f"[OK] Trained model for {role}: {count} samples")
            except Exception as e:
                logger.warning(f"[WARNING] Failed to train model for {role}: {e}")
        
        logger.info(f"[OK] Trained {len(self.role_models)} role-specific models")
    
    def _prepare_base_features(self):
        """Prepare base features for ML training"""
        # Add projects count if not exists (simulate from experience)
        if 'Projects Count' not in self.ats_df.columns:
            # Simulate projects based on experience and skills
            self.ats_df['projects_count'] = (
                self.ats_df['experience_years'] * 1.5 + 
                self.ats_df['skills_count'] * 0.3
            ).round().astype(int)
        else:
            self.ats_df['projects_count'] = self.ats_df['Projects Count']
        
        # Ensure all required columns exist
        for col in self.feature_columns:
            if col not in self.ats_df.columns:
                if col == 'projects_count':
                    self.ats_df[col] = 0
                else:
                    logger.warning(f"[WARNING] Missing column: {col}")
    
    def _train_general_model(self):
        """Train general model as fallback"""
        try:
            # Prepare features
            X = self.ats_df[self.feature_columns].fillna(0)
            y = self.ats_df['AI Score (0-100)']
            
            # Add skill features
            skill_columns = [col for col in self.ats_df.columns if col.startswith('skill_')]
            if skill_columns:
                X_skills = self.ats_df[skill_columns].fillna(0)
                X = pd.concat([X, X_skills], axis=1)
            
            # Scale features
            self.general_scaler = StandardScaler()
            X_scaled = self.general_scaler.fit_transform(X)
            
            # Train model
            self.general_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.general_model.fit(X_scaled, y)
            
            # Save model
            joblib.dump(self.general_model, self.models_dir / 'general_model.pkl')
            joblib.dump(self.general_scaler, self.models_dir / 'general_scaler.pkl')
            
            # Calculate performance
            y_pred = self.general_model.predict(X_scaled)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            logger.info(f"[OK] General model trained - R²: {r2:.3f}, RMSE: {rmse:.2f}")
            
        except Exception as e:
            logger.error(f"[ERROR] General model training failed: {e}")
    
    def _train_role_specific_model(self, role: str):
        """Train ML model for specific role"""
        # Filter data for this role
        role_data = self.ats_df[self.ats_df['job_role_normalized'] == role].copy()
        
        if len(role_data) < 10:
            raise ValueError(f"Insufficient data for role {role}: {len(role_data)} samples")
        
        # Prepare features
        X = role_data[self.feature_columns].fillna(0)
        y = role_data['AI Score (0-100)']
        
        # Add skill features specific to this role
        skill_columns = [col for col in role_data.columns if col.startswith('skill_')]
        if skill_columns:
            # Only include skills that appear in this role
            relevant_skills = []
            for col in skill_columns:
                if role_data[col].sum() > 0:  # Skill appears in at least one resume
                    relevant_skills.append(col)
            
            if relevant_skills:
                X_skills = role_data[relevant_skills].fillna(0)
                X = pd.concat([X, X_skills], axis=1)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Choose model based on data size
        if len(role_data) < 50:
            model = LinearRegression()
        elif len(role_data) < 100:
            model = RandomForestRegressor(
                n_estimators=50,
                max_depth=5,
                random_state=42
            )
        else:
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        
        # Train model
        model.fit(X_scaled, y)
        
        # Store model and scaler
        role_clean = role.replace(' ', '_').replace('/', '_')
        self.role_models[role] = model
        self.role_scalers[role] = scaler
        
        # Save to disk
        joblib.dump(model, self.models_dir / f'{role_clean}_model.pkl')
        joblib.dump(scaler, self.models_dir / f'{role_clean}_scaler.pkl')
        
        # Calculate performance
        y_pred = model.predict(X_scaled)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        logger.info(f"[OK] {role} model - R²: {r2:.3f}, RMSE: {rmse:.2f}")
        
        return {
            'role': role,
            'samples': len(role_data),
            'r2_score': r2,
            'rmse': rmse,
            'features': X.columns.tolist()
        }
    
    def score_resume_general(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score resume using general ATS model"""
        try:
            if self.general_model is None or self.general_scaler is None:
                return {
                    'success': False,
                    'error': 'General model not available',
                    'score': 0
                }
            
            # Extract features from resume
            features = self._extract_features_from_resume(resume_data)
            
            # Prepare feature vector
            feature_vector = []
            for col in self.feature_columns:
                feature_vector.append(features.get(col, 0))
            
            # Add skill features
            skill_columns = [col for col in self.ats_df.columns if col.startswith('skill_')]
            resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
            
            for col in skill_columns:
                skill_name = col.replace('skill_', '')
                feature_vector.append(1 if skill_name in resume_skills else 0)
            
            # Scale and predict
            X = np.array(feature_vector).reshape(1, -1)
            X_scaled = self.general_scaler.transform(X)
            score = self.general_model.predict(X_scaled)[0]
            
            # Ensure score is within bounds
            score = max(0, min(100, score))
            
            return {
                'success': True,
                'score': round(score, 1),
                'model_type': 'general',
                'confidence': 'medium',
                'features_used': len(feature_vector)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] General scoring failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'score': 0
            }
    
    def score_resume_role_based(self, resume_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
        """🔥 FEATURE 3: Score resume for specific role using trained ML model"""
        
        # Normalize role name
        target_role_lower = target_role.lower()
        
        # Find matching role model
        matching_role = None
        for role in self.role_models.keys():
            if role.lower() in target_role_lower or target_role_lower in role.lower():
                matching_role = role
                break
        
        if matching_role is None:
            # Fallback to general model
            logger.info(f"[INFO] No specific model for {target_role}, using general model")
            general_result = self.score_resume_general(resume_data)
            general_result['model_type'] = 'general_fallback'
            general_result['target_role'] = target_role
            return general_result
        
        try:
            model = self.role_models[matching_role]
            scaler = self.role_scalers[matching_role]
            
            # Extract features from resume
            features = self._extract_features_from_resume(resume_data)
            
            # Get role-specific training data for feature alignment
            role_data = self.ats_df[self.ats_df['job_role_normalized'] == matching_role]
            
            # Prepare feature vector
            feature_vector = []
            for col in self.feature_columns:
                feature_vector.append(features.get(col, 0))
            
            # Add role-specific skill features
            skill_columns = [col for col in role_data.columns if col.startswith('skill_')]
            resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
            
            relevant_skills = []
            for col in skill_columns:
                if role_data[col].sum() > 0:  # Skill appears in this role
                    relevant_skills.append(col)
                    skill_name = col.replace('skill_', '')
                    feature_vector.append(1 if skill_name in resume_skills else 0)
            
            # Scale and predict
            X = np.array(feature_vector).reshape(1, -1)
            X_scaled = scaler.transform(X)
            score = model.predict(X_scaled)[0]
            
            # Ensure score is within bounds
            score = max(0, min(100, score))
            
            # Calculate confidence based on feature match
            skill_match_ratio = sum(1 for col in relevant_skills 
                                  if col.replace('skill_', '') in resume_skills) / len(relevant_skills) if relevant_skills else 0
            
            confidence = 'high' if skill_match_ratio > 0.6 else 'medium' if skill_match_ratio > 0.3 else 'low'
            
            # Get role benchmarks
            role_benchmarks = self._get_role_benchmarks(matching_role)
            
            return {
                'success': True,
                'score': round(score, 1),
                'target_role': target_role,
                'matched_role': matching_role,
                'model_type': 'role_specific',
                'confidence': confidence,
                'skill_match_ratio': round(skill_match_ratio, 2),
                'features_used': len(feature_vector),
                'benchmarks': role_benchmarks,
                'interpretation': self._interpret_score(score, role_benchmarks)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Role-based scoring failed for {target_role}: {e}")
            # Fallback to general model
            general_result = self.score_resume_general(resume_data)
            general_result['model_type'] = 'general_fallback'
            general_result['target_role'] = target_role
            general_result['error'] = f"Role-specific model failed: {str(e)}"
            return general_result
    
    def _extract_features_from_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ML features from resume data"""
        features = {}
        
        # Experience features
        experience_info = resume_data.get('experience', {})
        features['experience_years'] = experience_info.get('total_years', 0)
        
        # Map experience level to numeric
        exp_level = experience_info.get('level', 'fresher')
        level_map = {'fresher': 0, 'junior': 1, 'mid-level': 2, 'senior': 3}
        features['experience_level_numeric'] = level_map.get(exp_level, 0)
        
        # Education features (simulate from text)
        education_text = resume_data.get('sections', {}).get('education', '')
        features['education_level'] = self._extract_education_level(education_text)
        
        # Skills features
        skills = resume_data.get('skills', [])
        features['skills_count'] = len(skills)
        
        # Projects features (simulate from experience and skills)
        features['projects_count'] = min(
            features['experience_years'] * 2 + len(skills) // 3,
            10  # Cap at 10 projects
        )
        
        return features
    
    def _extract_education_level(self, education_text: str) -> int:
        """Extract education level from text"""
        if not education_text:
            return 2  # Default to bachelor's
        
        education_lower = education_text.lower()
        
        if any(term in education_lower for term in ['phd', 'doctorate', 'ph.d']):
            return 4
        elif any(term in education_lower for term in ['master', 'mba', 'm.tech', 'm.sc', 'ms']):
            return 3
        elif any(term in education_lower for term in ['bachelor', 'b.tech', 'b.sc', 'be', 'bs']):
            return 2
        elif any(term in education_lower for term in ['diploma', 'associate']):
            return 1
        else:
            return 2  # Default to bachelor's
    
    def _get_role_benchmarks(self, role: str) -> Dict[str, Any]:
        """Get scoring benchmarks for a role"""
        role_data = self.ats_df[self.ats_df['job_role_normalized'] == role]
        
        if role_data.empty:
            return {}
        
        scores = role_data['AI Score (0-100)']
        
        return {
            'average_score': round(scores.mean(), 1),
            'median_score': round(scores.median(), 1),
            'std_score': round(scores.std(), 1),
            'min_score': int(scores.min()),
            'max_score': int(scores.max()),
            'percentiles': {
                '25th': round(scores.quantile(0.25), 1),
                '75th': round(scores.quantile(0.75), 1),
                '90th': round(scores.quantile(0.90), 1)
            },
            'sample_size': len(role_data)
        }
    
    def _interpret_score(self, score: float, benchmarks: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret the score relative to role benchmarks"""
        if not benchmarks:
            return {'interpretation': 'No benchmark data available'}
        
        avg_score = benchmarks.get('average_score', 70)
        percentiles = benchmarks.get('percentiles', {})
        
        if score >= percentiles.get('90th', 90):
            level = 'excellent'
            description = 'Top 10% of candidates for this role'
        elif score >= percentiles.get('75th', 80):
            level = 'very_good'
            description = 'Top 25% of candidates for this role'
        elif score >= avg_score:
            level = 'above_average'
            description = 'Above average for this role'
        elif score >= percentiles.get('25th', 60):
            level = 'average'
            description = 'Average range for this role'
        else:
            level = 'below_average'
            description = 'Below average for this role'
        
        return {
            'level': level,
            'description': description,
            'percentile_rank': self._calculate_percentile_rank(score, benchmarks)
        }
    
    def _calculate_percentile_rank(self, score: float, benchmarks: Dict[str, Any]) -> int:
        """Calculate approximate percentile rank"""
        percentiles = benchmarks.get('percentiles', {})
        
        if score >= percentiles.get('90th', 90):
            return 95
        elif score >= percentiles.get('75th', 80):
            return 85
        elif score >= benchmarks.get('median_score', 70):
            return 60
        elif score >= percentiles.get('25th', 60):
            return 40
        else:
            return 20
    
    def get_available_roles(self) -> List[Dict[str, Any]]:
        """Get list of available roles with model information"""
        roles = []
        
        # Role-specific models
        for role in self.role_models.keys():
            role_data = self.ats_df[self.ats_df['job_role_normalized'] == role]
            roles.append({
                'role': role,
                'model_type': 'role_specific',
                'sample_size': len(role_data),
                'confidence': 'high'
            })
        
        # Add general model info
        roles.append({
            'role': 'General (Any Role)',
            'model_type': 'general',
            'sample_size': len(self.ats_df),
            'confidence': 'medium'
        })
        
        return roles
    
    def retrain_model(self, role: str = None) -> Dict[str, Any]:
        """Retrain specific role model or all models"""
        try:
            if role:
                result = self._train_role_specific_model(role)
                return {
                    'success': True,
                    'message': f'Model retrained for {role}',
                    'details': result
                }
            else:
                self._train_all_models()
                return {
                    'success': True,
                    'message': 'All models retrained',
                    'role_models': len(self.role_models)
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global scorer instance
_scorer_instance = None

def get_role_based_scorer() -> RoleBasedMLScorer:
    """Get singleton role-based scorer instance"""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = RoleBasedMLScorer()
    return _scorer_instance

# Main API functions
def score_resume_general(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Score resume using general ATS model"""
    scorer = get_role_based_scorer()
    return scorer.score_resume_general(resume_data)

def score_resume_role_based(resume_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """🔥 FEATURE 3: Role-Based Resume Scoring API"""
    scorer = get_role_based_scorer()
    return scorer.score_resume_role_based(resume_data, target_role)

def get_available_scoring_roles() -> List[Dict[str, Any]]:
    """Get available roles for scoring"""
    scorer = get_role_based_scorer()
    return scorer.get_available_roles()