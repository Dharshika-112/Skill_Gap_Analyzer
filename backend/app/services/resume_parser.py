"""Resume parser service

Capabilities:
- Save uploaded file to backend/data/raw/uploads
- Extract text from PDF, DOCX, TXT (lazy imports)
- Extract skills by matching against dataset skills
- Detect experience keywords and years
- Save parsed resume metadata to MongoDB
"""
from pathlib import Path
import re
import uuid
import os
from datetime import datetime
from typing import Tuple, List, Dict

from .extended_dataset import get_dataset_skills
from ..core.database import get_collection

UPLOAD_DIR = Path(__file__).parents[2] / 'data' / 'raw' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {'.pdf', '.docx', '.txt'}

def _save_file(file_bytes: bytes, filename: str) -> Path:
    ext = Path(filename).suffix.lower()
    safe_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / safe_name
    with open(dest, 'wb') as f:
        f.write(file_bytes)
    return dest

def _extract_text_from_pdf(path: Path) -> str:
    try:
        # lazy import to avoid hard dependency at module import
        from pdfminer.high_level import extract_text
        return extract_text(str(path)) or ''
    except Exception:
        return ''

def _extract_text_from_docx(path: Path) -> str:
    try:
        import docx
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return '\n'.join(paragraphs)
    except Exception:
        return ''

def _extract_text_from_txt(path: Path) -> str:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''

def _clean_text(text: str) -> str:
    # normalize whitespace and remove odd characters
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text

