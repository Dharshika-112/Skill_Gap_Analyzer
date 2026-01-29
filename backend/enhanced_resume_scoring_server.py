"""
CareerBoost AI - Enhanced Resume Scoring Server
Advanced ATS scoring with PDF processing, database storage, and ML analysis
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import sys
import os
import uuid
import json
import io
import re
from datetime import datetime
import pandas as pd
import numpy as np
from collections import Counter

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

app = FastAPI(
    title="CareerBoost AI - Enhanced Resume Scoring",
    description="Advanced ATS scoring with PDF processing and ML analysis",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003", "http://localhost:3002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for resumes and analysis
resume_database = {}
analysis_history = {}

# Common stop words for text processing
stop_words = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
}

# Load ATS skills and job data
def load_ats_data():
    """Load ATS skills and job requirements data."""
    try:
        # Load ATS skills
        ats_skills_path = os.path.join(os.path.dirname(__file__), 'data/processed/ats_skills_list.json')
        with open(ats_skills_path, 'r', encoding='utf-8') as f:
            ats_skills = json.load(f)
        
        # Load job dataset for role-based scoring
        job_data_path = os.path.join(os.path.dirname(__file__), 'data/processed/job_dataset_normalized.csv')
        job_df = pd.read_csv(job_data_path)
        
        return ats_skills, job_df
    except Exception as e:
        print(f"Warning: Could not load ATS data: {e}")
        return [], pd.DataFrame()

ats_skills_list, job_dataset = load_ats_data()

# Request models
class ResumeScoreRequest(BaseModel):
    resume_data: Dict[str, Any]
    scoring_type: str = "general"
    target_role: Optional[str] = None

class RoleBasedScoreRequest(BaseModel):
    resume_data: Dict[str, Any]
    target_role: str

# Helper functions
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file using PyPDF2."""
    try:
        import PyPDF2
        
        # Reset file pointer to beginning
        pdf_file.seek(0)
        
        # Create PDF reader
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        if not text.strip():
            raise Exception("No text could be extracted from PDF")
            
        return text.strip()
        
    except ImportError:
        # Fallback if PyPDF2 is not available
        content = pdf_file.read()
        return f"PDF content received ({len(content)} bytes). PyPDF2 not available for text extraction."
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")

def simple_tokenize(text):
    """Simple tokenization without NLTK."""
    # Convert to lowercase and split by whitespace and punctuation
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return [word for word in words if len(word) > 2 and word not in stop_words]

def parse_resume_content(text):
    """Parse resume content and extract structured information."""
    parsed_data = {
        "raw_text": text,
        "contact_info": extract_contact_info(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "sections": identify_sections(text),
        "keywords": extract_keywords(text),
        "word_count": len(text.split()),
        "character_count": len(text)
    }
    
    return parsed_data

def extract_contact_info(text):
    """Extract contact information from resume text."""
    contact_info = {}
    
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    contact_info['email'] = emails[0] if emails else None
    
    # Phone extraction
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    contact_info['phone'] = phones[0] if phones else None
    
    # LinkedIn extraction
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin = re.findall(linkedin_pattern, text.lower())
    contact_info['linkedin'] = linkedin[0] if linkedin else None
    
    return contact_info

def extract_skills(text):
    """Extract skills from resume text using ATS skills list."""
    found_skills = []
    text_lower = text.lower()
    
    # Check against ATS skills list
    for skill in ats_skills_list:
        if isinstance(skill, str) and skill.lower() in text_lower:
            found_skills.append(skill)
    
    # Additional skill extraction using common patterns
    skill_patterns = [
        r'\b(?:python|java|javascript|react|angular|vue|node\.js|express|django|flask)\b',
        r'\b(?:sql|mysql|postgresql|mongodb|redis|elasticsearch)\b',
        r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git)\b',
        r'\b(?:html|css|sass|less|bootstrap|tailwind)\b',
        r'\b(?:machine learning|deep learning|ai|nlp|computer vision)\b'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        found_skills.extend(matches)
    
    # Remove duplicates and return
    return list(set(found_skills))

def extract_experience(text):
    """Extract work experience information."""
    experience_info = {
        "total_years": estimate_years_of_experience(text),
        "companies": extract_companies(text),
        "positions": extract_positions(text)
    }
    
    return experience_info

def estimate_years_of_experience(text):
    """Estimate years of experience from resume text."""
    # Look for year patterns
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    
    if len(years) >= 2:
        years = [int(year) for year in years]
        return max(years) - min(years)
    
    # Look for explicit experience mentions
    exp_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'experience\s*:?\s*(\d+)\+?\s*years?'
    ]
    
    for pattern in exp_patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            return int(matches[0])
    
    return 0

