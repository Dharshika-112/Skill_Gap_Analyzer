#!/usr/bin/env python3
"""
Debug Parser Step by Step
"""

import sys
sys.path.append('backend')

from backend.app.services.resume_parser import (
    _extract_skills_section, 
    _tokenize_candidates, 
    extract_skills_from_text,
    clean_mixed_content,
    is_certification_content
)

def debug_parser():
    resume_text = """
    John Doe
    Software Developer
    
    TECHNICAL SKILLS
    • Programming: Python, C, DSA, Java
    • Web: HTML, CSS, JavaScript, ReactJS
    • Database: SQL, DBMS
    • AI & Data Science: Machine Learning, Deep Learning, AI Deployment
    • Tools & Platform: Git, GitHub, Docker
    
    CERTIFICATIONS & COURSES
    • CISCO - Python Essentials
    • Google - Foundations of Data Science
    
    EXPERIENCE
    Software Developer Intern at TechCorp
    """
    
    print("🔍 DEBUGGING PARSER STEP BY STEP")
    print("=" * 60)
    
    print("📄 ORIGINAL TEXT:")
    print(resume_text)
    
    print(f"\n1️⃣ SKILLS SECTION EXTRACTION:")
    skills_section = _extract_skills_section(resume_text)
    print("Extracted section:")
    print(repr(skills_section))
    print("Readable:")
    print(skills_section)
    
    print(f"\n2️⃣ TOKENIZATION:")
    candidates = _tokenize_candidates(resume_text)
    print(f"Found {len(candidates)} candidates:")
    for i, candidate in enumerate(candidates, 1):
        print(f"  {i}. '{candidate}'")
    
    print(f"\n3️⃣ CERTIFICATION FILTERING:")
    filtered_candidates = []
    for candidate in candidates:
        is_cert = is_certification_content(candidate)
        print(f"  '{candidate}' -> Certification: {is_cert}")
        if not is_cert:
            filtered_candidates.append(candidate)
    
    print(f"\nFiltered candidates ({len(filtered_candidates)}):")
    for candidate in filtered_candidates:
        print(f"  • {candidate}")
    
    print(f"\n4️⃣ FINAL EXTRACTION:")
    final_skills = extract_skills_from_text(resume_text)
    print(f"Final skills ({len(final_skills)}):")
    for skill in final_skills:
        print(f"  • {skill}")
    
    print(f"\n5️⃣ TESTING INDIVIDUAL SKILLS:")
    expected_skills = ['Python', 'C', 'Java', 'HTML', 'CSS', 'JavaScript', 'ReactJS', 'SQL', 'DBMS', 'Machine Learning', 'Deep Learning', 'Git', 'GitHub', 'Docker']
    for skill in expected_skills:
        # Test if skill would be found in candidates
        found_in_candidates = any(skill.lower() in candidate.lower() for candidate in candidates)
        found_in_final = any(skill.lower() in final_skill.lower() for final_skill in final_skills)
        print(f"  {skill}: Candidates={found_in_candidates}, Final={found_in_final}")
def test_clean_mixed_content():
    print(f"\n6️⃣ TESTING CLEAN MIXED CONTENT:")
    test_cases = [
        "Python, C, DSA, Java                    CISCO  Python Essentials",
        "HTML, CSS, JavaScript, ReactJS              Google  Foundations of Data Science",
        "Machine Learning, Deep Learning, AI        IBM  Machine Learning with Python",
        "Git, GitHub, Docker               Infosys – Programming Fundamentals Using Java"
    ]
    for test_case in test_cases:
        cleaned = clean_mixed_content(test_case)
        print(f"Original: {test_case}")
        print(f"Cleaned:  {cleaned}")
        print()
if __name__ == "__main__":
    debug_parser()
    test_clean_mixed_content()