def _extract_skills_section(text: str) -> str:
    """Extract ONLY the Technical Skills section from resume, strictly excluding certifications"""
    
    # Clean and normalize text
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Approach 1: Strict pattern matching for skills sections
    skills_patterns = [
        # Match "TECHNICAL SKILLS" until next major section
        r'TECHNICAL\s+SKILLS?\s*:?\s*(.*?)(?=\n\s*(?:CERTIFICATIONS?|CERTIFICATES?|COURSES?|ACHIEVEMENTS?|EXPERIENCE|EDUCATION|PROJECTS?|AWARDS?|PUBLICATIONS?|REFERENCES?)\s*[:\n]|$)',
        # Match "SKILLS" until next major section  
        r'(?:^|\n)\s*SKILLS?\s*:?\s*(.*?)(?=\n\s*(?:CERTIFICATIONS?|CERTIFICATES?|COURSES?|ACHIEVEMENTS?|EXPERIENCE|EDUCATION|PROJECTS?|AWARDS?|PUBLICATIONS?|REFERENCES?)\s*[:\n]|$)',
        # Match "PROGRAMMING SKILLS"
        r'PROGRAMMING\s+SKILLS?\s*:?\s*(.*?)(?=\n\s*(?:CERTIFICATIONS?|CERTIFICATES?|COURSES?|ACHIEVEMENTS?|EXPERIENCE|EDUCATION|PROJECTS?|AWARDS?)\s*[:\n]|$)',
        # Match "TECHNICAL COMPETENCIES"
        r'TECHNICAL\s+COMPETENCIES?\s*:?\s*(.*?)(?=\n\s*(?:CERTIFICATIONS?|CERTIFICATES?|COURSES?|ACHIEVEMENTS?|EXPERIENCE|EDUCATION|PROJECTS?|AWARDS?)\s*[:\n]|$)',
    ]
    
    for pattern in skills_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if match:
            skills_section = match.group(1).strip()
            if len(skills_section) > 15:  # Must have substantial content
                cleaned_section = clean_skills_section(skills_section)
                if cleaned_section and len(cleaned_section) > 10:
                    return cleaned_section
    
    # Approach 2: Line-by-line parsing with strict boundaries
    lines = text.split('\n')
    skills_lines = []
    in_skills_section = False
    skills_section_found = False
    
    for i, line in enumerate(lines):
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        if not line_clean:
            continue
        
        # Detect skills section start - be more specific
        if not in_skills_section:
            skills_indicators = [
                'technical skills', 'programming skills', 'technical competencies',
                'core technical skills', 'key technical skills', 'programming languages'
            ]
            
            # Check if line is a skills header
            for indicator in skills_indicators:
                if indicator in line_lower:
                    # Must be a header (short line, ends with colon, or all caps)
                    if (len(line_clean.split()) <= 4 and 
                        (line_clean.endswith(':') or line_clean.isupper() or 
                         'skills' in line_lower)):
                        in_skills_section = True
                        skills_section_found = True
                        break
        
        # Detect section end - be very strict
        elif in_skills_section:
            # Stop at certification/course sections
            cert_indicators = [
                'certifications', 'certificates', 'courses', 'training',
                'achievements', 'awards', 'experience', 'education', 
                'projects', 'publications', 'references', 'contact'
            ]
            
            # Check if this line starts a new section
            is_section_header = False
            for indicator in cert_indicators:
                if indicator in line_lower:
                    # Must look like a section header
                    if (len(line_clean.split()) <= 3 and 
                        (line_clean.endswith(':') or line_clean.isupper())):
                        is_section_header = True
                        break
            
            if is_section_header:
                break
        
        # Collect skills content - only if in skills section
        if in_skills_section and skills_section_found:
            # Additional filtering - skip obvious non-skill content
            if not is_certification_content(line_clean):
                # Only include lines that look like skills
                if (line_clean.startswith('•') or line_clean.startswith('-') or 
                    line_clean.startswith('*') or ':' in line_clean or
                    any(tech in line_lower for tech in ['programming', 'web', 'database', 'cloud', 'tools'])):
                    skills_lines.append(line_clean)
    
    if skills_lines:
        skills_text = '\n'.join(skills_lines)
        return clean_skills_section(skills_text)
    
    # Approach 3: Look for technical bullet points only
    tech_bullets = []
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        # Must be a bullet point
        if (line_clean.startswith('•') or line_clean.startswith('-') or line_clean.startswith('*')):
            # Must contain technical keywords and NOT certification keywords
            tech_keywords = [
                'python', 'java', 'javascript', 'html', 'css', 'react', 'angular', 'vue',
                'node', 'sql', 'mysql', 'postgresql', 'mongodb', 'git', 'docker', 
                'aws', 'azure', 'kubernetes', 'tensorflow', 'pytorch', 'machine learning',
                'programming', 'development', 'framework', 'library', 'api', 'database'
            ]
            
            cert_keywords = [
                'cisco', 'google', 'ibm', 'microsoft', 'aws certification', 'certificate',
                'course', 'training', 'specialization', 'coursera', 'udemy'
            ]
            
            has_tech = any(keyword in line_lower for keyword in tech_keywords)
            has_cert = any(keyword in line_lower for keyword in cert_keywords)
            
            if has_tech and not has_cert:
                tech_bullets.append(line_clean)
    
    if tech_bullets:
        return '\n'.join(tech_bullets)
    
    # If nothing found, return empty
    return ""

def clean_skills_section(text: str) -> str:
    """Clean the skills section to remove certification content"""
    
    # Split into lines and clean each line
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip lines that are clearly certifications
        line_lower = line.lower()
        if any(cert_indicator in line_lower for cert_indicator in [
            'cisco', 'google', 'ibm', 'microsoft', 'aws certification', 'azure certification',
            'certificate', 'certification', 'course completion', 'specialization',
            'coursera', 'udemy', 'edx', 'pluralsight'
        ]):
            continue
        
        # Clean up the line - remove certification content that might be mixed in
        # Split by common separators and keep only skill-related parts
        parts = re.split(r'[•\-]\s*', line)
        for part in parts:
            part = part.strip()
            if part and not any(cert in part.lower() for cert in ['cisco', 'google', 'ibm', 'certificate']):
                cleaned_lines.append(part)
    
    return '\n'.join(cleaned_lines)

