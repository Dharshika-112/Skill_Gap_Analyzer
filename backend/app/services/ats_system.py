"""
AI-Powered Resume Screening System (Real ATS Style)
Combines ML-based ATS scoring with skill gap analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import joblib
import pickle
from datetime import datetime

# Dataset paths
ATS_DATASET_PATH = Path(__file__).parents[2] / 'data' / 'raw' / 'AI_Resume_Screening.csv'
JOB_DATASET_PATH = Path(__file__).parents[2] / 'data' / 'raw' / 'job_dataset.csv'
MODEL_DIR = Path(__file__).parents[2] / 'data' / 'models'
MODEL_DIR.mkdir(exist_ok=True)

class ATSSystem:
    def __init__(self):
        self.ats_model = None
        self.tfidf_vectorizer = None
        self.label_encoders = {}
        self.ats_df = None
        self.job_df = None
        self.is_trained = False
        
        # Load datasets
        self.load_datasets()
        
        # Try to load pre-trained model, otherwise train new one
        if not self.load_model():
            print("[INFO] Training new ATS model...")
            self.train_ats_model()
    
    def load_datasets(self):
        """Load both datasets"""
        try:
            if ATS_DATASET_PATH.exists():
                self.ats_df = pd.read_csv(ATS_DATASET_PATH)
                print(f"[INFO] Loaded ATS dataset: {len(self.ats_df)} resumes")
            else:
                print(f"[WARNING] ATS dataset not found at {ATS_DATASET_PATH}")
                
            if JOB_DATASET_PATH.exists():
                self.job_df = pd.read_csv(JOB_DATASET_PATH)
                print(f"[INFO] Loaded Job dataset: {len(self.job_df)} jobs, {self.job_df['Title'].nunique()} roles")
            else:
                print(f"[WARNING] Job dataset not found at {JOB_DATASET_PATH}")
                
        except Exception as e:
            print(f"[ERROR] Failed to load datasets: {e}")
    
    def preprocess_ats_data(self):
        """Preprocess ATS dataset for training"""
        if self.ats_df is None:
            return None, None
        
        # Create feature columns
        df = self.ats_df.copy()
        
        # Clean and prepare features
        df['Skills_Clean'] = df['Skills'].fillna('').str.lower()
        df['Education_Clean'] = df['Education'].fillna('').str.lower()
        df['Certifications_Clean'] = df['Certifications'].fillna('none').str.lower()
        df['Job_Role_Clean'] = df['Job Role'].fillna('').str.lower()
        
        # Encode categorical variables
        categorical_cols = ['Education', 'Job Role']
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            df[f'{col}_Encoded'] = self.label_encoders[col].fit_transform(df[col].fillna('Unknown'))
        
        # Create combined text features for TF-IDF
        df['Combined_Text'] = (
            df['Skills_Clean'] + ' ' + 
            df['Education_Clean'] + ' ' + 
            df['Certifications_Clean'] + ' ' +
            df['Job_Role_Clean']
        )
        
        # Numerical features
        numerical_features = [
            'Experience (Years)', 'Projects Count', 
            'Education_Encoded', 'Job Role_Encoded'
        ]
        
        # Fill missing values
        for col in numerical_features:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        return df, numerical_features
    
    def train_ats_model(self):
        """Train ATS scoring model using Random Forest"""
        df, numerical_features = self.preprocess_ats_data()
        if df is None:
            print("[ERROR] Cannot train model - no ATS data available")
            return False
        
        try:
            # Prepare text features using TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            
            tfidf_features = self.tfidf_vectorizer.fit_transform(df['Combined_Text'])
            
            # Combine numerical and text features
            numerical_data = df[numerical_features].values
            combined_features = np.hstack([numerical_data, tfidf_features.toarray()])
            
            # Target variable
            y = df['AI Score (0-100)'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                combined_features, y, test_size=0.2, random_state=42
            )
            
            # Train Random Forest model
            self.ats_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            self.ats_model.fit(X_train, y_train)
            
            # Evaluate model
            train_score = self.ats_model.score(X_train, y_train)
            test_score = self.ats_model.score(X_test, y_test)
            
            print(f"[INFO] ATS Model trained successfully!")
            print(f"[INFO] Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to train ATS model: {e}")
            return False
    
    def save_model(self):
        """Save trained model and components"""
        try:
            model_data = {
                'ats_model': self.ats_model,
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'label_encoders': self.label_encoders,
                'is_trained': self.is_trained
            }
            
            model_path = MODEL_DIR / 'ats_system.pkl'
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"[INFO] ATS model saved to {model_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save model: {e}")
    
    def load_model(self):
        """Load pre-trained model"""
        try:
            model_path = MODEL_DIR / 'ats_system.pkl'
            if not model_path.exists():
                return False
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.ats_model = model_data['ats_model']
            self.tfidf_vectorizer = model_data['tfidf_vectorizer']
            self.label_encoders = model_data['label_encoders']
            self.is_trained = model_data['is_trained']
            
            print("[INFO] Pre-trained ATS model loaded successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            return False
    
    def predict_ats_score(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict ATS score for a resume"""
        if not self.is_trained:
            return {"error": "ATS model not trained"}
        
        try:
            # Prepare resume data
            skills = resume_data.get('skills', [])
            experience_years = resume_data.get('experience_years', 0)
            education = resume_data.get('education', 'Unknown')
            certifications = resume_data.get('certifications', [])
            job_role = resume_data.get('target_role', 'Unknown')
            projects_count = resume_data.get('projects_count', 0)
            
            # Create feature vector
            skills_text = ' '.join(skills).lower() if skills else ''
            cert_text = ' '.join(certifications).lower() if certifications else 'none'
            
            combined_text = f"{skills_text} {education.lower()} {cert_text} {job_role.lower()}"
            
            # TF-IDF features
            tfidf_features = self.tfidf_vectorizer.transform([combined_text])
            
            # Numerical features
            education_encoded = 0
            job_role_encoded = 0
            
            if 'Education' in self.label_encoders:
                try:
                    education_encoded = self.label_encoders['Education'].transform([education])[0]
                except:
                    education_encoded = 0
            
            if 'Job Role' in self.label_encoders:
                try:
                    job_role_encoded = self.label_encoders['Job Role'].transform([job_role])[0]
                except:
                    job_role_encoded = 0
            
            numerical_features = np.array([[
                experience_years, projects_count, education_encoded, job_role_encoded
            ]])
            
            # Combine features
            combined_features = np.hstack([numerical_features, tfidf_features.toarray()])
            
            # Predict
            ats_score = self.ats_model.predict(combined_features)[0]
            ats_score = max(0, min(100, ats_score))  # Clamp to 0-100
            
            # Determine category
            if ats_score >= 90:
                category = "Excellent"
                recommendation = "Strong candidate - Proceed to interview"
            elif ats_score >= 75:
                category = "Good"
                recommendation = "Good candidate - Review details"
            elif ats_score >= 60:
                category = "Average"
                recommendation = "Moderate fit - Consider with reservations"
            elif ats_score >= 40:
                category = "Below Average"
                recommendation = "Weak candidate - Needs improvement"
            else:
                category = "Poor"
                recommendation = "Not suitable - Major gaps identified"
            
            return {
                "ats_score": round(ats_score, 2),
                "category": category,
                "recommendation": recommendation,
                "confidence": "High" if abs(ats_score - 50) > 25 else "Medium"
            }
            
        except Exception as e:
            print(f"[ERROR] ATS prediction failed: {e}")
            return {"error": f"Prediction failed: {str(e)}"}
    
    def skill_gap_analysis(self, resume_skills: List[str], target_role: str) -> Dict[str, Any]:
        """Perform skill gap analysis using job dataset"""
        if self.job_df is None:
            return {"error": "Job dataset not available"}
        
        try:
            # Find jobs for target role
            role_jobs = self.job_df[self.job_df['Title'].str.contains(target_role, case=False, na=False)]
            
            if role_jobs.empty:
                return {"error": f"No jobs found for role: {target_role}"}
            
            # Extract required skills
            all_required_skills = set()
            for _, job in role_jobs.iterrows():
                if pd.notna(job['Skills']):
                    skills = [s.strip() for s in str(job['Skills']).split(';')]
                    all_required_skills.update(skills)
                
                if pd.notna(job['Keywords']):
                    keywords = [k.strip() for k in str(job['Keywords']).split(';')]
                    all_required_skills.update(keywords)
            
            required_skills = list(all_required_skills)
            
            # Normalize skills for comparison
            resume_skills_lower = [s.lower().strip() for s in resume_skills]
            required_skills_lower = [s.lower().strip() for s in required_skills]
            
            # Find matches and gaps
            matched_skills = []
            missing_skills = []
            
            for req_skill in required_skills:
                req_lower = req_skill.lower().strip()
                if any(req_lower in res_skill or res_skill in req_lower 
                       for res_skill in resume_skills_lower):
                    matched_skills.append(req_skill)
                else:
                    missing_skills.append(req_skill)
            
            # Calculate match percentage
            match_percentage = (len(matched_skills) / len(required_skills) * 100) if required_skills else 0
            
            return {
                "target_role": target_role,
                "total_jobs_analyzed": len(role_jobs),
                "required_skills": required_skills,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "match_percentage": round(match_percentage, 2),
                "skill_gap_count": len(missing_skills),
                "readiness_level": self._get_readiness_level(match_percentage)
            }
            
        except Exception as e:
            print(f"[ERROR] Skill gap analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _get_readiness_level(self, match_percentage: float) -> Dict[str, str]:
        """Determine readiness level based on match percentage"""
        if match_percentage >= 80:
            return {"level": "Ready", "color": "green", "message": "Excellent match - Ready to apply"}
        elif match_percentage >= 60:
            return {"level": "Almost Ready", "color": "orange", "message": "Good match - Minor gaps to fill"}
        elif match_percentage >= 40:
            return {"level": "Needs Preparation", "color": "yellow", "message": "Moderate gaps - Requires preparation"}
        else:
            return {"level": "Significant Gap", "color": "red", "message": "Major skill gaps - Extensive preparation needed"}
    
    def role_based_scoring(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score resume for different roles"""
        if self.job_df is None:
            return {"error": "Job dataset not available"}
        
        try:
            # Get all unique roles
            roles = self.job_df['Title'].unique()
            role_scores = []
            
            for role in roles[:10]:  # Limit to top 10 roles for performance
                # Get ATS score for this role
                resume_copy = resume_data.copy()
                resume_copy['target_role'] = role
                
                ats_result = self.predict_ats_score(resume_copy)
                if 'error' not in ats_result:
                    # Get skill gap analysis
                    gap_analysis = self.skill_gap_analysis(
                        resume_data.get('skills', []), role
                    )
                    
                    if 'error' not in gap_analysis:
                        role_scores.append({
                            "role": role,
                            "ats_score": ats_result['ats_score'],
                            "match_percentage": gap_analysis['match_percentage'],
                            "combined_score": (ats_result['ats_score'] + gap_analysis['match_percentage']) / 2,
                            "readiness": gap_analysis['readiness_level']['level'],
                            "job_count": len(self.job_df[self.job_df['Title'] == role])
                        })
            
            # Sort by combined score
            role_scores.sort(key=lambda x: x['combined_score'], reverse=True)
            
            return {
                "role_scores": role_scores,
                "best_match": role_scores[0] if role_scores else None,
                "total_roles_analyzed": len(role_scores)
            }
            
        except Exception as e:
            print(f"[ERROR] Role-based scoring failed: {e}")
            return {"error": f"Scoring failed: {str(e)}"}
    
    def resume_jd_similarity(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate resume-JD similarity using TF-IDF and cosine similarity"""
        try:
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=1000
            )
            
            documents = [resume_text, job_description]
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            overall_similarity = similarity_matrix[0, 1]
            
            # Section-wise similarity (if we can parse sections)
            sections = self._parse_resume_sections(resume_text)
            section_similarities = {}
            
            for section_name, section_text in sections.items():
                if section_text.strip():
                    section_docs = [section_text, job_description]
                    section_tfidf = vectorizer.fit_transform(section_docs)
                    section_sim = cosine_similarity(section_tfidf)[0, 1]
                    section_similarities[section_name] = round(section_sim * 100, 2)
            
            return {
                "overall_similarity": round(overall_similarity * 100, 2),
                "section_similarities": section_similarities,
                "similarity_level": self._get_similarity_level(overall_similarity * 100)
            }
            
        except Exception as e:
            print(f"[ERROR] Similarity calculation failed: {e}")
            return {"error": f"Similarity calculation failed: {str(e)}"}
    
    def _parse_resume_sections(self, resume_text: str) -> Dict[str, str]:
        """Parse resume into sections"""
        sections = {
            "skills": "",
            "experience": "",
            "education": "",
            "projects": ""
        }
        
        # Simple section parsing based on keywords
        lines = resume_text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in ['skill', 'technical', 'programming']):
                current_section = 'skills'
            elif any(keyword in line_lower for keyword in ['experience', 'work', 'employment']):
                current_section = 'experience'
            elif any(keyword in line_lower for keyword in ['education', 'degree', 'university']):
                current_section = 'education'
            elif any(keyword in line_lower for keyword in ['project', 'portfolio']):
                current_section = 'projects'
            elif current_section and line.strip():
                sections[current_section] += line + '\n'
        
        return sections
    
    def _get_similarity_level(self, similarity_percentage: float) -> Dict[str, str]:
        """Get similarity level description"""
        if similarity_percentage >= 80:
            return {"level": "Excellent", "color": "green"}
        elif similarity_percentage >= 60:
            return {"level": "Good", "color": "orange"}
        elif similarity_percentage >= 40:
            return {"level": "Moderate", "color": "yellow"}
        else:
            return {"level": "Poor", "color": "red"}
    
    def generate_improvement_suggestions(self, gap_analysis: Dict[str, Any], ats_score: float) -> List[str]:
        """Generate actionable improvement suggestions"""
        suggestions = []
        
        if 'missing_skills' in gap_analysis:
            missing_skills = gap_analysis['missing_skills']
            
            if len(missing_skills) > 0:
                # Prioritize missing skills
                high_priority = missing_skills[:5]  # Top 5 missing skills
                suggestions.append(f"🎯 Add these high-priority skills: {', '.join(high_priority)}")
                
                if len(missing_skills) > 5:
                    suggestions.append(f"📚 Consider learning: {', '.join(missing_skills[5:10])}")
        
        # ATS score based suggestions
        if ats_score < 60:
            suggestions.append("📝 Improve keyword density by including more job-relevant terms")
            suggestions.append("🏆 Add more quantifiable achievements and project details")
        
        if ats_score < 40:
            suggestions.append("🎓 Consider additional certifications in your field")
            suggestions.append("💼 Gain more relevant work experience or projects")
        
        # Match percentage based suggestions
        match_percentage = gap_analysis.get('match_percentage', 0)
        if match_percentage < 50:
            suggestions.append("🔧 Focus on building core technical skills for this role")
            suggestions.append("📖 Take online courses to fill major skill gaps")
        
        return suggestions

# Global instance
ats_system = ATSSystem()

# Convenience functions
def predict_ats_score(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Predict ATS score for resume"""
    return ats_system.predict_ats_score(resume_data)

def analyze_skill_gap(resume_skills: List[str], target_role: str) -> Dict[str, Any]:
    """Analyze skill gap for target role"""
    return ats_system.skill_gap_analysis(resume_skills, target_role)

def score_resume_for_roles(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Score resume for multiple roles"""
    return ats_system.role_based_scoring(resume_data)

def calculate_resume_jd_similarity(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Calculate resume-JD similarity"""
    return ats_system.resume_jd_similarity(resume_text, job_description)

def get_improvement_suggestions(gap_analysis: Dict[str, Any], ats_score: float) -> List[str]:
    """Get improvement suggestions"""
    return ats_system.generate_improvement_suggestions(gap_analysis, ats_score)