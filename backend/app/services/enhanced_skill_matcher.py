"""
Enhanced Skill Gap Analyzer Service
Real ATS-style skill matching and gap analysis using normalized datasets
"""

import re
import json
from typing import List, Dict, Set, Tuple, Any, Optional
from pathlib import Path
from difflib import SequenceMatcher
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .dataset_normalizer import get_normalized_datasets, get_skill_gap_reference
from ..core.database import get_collection

class EnhancedSkillGapAnalyzer:
    """Production-grade skill gap analyzer using real ATS logic"""
    
    def __init__(self):
        # Load normalized datasets
        self.ats_df, self.job_df = get_normalized_datasets()
        self.skill_gap_reference = get_skill_gap_reference()
        
        # Extract all unique skills from both datasets
        self.all_skills = self._extract_all_skills()
        
        # Initialize TF-IDF vectorizer for semantic matching
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True,
            max_features=5000
        )
        
        # Prepare skill vectors
        self._prepare_skill_vectors()
        
        # Skill normalization mappings
        self.skill_mappings = {
            'c#': ['csharp', 'c sharp', 'c-sharp'],
            'c++': ['cpp', 'c plus plus', 'cplusplus'],
            'javascript': ['js', 'java script', 'ecmascript'],
            'typescript': ['ts'],
            'python': ['py', 'python3'],
            'node.js': ['nodejs', 'node'],
            'react.js': ['reactjs', 'react'],
            'vue.js': ['vuejs', 'vue'],
            'angular.js': ['angularjs', 'angular'],
            'asp.net': ['aspnet', 'asp net'],
            'asp.net mvc': ['aspnet mvc', 'asp net mvc'],
            'entity framework': ['ef', 'entityframework'],
            '.net framework': ['dotnet framework', 'net framework'],
            '.net core': ['dotnet core', 'net core'],
            'sql server': ['sqlserver', 'mssql', 'microsoft sql server'],
            'mysql': ['my sql'],
            'postgresql': ['postgres', 'postgre sql'],
            'mongodb': ['mongo db', 'mongo'],
            'visual studio': ['vs', 'visualstudio'],
            'git': ['github', 'gitlab', 'version control'],
            'unit testing': ['unittest', 'testing', 'test driven development', 'tdd'],
            'machine learning': ['ml', 'machinelearning'],
            'deep learning': ['dl', 'deeplearning'],
            'natural language processing': ['nlp'],
            'tensorflow': ['tensor flow'],
            'pytorch': ['torch'],
            'cybersecurity': ['cyber security', 'information security', 'infosec'],
            'ethical hacking': ['penetration testing', 'pen testing', 'white hat hacking']
        }
    
    def _extract_all_skills(self) -> Set[str]:
        """Extract all unique skills from both datasets"""
        all_skills = set()
        
        # From ATS dataset
        if 'skills_normalized' in self.ats_df.columns:
            for skills_list in self.ats_df['skills_normalized']:
                if isinstance(skills_list, str):
                    try:
                        skills_list = eval(skills_list)
                    except:
                        continue
                if isinstance(skills_list, list):
                    all_skills.update(skills_list)
        
        # From Job dataset
        if 'all_skills' in self.job_df.columns:
            for skills_list in self.job_df['all_skills']:
                if isinstance(skills_list, str):
                    try:
                        skills_list = eval(skills_list)
                    except:
                        continue
                if isinstance(skills_list, list):
                    all_skills.update(skills_list)
        
        return all_skills
    
    def _prepare_skill_vectors(self):
        """Prepare TF-IDF vectors for semantic skill matching"""
        try:
            skill_texts = list(self.all_skills)
            if skill_texts:
                self.skill_vectors = self.vectorizer.fit_transform(skill_texts)
                self.skill_names = skill_texts
            else:
                self.skill_vectors = None
                self.skill_names = []
        except Exception as e:
            print(f"[WARNING] Could not prepare skill vectors: {e}")
            self.skill_vectors = None
            self.skill_names = []
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name using comprehensive mappings"""
        if not skill:
            return ""
        
        skill = skill.lower().strip()
        
        # Check mappings
        for standard_skill, variations in self.skill_mappings.items():
            if skill == standard_skill or skill in variations:
                return standard_skill
        
        # Clean skill name
        skill = re.sub(r'[^\w\s\.\+\#]', '', skill).strip()
        return skill
    
    def get_job_skills_by_role(self, job_role: str) -> Dict[str, Any]:
        """Get required skills for a specific job role from dataset"""
        job_role_lower = job_role.lower()
        
        # Find matching jobs in dataset
        matching_jobs = self.job_df[
            self.job_df['title_normalized'].str.contains(job_role_lower, na=False)
        ]
        
        if matching_jobs.empty:
            # Try partial matching
            matching_jobs = self.job_df[
                self.job_df['title_normalized'].str.contains(
                    job_role_lower.split()[0], na=False
                )
            ]
        
        if matching_jobs.empty:
            return {
                'required_skills': [],
                'experience_level': 'fresher',
                'job_count': 0,
                'error': f'No jobs found for role: {job_role}'
            }
        
        # Aggregate skills from all matching jobs
        all_required_skills = set()
        experience_levels = []
        
        for _, job in matching_jobs.iterrows():
            skills = job.get('all_skills', [])
            if isinstance(skills, str):
                try:
                    skills = eval(skills)
                except:
                    continue
            
            if isinstance(skills, list):
                all_required_skills.update(skills)
            
            exp_level = job.get('experience_level_normalized', 'fresher')
            if exp_level:
                experience_levels.append(exp_level)
        
        # Determine most common experience level
        if experience_levels:
            exp_level = max(set(experience_levels), key=experience_levels.count)
        else:
            exp_level = 'fresher'
        
        return {
            'required_skills': list(all_required_skills),
            'experience_level': exp_level,
            'job_count': len(matching_jobs),
            'sample_jobs': matching_jobs['Title'].head(3).tolist()
        }
    
    def analyze_skill_gap(self, user_skills: List[str], target_role: str) -> Dict[str, Any]:
        """🔥 FEATURE 1: Comprehensive Skill Gap Analysis"""
        
        # Normalize user skills
        user_skills_normalized = [self.normalize_skill(skill) for skill in user_skills if skill]
        user_skills_set = set(user_skills_normalized)
        
        # Get job requirements
        job_requirements = self.get_job_skills_by_role(target_role)
        
        if 'error' in job_requirements:
            return {
                'success': False,
                'error': job_requirements['error'],
                'suggestions': ['Try a different role name', 'Check available roles in our database']
            }
        
        required_skills = set(job_requirements['required_skills'])
        
        # 📌 Algorithm: Keyword Matching + Normalization
        matched_skills = user_skills_set.intersection(required_skills)
        missing_skills = required_skills - user_skills_set
        additional_skills = user_skills_set - required_skills
        
        # Calculate match percentage
        total_required = len(required_skills)
        matched_count = len(matched_skills)
        match_percentage = (matched_count / total_required * 100) if total_required > 0 else 0
        
        # Skill gap severity analysis
        gap_severity = self._calculate_gap_severity(match_percentage, len(missing_skills))
        
        # Find similar skills for better matching
        enhanced_matches = self._find_similar_skills_in_gap(user_skills_normalized, list(missing_skills))
        
        return {
            'success': True,
            'target_role': target_role,
            'job_count': job_requirements['job_count'],
            'experience_level': job_requirements['experience_level'],
            
            # ✅ Core Results
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'additional_skills': list(additional_skills),
            
            # 📊 Metrics
            'match_percentage': round(match_percentage, 1),
            'matched_count': matched_count,
            'total_required': total_required,
            'gap_count': len(missing_skills),
            
            # 🎯 Analysis
            'gap_severity': gap_severity,
            'enhanced_matches': enhanced_matches,
            'skill_categories': self._categorize_skills(missing_skills),
            
            # 📈 Insights
            'insights': self._generate_gap_insights(match_percentage, missing_skills, additional_skills),
            'sample_jobs': job_requirements.get('sample_jobs', [])
        }
    
    def generate_improvement_suggestions(self, skill_gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """🔥 FEATURE 2: Resume Improvement Suggestions"""
        
        missing_skills = skill_gap_analysis.get('missing_skills', [])
        match_percentage = skill_gap_analysis.get('match_percentage', 0)
        additional_skills = skill_gap_analysis.get('additional_skills', [])
        target_role = skill_gap_analysis.get('target_role', '')
        
        suggestions = []
        priority_actions = []
        
        # 🧠 Logic: Rule-based (Explainable)
        
        # Condition 1: Skill match < 60%
        if match_percentage < 60:
            suggestions.append({
                'type': 'critical',
                'category': 'Skills',
                'title': 'Add Missing Critical Skills',
                'description': f'Your skill match is {match_percentage:.1f}%. Focus on learning these high-priority skills.',
                'action_items': missing_skills[:5],  # Top 5 missing skills
                'impact': 'High - Directly improves ATS score'
            })
            priority_actions.append('Learn missing technical skills')
        
        # Condition 2: Low keyword density
        if len(missing_skills) > 3:
            role_keywords = self._get_role_specific_keywords(target_role)
            suggestions.append({
                'type': 'important',
                'category': 'Keywords',
                'title': 'Optimize Resume Keywords',
                'description': 'Add role-specific keywords to improve ATS scanning.',
                'action_items': role_keywords[:3],
                'impact': 'Medium - Better keyword matching'
            })
            priority_actions.append('Include role-specific keywords')
        
        # Condition 3: Experience gap suggestions
        if match_percentage < 80:
            suggestions.append({
                'type': 'recommended',
                'category': 'Experience',
                'title': 'Demonstrate Practical Experience',
                'description': 'Show hands-on experience with missing skills through projects.',
                'action_items': [
                    f'Create projects using {", ".join(missing_skills[:3])}',
                    'Add internships or freelance work',
                    'Include relevant coursework or certifications'
                ],
                'impact': 'High - Proves practical knowledge'
            })
            priority_actions.append('Build practical projects')
        
        # Additional skill leverage
        if additional_skills:
            suggestions.append({
                'type': 'opportunity',
                'category': 'Positioning',
                'title': 'Leverage Additional Skills',
                'description': 'Highlight your unique skills that add value.',
                'action_items': list(additional_skills)[:3],
                'impact': 'Medium - Differentiates your profile'
            })
        
        # Role-specific suggestions
        role_specific = self._get_role_specific_suggestions(target_role, missing_skills)
        if role_specific:
            suggestions.extend(role_specific)
        
        return {
            'success': True,
            'target_role': target_role,
            'overall_priority': self._determine_overall_priority(match_percentage),
            'suggestions': suggestions,
            'priority_actions': priority_actions,
            'estimated_improvement': self._estimate_improvement_potential(missing_skills),
            'timeline': self._suggest_learning_timeline(missing_skills)
        }
    
    def get_role_based_scoring_data(self, target_role: str) -> Dict[str, Any]:
        """🔥 FEATURE 3: Role-Based Resume Scoring Data"""
        
        role_lower = target_role.lower()
        
        # Filter ATS dataset by role
        role_data = self.ats_df[
            self.ats_df['job_role_normalized'].str.contains(role_lower, na=False)
        ]
        
        if role_data.empty:
            # Try partial matching
            role_data = self.ats_df[
                self.ats_df['job_role_normalized'].str.contains(
                    role_lower.split()[0], na=False
                )
            ]
        
        if role_data.empty:
            return {
                'success': False,
                'error': f'No training data found for role: {target_role}',
                'available_roles': self.ats_df['job_role_normalized'].unique().tolist()[:10]
            }
        
        # Extract role-specific patterns
        avg_score = role_data['AI Score (0-100)'].mean()
        score_std = role_data['AI Score (0-100)'].std()
        
        # Get top skills for this role
        all_role_skills = []
        for skills_list in role_data['skills_normalized']:
            if isinstance(skills_list, str):
                try:
                    skills_list = eval(skills_list)
                except:
                    continue
            if isinstance(skills_list, list):
                all_role_skills.extend(skills_list)
        
        # Count skill frequency
        skill_counts = {}
        for skill in all_role_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Get top skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Experience analysis
        exp_analysis = {
            'avg_years': role_data['experience_years'].mean(),
            'common_level': role_data['experience_level'].mode().iloc[0] if not role_data['experience_level'].mode().empty else 'fresher'
        }
        
        # Education analysis
        edu_analysis = {
            'common_education': role_data['education_normalized'].mode().iloc[0] if not role_data['education_normalized'].mode().empty else 'B.Tech'
        }
        
        return {
            'success': True,
            'role': target_role,
            'sample_size': len(role_data),
            'scoring_benchmarks': {
                'average_score': round(avg_score, 1),
                'score_std': round(score_std, 1),
                'score_range': {
                    'min': int(role_data['AI Score (0-100)'].min()),
                    'max': int(role_data['AI Score (0-100)'].max())
                }
            },
            'top_skills': [{'skill': skill, 'frequency': count} for skill, count in top_skills],
            'experience_profile': exp_analysis,
            'education_profile': edu_analysis,
            'success_factors': self._identify_success_factors(role_data)
        }
    
    def _calculate_gap_severity(self, match_percentage: float, gap_count: int) -> Dict[str, Any]:
        """Calculate skill gap severity"""
        if match_percentage >= 80:
            severity = 'low'
            level = 1
        elif match_percentage >= 60:
            severity = 'medium'
            level = 2
        elif match_percentage >= 40:
            severity = 'high'
            level = 3
        else:
            severity = 'critical'
            level = 4
        
        return {
            'level': severity,
            'numeric_level': level,
            'description': self._get_severity_description(severity),
            'recommendation': self._get_severity_recommendation(severity)
        }
    
    def _find_similar_skills_in_gap(self, user_skills: List[str], missing_skills: List[str]) -> Dict[str, Any]:
        """Find similar skills that might bridge the gap"""
        similar_matches = {}
        
        for missing_skill in missing_skills[:5]:  # Top 5 missing skills
            best_matches = []
            
            for user_skill in user_skills:
                # Calculate similarity
                similarity = SequenceMatcher(None, missing_skill.lower(), user_skill.lower()).ratio()
                
                if similarity > 0.6:  # 60% similarity threshold
                    best_matches.append({
                        'user_skill': user_skill,
                        'similarity': round(similarity, 2),
                        'suggestion': f'Leverage {user_skill} experience to learn {missing_skill}'
                    })
            
            if best_matches:
                similar_matches[missing_skill] = sorted(best_matches, key=lambda x: x['similarity'], reverse=True)[:2]
        
        return similar_matches
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills by type"""
        categories = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'tools': [],
            'cloud': [],
            'other': []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            
            if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'c#', 'c++', 'php', 'ruby']):
                categories['programming_languages'].append(skill)
            elif any(fw in skill_lower for fw in ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'asp.net']):
                categories['frameworks'].append(skill)
            elif any(db in skill_lower for db in ['sql', 'mysql', 'postgresql', 'mongodb', 'redis']):
                categories['databases'].append(skill)
            elif any(tool in skill_lower for tool in ['git', 'docker', 'jenkins', 'visual studio']):
                categories['tools'].append(skill)
            elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'kubernetes']):
                categories['cloud'].append(skill)
            else:
                categories['other'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _generate_gap_insights(self, match_percentage: float, missing_skills: List[str], additional_skills: List[str]) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        if match_percentage >= 80:
            insights.append("🎉 Excellent skill match! You're well-qualified for this role.")
        elif match_percentage >= 60:
            insights.append("👍 Good skill foundation. Focus on filling key gaps.")
        else:
            insights.append("⚠️ Significant skill gaps identified. Consider targeted learning.")
        
        if len(missing_skills) <= 3:
            insights.append(f"💡 Focus on learning {len(missing_skills)} key skills to become highly competitive.")
        else:
            insights.append(f"📚 Prioritize the top 3-5 skills from {len(missing_skills)} missing skills.")
        
        if additional_skills:
            insights.append(f"✨ You have {len(additional_skills)} additional skills that add unique value.")
        
        return insights
    
    def _get_role_specific_keywords(self, role: str) -> List[str]:
        """Get role-specific keywords for optimization"""
        role_lower = role.lower()
        
        keyword_map = {
            '.net developer': ['asp.net', 'c#', 'mvc', 'entity framework', 'sql server', 'visual studio'],
            'web developer': ['html', 'css', 'javascript', 'react', 'node.js', 'responsive design'],
            'data scientist': ['python', 'machine learning', 'pandas', 'numpy', 'sql', 'statistics'],
            'cybersecurity': ['security', 'penetration testing', 'vulnerability assessment', 'compliance']
        }
        
        for role_key, keywords in keyword_map.items():
            if role_key in role_lower:
                return keywords
        
        return ['technical skills', 'problem solving', 'teamwork']
    
    def _get_role_specific_suggestions(self, role: str, missing_skills: List[str]) -> List[Dict[str, Any]]:
        """Generate role-specific improvement suggestions"""
        suggestions = []
        role_lower = role.lower()
        
        if '.net' in role_lower and any('c#' in skill.lower() for skill in missing_skills):
            suggestions.append({
                'type': 'technical',
                'category': 'Certification',
                'title': 'Get Microsoft .NET Certification',
                'description': 'Microsoft certifications are highly valued for .NET roles.',
                'action_items': ['Microsoft Certified: Azure Developer Associate', 'C# programming certification'],
                'impact': 'High - Industry recognition'
            })
        
        if 'data' in role_lower and any('python' in skill.lower() for skill in missing_skills):
            suggestions.append({
                'type': 'technical',
                'category': 'Portfolio',
                'title': 'Build Data Science Portfolio',
                'description': 'Create projects showcasing data analysis and ML skills.',
                'action_items': ['Kaggle competitions', 'GitHub data projects', 'Blog about findings'],
                'impact': 'High - Demonstrates practical skills'
            })
        
        return suggestions
    
    def _determine_overall_priority(self, match_percentage: float) -> str:
        """Determine overall improvement priority"""
        if match_percentage >= 80:
            return 'low'
        elif match_percentage >= 60:
            return 'medium'
        else:
            return 'high'
    
    def _estimate_improvement_potential(self, missing_skills: List[str]) -> Dict[str, Any]:
        """Estimate potential score improvement"""
        skill_count = len(missing_skills)
        
        if skill_count <= 2:
            potential_gain = '10-15 points'
            timeline = '2-4 weeks'
        elif skill_count <= 5:
            potential_gain = '15-25 points'
            timeline = '1-3 months'
        else:
            potential_gain = '25-40 points'
            timeline = '3-6 months'
        
        return {
            'score_gain': potential_gain,
            'timeline': timeline,
            'confidence': 'high' if skill_count <= 5 else 'medium'
        }
    
    def _suggest_learning_timeline(self, missing_skills: List[str]) -> Dict[str, List[str]]:
        """Suggest learning timeline for missing skills"""
        timeline = {
            'week_1_2': [],
            'month_1': [],
            'month_2_3': [],
            'ongoing': []
        }
        
        # Prioritize skills by learning difficulty
        easy_skills = []
        medium_skills = []
        hard_skills = []
        
        for skill in missing_skills:
            skill_lower = skill.lower()
            if any(easy in skill_lower for easy in ['git', 'html', 'css', 'unit testing']):
                easy_skills.append(skill)
            elif any(medium in skill_lower for medium in ['javascript', 'sql', 'linux']):
                medium_skills.append(skill)
            else:
                hard_skills.append(skill)
        
        timeline['week_1_2'] = easy_skills[:2]
        timeline['month_1'] = medium_skills[:2]
        timeline['month_2_3'] = hard_skills[:2]
        timeline['ongoing'] = ['Practice and build projects', 'Stay updated with industry trends']
        
        return timeline
    
    def _identify_success_factors(self, role_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify success factors from high-scoring profiles"""
        high_performers = role_data[role_data['AI Score (0-100)'] >= 90]
        
        if high_performers.empty:
            return []
        
        factors = []
        
        # Skill count factor
        avg_skills_high = high_performers['skills_count'].mean()
        avg_skills_all = role_data['skills_count'].mean()
        
        if avg_skills_high > avg_skills_all:
            factors.append({
                'factor': 'Skill Diversity',
                'description': f'High performers have {avg_skills_high:.1f} skills vs {avg_skills_all:.1f} average',
                'recommendation': 'Develop a broader skill set'
            })
        
        # Experience factor
        avg_exp_high = high_performers['experience_years'].mean()
        avg_exp_all = role_data['experience_years'].mean()
        
        if avg_exp_high > avg_exp_all:
            factors.append({
                'factor': 'Experience Level',
                'description': f'High performers have {avg_exp_high:.1f} years vs {avg_exp_all:.1f} average',
                'recommendation': 'Gain more hands-on experience'
            })
        
        return factors
    
    def _get_severity_description(self, severity: str) -> str:
        """Get description for severity level"""
        descriptions = {
            'low': 'Minor gaps that can be easily addressed',
            'medium': 'Moderate gaps requiring focused learning',
            'high': 'Significant gaps needing substantial skill development',
            'critical': 'Major gaps requiring comprehensive upskilling'
        }
        return descriptions.get(severity, 'Unknown severity')
    
    def _get_severity_recommendation(self, severity: str) -> str:
        """Get recommendation for severity level"""
        recommendations = {
            'low': 'Quick skill updates and resume optimization',
            'medium': 'Targeted learning plan over 1-2 months',
            'high': 'Comprehensive skill development program',
            'critical': 'Consider additional training or certification programs'
        }
        return recommendations.get(severity, 'Consult with career advisor')

# Global analyzer instance
_analyzer_instance = None

def get_skill_gap_analyzer() -> EnhancedSkillGapAnalyzer:
    """Get singleton skill gap analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = EnhancedSkillGapAnalyzer()
    return _analyzer_instance

# Main API functions
def analyze_skill_gap(user_skills: List[str], target_role: str) -> Dict[str, Any]:
    """🔥 FEATURE 1: Skill Gap Analyzer API"""
    analyzer = get_skill_gap_analyzer()
    return analyzer.analyze_skill_gap(user_skills, target_role)

def generate_improvement_suggestions(skill_gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """🔥 FEATURE 2: Resume Improvement Suggestions API"""
    analyzer = get_skill_gap_analyzer()
    return analyzer.generate_improvement_suggestions(skill_gap_analysis)

def get_role_based_scoring_data(target_role: str) -> Dict[str, Any]:
    """🔥 FEATURE 3: Role-Based Scoring Data API"""
    analyzer = get_skill_gap_analyzer()
    return analyzer.get_role_based_scoring_data(target_role)