def _tokenize_candidates(text: str) -> List[str]:
    """Enhanced tokenization for bullet point format and mixed content"""
    
    # First extract skills section
    skills_text = _extract_skills_section(text)
    
    candidates = []
    
    # Split by lines first to handle bullet points
    lines = skills_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Remove bullet points and clean
        line = re.sub(r'^[•\-\*]\s*', '', line)
        
        # Handle category format like "Programming: Python, C, DSA, Java"
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                category = parts[0].strip()
                skills_part = parts[1].strip()
                
                # Add category as potential skill if relevant
                category_lower = category.lower()
                if any(tech_word in category_lower for tech_word in [
                    'programming', 'web', 'database', 'ai', 'data science', 'tools', 
                    'platform', 'frameworks', 'languages', 'technologies', 'software'
                ]):
                    candidates.append(category)
                
                # Clean skills part - remove certification content that might be mixed in
                skills_part = clean_mixed_content(skills_part)
                
                # Split skills by common separators
                skills = re.split(r'[,;]\s*', skills_part)
                for skill in skills:
                    skill = skill.strip()
                    if skill and len(skill) > 1 and not is_certification_content(skill):
                        candidates.append(skill)
        else:
            # Handle direct skill lists
            # Clean mixed content first
            line = clean_mixed_content(line)
            
            # Split on common separators
            parts = re.split(r'[;,\n\r\t]|\band\b|\bwith\b|\busing\b', line, flags=re.IGNORECASE)
            for p in parts:
                p = p.strip()
                if not p or is_certification_content(p):
                    continue
                # Skip common non-skill words
                skip_words = ['stress', 'innovation', 'leadership', 'teamwork', 'communication', 'deployment', 'experience', 'years', 'months']
                if p.lower() not in skip_words and len(p) > 1:
                    candidates.append(p)
    
    # Also look for technical terms anywhere in the text
    tech_terms = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite',
        'git', 'github', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'machine learning', 'deep learning', 'artificial intelligence', 'data science',
        'linux', 'windows', 'macos', 'ubuntu'
    ]
    
    text_lower = text.lower()
    for term in tech_terms:
        if term in text_lower:
            candidates.append(term.title())
    
    # Deduplicate and clean
    unique_candidates = []
    seen = set()
    for candidate in candidates:
        candidate_clean = candidate.strip()
        if candidate_clean and candidate_clean.lower() not in seen and len(candidate_clean) > 1:
            seen.add(candidate_clean.lower())
            unique_candidates.append(candidate_clean)
    
    return unique_candidates

def clean_mixed_content(text: str) -> str:
    """Clean text that might have skills mixed with certification content"""
    
    # Remove common certification patterns more aggressively
    text = re.sub(r'\b(CISCO|Google|IBM|Microsoft|AWS|Azure|Juniper|Infosys)\s*[-–]\s*[^,;]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(Certificate|Certification|Course|Specialization|Essentials|Foundations)\b[^,;]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(CU Boulder|Programming Fundamentals|NCIA-Cloud|Mist AI Associate)\b[^,;]*', '', text, flags=re.IGNORECASE)
    
    # Remove extra whitespace and clean up separators
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[,;]\s*[,;]', ',', text)  # Remove duplicate separators
    text = re.sub(r'^[,;\s]+|[,;\s]+$', '', text)  # Remove leading/trailing separators
    
    return text

def is_certification_content(text: str) -> bool:
    """Check if text is certification-related content"""
    
    text_lower = text.lower().strip()
    
    # Skip very short text
    if len(text_lower) < 2:
        return True
    
    cert_indicators = [
        'cisco', 'google', 'ibm', 'microsoft', 'aws certification', 'azure certification',
        'certificate', 'certification', 'course', 'specialization',
        'foundations of', 'essentials', 'fundamentals using', 'fundamentals with',
        'coursera', 'udemy', 'edx', 'pluralsight', 'juniper', 'infosys',
        'cu boulder', 'ncia-cloud', 'mist ai associate', 'programming fundamentals'
    ]
    
    # Check if the entire text is certification content
    for indicator in cert_indicators:
        if indicator in text_lower:
            return True
    
    # Check for patterns like "Company - Course Name"
    if re.search(r'\b(cisco|google|ibm|microsoft|aws|azure|juniper|infosys)\s*[-–]', text_lower):
        return True
    
    return False

