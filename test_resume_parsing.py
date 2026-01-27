#!/usr/bin/env python3
"""
Test Resume Parsing with Your Specific Format
"""

import sys
sys.path.append('backend')

from backend.app.services.resume_parser import extract_skills_from_text, _extract_skills_section, _tokenize_candidates

def test_your_resume_format():
    # Your exact resume format
    resume_text = """
    Python, OpenCV, TensorFlow/PyTorch
    • Built a real-time AI model for crowd detection and density estimation from video feeds.
    • Tracked movement patterns and generated congestion-level insights.
    • Designed dashboards to support public safety and event management decisions.
    
    TECHNICAL SKILLS                           CERTIFICATIONS & COURSES
    •    Programming: Python, C, DSA, Java                •    CISCO - Python Essentials
    •    Web: HTML, CSS, JavaScript, ReactJS              •    Google - Foundations of Data Science
    •    Database: SQL, DBMS                              •    CU Boulder - Foundations of DSA (Specialization)
    •    AI & Data Science: Machine Learning, Deep Learning, AI    •    IBM - Machine Learning with Python
         Deployment                                       •    Juniper - NCIA-Cloud / Mist AI Associate
    •    Tools & Platform: Git, GitHub, Docker           •    Infosys – Programming Fundamentals Using Java
    
    COMPETITIVE PROGRAMMING
    """
    
    print("🧪 TESTING RESUME PARSING WITH YOUR FORMAT")
    print("=" * 60)
    
    # Test 1: Extract skills section
    print("\n1️⃣ TESTING SKILLS SECTION EXTRACTION")
    skills_section = _extract_skills_section(resume_text)
    print("Extracted Skills Section:")
    print(skills_section)
    print(f"Length: {len(skills_section)} characters")
    
    # Test 2: Tokenize candidates
    print("\n2️⃣ TESTING SKILL TOKENIZATION")
    candidates = _tokenize_candidates(resume_text)
    print("Tokenized Candidates:")
    for i, candidate in enumerate(candidates, 1):
        print(f"  {i}. '{candidate}'")
    
    # Test 3: Full skill extraction
    print("\n3️⃣ TESTING FULL SKILL EXTRACTION")
    extracted_skills = extract_skills_from_text(resume_text)
    print("Final Extracted Skills:")
    for i, skill in enumerate(extracted_skills, 1):
        print(f"  {i}. {skill}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total candidates found: {len(candidates)}")
    print(f"   Skills matched to dataset: {len(extracted_skills)}")
    
    # Expected skills from your resume
    expected_skills = [
        'Python', 'C', 'Java', 'HTML', 'CSS', 'JavaScript', 'React', 'ReactJS',
        'SQL', 'Machine Learning', 'Deep Learning', 'Git', 'GitHub', 'Docker',
        'TensorFlow', 'PyTorch', 'OpenCV'
    ]
    
    print(f"\n🎯 EXPECTED VS ACTUAL:")
    print(f"   Expected skills: {len(expected_skills)}")
    print(f"   Found skills: {len(extracted_skills)}")
    
    found_expected = []
    missing_expected = []
    
    for expected in expected_skills:
        found = False
        for extracted in extracted_skills:
            if expected.lower() in extracted.lower() or extracted.lower() in expected.lower():
                found = True
                found_expected.append(expected)
                break
        if not found:
            missing_expected.append(expected)
    
    print(f"\n✅ FOUND EXPECTED SKILLS ({len(found_expected)}):")
    for skill in found_expected:
        print(f"   • {skill}")
    
    if missing_expected:
        print(f"\n❌ MISSING EXPECTED SKILLS ({len(missing_expected)}):")
        for skill in missing_expected:
            print(f"   • {skill}")
    
    return len(extracted_skills) > 0

if __name__ == "__main__":
    success = test_your_resume_format()
    if success:
        print(f"\n🎉 SUCCESS: Skills were extracted from your resume format!")
    else:
        print(f"\n❌ FAILED: No skills were extracted. Need to improve parser.")