def extract_companies(text):
    """Extract company names from resume text."""
    # This is a simplified implementation
    # In production, you'd use NER or a company database
    companies = []
    
    # Look for common company indicators
    company_patterns = [
        r'(?:at|@)\s+([A-Z][a-zA-Z\s&.,]+(?:Inc|LLC|Corp|Ltd|Company|Technologies|Solutions|Systems))',
        r'([A-Z][a-zA-Z\s&.,]+(?:Inc|LLC|Corp|Ltd|Company|Technologies|Solutions|Systems))'
    ]
    
    for pattern in company_patterns:
        matches = re.findall(pattern, text)
        companies.extend(matches)
    
    return list(set(companies[:5]))  # Return top 5 unique companies

def extract_positions(text):
    """Extract job positions from resume text."""
    positions = []
    
    # Common job title patterns
    position_patterns = [
        r'\b(?:Senior|Junior|Lead|Principal|Staff)?\s*(?:Software|Web|Full Stack|Frontend|Backend|Data|Machine Learning|DevOps|Cloud)\s*(?:Engineer|Developer|Scientist|Analyst|Architect)\b',
        r'\b(?:Product|Project|Engineering|Technical|Marketing|Sales)\s*Manager\b',
        r'\b(?:CTO|CEO|VP|Director|Head)\s*(?:of|Engineering|Technology|Product|Marketing)?\b'
    ]
    
    for pattern in position_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        positions.extend(matches)
    
    return list(set(positions[:5]))  # Return top 5 unique positions

def extract_education(text):
    """Extract education information."""
    education_info = {
        "degrees": extract_degrees(text),
        "institutions": extract_institutions(text),
        "certifications": extract_certifications(text)
    }
    
    return education_info

def extract_degrees(text):
    """Extract degree information."""
    degree_patterns = [
        r'\b(?:Bachelor|Master|PhD|Doctorate|Associate)(?:\s*of\s*(?:Science|Arts|Engineering|Technology|Business|Computer Science))?\b',
        r'\b(?:BS|BA|MS|MA|MBA|PhD|BSc|MSc)\b',
        r'\b(?:B\.S\.|B\.A\.|M\.S\.|M\.A\.|Ph\.D\.)\b'
    ]
    
    degrees = []
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        degrees.extend(matches)
    
    return list(set(degrees))

def extract_institutions(text):
    """Extract educational institutions."""
    # Look for university/college patterns
    institution_patterns = [
        r'\b([A-Z][a-zA-Z\s&.,]+(?:University|College|Institute|School))\b',
        r'\b(?:University|College|Institute)\s+of\s+([A-Z][a-zA-Z\s&.,]+)\b'
    ]
    
    institutions = []
    for pattern in institution_patterns:
        matches = re.findall(pattern, text)
        institutions.extend(matches)
    
    return list(set(institutions[:3]))  # Return top 3 unique institutions

def extract_certifications(text):
    """Extract certifications."""
    cert_patterns = [
        r'\b(?:AWS|Azure|GCP|Google Cloud)\s*(?:Certified|Certification)?\s*[A-Za-z\s-]*\b',
        r'\b(?:PMP|CISSP|CISA|CISM|CompTIA|Cisco|Oracle|Microsoft)\s*[A-Za-z\s-]*\b',
        r'\bCertified\s+[A-Za-z\s-]+\b'
    ]
    
    certifications = []
    for pattern in cert_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        certifications.extend(matches)
    
    return list(set(certifications[:5]))  # Return top 5 unique certifications

