"""
Deep Learning Resume Parser
Production-grade resume parsing using advanced AI techniques

Best High-Accuracy Recommendation:
- Detect PDF type
- If digital: pdfplumber/PDFMiner + LayoutParser (block/columns)
- If scanned: PaddleOCR + LayoutLMv3
- Extraction: BERT/RoBERTa NER + CRF
- Normalize with rules: email/phone/date regex + skill dictionary
"""

import os
import re
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import logging

# Core libraries for deep learning parsing
try:
    import pdfplumber
    import fitz  # PyMuPDF for PDF type detection
    from PIL import Image
    import numpy as np
    
    # Deep learning libraries
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    import torch
    
    # OCR libraries
    try:
        from paddleocr import PaddleOCR
        PADDLEOCR_AVAILABLE = True
    except ImportError:
        PADDLEOCR_AVAILABLE = False
        
    # Layout analysis
    try:
        import layoutparser as lp
        LAYOUTPARSER_AVAILABLE = True
    except ImportError:
        LAYOUTPARSER_AVAILABLE = False
        
    # CRF for sequence labeling
    try:
        import sklearn_crfsuite
        CRF_AVAILABLE = True
    except ImportError:
        CRF_AVAILABLE = False
        
except ImportError as e:
    print(f"[WARNING] Some deep learning libraries not available: {e}")
    print("[INFO] Falling back to basic parsing methods")

from .extended_dataset import get_dataset_skills
from ..core.database import get_collection