def _normalize_skill(s: str) -> str:
    s = s.strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def extract_skills_from_text(text: str) -> List[str]:
    """
    Enhanced skill extraction that finds skills from the job dataset.
    Uses fuzzy matching and multiple extraction strategies.
    """
    cleaned = _clean_text(text)
    
    # Get skills from the actual job dataset
    from .dataset_loader import get_all_skills_from_dataset
    dataset_skills = get_all_skills_from_dataset()
    
    if not dataset_skills:
        # Fallback to extended dataset if job dataset not available
        dataset_skills = get_dataset_skills()
    
    # Extract skills section first
    skills_text = _extract_skills_section(cleaned)
    
    # Enhanced tokenization
    candidates = _tokenize_candidates(skills_text)
    
    # Also check full text for skills that might be mentioned elsewhere (like in projects)
    full_text_candidates = _tokenize_candidates(cleaned)
    
    # Add specific technical terms that might appear anywhere in resume
    tech_terms = ['tensorflow', 'pytorch', 'opencv', 'keras', 'pandas', 'numpy', 'matplotlib', 'scikit-learn', 'flask', 'django', 'spring', 'angular', 'vue', 'react', 'node.js', 'express']
    for term in tech_terms:
        if term in cleaned.lower():
            full_text_candidates.append(term)
    
    all_candidates = list(set(candidates + full_text_candidates))
    
    found_skills = []

    # Enhanced matching with improved logic
    for cand in all_candidates:
        cand_norm = _normalize_skill(cand).strip()
        if not cand_norm or len(cand_norm) < 2:
            continue
            
        # Skip if it's certification content
        if is_certification_content(cand_norm):
            continue
        
        # Find best match using improved matching
        best_match = _find_best_skill_match(cand_norm, dataset_skills)
        if best_match and best_match not in found_skills:
            found_skills.append(best_match)
    
    return sorted(found_skills)

def _are_skill_variants(skill1: str, skill2: str) -> bool:
    """Check if two skills are variants of each other"""
    # Common variations
    variations = {
        'js': 'javascript',
        'javascript': 'js',
        'ts': 'typescript',
        'typescript': 'ts',
        'py': 'python',
        'python': 'py',
        'react.js': 'react',
        'react': 'reactjs',
        'reactjs': 'react',
        'node.js': 'nodejs',
        'nodejs': 'node.js',
        'node': 'nodejs',
        'c++': 'cpp',
        'cpp': 'c++',
        'c#': 'csharp',
        'csharp': 'c#',
        'sql server': 'sqlserver',
        'sqlserver': 'sql server',
        'mysql': 'sql',
        'postgresql': 'sql',
        'postgres': 'postgresql',
        'mongodb': 'mongo',
        'mongo': 'mongodb',
        'html5': 'html',
        'html': 'html5',
        'css3': 'css',
        'css': 'css3',
        'machine learning': 'ml',
        'ml': 'machine learning',
        'artificial intelligence': 'ai',
        'ai': 'artificial intelligence',
        'deep learning': 'dl',
        'dl': 'deep learning',
        'data structures and algorithms': 'dsa',
        'dsa': 'data structures and algorithms',
        'data structures': 'dsa',
        'algorithms': 'dsa',
        'database management system': 'dbms',
        'dbms': 'database management system',
        'github': 'git',
        'git': 'github'
    }
    
    skill1_lower = skill1.lower().strip()
    skill2_lower = skill2.lower().strip()
    
    return (skill1_lower in variations and variations[skill1_lower] == skill2_lower) or \
           (skill2_lower in variations and variations[skill2_lower] == skill1_lower)