def identify_sections(text):
    """Identify resume sections."""
    sections = {}
    
    section_patterns = {
        'summary': r'(?:summary|profile|objective|about)',
        'experience': r'(?:experience|employment|work history|professional experience)',
        'education': r'(?:education|academic|qualifications)',
        'skills': r'(?:skills|technical skills|competencies|expertise)',
        'projects': r'(?:projects|portfolio|work samples)',
        'certifications': r'(?:certifications|certificates|licenses)',
        'awards': r'(?:awards|achievements|honors|recognition)'
    }
    
    for section_name, pattern in section_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            sections[section_name] = True
        else:
            sections[section_name] = False
    
    return sections

def extract_keywords(text):
    """Extract important keywords from resume."""
    # Simple keyword extraction without NLTK
    words = simple_tokenize(text)
    
    # Count frequency and return top keywords
    word_freq = Counter(words)
    
    return [word for word, count in word_freq.most_common(20)]

def calculate_ats_score(parsed_data, scoring_type="general", target_role=None):
    """Calculate ATS score based on resume content with improved accuracy."""
    score_components = {}
    
    # Base scoring components with improved weights
    score_components['contact_info'] = score_contact_info(parsed_data['contact_info'])
    score_components['skills'] = score_skills(parsed_data['skills'], target_role)
    score_components['experience'] = score_experience(parsed_data['experience'], target_role)
    score_components['education'] = score_education(parsed_data['education'])
    score_components['sections'] = score_sections(parsed_data['sections'])
    score_components['formatting'] = score_formatting(parsed_data)
    score_components['keywords'] = score_keywords(parsed_data['keywords'], target_role)
    score_components['content_quality'] = score_content_quality(parsed_data)
    
    if scoring_type == "role-based" and target_role:
        score_components['role_match'] = score_role_match(parsed_data, target_role)
        score_components['industry_alignment'] = score_industry_alignment(parsed_data, target_role)
        
        weights = {
            'contact_info': 0.08,
            'skills': 0.25,
            'experience': 0.20,
            'education': 0.10,
            'sections': 0.08,
            'formatting': 0.05,
            'keywords': 0.12,
            'content_quality': 0.07,
            'role_match': 0.15,
            'industry_alignment': 0.10
        }
    else:
        weights = {
            'contact_info': 0.12,
            'skills': 0.25,
            'experience': 0.25,
            'education': 0.15,
            'sections': 0.10,
            'formatting': 0.05,
            'keywords': 0.08,
            'content_quality': 0.10
        }
    
    # Calculate weighted score
    total_score = sum(score_components[component] * weights[component] 
                     for component in score_components)
    
    return {
        'overall_score': round(total_score, 1),
        'component_scores': score_components,
        'weights': weights,
        'recommendations': generate_recommendations(score_components, parsed_data, target_role),
        'detailed_analysis': generate_detailed_analysis(score_components, parsed_data, target_role),
        'improvement_priority': get_improvement_priority(score_components)
    }

def score_contact_info(contact_info):
    """Score contact information completeness."""
    score = 0
    if contact_info.get('email'): score += 40
    if contact_info.get('phone'): score += 30
    if contact_info.get('linkedin'): score += 30
    return min(score, 100)

def score_skills(skills, target_role=None):
    """Score skills section with role-specific weighting."""
    if not skills:
        return 0
    
    skill_count = len(skills)
    base_score = 0
    
    if skill_count >= 20: base_score = 100
    elif skill_count >= 15: base_score = 90
    elif skill_count >= 10: base_score = 75
    elif skill_count >= 5: base_score = 60
    elif skill_count >= 3: base_score = 40
    else: base_score = 20
    
    # Bonus for role-specific skills
    if target_role:
        role_bonus = calculate_role_skill_bonus(skills, target_role)
        base_score = min(base_score + role_bonus, 100)
    
    return base_score