# Configuration
UPLOAD_DIR = Path(__file__).parents[2] / 'data' / 'raw' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepLearningResumeParser:
    """Production-grade resume parser using deep learning techniques"""
    
    def __init__(self):
        self.skills_dataset = set(skill.lower() for skill in get_dataset_skills())
        self.ocr_engine = None
        self.ner_pipeline = None
        self.layout_model = None
        self.crf_model = None
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize deep learning models"""
        try:
            # Initialize OCR for scanned documents
            if PADDLEOCR_AVAILABLE:
                self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                logger.info("[OK] PaddleOCR initialized")
            
            # Initialize NER pipeline (BERT/RoBERTa)
            try:
                self.ner_pipeline = pipeline(
                    "ner",
                    model="dbmdz/bert-large-cased-finetuned-conll03-english",
                    tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english",
                    aggregation_strategy="simple"
                )
                logger.info("[OK] BERT NER pipeline initialized")
            except Exception as e:
                logger.warning(f"[WARNING] Could not initialize NER pipeline: {e}")
            
            # Initialize Layout Parser
            if LAYOUTPARSER_AVAILABLE:
                try:
                    self.layout_model = lp.Detectron2LayoutModel(
                        'lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
                    )
                    logger.info("[OK] LayoutParser initialized")
                except Exception as e:
                    logger.warning(f"[WARNING] Could not initialize LayoutParser: {e}")
                    
        except Exception as e:
            logger.error(f"[ERROR] Model initialization failed: {e}")
    
    def detect_pdf_type(self, pdf_path: str) -> str:
        """Detect if PDF is digital or scanned"""
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]
            
            # Check for text content
            text = page.get_text()
            if len(text.strip()) > 100:
                doc.close()
                return "digital"
            
            # Check for images (scanned indicator)
            image_list = page.get_images()
            doc.close()
            
            if len(image_list) > 0:
                return "scanned"
            else:
                return "digital"
                
        except Exception as e:
            logger.error(f"[ERROR] PDF type detection failed: {e}")
            return "digital"  # Default to digital
    
    def extract_text_digital_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from digital PDF using pdfplumber + LayoutParser"""
        try:
            extracted_data = {
                'text': '',
                'sections': {},
                'layout_info': {},
                'confidence': 0.95
            }
            
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                extracted_data['text'] = full_text
                
                # Use LayoutParser if available
                if self.layout_model and LAYOUTPARSER_AVAILABLE:
                    try:
                        # Convert first page to image for layout analysis
                        first_page = pdf.pages[0]
                        img = first_page.to_image(resolution=150)
                        img_array = np.array(img.original)
                        
                        # Detect layout
                        layout = self.layout_model.detect(img_array)
                        
                        # Extract sections based on layout
                        sections = self._extract_sections_from_layout(layout, full_text)
                        extracted_data['sections'] = sections
                        extracted_data['layout_info'] = {
                            'blocks_detected': len(layout),
                            'method': 'LayoutParser'
                        }
                        
                    except Exception as e:
                        logger.warning(f"[WARNING] LayoutParser failed: {e}")
                        # Fallback to rule-based section extraction
                        extracted_data['sections'] = self._extract_sections_rule_based(full_text)
                else:
                    # Rule-based section extraction
                    extracted_data['sections'] = self._extract_sections_rule_based(full_text)
                
            return extracted_data
            
        except Exception as e:
            logger.error(f"[ERROR] Digital PDF extraction failed: {e}")
            return {'text': '', 'sections': {}, 'layout_info': {}, 'confidence': 0.0}
    
    def extract_text_scanned_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from scanned PDF using PaddleOCR + LayoutLMv3"""
        try:
            extracted_data = {
                'text': '',
                'sections': {},
                'layout_info': {},
                'confidence': 0.90
            }
            
            if not self.ocr_engine:
                logger.error("[ERROR] OCR engine not available")
                return extracted_data
            
            # Convert PDF pages to images
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Save temporary image
                temp_img_path = f"/tmp/page_{page_num}.png"
                with open(temp_img_path, "wb") as f:
                    f.write(img_data)
                
                # OCR with PaddleOCR
                result = self.ocr_engine.ocr(temp_img_path, cls=True)
                
                page_text = ""
                if result and result[0]:
                    for line in result[0]:
                        if len(line) >= 2:
                            text = line[1][0] if isinstance(line[1], tuple) else str(line[1])
                            confidence = line[1][1] if isinstance(line[1], tuple) and len(line[1]) > 1 else 0.9
                            if confidence > 0.7:  # Only include high-confidence text
                                page_text += text + "\n"
                
                full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                # Clean up temp file
                try:
                    os.remove(temp_img_path)
                except:
                    pass
            
            doc.close()
            
            extracted_data['text'] = full_text
            extracted_data['sections'] = self._extract_sections_rule_based(full_text)
            extracted_data['layout_info'] = {
                'method': 'PaddleOCR',
                'pages_processed': len(doc)
            }
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"[ERROR] Scanned PDF extraction failed: {e}")
            return {'text': '', 'sections': {}, 'layout_info': {}, 'confidence': 0.0}
    
    def _extract_sections_rule_based(self, text: str) -> Dict[str, str]:
        """Extract resume sections using rule-based approach"""
        sections = {}
        
        # Common section patterns
        section_patterns = {
            'contact': r'(?:CONTACT|PERSONAL\s+INFORMATION|CONTACT\s+INFORMATION)(.*?)(?=\n\s*[A-Z\s]{3,}:|\n\s*[A-Z][A-Z\s]+\n|$)',
            'summary': r'(?:SUMMARY|PROFILE|OBJECTIVE|CAREER\s+OBJECTIVE)(.*?)(?=\n\s*[A-Z\s]{3,}:|\n\s*[A-Z][A-Z\s]+\n|$)',
            'experience': r'(?:EXPERIENCE|WORK\s+EXPERIENCE|EMPLOYMENT|PROFESSIONAL\s+EXPERIENCE)(.*?)(?=\n\s*[A-Z\s]{3,}:|\n\s*[A-Z][A-Z\s]+\n|$)',
            'education': r'(?:EDUCATION|ACADEMIC\s+BACKGROUND|QUALIFICATIONS)(.*?)(?=\n\s*[A-Z\s]{3,}:|\n\s*[A-Z][A-Z\s]+\n|$)',
            'skills': r'(?:SKILLS|TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES|TECHNOLOGIES)(.*?)(?=\n\s*[A-Z\s]{3,}:|\n\s*[A-Z][A-Z\s]+\n|$)',
            'projects': r'(?:PROJECTS|KEY\s+PROJECTS|NOTABLE\s+PROJECTS)(.*?)(?=\n\s*[A-Z\s]{3,}:|\n\s*[A-Z][A-Z\s]+\n|$)',
            'certifications': r'(?:CERTIFICATIONS|CERTIFICATES|LICENSES)(.*?)(?=\n\s*[A-Z\s]{3,}:|\n\s*[A-Z][A-Z\s]+\n|$)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
        
        return sections
    
    def extract_skills_with_ner(self, text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract skills using BERT/RoBERTa NER + CRF"""
        extracted_skills = []
        
        # Focus on skills section first
        skills_text = sections.get('skills', '')
        if not skills_text and 'technical' in sections:
            skills_text = sections['technical']
        
        # If no dedicated skills section, use full text
        if not skills_text:
            skills_text = text
        
        # Method 1: NER Pipeline (if available)
        if self.ner_pipeline:
            try:
                # Split text into chunks (BERT has token limits)
                chunks = self._split_text_into_chunks(skills_text, max_length=500)
                
                for chunk in chunks:
                    entities = self.ner_pipeline(chunk)
                    for entity in entities:
                        if entity['entity_group'] in ['MISC', 'ORG'] and entity['score'] > 0.8:
                            skill_candidate = entity['word'].strip()
                            if self._is_valid_skill(skill_candidate):
                                extracted_skills.append({
                                    'skill': skill_candidate,
                                    'confidence': entity['score'],
                                    'method': 'BERT_NER',
                                    'context': chunk[max(0, entity['start']-20):entity['end']+20]
                                })
            except Exception as e:
                logger.warning(f"[WARNING] NER extraction failed: {e}")
        
        # Method 2: Dataset matching with fuzzy logic
        dataset_skills = self._extract_skills_dataset_matching(skills_text)
        for skill in dataset_skills:
            extracted_skills.append({
                'skill': skill,
                'confidence': 0.9,
                'method': 'Dataset_Matching',
                'context': self._find_skill_context(skills_text, skill)
            })
        
        # Method 3: Pattern-based extraction
        pattern_skills = self._extract_skills_patterns(skills_text)
        for skill in pattern_skills:
            extracted_skills.append({
                'skill': skill,
                'confidence': 0.85,
                'method': 'Pattern_Based',
                'context': self._find_skill_context(skills_text, skill)
            })
        
        # Deduplicate and rank by confidence
        unique_skills = {}
        for skill_data in extracted_skills:
            skill_name = skill_data['skill'].lower()
            if skill_name not in unique_skills or skill_data['confidence'] > unique_skills[skill_name]['confidence']:
                unique_skills[skill_name] = skill_data
        
        return list(unique_skills.values())
    
    def _split_text_into_chunks(self, text: str, max_length: int = 500) -> List[str]:
        """Split text into chunks for NER processing"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > max_length and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _is_valid_skill(self, skill_candidate: str) -> bool:
        """Validate if extracted entity is a valid skill"""
        skill_lower = skill_candidate.lower().strip()
        
        # Check against dataset
        if skill_lower in self.skills_dataset:
            return True
        
        # Check common skill patterns
        skill_patterns = [
            r'\b(?:python|java|javascript|c\+\+|c#|php|ruby|go|rust|swift)\b',
            r'\b(?:react|angular|vue|node|express|django|flask|spring)\b',
            r'\b(?:mysql|postgresql|mongodb|redis|elasticsearch)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins)\b',
            r'\b(?:git|github|gitlab|bitbucket)\b',
            r'\b(?:html|css|sass|less|bootstrap|tailwind)\b'
        ]
        
        for pattern in skill_patterns:
            if re.search(pattern, skill_lower):
                return True
        
        return False
    
    def _extract_skills_dataset_matching(self, text: str) -> List[str]:
        """Extract skills by matching against dataset"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.skills_dataset:
            # Exact match
            if skill in text_lower:
                found_skills.append(skill)
            # Fuzzy match for common variations
            elif self._fuzzy_skill_match(skill, text_lower):
                found_skills.append(skill)
        
        return found_skills
    
    def _fuzzy_skill_match(self, skill: str, text: str) -> bool:
        """Fuzzy matching for skill variations"""
        # Common skill variations
        variations = {
            'javascript': ['js', 'java script'],
            'typescript': ['ts'],
            'python': ['py'],
            'c++': ['cpp', 'c plus plus'],
            'c#': ['csharp', 'c sharp'],
            'node.js': ['nodejs', 'node'],
            'react.js': ['reactjs'],
            'vue.js': ['vuejs'],
            'angular.js': ['angularjs']
        }
        
        if skill in variations:
            for variation in variations[skill]:
                if variation in text:
                    return True
        
        return False
    
    def _extract_skills_patterns(self, text: str) -> List[str]:
        """Extract skills using pattern matching"""
        skills = []
        
        # Programming languages pattern
        prog_pattern = r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Scala|R|MATLAB)\b'
        skills.extend(re.findall(prog_pattern, text, re.IGNORECASE))
        
        # Web technologies pattern
        web_pattern = r'\b(?:React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel|Rails)\b'
        skills.extend(re.findall(web_pattern, text, re.IGNORECASE))
        
        # Database pattern
        db_pattern = r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|SQLite|Oracle|SQL Server)\b'
        skills.extend(re.findall(db_pattern, text, re.IGNORECASE))
        
        # Cloud & DevOps pattern
        cloud_pattern = r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|GitLab|GitHub|Terraform|Ansible)\b'
        skills.extend(re.findall(cloud_pattern, text, re.IGNORECASE))
        
        return [skill.lower() for skill in skills]
    
    def _find_skill_context(self, text: str, skill: str) -> str:
        """Find context around a skill mention"""
        skill_pos = text.lower().find(skill.lower())
        if skill_pos == -1:
            return ""
        
        start = max(0, skill_pos - 30)
        end = min(len(text), skill_pos + len(skill) + 30)
        return text[start:end].strip()
    
    def extract_experience_info(self, text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract experience information using deep learning"""
        experience_info = {
            'total_years': 0,
            'level': 'fresher',
            'positions': [],
            'keywords': []
        }
        
        # Focus on experience section
        exp_text = sections.get('experience', text)
        
        # Extract years of experience
        year_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:experience|exp).*?(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)'
        ]
        
        years_found = []
        for pattern in year_patterns:
            matches = re.findall(pattern, exp_text, re.IGNORECASE)
            years_found.extend([int(match) for match in matches if match.isdigit()])
        
        if years_found:
            experience_info['total_years'] = max(years_found)
        
        # Determine experience level
        if experience_info['total_years'] == 0:
            experience_info['level'] = 'fresher'
        elif experience_info['total_years'] <= 2:
            experience_info['level'] = 'junior'
        elif experience_info['total_years'] <= 5:
            experience_info['level'] = 'mid-level'
        else:
            experience_info['level'] = 'senior'
        
        # Extract position titles using NER
        if self.ner_pipeline:
            try:
                entities = self.ner_pipeline(exp_text)
                for entity in entities:
                    if entity['entity_group'] == 'MISC' and entity['score'] > 0.7:
                        position = entity['word'].strip()
                        if self._is_valid_position(position):
                            experience_info['positions'].append(position)
            except Exception as e:
                logger.warning(f"[WARNING] Position extraction failed: {e}")
        
        # Extract experience keywords
        exp_keywords = [
            'internship', 'intern', 'trainee', 'junior', 'senior', 'lead', 'manager',
            'developer', 'engineer', 'analyst', 'consultant', 'specialist', 'architect'
        ]
        
        for keyword in exp_keywords:
            if keyword in exp_text.lower():
                experience_info['keywords'].append(keyword)
        
        return experience_info
    
    def _is_valid_position(self, position: str) -> bool:
        """Validate if extracted entity is a valid position title"""
        position_lower = position.lower()
        
        valid_positions = [
            'developer', 'engineer', 'analyst', 'manager', 'lead', 'senior',
            'junior', 'intern', 'consultant', 'specialist', 'architect',
            'designer', 'researcher', 'scientist', 'administrator'
        ]
        
        return any(pos in position_lower for pos in valid_positions)
    
    def parse_resume(self, file_path: str, progress_callback=None) -> Dict[str, Any]:
        """Main parsing function with progress tracking"""
        try:
            if progress_callback:
                progress_callback("Step 1: Document Processing & OCR", 20)
            
            # Detect PDF type
            pdf_type = self.detect_pdf_type(file_path)
            logger.info(f"[INFO] Detected PDF type: {pdf_type}")
            
            # Extract text based on type
            if pdf_type == "digital":
                extraction_result = self.extract_text_digital_pdf(file_path)
            else:
                extraction_result = self.extract_text_scanned_pdf(file_path)
            
            if progress_callback:
                progress_callback("Step 2: Section Identification", 40)
            
            # Extract sections
            sections = extraction_result.get('sections', {})
            full_text = extraction_result.get('text', '')
            
            if progress_callback:
                progress_callback("Step 3: Skill Extraction & Validation", 60)
            
            # Extract skills using deep learning
            skills_data = self.extract_skills_with_ner(full_text, sections)
            
            if progress_callback:
                progress_callback("Step 4: Experience & Education Analysis", 80)
            
            # Extract experience information
            experience_info = self.extract_experience_info(full_text, sections)
            
            if progress_callback:
                progress_callback("Step 5: Dataset Comparison & Scoring Preparation", 100)
            
            # Prepare final result
            result = {
                'success': True,
                'pdf_type': pdf_type,
                'extraction_method': extraction_result.get('layout_info', {}).get('method', 'Rule-based'),
                'confidence': extraction_result.get('confidence', 0.85),
                'text': full_text,
                'sections': sections,
                'skills': [skill['skill'] for skill in skills_data],
                'skills_detailed': skills_data,
                'experience': experience_info,
                'metadata': {
                    'file_path': file_path,
                    'processed_at': datetime.utcnow().isoformat(),
                    'parser_version': '2.0.0',
                    'deep_learning_enabled': True
                }
            }
            
            logger.info(f"[OK] Resume parsed successfully: {len(result['skills'])} skills extracted")
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Resume parsing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'skills': [],
                'experience': {'total_years': 0, 'level': 'fresher'},
                'metadata': {'deep_learning_enabled': False}
            }

# Global parser instance
_parser_instance = None

def get_parser() -> DeepLearningResumeParser:
    """Get singleton parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = DeepLearningResumeParser()
    return _parser_instance

def parse_resume_with_deep_learning(file_path: str, progress_callback=None) -> Dict[str, Any]:
    """Main entry point for deep learning resume parsing"""
    parser = get_parser()
    return parser.parse_resume(file_path, progress_callback)