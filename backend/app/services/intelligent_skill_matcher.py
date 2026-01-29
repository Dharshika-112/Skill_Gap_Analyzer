"""
Skill Gap Analyzer - Step 3: Intelligent Skill Matching
CareerBoost AI - Advanced Skill Matching Engine

This module implements the third step of the 8-step skill gap analysis process:
- Exact matching for perfect skill alignment
- Fuzzy matching for typos and close variants
- Hierarchical matching for advanced skills covering basic requirements
"""

import re
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
from enum import Enum

class MatchType(Enum):
    """Types of skill matches."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    HIERARCHICAL = "hierarchical"
    NO_MATCH = "no_match"

class SkillMatch:
    """Represents a skill match result."""
    def __init__(self, user_skill: str, required_skill: str, match_type: MatchType, 
                 confidence: float, explanation: str = ""):
        self.user_skill = user_skill
        self.required_skill = required_skill
        self.match_type = match_type
        self.confidence = confidence
        self.explanation = explanation
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "user_skill": self.user_skill,
            "required_skill": self.required_skill,
            "match_type": self.match_type.value,
            "confidence": self.confidence,
            "explanation": self.explanation
        }

class IntelligentSkillMatcher:
    def __init__(self):
        """Initialize the intelligent skill matcher."""
        self.fuzzy_threshold = 0.85
        self.partial_threshold = 0.75
        
        # Hierarchical skill relationships (advanced -> basic)
        self.skill_hierarchy = {
            # .NET Technologies
            "asp.net core": [".net", ".net core", "web development"],
            "entity framework": [".net", "orm", "database"],
            "blazor": [".net", "web development", "frontend"],
            
            # JavaScript Ecosystem
            "react": ["javascript", "frontend", "web development"],
            "angular": ["javascript", "typescript", "frontend", "web development"],
            "vue": ["javascript", "frontend", "web development"],
            "node.js": ["javascript", "backend", "server-side"],
            "express.js": ["node.js", "javascript", "backend", "web development"],
            "next.js": ["react", "javascript", "frontend", "web development"],
            "nuxt.js": ["vue", "javascript", "frontend", "web development"],
            
            # Python Ecosystem
            "django": ["python", "web development", "backend"],
            "flask": ["python", "web development", "backend"],
            "fastapi": ["python", "api development", "backend"],
            "pandas": ["python", "data analysis"],
            "numpy": ["python", "data science"],
            "tensorflow": ["python", "machine learning", "deep learning"],
            "pytorch": ["python", "machine learning", "deep learning"],
            "scikit-learn": ["python", "machine learning"],
            
            # Java Ecosystem
            "spring boot": ["java", "backend", "web development"],
            "hibernate": ["java", "orm", "database"],
            "maven": ["java", "build tools"],
            "gradle": ["java", "build tools"],
            
            # Database Technologies
            "postgresql": ["sql", "database", "relational database"],
            "mysql": ["sql", "database", "relational database"],
            "mongodb": ["nosql", "database", "document database"],
            "redis": ["nosql", "caching", "in-memory database"],
            "elasticsearch": ["nosql", "search engine", "database"],
            
            # Cloud & DevOps
            "kubernetes": ["docker", "containerization", "orchestration"],
            "docker": ["containerization", "devops"],
            "terraform": ["infrastructure as code", "devops", "cloud"],
            "ansible": ["configuration management", "devops", "automation"],
            "jenkins": ["cicd", "automation", "devops"],
            "github actions": ["cicd", "automation", "devops"],
            "aws lambda": ["aws", "serverless", "cloud"],
            "azure functions": ["azure", "serverless", "cloud"],
            
            # Testing
            "selenium": ["automation testing", "web testing", "testing"],
            "cypress": ["frontend testing", "e2e testing", "testing"],
            "jest": ["javascript testing", "unit testing", "testing"],
            "pytest": ["python testing", "unit testing", "testing"],
            "junit": ["java testing", "unit testing", "testing"],
            
            # Mobile Development
            "react native": ["react", "javascript", "mobile development"],
            "flutter": ["dart", "mobile development", "cross-platform"],
            "xamarin": ["c#", ".net", "mobile development"],
            "android studio": ["android", "mobile development"],
            "xcode": ["ios", "mobile development"],
            
            # AI/ML Advanced
            "transformers": ["nlp", "deep learning", "machine learning"],
            "bert": ["nlp", "transformers", "deep learning"],
            "gpt": ["nlp", "transformers", "deep learning"],
            "opencv": ["computer vision", "image processing", "python"],
            "yolo": ["computer vision", "object detection", "deep learning"],
            
            # Web Technologies
            "graphql": ["api development", "web development"],
            "rest api": ["api development", "web development"],
            "websockets": ["real-time communication", "web development"],
            "oauth": ["authentication", "security", "web development"],
            "jwt": ["authentication", "security", "web development"],
            
            # Data & Analytics
            "tableau": ["data visualization", "business intelligence"],
            "power bi": ["data visualization", "business intelligence"],
            "apache spark": ["big data", "data processing"],
            "hadoop": ["big data", "distributed computing"],
            "kafka": ["message queues", "streaming", "big data"],
            
            # Security
            "penetration testing": ["cybersecurity", "ethical hacking", "security"],
            "burp suite": ["web security", "penetration testing", "security"],
            "metasploit": ["penetration testing", "ethical hacking", "security"],
            "wireshark": ["network analysis", "security", "networking"],
        }
        
        # Skill synonyms for better matching
        self.skill_synonyms = {
            "javascript": ["js", "ecmascript"],
            "typescript": ["ts"],
            "python": ["py"],
            "c#": ["csharp", "c sharp"],
            "c++": ["cpp", "c plus plus"],
            "machine learning": ["ml", "artificial intelligence", "ai"],
            "artificial intelligence": ["ai", "machine learning", "ml"],
            "database": ["db"],
            "user interface": ["ui"],
            "user experience": ["ux"],
            "application programming interface": ["api"],
            "continuous integration": ["ci"],
            "continuous deployment": ["cd"],
            "version control": ["git"],
        }
    
    def calculate_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calculate similarity between two skills using multiple methods.
        
        Args:
            skill1: First skill
            skill2: Second skill
            
        Returns:
            Similarity score between 0 and 1
        """
        skill1_lower = skill1.lower().strip()
        skill2_lower = skill2.lower().strip()
        
        # Exact match
        if skill1_lower == skill2_lower:
            return 1.0
        
        # Check synonyms
        for canonical, synonyms in self.skill_synonyms.items():
            if skill1_lower in synonyms and skill2_lower in synonyms:
                return 1.0
            if skill1_lower == canonical and skill2_lower in synonyms:
                return 1.0
            if skill2_lower == canonical and skill1_lower in synonyms:
                return 1.0
        
        # Sequence matching for typos and variations
        sequence_similarity = SequenceMatcher(None, skill1_lower, skill2_lower).ratio()
        
        # Partial matching for compound skills
        partial_similarity = 0.0
        if skill1_lower in skill2_lower or skill2_lower in skill1_lower:
            partial_similarity = 0.8
        
        # Word-based matching for multi-word skills
        words1 = set(skill1_lower.split())
        words2 = set(skill2_lower.split())
        if words1 and words2:
            word_intersection = len(words1 & words2)
            word_union = len(words1 | words2)
            word_similarity = word_intersection / word_union if word_union > 0 else 0
        else:
            word_similarity = 0
        
        return max(sequence_similarity, partial_similarity, word_similarity)
    
    def find_exact_match(self, user_skill: str, required_skills: List[str]) -> Optional[SkillMatch]:
        """
        Find exact matches between user skill and required skills.
        
        Args:
            user_skill: User's skill
            required_skills: List of required skills
            
        Returns:
            SkillMatch object if exact match found, None otherwise
        """
        user_skill_lower = user_skill.lower().strip()
        
        for required_skill in required_skills:
            required_skill_lower = required_skill.lower().strip()
            
            if user_skill_lower == required_skill_lower:
                return SkillMatch(
                    user_skill=user_skill,
                    required_skill=required_skill,
                    match_type=MatchType.EXACT,
                    confidence=1.0,
                    explanation="Perfect skill match"
                )
            
            # Check synonyms
            for canonical, synonyms in self.skill_synonyms.items():
                if (user_skill_lower in synonyms and required_skill_lower in synonyms) or \
                   (user_skill_lower == canonical and required_skill_lower in synonyms) or \
                   (required_skill_lower == canonical and user_skill_lower in synonyms):
                    return SkillMatch(
                        user_skill=user_skill,
                        required_skill=required_skill,
                        match_type=MatchType.EXACT,
                        confidence=1.0,
                        explanation=f"Synonym match via {canonical}"
                    )
        
        return None
    
    def find_fuzzy_match(self, user_skill: str, required_skills: List[str]) -> Optional[SkillMatch]:
        """
        Find fuzzy matches for typos and close variants.
        
        Args:
            user_skill: User's skill
            required_skills: List of required skills
            
        Returns:
            Best fuzzy match if found, None otherwise
        """
        best_match = None
        best_similarity = 0.0
        
        for required_skill in required_skills:
            similarity = self.calculate_similarity(user_skill, required_skill)
            
            if similarity >= self.fuzzy_threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = SkillMatch(
                    user_skill=user_skill,
                    required_skill=required_skill,
                    match_type=MatchType.FUZZY,
                    confidence=similarity,
                    explanation=f"Fuzzy match with {similarity:.1%} similarity"
                )
        
        return best_match
    
    def find_hierarchical_match(self, user_skill: str, required_skills: List[str]) -> Optional[SkillMatch]:
        """
        Find hierarchical matches where advanced skills cover basic requirements.
        
        Args:
            user_skill: User's skill
            required_skills: List of required skills
            
        Returns:
            Best hierarchical match if found, None otherwise
        """
        user_skill_lower = user_skill.lower().strip()
        
        # Check if user's advanced skill covers any required basic skill
        if user_skill_lower in self.skill_hierarchy:
            covered_skills = self.skill_hierarchy[user_skill_lower]
            
            for required_skill in required_skills:
                required_skill_lower = required_skill.lower().strip()
                
                # Direct coverage
                if required_skill_lower in covered_skills:
                    return SkillMatch(
                        user_skill=user_skill,
                        required_skill=required_skill,
                        match_type=MatchType.HIERARCHICAL,
                        confidence=0.9,
                        explanation=f"{user_skill} covers {required_skill}"
                    )
                
                # Partial coverage through similarity
                for covered_skill in covered_skills:
                    similarity = self.calculate_similarity(covered_skill, required_skill_lower)
                    if similarity >= self.partial_threshold:
                        return SkillMatch(
                            user_skill=user_skill,
                            required_skill=required_skill,
                            match_type=MatchType.HIERARCHICAL,
                            confidence=0.8,
                            explanation=f"{user_skill} covers {covered_skill}, which matches {required_skill}"
                        )
        
        return None
    
    def match_skill(self, user_skill: str, required_skills: List[str]) -> SkillMatch:
        """
        Match a user skill against required skills using all matching methods.
        
        Args:
            user_skill: User's skill
            required_skills: List of required skills
            
        Returns:
            Best skill match found
        """
        # Try exact match first
        exact_match = self.find_exact_match(user_skill, required_skills)
        if exact_match:
            return exact_match
        
        # Try hierarchical match
        hierarchical_match = self.find_hierarchical_match(user_skill, required_skills)
        if hierarchical_match:
            return hierarchical_match
        
        # Try fuzzy match
        fuzzy_match = self.find_fuzzy_match(user_skill, required_skills)
        if fuzzy_match:
            return fuzzy_match
        
        # No match found
        return SkillMatch(
            user_skill=user_skill,
            required_skill="",
            match_type=MatchType.NO_MATCH,
            confidence=0.0,
            explanation="No matching skill found"
        )
    
    def match_skills_comprehensive(self, user_skills: List[str], required_skills: List[str]) -> Dict:
        """
        Perform comprehensive skill matching analysis.
        
        Args:
            user_skills: List of user's skills
            required_skills: List of required skills
            
        Returns:
            Comprehensive matching analysis
        """
        matches = []
        matched_required_skills = set()
        
        # Match each user skill
        for user_skill in user_skills:
            match = self.match_skill(user_skill, required_skills)
            matches.append(match)
            
            if match.match_type != MatchType.NO_MATCH:
                matched_required_skills.add(match.required_skill)
        
        # Find unmatched required skills
        unmatched_required = [skill for skill in required_skills 
                            if skill not in matched_required_skills]
        
        # Calculate statistics
        total_required = len(required_skills)
        total_matched = len(matched_required_skills)
        match_percentage = (total_matched / total_required * 100) if total_required > 0 else 0
        
        # Group matches by type
        exact_matches = [m for m in matches if m.match_type == MatchType.EXACT]
        fuzzy_matches = [m for m in matches if m.match_type == MatchType.FUZZY]
        hierarchical_matches = [m for m in matches if m.match_type == MatchType.HIERARCHICAL]
        no_matches = [m for m in matches if m.match_type == MatchType.NO_MATCH]
        
        return {
            "total_user_skills": len(user_skills),
            "total_required_skills": total_required,
            "total_matched_skills": total_matched,
            "match_percentage": round(match_percentage, 1),
            "unmatched_required_skills": unmatched_required,
            "matches": {
                "exact": [m.to_dict() for m in exact_matches],
                "fuzzy": [m.to_dict() for m in fuzzy_matches],
                "hierarchical": [m.to_dict() for m in hierarchical_matches],
                "no_match": [m.to_dict() for m in no_matches]
            },
            "match_summary": {
                "exact_count": len(exact_matches),
                "fuzzy_count": len(fuzzy_matches),
                "hierarchical_count": len(hierarchical_matches),
                "no_match_count": len(no_matches)
            }
        }
    
    def get_skill_suggestions(self, missing_skills: List[str], user_skills: List[str]) -> List[Dict]:
        """
        Get suggestions for acquiring missing skills based on user's current skills.
        
        Args:
            missing_skills: List of missing required skills
            user_skills: List of user's current skills
            
        Returns:
            List of skill acquisition suggestions
        """
        suggestions = []
        
        for missing_skill in missing_skills:
            suggestion = {
                "missing_skill": missing_skill,
                "difficulty": "medium",
                "learning_path": [],
                "related_user_skills": [],
                "estimated_time": "2-4 weeks"
            }
            
            # Find related skills user already has
            for user_skill in user_skills:
                similarity = self.calculate_similarity(user_skill, missing_skill)
                if similarity > 0.3:  # Some relation
                    suggestion["related_user_skills"].append({
                        "skill": user_skill,
                        "similarity": similarity
                    })
            
            # Check if user has prerequisite skills
            prerequisites_met = 0
            total_prerequisites = 0
            
            for advanced_skill, prerequisites in self.skill_hierarchy.items():
                if missing_skill.lower() in prerequisites:
                    total_prerequisites = len(prerequisites)
                    for prereq in prerequisites:
                        for user_skill in user_skills:
                            if self.calculate_similarity(user_skill, prereq) > 0.8:
                                prerequisites_met += 1
                                break
                    break
            
            # Adjust difficulty based on prerequisites
            if total_prerequisites > 0:
                prereq_ratio = prerequisites_met / total_prerequisites
                if prereq_ratio > 0.7:
                    suggestion["difficulty"] = "easy"
                    suggestion["estimated_time"] = "1-2 weeks"
                elif prereq_ratio < 0.3:
                    suggestion["difficulty"] = "hard"
                    suggestion["estimated_time"] = "4-8 weeks"
            
            suggestions.append(suggestion)
        
        return suggestions

# Global instance for easy import
intelligent_skill_matcher = IntelligentSkillMatcher()