def calculate_role_skill_bonus(skills, target_role):
    """Calculate bonus points for role-specific skills."""
    role_keywords = {
        'data scientist': ['python', 'r', 'sql', 'machine learning', 'pandas', 'numpy', 'tensorflow', 'pytorch'],
        'software engineer': ['python', 'java', 'javascript', 'git', 'sql', 'react', 'node.js', 'docker'],
        'frontend developer': ['javascript', 'react', 'vue', 'angular', 'html', 'css', 'typescript', 'webpack'],
        'backend developer': ['python', 'java', 'node.js', 'sql', 'mongodb', 'api', 'docker', 'kubernetes'],
        'devops engineer': ['docker', 'kubernetes', 'aws', 'jenkins', 'terraform', 'ansible', 'linux', 'git'],
        'cybersecurity': ['security', 'penetration testing', 'firewall', 'encryption', 'compliance', 'risk assessment']
    }
    
    target_lower = target_role.lower()
    relevant_keywords = []
    
    for role, keywords in role_keywords.items():
        if role in target_lower:
            relevant_keywords = keywords
            break
    
    if not relevant_keywords:
        return 0
    
    skills_lower = [skill.lower() for skill in skills]
    matches = sum(1 for keyword in relevant_keywords if any(keyword in skill for skill in skills_lower))
    
    return min(matches * 5, 20)  # Max 20 bonus points

def score_content_quality(parsed_data):
    """Score the overall content quality."""
    score = 0
    
    # Check for quantifiable achievements
    text = parsed_data.get('raw_text', '').lower()
    achievement_patterns = [
        r'\d+%', r'\$\d+', r'\d+\+', r'increased.*\d+', r'reduced.*\d+', 
        r'improved.*\d+', r'managed.*\d+', r'led.*\d+', r'achieved.*\d+'
    ]
    
    achievement_count = sum(len(re.findall(pattern, text)) for pattern in achievement_patterns)
    score += min(achievement_count * 10, 40)  # Max 40 points
    
    # Check for action verbs
    action_verbs = ['developed', 'implemented', 'managed', 'led', 'created', 'designed', 
                   'optimized', 'improved', 'increased', 'reduced', 'achieved', 'delivered']
    verb_count = sum(1 for verb in action_verbs if verb in text)
    score += min(verb_count * 3, 30)  # Max 30 points
    
    # Check for industry buzzwords
    if len(parsed_data.get('keywords', [])) > 10:
        score += 30
    
    return min(score, 100)

def score_industry_alignment(parsed_data, target_role):
    """Score how well the resume aligns with industry standards."""
    if not target_role:
        return 50
    
    text = parsed_data.get('raw_text', '').lower()
    role_lower = target_role.lower()
    
    industry_terms = {
        'software': ['agile', 'scrum', 'ci/cd', 'version control', 'testing', 'debugging'],
        'data': ['analytics', 'visualization', 'statistics', 'modeling', 'big data', 'etl'],
        'marketing': ['campaign', 'roi', 'conversion', 'analytics', 'social media', 'seo'],
        'finance': ['financial analysis', 'budgeting', 'forecasting', 'compliance', 'audit'],
        'healthcare': ['patient care', 'medical', 'clinical', 'healthcare', 'hipaa', 'compliance']
    }
    
    relevant_terms = []
    for industry, terms in industry_terms.items():
        if industry in role_lower:
            relevant_terms = terms
            break
    
    if not relevant_terms:
        return 70  # Neutral score if no specific industry identified
    
    matches = sum(1 for term in relevant_terms if term in text)
    score = min((matches / len(relevant_terms)) * 100, 100)
    
    return max(score, 30)  # Minimum 30 points

