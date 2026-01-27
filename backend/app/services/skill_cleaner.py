"""Utilities to clean and normalize skill names"""
import re
from typing import List

# Simple canonicalization map
CANONICAL_MAP = {
    'js': 'JavaScript',
    'javascript': 'JavaScript',
    'py': 'Python',
    'csharp': 'C#',
    'dotnet': '.NET',
    'sql': 'SQL',
    'tf': 'TensorFlow',
    'pytorch': 'PyTorch'
}

def normalize_skill(skill: str) -> str:
    s = skill.strip()
    s = re.sub(r"[\s\-_]+", ' ', s)
    key = s.lower()
    if key in CANONICAL_MAP:
        return CANONICAL_MAP[key]
    # title case common multiword skills
    if len(s) <= 4:
        return s.upper() if s.isupper() else s.capitalize()
    return ' '.join([w.capitalize() for w in s.split()])

def clean_skill_list(skills: List[str]) -> List[str]:
    seen = set()
    out = []
    for s in skills:
        if not s:
            continue
        n = normalize_skill(s)
        key = n.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(n)
    return out
