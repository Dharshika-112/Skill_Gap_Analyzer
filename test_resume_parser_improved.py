#!/usr/bin/env python3
"""
Test and Improve Resume Parser for Your Format
"""

import sys
sys.path.append('backend')

from backend.app.services.resume_parser import extract_skills_from_text, _extract_skills_section

def test_your_resume_format():
    # Your exact resume format
    resume_text = """
    TECHNICAL SKILLS                           CERTIFICATIONS & COURSES
    •    Programming: Python, C, DSA, Java                •    CISCO - Python Essentials
    •    Web: HTML, CSS, JavaScript, ReactJS              •    Google - Foundations of Data Science
    •    Database: SQL, DBMS                              •    CU Boulder - Foundations of DSA (Specialization)
    •    AI & Data Science: Machine Learning, Deep Learning, AI    •    IBM - Machine Learning with Python
         Deployment                                       •    Juniper - NCIA-Cloud / Mist AI Associate
    •    Tools & Platform: Git, GitHub, Docker           •    Infosys – Programming Fundamentals Using Java
    
    COMPETITIVE PROGRAMMING
    """
    
    print("🧪 TESTING IMPROVED RESUME PARSING")
    print("=" * 60)
    
    # Test current extraction
    print("1️⃣ CURRENT EXTRACTION:")
    current_skills = extract_skills_from_text(resume_text)
    print(f"Current skills found: {len(current_skills)}")
    for skill in current_skills:
        print(f"  • {skill}")
    
    # Test improved extraction
    print(f"\n2️⃣ IMPROVED EXTRACTION:")
    improved_skills = extract_skills_improved(resume_text)
    print(f"Improved skills found: {len(improved_skills)}")
    for skill in improved_skills:
        print(f"  • {skill}")
    
    return improved_skills

def extract_skills_improved(text: str) -> list:
    """Improved skill extraction specifically for your resume format"""
    
    # Get dataset skills for matching
    from backend.app.services.dataset_loader import get_all_skills_from_dataset
    dataset_skills = get_all_skills_from_dataset()
    
    if not dataset_skills:
        from backend.app.services.extended_dataset import get_dataset_skills
        dataset_skills = get_dataset_skills()
    
    dataset_lower = [s.lower().strip() for s in dataset_skills if s and len(s.strip()) > 1]
    
    # Extract technical skills section only
    skills_section = extract_technical_skills_section(text)
    print(f"Skills section extracted:\n{skills_section}")
    
    # Parse skills from the section
    extracted_skills = parse_skills_from_section(skills_section)
    print(f"Raw extracted skills: {extracted_skills}")
    
    # Match against dataset
    matched_skills = []
    for skill in extracted_skills:
        skill_lower = skill.lower().strip()
        
        # Direct match
        if skill_lower in dataset_lower:
            matched_skills.append(skill)
            continue
        
        # Fuzzy match
        for dataset_skill in dataset_lower:
            if len(dataset_skill) >= 3 and len(skill_lower) >= 3:
                if (dataset_skill in skill_lower or skill_lower in dataset_skill or
                    are_similar_skills(skill_lower, dataset_skill)):
                    matched_skills.append(skill)
                    break
    
    return list(set(matched_skills))

def extract_technical_skills_section(text: str) -> str:
    """Extract only the technical skills section, excluding certifications"""
    
    lines = text.split('\n')
    skills_lines = []
    in_skills = False
    
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        # Start of technical skills section
        if 'technical skills' in line_lower:
            in_skills = True
            continue
        
        # Stop at certifications or other sections
        if in_skills and any(stop in line_lower for stop in ['certifications', 'competitive', 'experience', 'education', 'projects']):
            break
        
        # Collect skill lines
        if in_skills and line_clean:
            # Skip empty lines and section headers
            if not any(skip in line_lower for skip in ['certifications', 'courses']):
                skills_lines.append(line_clean)
    
    return '\n'.join(skills_lines)

def parse_skills_from_section(skills_text: str) -> list:
    """Parse individual skills from the skills section"""
    
    skills = []
    lines = skills_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove bullet points
        line = line.replace('•', '').replace('-', '').strip()
        
        # Handle category format: "Programming: Python, C, DSA, Java"
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                category = parts[0].strip()
                skills_part = parts[1].strip()
                
                # Add category as a skill if it's relevant
                if category.lower() in ['programming', 'web', 'database', 'ai', 'data science', 'tools', 'platform']:
                    skills.append(category)
                
                # Parse individual skills
                individual_skills = parse_skill_list(skills_part)
                skills.extend(individual_skills)
        else:
            # Direct skill line
            individual_skills = parse_skill_list(line)
            skills.extend(individual_skills)
    
    return skills

def parse_skill_list(text: str) -> list:
    """Parse a comma/semicolon separated list of skills"""
    
    # Split by common separators
    separators = [',', ';', '&', ' and ', '|']
    skills = [text]
    
    for sep in separators:
        new_skills = []
        for skill in skills:
            new_skills.extend([s.strip() for s in skill.split(sep) if s.strip()])
        skills = new_skills
    
    # Clean up skills
    cleaned_skills = []
    for skill in skills:
        skill = skill.strip()
        if len(skill) > 1 and not skill.lower() in ['deployment', 'platform']:
            cleaned_skills.append(skill)
    
    return cleaned_skills

def are_similar_skills(skill1: str, skill2: str) -> bool:
    """Check if two skills are similar"""
    
    variations = {
        'js': 'javascript', 'javascript': 'js',
        'reactjs': 'react', 'react': 'reactjs',
        'nodejs': 'node', 'node': 'nodejs',
        'ml': 'machine learning', 'machine learning': 'ml',
        'ai': 'artificial intelligence',
        'dsa': 'data structures and algorithms',
        'dbms': 'database management system'
    }
    
    return (skill1 in variations and variations[skill1] == skill2) or \
           (skill2 in variations and variations[skill2] == skill1)

if __name__ == "__main__":
    skills = test_your_resume_format()
    
    print(f"\n🎯 EXPECTED SKILLS FROM YOUR RESUME:")
    expected = ['Python', 'C', 'Java', 'HTML', 'CSS', 'JavaScript', 'React', 'ReactJS', 'SQL', 'DBMS', 'Machine Learning', 'Deep Learning', 'AI', 'Git', 'GitHub', 'Docker']
    
    print(f"Expected: {len(expected)} skills")
    print(f"Found: {len(skills)} skills")
    
    found_expected = [skill for skill in expected if any(skill.lower() in found.lower() or found.lower() in skill.lower() for found in skills)]
    missing = [skill for skill in expected if not any(skill.lower() in found.lower() or found.lower() in skill.lower() for found in skills)]
    
    print(f"\n✅ FOUND ({len(found_expected)}):")
    for skill in found_expected:
        print(f"  • {skill}")
    
    if missing:
        print(f"\n❌ MISSING ({len(missing)}):")
        for skill in missing:
            print(f"  • {skill}")
    
    success_rate = len(found_expected) / len(expected) * 100
    print(f"\n📊 SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 PARSER WORKING WELL!")
    else:
        print("⚠️ PARSER NEEDS IMPROVEMENT")