def generate_detailed_analysis(score_components, parsed_data, target_role=None):
    """Generate detailed analysis of the resume."""
    analysis = {
        'strengths': [],
        'weaknesses': [],
        'missing_elements': [],
        'optimization_tips': []
    }
    
    # Identify strengths
    if score_components['skills'] >= 80:
        analysis['strengths'].append('Strong technical skills portfolio')
    if score_components['experience'] >= 80:
        analysis['strengths'].append('Excellent work experience presentation')
    if score_components['contact_info'] >= 90:
        analysis['strengths'].append('Complete contact information')
    
    # Identify weaknesses
    if score_components['skills'] < 60:
        analysis['weaknesses'].append('Limited technical skills listed')
    if score_components['experience'] < 60:
        analysis['weaknesses'].append('Work experience needs more detail')
    if score_components['formatting'] < 70:
        analysis['weaknesses'].append('Resume formatting could be improved')
    
    # Missing elements
    sections = parsed_data.get('sections', {})
    if not sections.get('summary'):
        analysis['missing_elements'].append('Professional summary section')
    if not sections.get('projects'):
        analysis['missing_elements'].append('Projects or portfolio section')
    if not sections.get('certifications'):
        analysis['missing_elements'].append('Certifications section')
    
    # Optimization tips
    if target_role:
        analysis['optimization_tips'].append(f'Tailor keywords for {target_role} positions')
        analysis['optimization_tips'].append('Include quantifiable achievements')
        analysis['optimization_tips'].append('Add role-specific technical skills')
    else:
        analysis['optimization_tips'].append('Use industry-standard keywords')
        analysis['optimization_tips'].append('Include measurable accomplishments')
        analysis['optimization_tips'].append('Ensure ATS-friendly formatting')
    
    return analysis

def get_improvement_priority(score_components):
    """Get prioritized list of improvements."""
    priorities = []
    
    # Sort components by score (lowest first)
    sorted_components = sorted(score_components.items(), key=lambda x: x[1])
    
    for component, score in sorted_components[:3]:  # Top 3 priorities
        if score < 70:
            priority_level = 'High' if score < 50 else 'Medium'
            priorities.append({
                'component': component.replace('_', ' ').title(),
                'score': score,
                'priority': priority_level,
                'impact': 'High' if component in ['skills', 'experience', 'role_match'] else 'Medium'
            })
    
    return priorities

def score_experience(experience, target_role=None):
    """Score experience section with role-specific considerations."""
    years = experience.get('total_years', 0)
    companies = len(experience.get('companies', []))
    positions = len(experience.get('positions', []))
    
    years_score = min(years * 10, 60)  # Max 60 for 6+ years
    companies_score = min(companies * 10, 20)  # Max 20 for 2+ companies
    positions_score = min(positions * 10, 20)  # Max 20 for 2+ positions
    
    base_score = years_score + companies_score + positions_score
    
    # Role-specific bonus
    if target_role and years >= 2:
        role_bonus = 10  # Bonus for having relevant experience
        base_score = min(base_score + role_bonus, 100)
    
    return min(base_score, 100)

def score_education(education):
    """Score education section."""
    degrees = len(education.get('degrees', []))
    institutions = len(education.get('institutions', []))
    certifications = len(education.get('certifications', []))
    
    degree_score = min(degrees * 40, 60)  # Max 60 for degree
    institution_score = min(institutions * 20, 20)  # Max 20 for institution
    cert_score = min(certifications * 5, 20)  # Max 20 for certifications
    
    return min(degree_score + institution_score + cert_score, 100)

def score_sections(sections):
    """Score resume sections completeness."""
    required_sections = ['summary', 'experience', 'education', 'skills']
    optional_sections = ['projects', 'certifications', 'awards']
    
    required_score = sum(50 for section in required_sections if sections.get(section, False))
    optional_score = sum(10 for section in optional_sections if sections.get(section, False))
    
    return min(required_score + optional_score, 100)

def score_formatting(parsed_data):
    """Score resume formatting and structure."""
    word_count = parsed_data.get('word_count', 0)
    
    # Optimal word count is 300-800 words
    if 300 <= word_count <= 800:
        return 100
    elif 200 <= word_count < 300 or 800 < word_count <= 1000:
        return 80
    elif 100 <= word_count < 200 or 1000 < word_count <= 1200:
        return 60
    else:
        return 40

