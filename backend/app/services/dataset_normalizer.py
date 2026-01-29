"""
Dataset Normalizer for CareerBoost AI
Normalizes both AI Resume Screening and Job Dataset for optimal feature implementation
"""

import pandas as pd
import numpy as np
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetNormalizer:
    """Comprehensive dataset normalizer for ATS and Job datasets"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parents[2] / 'data' / 'raw'
        self.processed_dir = Path(__file__).parents[2] / 'data' / 'processed'
        self.processed_dir.mkdir(exist_ok=True)
        
        # Skill normalization mappings
        self.skill_mappings = {
            # Programming Languages
            'c#': ['csharp', 'c sharp', 'c-sharp'],
            'c++': ['cpp', 'c plus plus', 'cplusplus'],
            'javascript': ['js', 'java script', 'ecmascript'],
            'typescript': ['ts'],
            'python': ['py', 'python3'],
            'node.js': ['nodejs', 'node'],
            'react.js': ['reactjs', 'react'],
            'vue.js': ['vuejs', 'vue'],
            'angular.js': ['angularjs', 'angular'],
            
            # Databases
            'sql server': ['sqlserver', 'mssql', 'microsoft sql server'],
            'mysql': ['my sql'],
            'postgresql': ['postgres', 'postgre sql'],
            'mongodb': ['mongo db', 'mongo'],
            
            # Frameworks
            'asp.net': ['aspnet', 'asp net'],
            'asp.net mvc': ['aspnet mvc', 'asp net mvc'],
            'entity framework': ['ef', 'entityframework'],
            '.net framework': ['dotnet framework', 'net framework'],
            '.net core': ['dotnet core', 'net core'],
            
            # Tools & Technologies
            'visual studio': ['vs', 'visualstudio'],
            'git': ['github', 'gitlab', 'version control'],
            'unit testing': ['unittest', 'testing', 'test driven development', 'tdd'],
            'linq': ['language integrated query'],
            
            # Cloud & DevOps
            'aws': ['amazon web services'],
            'azure': ['microsoft azure'],
            'docker': ['containerization'],
            'kubernetes': ['k8s'],
            
            # AI/ML
            'machine learning': ['ml', 'machinelearning'],
            'deep learning': ['dl', 'deeplearning'],
            'natural language processing': ['nlp'],
            'tensorflow': ['tensor flow'],
            'pytorch': ['torch'],
            
            # Security
            'cybersecurity': ['cyber security', 'information security', 'infosec'],
            'ethical hacking': ['penetration testing', 'pen testing', 'white hat hacking'],
            
            # General
            'networking': ['network administration', 'network security'],
            'linux': ['unix', 'ubuntu', 'centos', 'redhat']
        }
        
        # Experience level mappings
        self.experience_mappings = {
            'fresher': ['0-1', '0', '1', 'entry level', 'junior', 'graduate'],
            'junior': ['1-2', '2', 'junior level'],
            'mid-level': ['2-5', '3', '4', '5', 'mid level', 'intermediate'],
            'senior': ['5+', '6', '7', '8', '9', '10+', 'senior level', 'expert']
        }
        
        # Job role categories
        self.role_categories = {
            'software_development': [
                '.net developer', 'software engineer', 'full stack developer',
                'backend developer', 'frontend developer', 'web developer'
            ],
            'data_science': [
                'data scientist', 'data analyst', 'machine learning engineer',
                'ai researcher', 'data engineer'
            ],
            'cybersecurity': [
                'cybersecurity analyst', 'security engineer', 'penetration tester',
                'information security analyst'
            ],
            'devops': [
                'devops engineer', 'cloud engineer', 'infrastructure engineer',
                'site reliability engineer'
            ]
        }
    
    def normalize_skills(self, skills_text: str) -> List[str]:
        """Normalize skills text into standardized skill list"""
        if pd.isna(skills_text) or not skills_text:
            return []
        
        # Convert to lowercase and split by common delimiters
        skills_text = str(skills_text).lower()
        skills = re.split(r'[;,\|\n\r]+', skills_text)
        
        normalized_skills = []
        for skill in skills:
            skill = skill.strip()
            if not skill:
                continue
            
            # Check for mappings
            found_mapping = False
            for standard_skill, variations in self.skill_mappings.items():
                if skill == standard_skill or skill in variations:
                    normalized_skills.append(standard_skill)
                    found_mapping = True
                    break
            
            # If no mapping found, keep original (cleaned)
            if not found_mapping:
                # Clean the skill
                cleaned_skill = re.sub(r'[^\w\s\.\+\#]', '', skill).strip()
                if len(cleaned_skill) > 1:  # Avoid single characters
                    normalized_skills.append(cleaned_skill)
        
        return list(set(normalized_skills))  # Remove duplicates
    
    def normalize_experience_level(self, exp_text: str, years: int = None) -> Dict[str, Any]:
        """Normalize experience level and years"""
        if pd.isna(exp_text):
            exp_text = ""
        
        exp_text = str(exp_text).lower()
        
        # Extract years if not provided
        if years is None:
            year_matches = re.findall(r'(\d+)', exp_text)
            years = int(year_matches[0]) if year_matches else 0
        
        # Determine level based on years and text
        level = 'fresher'
        if years == 0:
            level = 'fresher'
        elif years <= 2:
            level = 'junior'
        elif years <= 5:
            level = 'mid-level'
        else:
            level = 'senior'
        
        # Override with text-based detection
        for standard_level, variations in self.experience_mappings.items():
            if any(var in exp_text for var in variations):
                level = standard_level
                break
        
        return {
            'level': level,
            'years': years,
            'level_numeric': {'fresher': 0, 'junior': 1, 'mid-level': 2, 'senior': 3}[level]
        }
    
    def categorize_job_role(self, job_title: str) -> str:
        """Categorize job role into main categories"""
        if pd.isna(job_title):
            return 'other'
        
        job_title = str(job_title).lower()
        
        for category, roles in self.role_categories.items():
            if any(role in job_title for role in roles):
                return category
        
        return 'other'
    
    def normalize_ats_dataset(self) -> pd.DataFrame:
        """Normalize AI Resume Screening dataset"""
        logger.info("[*] Normalizing ATS Resume Screening dataset...")
        
        # Load dataset
        ats_file = self.data_dir / 'AI_Resume_Screening.csv'
        df = pd.read_csv(ats_file)
        
        logger.info(f"[*] Loaded {len(df)} records from ATS dataset")
        
        # Normalize skills
        df['skills_normalized'] = df['Skills'].apply(self.normalize_skills)
        df['skills_count'] = df['skills_normalized'].apply(len)
        
        # Normalize experience
        exp_info = df.apply(lambda row: self.normalize_experience_level(
            row.get('Experience (Years)', ''), 
            row.get('Experience (Years)', 0)
        ), axis=1)
        
        df['experience_level'] = [info['level'] for info in exp_info]
        df['experience_years'] = [info['years'] for info in exp_info]
        df['experience_level_numeric'] = [info['level_numeric'] for info in exp_info]
        
        # Normalize job roles
        df['job_role_normalized'] = df['Job Role'].str.lower().str.strip()
        df['job_category'] = df['Job Role'].apply(self.categorize_job_role)
        
        # Normalize education
        df['education_normalized'] = df['Education'].str.upper().str.strip()
        df['education_level'] = df['Education'].apply(self._normalize_education_level)
        
        # Normalize decision
        df['decision_binary'] = df['Recruiter Decision'].apply(lambda x: 1 if str(x).lower() == 'hire' else 0)
        
        # Create skill vectors for ML
        all_skills = set()
        for skills_list in df['skills_normalized']:
            all_skills.update(skills_list)
        
        all_skills = sorted(list(all_skills))
        
        # Create binary skill matrix
        skill_matrix = []
        for skills_list in df['skills_normalized']:
            skill_vector = [1 if skill in skills_list else 0 for skill in all_skills]
            skill_matrix.append(skill_vector)
        
        skill_df = pd.DataFrame(skill_matrix, columns=[f'skill_{skill}' for skill in all_skills])
        df = pd.concat([df, skill_df], axis=1)
        
        # Save normalized dataset
        output_file = self.processed_dir / 'ats_dataset_normalized.csv'
        df.to_csv(output_file, index=False)
        
        # Save skill list for reference
        with open(self.processed_dir / 'ats_skills_list.json', 'w') as f:
            json.dump(all_skills, f, indent=2)
        
        logger.info(f"[OK] ATS dataset normalized: {len(all_skills)} unique skills identified")
        return df
    
    def normalize_job_dataset(self) -> pd.DataFrame:
        """Normalize Job dataset for skill gap analysis"""
        logger.info("[*] Normalizing Job dataset...")
        
        # Load dataset
        job_file = self.data_dir / 'job_dataset.csv'
        df = pd.read_csv(job_file)
        
        logger.info(f"[*] Loaded {len(df)} job records")
        
        # Normalize skills
        df['skills_normalized'] = df['Skills'].apply(self.normalize_skills)
        df['skills_count'] = df['skills_normalized'].apply(len)
        
        # Normalize keywords
        df['keywords_normalized'] = df['Keywords'].apply(self.normalize_skills)
        df['keywords_count'] = df['keywords_normalized'].apply(len)
        
        # Combine skills and keywords for comprehensive skill list
        df['all_skills'] = df.apply(lambda row: list(set(
            row['skills_normalized'] + row['keywords_normalized']
        )), axis=1)
        df['all_skills_count'] = df['all_skills'].apply(len)
        
        # Normalize experience requirements
        exp_info = df.apply(lambda row: self.normalize_experience_level(
            row['ExperienceLevel'], 
            self._extract_years_from_range(row.get('YearsOfExperience', ''))
        ), axis=1)
        
        df['experience_level_normalized'] = [info['level'] for info in exp_info]
        df['experience_years_min'] = [info['years'] for info in exp_info]
        df['experience_level_numeric'] = [info['level_numeric'] for info in exp_info]
        
        # Normalize job titles
        df['title_normalized'] = df['Title'].str.lower().str.strip()
        df['job_category'] = df['Title'].apply(self.categorize_job_role)
        
        # Extract role-specific information
        df['is_dotnet_role'] = df['title_normalized'].str.contains('.net|dotnet|c#')
        df['is_web_dev_role'] = df['title_normalized'].str.contains('web|frontend|backend|full stack')
        df['is_senior_role'] = df['title_normalized'].str.contains('senior|lead|principal|architect')
        
        # Create comprehensive skill matrix for all jobs
        all_job_skills = set()
        for skills_list in df['all_skills']:
            all_job_skills.update(skills_list)
        
        all_job_skills = sorted(list(all_job_skills))
        
        # Create binary skill requirement matrix
        skill_req_matrix = []
        for skills_list in df['all_skills']:
            skill_vector = [1 if skill in skills_list else 0 for skill in all_job_skills]
            skill_req_matrix.append(skill_vector)
        
        skill_req_df = pd.DataFrame(skill_req_matrix, columns=[f'req_{skill}' for skill in all_job_skills])
        df = pd.concat([df, skill_req_df], axis=1)
        
        # Save normalized dataset
        output_file = self.processed_dir / 'job_dataset_normalized.csv'
        df.to_csv(output_file, index=False)
        
        # Save job skills list for reference
        with open(self.processed_dir / 'job_skills_list.json', 'w') as f:
            json.dump(all_job_skills, f, indent=2)
        
        logger.info(f"[OK] Job dataset normalized: {len(all_job_skills)} unique skills identified")
        return df
    
    def _normalize_education_level(self, education: str) -> int:
        """Convert education to numeric level"""
        if pd.isna(education):
            return 0
        
        education = str(education).lower()
        
        if 'phd' in education or 'doctorate' in education:
            return 4
        elif 'master' in education or 'mba' in education or 'm.tech' in education:
            return 3
        elif 'bachelor' in education or 'b.tech' in education or 'b.sc' in education:
            return 2
        elif 'diploma' in education or 'associate' in education:
            return 1
        else:
            return 0
    
    def _extract_years_from_range(self, years_text: str) -> int:
        """Extract minimum years from range like '0-1', '5+', etc."""
        if pd.isna(years_text):
            return 0
        
        years_text = str(years_text)
        
        # Handle ranges like '0-1', '2-5'
        range_match = re.search(r'(\d+)-(\d+)', years_text)
        if range_match:
            return int(range_match.group(1))
        
        # Handle '5+' format
        plus_match = re.search(r'(\d+)\+', years_text)
        if plus_match:
            return int(plus_match.group(1))
        
        # Handle single numbers
        num_match = re.search(r'(\d+)', years_text)
        if num_match:
            return int(num_match.group(1))
        
        return 0
    
    def create_role_based_models_data(self) -> Dict[str, pd.DataFrame]:
        """Create role-specific datasets for ML model training"""
        logger.info("[*] Creating role-based model datasets...")
        
        # Load normalized ATS dataset
        ats_df = pd.read_csv(self.processed_dir / 'ats_dataset_normalized.csv')
        
        role_datasets = {}
        
        # Group by job role
        for role in ats_df['job_role_normalized'].unique():
            if pd.isna(role):
                continue
            
            role_data = ats_df[ats_df['job_role_normalized'] == role].copy()
            
            if len(role_data) >= 5:  # Only create dataset if sufficient data
                # Prepare features for ML
                feature_columns = [col for col in role_data.columns if col.startswith('skill_')]
                feature_columns.extend(['experience_years', 'experience_level_numeric', 'education_level', 'skills_count'])
                
                X = role_data[feature_columns].fillna(0)
                y = role_data['AI Score (0-100)']
                
                role_datasets[role] = {
                    'data': role_data,
                    'features': X,
                    'target': y,
                    'feature_names': feature_columns
                }
                
                # Save role-specific dataset
                role_file = self.processed_dir / f'role_{role.replace(" ", "_")}_dataset.csv'
                role_data.to_csv(role_file, index=False)
                
                logger.info(f"[OK] Created dataset for {role}: {len(role_data)} samples")
        
        return role_datasets
    
    def create_skill_gap_reference(self) -> Dict[str, Any]:
        """Create comprehensive skill gap analysis reference"""
        logger.info("[*] Creating skill gap analysis reference...")
        
        # Load normalized datasets
        job_df = pd.read_csv(self.processed_dir / 'job_dataset_normalized.csv')
        
        # Create role-skill mapping
        role_skill_mapping = {}
        
        for _, row in job_df.iterrows():
            role = row['title_normalized']
            skills = row['all_skills']
            
            if pd.isna(role) or pd.isna(skills):
                continue
            
            # Parse skills list (stored as string)
            if isinstance(skills, str):
                try:
                    skills = eval(skills)  # Convert string representation back to list
                except:
                    continue
            
            if role not in role_skill_mapping:
                role_skill_mapping[role] = {
                    'required_skills': set(),
                    'experience_level': row['experience_level_normalized'],
                    'job_count': 0
                }
            
            role_skill_mapping[role]['required_skills'].update(skills)
            role_skill_mapping[role]['job_count'] += 1
        
        # Convert sets to lists for JSON serialization
        for role in role_skill_mapping:
            role_skill_mapping[role]['required_skills'] = list(role_skill_mapping[role]['required_skills'])
        
        # Save reference
        with open(self.processed_dir / 'skill_gap_reference.json', 'w') as f:
            json.dump(role_skill_mapping, f, indent=2)
        
        logger.info(f"[OK] Skill gap reference created for {len(role_skill_mapping)} roles")
        return role_skill_mapping
    
    def normalize_all_datasets(self) -> Dict[str, Any]:
        """Normalize all datasets and create ML-ready data"""
        logger.info("[*] Starting comprehensive dataset normalization...")
        
        results = {}
        
        try:
            # Normalize ATS dataset
            ats_df = self.normalize_ats_dataset()
            results['ats_dataset'] = {
                'status': 'success',
                'records': len(ats_df),
                'skills_count': len([col for col in ats_df.columns if col.startswith('skill_')])
            }
            
            # Normalize Job dataset
            job_df = self.normalize_job_dataset()
            results['job_dataset'] = {
                'status': 'success',
                'records': len(job_df),
                'skills_count': len([col for col in job_df.columns if col.startswith('req_')])
            }
            
            # Create role-based datasets
            role_datasets = self.create_role_based_models_data()
            results['role_datasets'] = {
                'status': 'success',
                'roles_count': len(role_datasets),
                'roles': list(role_datasets.keys())
            }
            
            # Create skill gap reference
            skill_gap_ref = self.create_skill_gap_reference()
            results['skill_gap_reference'] = {
                'status': 'success',
                'roles_count': len(skill_gap_ref)
            }
            
            logger.info("[OK] All datasets normalized successfully!")
            
        except Exception as e:
            logger.error(f"[ERROR] Dataset normalization failed: {e}")
            results['error'] = str(e)
        
        return results

# Utility functions
def get_normalized_datasets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get normalized ATS and Job datasets"""
    processed_dir = Path(__file__).parents[2] / 'data' / 'processed'
    
    ats_file = processed_dir / 'ats_dataset_normalized.csv'
    job_file = processed_dir / 'job_dataset_normalized.csv'
    
    if not ats_file.exists() or not job_file.exists():
        # Normalize datasets if not exists
        normalizer = DatasetNormalizer()
        normalizer.normalize_all_datasets()
    
    ats_df = pd.read_csv(ats_file)
    job_df = pd.read_csv(job_file)
    
    return ats_df, job_df

def get_skill_gap_reference() -> Dict[str, Any]:
    """Get skill gap analysis reference"""
    processed_dir = Path(__file__).parents[2] / 'data' / 'processed'
    ref_file = processed_dir / 'skill_gap_reference.json'
    
    if not ref_file.exists():
        normalizer = DatasetNormalizer()
        return normalizer.create_skill_gap_reference()
    
    with open(ref_file, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    # Run normalization
    normalizer = DatasetNormalizer()
    results = normalizer.normalize_all_datasets()
    print(json.dumps(results, indent=2))