"""
Advanced ML/DL Skill Matching Engine
Uses multiple algorithms for high-accuracy skill matching
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import List, Dict, Any
import json

class AdvancedSkillMatcher:
    """Advanced skill matching using ML/DL algorithms"""
    
    def __init__(self, skills_vocabulary: List[str] = None):
        self.skills_vocabulary = skills_vocabulary or []
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500)
        self.scaler = StandardScaler()
        self.skill_embeddings = None
        
    def calculate_match_score(self, user_skills: List[str], role_skills: List[str]) -> Dict[str, Any]:
        """
        Calculate skill match using multiple ML algorithms:
        1. Jaccard Similarity (Set overlap)
        2. TF-IDF Cosine Similarity
        3. Vector-based Similarity
        4. Frequency Weighting
        5. Ensemble Score
        """
        
        user_skills = [s.lower() for s in user_skills]
        role_skills = [s.lower() for s in role_skills]
        
        if not role_skills:
            return {'match_percentage': 0, 'algorithms': {}}
        
        # Algorithm 1: Jaccard Similarity (Set-based)
        jaccard_score = self._calculate_jaccard_similarity(user_skills, role_skills)
        
        # Algorithm 2: TF-IDF Cosine Similarity
        tfidf_score = self._calculate_tfidf_similarity(user_skills, role_skills)
        
        # Algorithm 3: Vector Cosine Similarity
        vector_score = self._calculate_vector_similarity(user_skills, role_skills)
        
        # Algorithm 4: Frequency-weighted Matching
        freq_score = self._calculate_frequency_weighted_match(user_skills, role_skills)
        
        # Algorithm 5: Levenshtein Distance for fuzzy matching
        fuzzy_score = self._calculate_fuzzy_match(user_skills, role_skills)
        
        # Ensemble: Weighted average
        weights = {
            'jaccard': 0.25,
            'tfidf': 0.25,
            'vector': 0.20,
            'frequency': 0.20,
            'fuzzy': 0.10
        }
        
        ensemble_score = (
            jaccard_score * weights['jaccard'] +
            tfidf_score * weights['tfidf'] +
            vector_score * weights['vector'] +
            freq_score * weights['frequency'] +
            fuzzy_score * weights['fuzzy']
        )
        
        # Calculate matching details
        user_set = set(user_skills)
        role_set = set(role_skills)
        matching = list(user_set & role_set)
        missing = list(role_set - user_set)
        extra = list(user_set - role_set)
        
        return {
            'match_percentage': round(ensemble_score, 2),
            'algorithms': {
                'jaccard_score': round(jaccard_score, 2),
                'tfidf_score': round(tfidf_score, 2),
                'vector_score': round(vector_score, 2),
                'frequency_score': round(freq_score, 2),
                'fuzzy_score': round(fuzzy_score, 2)
            },
            'matching_skills': matching,
            'missing_skills': missing,
            'extra_skills': extra,
            'matching_count': len(matching),
            'missing_count': len(missing),
            'total_required': len(role_skills),
            'match_ratio': round(len(matching) / len(role_skills) * 100, 2) if role_skills else 0
        }
    
    def _calculate_jaccard_similarity(self, user_skills: List[str], role_skills: List[str]) -> float:
        """Jaccard Index: |intersection| / |union|"""
        try:
            user_set = set(user_skills)
            role_set = set(role_skills)
            
            if not role_set:
                return 0.0
            
            intersection = len(user_set & role_set)
            union = len(user_set | role_set)
            
            return (intersection / union * 100) if union > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_tfidf_similarity(self, user_skills: List[str], role_skills: List[str]) -> float:
        """TF-IDF based cosine similarity"""
        try:
            user_doc = ' '.join(user_skills)
            role_doc = ' '.join(role_skills)
            
            if not user_doc or not role_doc:
                return 0.0
            
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([user_doc, role_doc])
            
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100
        except:
            return 0.0
    
    def _calculate_vector_similarity(self, user_skills: List[str], role_skills: List[str]) -> float:
        """Binary vector cosine similarity"""
        try:
            all_skills = list(set(user_skills + role_skills))
            
            if not all_skills:
                return 0.0
            
            # Create binary vectors
            user_vector = np.array([1 if skill in user_skills else 0 for skill in all_skills])
            role_vector = np.array([1 if skill in role_skills else 0 for skill in all_skills])
            
            # Cosine similarity
            dot_product = np.dot(user_vector, role_vector)
            norm_user = np.linalg.norm(user_vector)
            norm_role = np.linalg.norm(role_vector)
            
            if norm_user == 0 or norm_role == 0:
                return 0.0
            
            similarity = dot_product / (norm_user * norm_role)
            return similarity * 100
        except:
            return 0.0
    
    def _calculate_frequency_weighted_match(self, user_skills: List[str], role_skills: List[str]) -> float:
        """Weighted matching based on skill importance"""
        try:
            # Skills appearing multiple times are weighted higher
            from collections import Counter
            
            role_freq = Counter(role_skills)
            user_set = set(user_skills)
            
            total_weight = sum(role_freq.values())
            matched_weight = sum(freq for skill, freq in role_freq.items() if skill in user_set)
            
            return (matched_weight / total_weight * 100) if total_weight > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_fuzzy_match(self, user_skills: List[str], role_skills: List[str]) -> float:
        """Fuzzy matching for similar skill names (e.g., nodejs vs node.js)"""
        try:
            from difflib import SequenceMatcher
            
            matches = 0
            for role_skill in role_skills:
                best_ratio = 0
                for user_skill in user_skills:
                    ratio = SequenceMatcher(None, user_skill, role_skill).ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                
                if best_ratio > 0.7:  # 70% similarity threshold
                    matches += best_ratio
            
            return (matches / len(role_skills) * 100) if role_skills else 0.0
        except:
            return 0.0
    
    def rank_roles(self, user_skills: List[str], roles_with_skills: Dict[str, List[str]], top_n: int = 10) -> List[Dict]:
        """
        Rank roles based on skill match
        Returns top N matching roles with detailed analysis
        """
        try:
            rankings = []
            
            for role_name, role_skills in roles_with_skills.items():
                match_data = self.calculate_match_score(user_skills, role_skills)
                
                rankings.append({
                    'role': role_name,
                    'match_percentage': match_data['match_percentage'],
                    'match_ratio': match_data['match_ratio'],
                    'matching_skills': match_data['matching_skills'],
                    'missing_skills': match_data['missing_skills'],
                    'extra_skills': match_data['extra_skills'],
                    'algorithms': match_data['algorithms'],
                    'skill_details': {
                        'matched': len(match_data['matching_skills']),
                        'missing': len(match_data['missing_skills']),
                        'total_required': match_data['total_required']
                    }
                })
            
            # Sort by match percentage
            rankings.sort(key=lambda x: x['match_percentage'], reverse=True)
            
            return rankings[:top_n]
        except Exception as e:
            print(f"Error ranking roles: {e}")
            return []
    
    def get_learning_recommendations(self, user_skills: List[str], target_role_skills: List[str]) -> List[Dict]:
        """
        Generate personalized learning recommendations
        Prioritize skills by:
        1. Frequency in the target role
        2. Frequency across all roles
        3. Skill complexity (estimated)
        """
        try:
            from collections import Counter
            
            user_set = set(s.lower() for s in user_skills)
            target_set = set(s.lower() for s in target_role_skills)
            
            # Missing skills
            missing = list(target_set - user_set)
            
            if not missing:
                return []
            
            # Score each missing skill
            recommendations = []
            skill_freq = Counter(target_role_skills)
            
            for i, skill in enumerate(missing):
                # Priority 1: Very important (mentioned multiple times)
                importance_score = skill_freq[skill] / len(target_role_skills) * 100
                
                # Priority 2: Complexity estimation
                complexity = self._estimate_skill_complexity(skill)
                
                # Overall priority
                priority_score = importance_score * 0.7 + complexity * 0.3
                
                recommendations.append({
                    'rank': i + 1,
                    'skill': skill,
                    'importance': importance_score,
                    'complexity': complexity,
                    'priority': priority_score,
                    'estimated_hours': 20 + (complexity * 10),
                    'priority_level': 'Critical' if importance_score > 30 else 'High' if importance_score > 15 else 'Medium'
                })
            
            # Sort by priority
            recommendations.sort(key=lambda x: x['priority'], reverse=True)
            
            return recommendations[:15]  # Top 15 recommendations
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    def _estimate_skill_complexity(self, skill: str) -> float:
        """Estimate complexity of a skill (0-100)"""
        skill_lower = skill.lower()
        
        # Advanced skills
        advanced = ['machine learning', 'deep learning', 'ai', 'nlp', 'computer vision',
                   'blockchain', 'quantum', 'kubernetes', 'terraform']
        if any(adv in skill_lower for adv in advanced):
            return 80.0
        
        # Intermediate skills
        intermediate = ['docker', 'aws', 'azure', 'gcp', 'react', 'angular', 'django', 'spring']
        if any(inter in skill_lower for inter in intermediate):
            return 60.0
        
        # Basic skills
        basic = ['python', 'java', 'javascript', 'sql', 'git', 'html', 'css']
        if any(bas in skill_lower for bas in basic):
            return 40.0
        
        # Default: medium complexity
        return 50.0

# Global matcher instance
matcher = AdvancedSkillMatcher()

def calculate_skill_match(user_skills: List[str], role_skills: List[str]) -> Dict:
    """Wrapper function for skill matching"""
    return matcher.calculate_match_score(user_skills, role_skills)

def rank_matching_roles(user_skills: List[str], roles_dict: Dict[str, List[str]]) -> List[Dict]:
    """Wrapper for ranking roles"""
    return matcher.rank_roles(user_skills, roles_dict)

def get_skill_recommendations(user_skills: List[str], target_role_skills: List[str]) -> List[Dict]:
    """Wrapper for learning recommendations"""
    return matcher.get_learning_recommendations(user_skills, target_role_skills)