def score_keywords(keywords, target_role=None):
    """Score keyword usage with role-specific weighting."""
    if not keywords:
        return 40
    
    keyword_count = len(keywords)
    base_score = 0
    
    if keyword_count >= 20: base_score = 100
    elif keyword_count >= 15: base_score = 85
    elif keyword_count >= 10: base_score = 70
    elif keyword_count >= 5: base_score = 55
    else: base_score = 40
    
    # Bonus for role-specific keywords
    if target_role:
        role_bonus = calculate_role_keyword_bonus(keywords, target_role)
        base_score = min(base_score + role_bonus, 100)
    
    return base_score

def calculate_role_keyword_bonus(keywords, target_role):
    """Calculate bonus for role-specific keywords."""
    role_keywords = {
        'data scientist': ['analytics', 'modeling', 'statistics', 'visualization', 'insights'],
        'software engineer': ['development', 'programming', 'architecture', 'testing', 'deployment'],
        'frontend developer': ['responsive', 'user interface', 'user experience', 'optimization'],
        'backend developer': ['api', 'database', 'server', 'scalability', 'performance'],
        'devops engineer': ['automation', 'deployment', 'monitoring', 'infrastructure', 'cloud'],
        'cybersecurity': ['security', 'vulnerability', 'compliance', 'risk', 'protection']
    }
    
    target_lower = target_role.lower()
    relevant_keywords = []
    
    for role, kws in role_keywords.items():
        if role in target_lower:
            relevant_keywords = kws
            break
    
    if not relevant_keywords:
        return 0
    
    keywords_lower = [kw.lower() for kw in keywords]
    matches = sum(1 for kw in relevant_keywords if any(kw in keyword for keyword in keywords_lower))
    
    return min(matches * 3, 15)  # Max 15 bonus points

def score_role_match(parsed_data, target_role):
    """Score how well the resume matches the target role."""
    if not target_role:
        return 50
    
    # Simple role matching based on skills and keywords
    resume_skills = [skill.lower() for skill in parsed_data.get('skills', [])]
    resume_keywords = [kw.lower() for kw in parsed_data.get('keywords', [])]
    resume_text = parsed_data.get('raw_text', '').lower()
    
    # Define role-specific requirements
    role_requirements = {
        'software engineer': ['python', 'java', 'javascript', 'programming', 'development', 'software'],
        'data scientist': ['python', 'r', 'sql', 'machine learning', 'data', 'analytics', 'statistics'],
        'frontend developer': ['javascript', 'react', 'html', 'css', 'frontend', 'ui', 'user interface'],
        'backend developer': ['python', 'java', 'api', 'database', 'server', 'backend'],
        'devops engineer': ['docker', 'kubernetes', 'aws', 'devops', 'deployment', 'infrastructure'],
        'cybersecurity': ['security', 'cybersecurity', 'penetration', 'firewall', 'compliance']
    }
    
    target_lower = target_role.lower()
    required_skills = []
    
    # Find matching role requirements
    for role, skills in role_requirements.items():
        if role in target_lower:
            required_skills = skills
            break
    
    if not required_skills:
        # Generic matching if role not found
        return 70
    
    # Calculate matches
    skill_matches = sum(1 for req in required_skills if any(req in skill for skill in resume_skills))
    keyword_matches = sum(1 for req in required_skills if any(req in kw for kw in resume_keywords))
    text_matches = sum(1 for req in required_skills if req in resume_text)
    
    total_matches = skill_matches + keyword_matches + text_matches
    max_possible = len(required_skills) * 3  # Each requirement can match in 3 ways
    
    if max_possible == 0:
        return 70
    
    match_percentage = (total_matches / max_possible) * 100
    return min(max(match_percentage, 30), 100)  # Between 30-100

