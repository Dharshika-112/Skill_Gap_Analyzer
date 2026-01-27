"""Role matching utilities: compute common vs role-specific importance and enhanced scoring"""
from typing import List, Tuple, Dict
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .extended_dataset import get_extended_roles, get_role_requirements, get_extended_skills
from .skill_cleaner import clean_skill_list
from .experience_weighting import get_experience_weight
import numpy as np

def compute_common_skill_scores(roles: List[str]) -> Dict[str, float]:
    """Return a score for each skill indicating how common it is across roles (0-1)."""
    all_reqs = []
    for r in roles:
        reqs = [s.lower() for s in get_role_requirements(r)]
        all_reqs.append(reqs)

    cnt = Counter()
    for reqs in all_reqs:
        cnt.update(set(reqs))

    total = len(roles) if roles else 1
    scores = {skill: cnt[skill] / total for skill in cnt}
    return scores

def role_specific_booster(role_name: str, skill: str) -> float:
    """Return a booster for skills that are specific/important for the role (0-2)."""
    reqs = [s.lower() for s in get_role_requirements(role_name)]
    if skill.lower() in reqs:
        # if skill present in role reqs, give mild boost
        return 1.2
    return 1.0

def enhanced_match_score(user_skills: List[str], role_skills: List[str], experience: Dict = None) -> Dict:
    """Calculate enhanced match including common vs role-specific weighting and TF-IDF cosine."""
    us = clean_skill_list(user_skills)
    rs = clean_skill_list(role_skills)

    us_lower = [s.lower() for s in us]
    rs_lower = [s.lower() for s in rs]

    # Jaccard
    inter = len(set(us_lower) & set(rs_lower))
    union = len(set(us_lower) | set(rs_lower)) or 1
    jaccard = inter / union

    # TF-IDF cosine on skill names joined
    docs = [' '.join(us_lower), ' '.join(rs_lower)]
    try:
        vec = TfidfVectorizer().fit_transform(docs)
        cos = float(cosine_similarity(vec[0:1], vec[1:2])[0][0])
    except Exception:
        cos = 0.0

    # common vs specific
    roles = get_extended_roles()
    common_scores = compute_common_skill_scores(roles)
    common_bonus = 0.0
    specific_bonus = 0.0
    for s in rs_lower:
        if s in common_scores and common_scores[s] > 0.5:
            common_bonus += 0.1
        # role-specific booster
        specific_bonus += (role_specific_booster(' '.join(roles[:1]), s) - 1.0)

    # experience weight
    exp_w = get_experience_weight(experience or {})

    # final score aggregate
    score = (jaccard * 0.5 + cos * 0.5) * exp_w
    score = max(0.0, min(1.0, score + common_bonus + specific_bonus * 0.02))

    return {
        'jaccard': round(jaccard, 3),
        'cosine': round(cos, 3),
        'experience_weight': round(exp_w, 3),
        'score': round(score * 100, 2)
    }
