#!/usr/bin/env python3
"""
Debug Dataset Skills
"""

import sys
sys.path.append('backend')

from backend.app.services.dataset_loader import get_all_skills_from_dataset

def debug_dataset_skills():
    print("🔍 DEBUGGING DATASET SKILLS")
    print("=" * 60)
    
    skills = get_all_skills_from_dataset()
    print(f"Total skills in dataset: {len(skills)}")
    
    # Show first 50 skills
    print(f"\nFirst 50 skills:")
    for i, skill in enumerate(skills[:50], 1):
        print(f"  {i}. '{skill}'")
    
    # Look for common programming skills
    print(f"\nLooking for common programming skills:")
    common_skills = ['Python', 'Java', 'JavaScript', 'HTML', 'CSS', 'React', 'SQL', 'Git', 'Docker']
    
    for skill in common_skills:
        matches = [s for s in skills if skill.lower() in s.lower()]
        print(f"  {skill}: {len(matches)} matches")
        if matches:
            print(f"    Examples: {matches[:3]}")
    
    # Check for exact matches from our test resume
    test_skills = ['Python', 'C', 'DSA', 'Java', 'HTML', 'CSS', 'JavaScript', 'ReactJS', 'SQL', 'DBMS', 'Machine Learning', 'Deep Learning', 'Git', 'GitHub', 'Docker']
    
    print(f"\nChecking test resume skills:")
    for skill in test_skills:
        exact_match = skill in skills
        partial_matches = [s for s in skills if skill.lower() in s.lower() or s.lower() in skill.lower()]
        print(f"  {skill}: Exact={exact_match}, Partial={len(partial_matches)}")
        if partial_matches and not exact_match:
            print(f"    Partial matches: {partial_matches[:3]}")

if __name__ == "__main__":
    debug_dataset_skills()