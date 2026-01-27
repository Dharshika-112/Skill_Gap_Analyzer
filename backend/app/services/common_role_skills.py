"""
Common vs Role-Specific Skills Analyzer
Uses TF-IDF style analysis to identify common company skills vs role-specific boosters
"""

from typing import List, Dict, Tuple
from collections import Counter
from .extended_dataset import get_extended_roles, get_role_requirements
from ..core.database import get_collection

def compute_common_and_role_specific_skills(role_name: str, all_roles: List[str] = None) -> Dict:
    """
    Compute common skills (appearing in many roles) vs role-specific skills (unique to this role)
    Returns: {
        'common_skills': [...],  # Skills appearing in >30% of roles
        'role_specific_skills': [...],  # Skills unique or rare to this role
        'common_threshold': 0.3
    }
    """
    if all_roles is None:
        all_roles = get_extended_roles()
    
    # Get skills for all roles
    all_role_skills = {}
    for role in all_roles:
        try:
            skills = get_role_requirements(role)
            all_role_skills[role] = [s.lower() for s in skills]
        except:
            continue
    
    # Count skill frequency across all roles
    skill_frequency = Counter()
    for role, skills in all_role_skills.items():
        skill_frequency.update(set(skills))
    
    total_roles = len(all_role_skills) if all_role_skills else 1
    common_threshold = 0.3  # Skills appearing in >30% of roles are "common"
    
    # Get skills for the target role
    target_role_skills = [s.lower() for s in get_role_requirements(role_name)]
    target_role_skills_set = set(target_role_skills)
    
    common_skills = []
    role_specific_skills = []
    
    for skill in target_role_skills:
        frequency = skill_frequency.get(skill, 0) / total_roles
        
        if frequency >= common_threshold:
            common_skills.append(skill)
        else:
            role_specific_skills.append(skill)
    
    return {
        'common_skills': sorted(common_skills),
        'role_specific_skills': sorted(role_specific_skills),
        'common_threshold': common_threshold,
        'total_roles_analyzed': total_roles
    }

def get_essential_vs_overall_skills(role_skills: List[str], user_skills: List[str]) -> Dict:
    """
    Separate essential skills (must-have) vs overall skills (nice-to-have)
    Essential = skills that appear in >50% of similar roles
    """
    all_roles = get_extended_roles()
    
    # Find similar roles (roles with overlapping skills)
    similar_roles = []
    user_skills_set = set(s.lower() for s in user_skills)
    role_skills_set = set(s.lower() for s in role_skills)
    
    for role in all_roles:
        try:
            role_reqs = set(s.lower() for s in get_role_requirements(role))
            overlap = len(role_reqs & role_skills_set)
            if overlap > len(role_skills_set) * 0.3:  # >30% overlap
                similar_roles.append(role)
        except:
            continue
    
    # Count skill frequency in similar roles
    skill_freq = Counter()
    for role in similar_roles:
        try:
            skills = [s.lower() for s in get_role_requirements(role)]
            skill_freq.update(set(skills))
        except:
            continue
    
    total_similar = len(similar_roles) if similar_roles else 1
    essential_threshold = 0.5  # Skills in >50% of similar roles are essential
    
    essential_skills = []
    overall_skills = []
    
    for skill in role_skills:
        skill_lower = skill.lower()
        frequency = skill_freq.get(skill_lower, 0) / total_similar
        
        if frequency >= essential_threshold:
            essential_skills.append(skill)
        else:
            overall_skills.append(skill)
    
    # Also check which user skills match essential vs overall
    user_essential = [s for s in user_skills if s.lower() in [es.lower() for es in essential_skills]]
    user_overall = [s for s in user_skills if s.lower() in [os.lower() for os in overall_skills]]
    
    return {
        'essential_skills': essential_skills,
        'overall_skills': overall_skills,
        'user_essential_match': user_essential,
        'user_overall_match': user_overall,
        'essential_match_count': len(user_essential),
        'overall_match_count': len(user_overall),
        'total_essential': len(essential_skills),
        'total_overall': len(overall_skills)
    }