def _find_best_skill_match(candidate: str, dataset_skills: List[str]) -> str:
    """Find the best matching skill from dataset for a candidate skill"""
    candidate_lower = candidate.lower().strip()
    
    # First try exact match
    for skill in dataset_skills:
        if skill.lower().strip() == candidate_lower:
            return skill
    
    # Try variant matching
    for skill in dataset_skills:
        if _are_skill_variants(candidate_lower, skill.lower().strip()):
            return skill
    
    # Try partial matching for common cases
    for skill in dataset_skills:
        skill_lower = skill.lower().strip()
        
        # Handle specific cases
        if candidate_lower == 'c' and skill_lower in ['c programming', 'c language', 'c/c++']:
            return skill
        elif candidate_lower == 'reactjs' and 'react' in skill_lower and 'react' == skill_lower:
            return skill
        elif candidate_lower == 'dsa' and ('data structure' in skill_lower or 'algorithm' in skill_lower):
            return skill
        elif candidate_lower == 'dbms' and ('database' in skill_lower and 'management' in skill_lower):
            return skill
        elif candidate_lower in skill_lower or skill_lower in candidate_lower:
            # Only match if both are substantial (avoid false positives)
            if len(candidate_lower) >= 3 and len(skill_lower) >= 3:
                return skill
    
    return None

def detect_experience(text: str) -> Dict:
    """Detect experience type and approximate years from resume text."""
    txt = text.lower()
    exp_type = 'unknown'
    years = None

    if re.search(r'\bintern(ship)?\b', txt):
        exp_type = 'internship'
    elif re.search(r'\btraining\b', txt):
        exp_type = 'training'
    elif re.search(r'\bfresher\b|\bentry[- ]level\b', txt):
        exp_type = 'fresher'
    elif re.search(r'\bsenior\b|\bexpert\b|\blead\b|\bexperienced\b', txt):
        exp_type = 'experienced'
    else:
        exp_type = 'experienced' if re.search(r'\b\d+\+?\s+years?\b', txt) else 'fresher'

    # extract years like '3 years' or '3.5 years'
    m = re.search(r'(\d+(?:\.\d+)?)\s+years?', txt)
    if m:
        try:
            years = float(m.group(1))
        except Exception:
            years = None

    # fallback: months
    if years is None:
        m2 = re.search(r'(\d+)\s+months?', txt)
        if m2:
            try:
                years = round(float(int(m2.group(1))) / 12.0, 2)
            except Exception:
                years = None

    return {"type": exp_type, "years": years}

def parse_resume(file_bytes: bytes, filename: str) -> Dict:
    """Save file, extract text, return parsed skills and experience."""
    path = _save_file(file_bytes, filename)
    ext = path.suffix.lower()

    text = ''
    if ext == '.pdf':
        text = _extract_text_from_pdf(path)
    elif ext == '.docx':
        text = _extract_text_from_docx(path)
    elif ext == '.txt':
        text = _extract_text_from_txt(path)
    else:
        text = ''

    text = _clean_text(text)
    skills = extract_skills_from_text(text)
    experience = detect_experience(text)

    return {
        'filename': filename,
        'stored_path': str(path),
        'extracted_text_snippet': text[:2000],
        'skills': skills,
        'experience': experience,
        'parsed_at': datetime.utcnow()
    }

def save_parsed_resume(user_id: str, parsed: Dict) -> str:
    """Save parsed metadata to MongoDB and return inserted id"""
    col = get_collection('resumes')
    doc = {
        'user_id': user_id,
        'filename': parsed.get('filename'),
        'path': parsed.get('stored_path'),
        'skills': parsed.get('skills', []),
        'experience': parsed.get('experience', {}),
        'parsed_at': parsed.get('parsed_at', datetime.utcnow())
    }
    res = col.insert_one(doc)
    return str(res.inserted_id)