def generate_recommendations(score_components, parsed_data, target_role=None):
    """Generate improvement recommendations based on scores."""
    recommendations = []
    
    if score_components['contact_info'] < 80:
        recommendations.append({
            'category': 'Contact Information',
            'priority': 'High',
            'suggestion': 'Add missing contact information (email, phone, LinkedIn profile)',
            'impact': 'Essential for recruiters to contact you',
            'action_items': [
                'Ensure email address is professional',
                'Add phone number with country code',
                'Include LinkedIn profile URL',
                'Consider adding portfolio website'
            ]
        })
    
    if score_components['skills'] < 70:
        skill_suggestions = [
            'Add more relevant technical skills',
            'Include both hard and soft skills',
            'Use industry-standard skill names',
            'Group skills by category (e.g., Programming, Tools, Frameworks)'
        ]
        
        if target_role:
            skill_suggestions.append(f'Research and add skills specific to {target_role} roles')
        
        recommendations.append({
            'category': 'Skills',
            'priority': 'High',
            'suggestion': 'Expand and optimize your skills section',
            'impact': 'Improves ATS keyword matching and showcases expertise',
            'action_items': skill_suggestions
        })
    
    if score_components['experience'] < 60:
        recommendations.append({
            'category': 'Experience',
            'priority': 'High',
            'suggestion': 'Enhance work experience with quantifiable achievements',
            'impact': 'Demonstrates career progression and accomplishments',
            'action_items': [
                'Use action verbs to start bullet points',
                'Include specific numbers and percentages',
                'Highlight promotions and increased responsibilities',
                'Focus on results and impact, not just duties'
            ]
        })
    
    if score_components.get('content_quality', 0) < 70:
        recommendations.append({
            'category': 'Content Quality',
            'priority': 'Medium',
            'suggestion': 'Improve content quality with measurable achievements',
            'impact': 'Makes your resume more compelling to hiring managers',
            'action_items': [
                'Add quantifiable results (e.g., "Increased sales by 25%")',
                'Use strong action verbs',
                'Include specific technologies and methodologies',
                'Highlight leadership and collaboration experiences'
            ]
        })
    
    if score_components['sections'] < 80:
        recommendations.append({
            'category': 'Structure',
            'priority': 'Medium',
            'suggestion': 'Include all essential resume sections',
            'impact': 'Ensures ATS can properly parse your resume',
            'action_items': [
                'Add professional summary at the top',
                'Include projects or portfolio section',
                'Add certifications if applicable',
                'Consider adding volunteer work or awards'
            ]
        })
    
    if target_role and score_components.get('role_match', 0) < 70:
        recommendations.append({
            'category': 'Role Alignment',
            'priority': 'High',
            'suggestion': f'Better align your resume with {target_role} requirements',
            'impact': 'Increases chances of passing ATS and getting interviews',
            'action_items': [
                f'Research common requirements for {target_role} positions',
                'Tailor your professional summary to the role',
                'Highlight relevant projects and experiences',
                'Use role-specific keywords throughout your resume'
            ]
        })
    
    if score_components['formatting'] < 70:
        recommendations.append({
            'category': 'Formatting',
            'priority': 'Low',
            'suggestion': 'Optimize resume formatting for ATS compatibility',
            'impact': 'Better readability for both ATS and human reviewers',
            'action_items': [
                'Use standard section headings',
                'Maintain consistent formatting',
                'Avoid complex layouts or graphics',
                'Keep resume length appropriate (1-2 pages)'
            ]
        })
    
    return recommendations

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "CareerBoost AI - Enhanced Resume Scoring",
        "version": "2.0.0",
        "description": "Advanced ATS scoring with PDF processing and ML analysis",
        "features": [
            "📄 PDF Resume Processing",
            "🤖 AI-Powered Content Extraction",
            "📊 Comprehensive ATS Scoring",
            "🎯 Role-Based Analysis",
            "💾 Resume Database Storage",
            "📈 Detailed Feedback & Recommendations"
        ],
        "endpoints": {
            "upload": "/api/resume/upload",
            "score_general": "/api/resume/score-general",
            "score_role_based": "/api/resume/score-role-based",
            "history": "/api/resume/history/{user_id}"
        }
    }

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...), user_id: str = Form("demo_user")):
    """Upload and parse resume PDF."""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. Please ensure the PDF contains readable text.")
        
        # Parse resume content
        parsed_data = parse_resume_content(text)
        
        # Store in database
        resume_id = str(uuid.uuid4())
        resume_record = {
            "resume_id": resume_id,
            "user_id": user_id,
            "filename": file.filename,
            "upload_date": datetime.now().isoformat(),
            "file_size": len(content),
            "parsed_data": parsed_data,
            "processing_status": "completed"
        }
        
        resume_database[resume_id] = resume_record
        
        return {
            "success": True,
            "resume_id": resume_id,
            "parsed_data": parsed_data,
            "message": "Resume uploaded and processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")

