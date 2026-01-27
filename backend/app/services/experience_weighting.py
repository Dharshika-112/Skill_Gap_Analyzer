"""Experience detection and weighting helpers"""
from typing import Dict

WEIGHT_MAP = {
    'internship': 0.6,
    'training': 0.7,
    'fresher': 0.75,
    'experienced': 1.0,
    'unknown': 0.8
}

def get_experience_weight(experience: Dict) -> float:
    """Return a multiplier based on experience type and years."""
    if not experience:
        return WEIGHT_MAP['unknown']
    t = experience.get('type', 'unknown') or 'unknown'
    years = experience.get('years')
    base = WEIGHT_MAP.get(t, WEIGHT_MAP['unknown'])
    if years is None:
        return base
    # Slight boost for more years
    if years >= 5:
        return min(1.2, base + 0.2)
    if years >= 2:
        return min(1.05, base + 0.05)
    return base