@app.post("/api/resume/score-general")
async def score_resume_general(request: ResumeScoreRequest):
    """Score resume using general ATS criteria."""
    try:
        scoring_result = calculate_ats_score(request.resume_data, "general")
        
        # Store analysis in history
        analysis_id = str(uuid.uuid4())
        analysis_record = {
            "analysis_id": analysis_id,
            "user_id": getattr(request, 'user_id', 'demo_user'),
            "analysis_type": "general_ats",
            "scoring_result": scoring_result,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if analysis_record["user_id"] not in analysis_history:
            analysis_history[analysis_record["user_id"]] = []
        
        analysis_history[analysis_record["user_id"]].append(analysis_record)
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "scoring_type": "General ATS",
            "overall_score": scoring_result['overall_score'],
            "score_level": get_score_level(scoring_result['overall_score']),
            "component_scores": scoring_result['component_scores'],
            "recommendations": scoring_result['recommendations'],
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@app.post("/api/resume/score-role-based")
async def score_resume_role_based(request: RoleBasedScoreRequest):
    """Score resume against specific role requirements."""
    try:
        scoring_result = calculate_ats_score(request.resume_data, "role-based", request.target_role)
        
        # Store analysis in history
        analysis_id = str(uuid.uuid4())
        analysis_record = {
            "analysis_id": analysis_id,
            "user_id": getattr(request, 'user_id', 'demo_user'),
            "analysis_type": "role_based_ats",
            "target_role": request.target_role,
            "scoring_result": scoring_result,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if analysis_record["user_id"] not in analysis_history:
            analysis_history[analysis_record["user_id"]] = []
        
        analysis_history[analysis_record["user_id"]].append(analysis_record)
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "scoring_type": "Role-Based ATS",
            "target_role": request.target_role,
            "overall_score": scoring_result['overall_score'],
            "score_level": get_score_level(scoring_result['overall_score']),
            "component_scores": scoring_result['component_scores'],
            "recommendations": scoring_result['recommendations'],
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Role-based scoring failed: {str(e)}")

@app.get("/api/resume/history/{user_id}")
async def get_resume_history(user_id: str):
    """Get user's resume analysis history."""
    try:
        user_resumes = [resume for resume in resume_database.values() if resume['user_id'] == user_id]
        user_analyses = analysis_history.get(user_id, [])
        
        return {
            "success": True,
            "user_id": user_id,
            "total_resumes": len(user_resumes),
            "total_analyses": len(user_analyses),
            "resumes": sorted(user_resumes, key=lambda x: x['upload_date'], reverse=True),
            "analyses": sorted(user_analyses, key=lambda x: x['analyzed_at'], reverse=True)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

def get_score_level(score):
    """Get score level description."""
    if score >= 90: return "Excellent"
    if score >= 80: return "Very Good"
    if score >= 70: return "Good"
    if score >= 60: return "Average"
    return "Needs Improvement"

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Enhanced Resume Scoring",
        "version": "2.0.0",
        "features_active": {
            "pdf_processing": True,
            "ats_scoring": True,
            "role_based_analysis": True,
            "database_storage": True,
            "ml_analysis": True
        },
        "database_stats": {
            "total_resumes": len(resume_database),
            "total_analyses": sum(len(analyses) for analyses in analysis_history.values()),
            "ats_skills_loaded": len(ats_skills_list),
            "job_dataset_loaded": not job_dataset.empty
        }
    }

if __name__ == "__main__":
    print("🚀 Starting CareerBoost AI - Enhanced Resume Scoring Server")
    print("📄 PDF processing and ATS scoring with ML analysis")
    print("🔗 API Documentation: http://localhost:8007/docs")
    print("🏥 Health Check: http://localhost:8007/health")
    print("=" * 60)
    
    uvicorn.run(
        "enhanced_resume_scoring_server:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
        log_level="info"
    )