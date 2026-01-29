"""
Skill Gap Analyzer - Step 4: Weighted Gap Scoring System
CareerBoost AI - Advanced Skill Gap Scoring Engine

This module implements the fourth step of the 8-step skill gap analysis process:
- Assigns weights based on skill importance (core vs optional)
- Considers frequency across job postings
- Adjusts for experience level requirements
- Outputs comprehensive scoring metrics
"""

import json
from typing import Dict, List, Tuple
from enum import Enum
from .skill_taxonomy import skill_taxonomy, SkillCategory
from .intelligent_skill_matcher import intelligent_skill_matcher, MatchType

class ReadinessLevel(Enum):
    """Job readiness levels based on skill gap analysis."""
    BEGINNER = "Beginner"
    INTERVIEW_READY = "Interview-Ready"
    JOB_READY = "Job-Ready"

class SkillImportance(Enum):
    """Skill importance levels."""
    CRITICAL = "critical"      # Must-have skills
    IMPORTANT = "important"    # Highly valuable skills
    PREFERRED = "preferred"    # Nice-to-have skills
    OPTIONAL = "optional"      # Bonus skills

class WeightedGapScorer:
    def __init__(self):
        """Initialize the weighted gap scoring system."""
        
        # Core skills that are typically critical for most roles
        self.critical_skills = {
            "programming": ["python", "java", "javascript", "c#", "c++"],
            "web": ["html", "css", "javascript", "react", "angular", "vue"],
            "backend": ["sql", "database", "api development", "rest api"],
            "data": ["sql", "python", "data analysis", "excel"],
            "mobile": ["android", "ios", "react native", "flutter"],
            "devops": ["docker", "kubernetes", "aws", "azure", "cicd"],
            "ai": ["python", "machine learning", "tensorflow", "pytorch"]
        }
        
        # Experience level multipliers
        self.experience_multipliers = {
            "fresher": {
                "fundamentals_weight": 1.5,  # Emphasize fundamentals
                "advanced_weight": 0.7,      # Less emphasis on advanced
                "soft_skills_weight": 1.2    # Important for freshers
            },
            "junior": {
                "fundamentals_weight": 1.3,
                "advanced_weight": 0.9,
                "soft_skills_weight": 1.1
            },
            "mid-level": {
                "fundamentals_weight": 1.0,
                "advanced_weight": 1.2,
                "soft_skills_weight": 1.0
            },
            "senior": {
                "fundamentals_weight": 0.8,
                "advanced_weight": 1.5,
                "soft_skills_weight": 1.3    # Leadership becomes important
            }
        }
        
        # Skill frequency weights (based on job market analysis)
        self.skill_frequency_weights = {
            # High frequency skills (appear in 70%+ of jobs)
            "javascript": 1.4, "python": 1.4, "sql": 1.3, "git": 1.2,
            "html": 1.3, "css": 1.3, "react": 1.2, "java": 1.3,
            
            # Medium frequency skills (appear in 40-70% of jobs)
            "angular": 1.1, "vue": 1.1, "node.js": 1.1, "docker": 1.2,
            "aws": 1.2, "azure": 1.1, "mongodb": 1.1, "postgresql": 1.1,
            
            # Lower frequency but specialized skills
            "machine learning": 1.0, "tensorflow": 1.0, "kubernetes": 1.1,
            "blockchain": 0.9, "ar/vr": 0.8
        }
    
    def determine_skill_importance(self, skill: str, role_category: str, 
                                 job_frequency: float = 0.5) -> SkillImportance:
        """
        Determine the importance level of a skill for a specific role.
        
        Args:
            skill: Skill name
            role_category: Category of the role (e.g., "web", "data", "mobile")
            job_frequency: Frequency of this skill across similar jobs (0-1)
            
        Returns:
            SkillImportance level
        """
        skill_lower = skill.lower().strip()
        
        # Check if it's a critical skill for this role category
        critical_for_role = self.critical_skills.get(role_category, [])
        if any(critical_skill in skill_lower or skill_lower in critical_skill 
               for critical_skill in critical_for_role):
            return SkillImportance.CRITICAL
        
        # High frequency skills are typically important
        if job_frequency > 0.7:
            return SkillImportance.CRITICAL
        elif job_frequency > 0.4:
            return SkillImportance.IMPORTANT
        elif job_frequency > 0.2:
            return SkillImportance.PREFERRED
        else:
            return SkillImportance.OPTIONAL
    
    def calculate_skill_weight(self, skill: str, importance: SkillImportance, 
                             category: SkillCategory, experience_level: str = "fresher",
                             role_type: str = "general") -> float:
        """
        Calculate the weight of a skill based on multiple factors.
        
        Args:
            skill: Skill name
            importance: Skill importance level
            category: Skill category
            experience_level: Required experience level
            role_type: Type of role
            
        Returns:
            Calculated weight (0-1)
        """
        # Base weight from importance
        importance_weights = {
            SkillImportance.CRITICAL: 1.0,
            SkillImportance.IMPORTANT: 0.8,
            SkillImportance.PREFERRED: 0.6,
            SkillImportance.OPTIONAL: 0.3
        }
        base_weight = importance_weights[importance]
        
        # Category weight adjustment
        category_weight = skill_taxonomy.get_category_weight(category, role_type)
        
        # Experience level adjustment
        exp_multipliers = self.experience_multipliers.get(experience_level, 
                                                        self.experience_multipliers["fresher"])
        
        # Determine if skill is fundamental or advanced
        fundamental_skills = ["html", "css", "javascript", "python", "java", "sql", "git"]
        is_fundamental = any(fund_skill in skill.lower() for fund_skill in fundamental_skills)
        
        if is_fundamental:
            exp_adjustment = exp_multipliers["fundamentals_weight"]
        elif category == SkillCategory.SOFT_COGNITIVE:
            exp_adjustment = exp_multipliers["soft_skills_weight"]
        else:
            exp_adjustment = exp_multipliers["advanced_weight"]
        
        # Frequency adjustment
        frequency_weight = self.skill_frequency_weights.get(skill.lower(), 1.0)
        
        # Calculate final weight
        final_weight = base_weight * category_weight * exp_adjustment * frequency_weight
        
        # Normalize to 0-1 range
        return min(final_weight, 1.0)
    
    def calculate_weighted_score(self, user_skills: List[str], required_skills: List[str],
                               role_type: str = "general", experience_level: str = "fresher",
                               job_data: Dict = None) -> Dict:
        """
        Calculate comprehensive weighted skill gap score.
        
        Args:
            user_skills: List of user's skills
            required_skills: List of required skills
            role_type: Type of role for weight adjustments
            experience_level: Required experience level
            job_data: Additional job data for context
            
        Returns:
            Comprehensive scoring analysis
        """
        # Perform skill matching
        matching_result = intelligent_skill_matcher.match_skills_comprehensive(
            user_skills, required_skills
        )
        
        # Categorize skills
        user_categorized = skill_taxonomy.classify_skills_list(user_skills)
        required_categorized = skill_taxonomy.classify_skills_list(required_skills)
        
        # Calculate weights for each required skill
        skill_weights = {}
        total_possible_weight = 0
        
        for skill in required_skills:
            categories = skill_taxonomy.classify_skill(skill)
            primary_category = categories[0] if categories else SkillCategory.CORE_PROGRAMMING
            
            # Determine importance (simplified - in real implementation, use job frequency data)
            importance = self.determine_skill_importance(skill, role_type, 0.5)
            
            weight = self.calculate_skill_weight(
                skill, importance, primary_category, experience_level, role_type
            )
            
            skill_weights[skill] = {
                "weight": weight,
                "importance": importance.value,
                "category": primary_category.value
            }
            total_possible_weight += weight
        
        # Calculate weighted scores for matched skills
        achieved_weight = 0
        skill_scores = {}
        
        for match_type, matches in matching_result["matches"].items():
            for match in matches:
                if match["required_skill"] and match["required_skill"] in skill_weights:
                    skill_info = skill_weights[match["required_skill"]]
                    confidence_multiplier = match["confidence"]
                    
                    # Adjust score based on match type
                    match_type_multipliers = {
                        "exact": 1.0,
                        "hierarchical": 0.95,
                        "fuzzy": 0.85,
                        "no_match": 0.0
                    }
                    
                    type_multiplier = match_type_multipliers.get(match_type, 0.0)
                    skill_score = skill_info["weight"] * confidence_multiplier * type_multiplier
                    achieved_weight += skill_score
                    
                    skill_scores[match["required_skill"]] = {
                        "user_skill": match["user_skill"],
                        "match_type": match_type,
                        "confidence": confidence_multiplier,
                        "weight": skill_info["weight"],
                        "score": skill_score,
                        "importance": skill_info["importance"],
                        "category": skill_info["category"]
                    }
        
        # Calculate overall scores
        total_skill_coverage = (achieved_weight / total_possible_weight * 100) if total_possible_weight > 0 else 0
        
        # Category-wise coverage
        category_coverage = skill_taxonomy.get_category_coverage(user_skills, required_skills)
        
        # Calculate weighted category scores
        weighted_category_scores = {}
        for category_name, coverage_data in category_coverage.items():
            category_enum = next((cat for cat in SkillCategory if cat.value == category_name), None)
            if category_enum:
                category_weight = skill_taxonomy.get_category_weight(category_enum, role_type)
                weighted_score = coverage_data["coverage_percentage"] * category_weight
                weighted_category_scores[category_name] = {
                    **coverage_data,
                    "weighted_score": round(weighted_score, 1),
                    "category_weight": category_weight
                }
        
        # Determine readiness level
        readiness_level = self.determine_readiness_level(
            total_skill_coverage, category_coverage, experience_level
        )
        
        # Calculate missing skill priority index
        missing_skills_analysis = self.analyze_missing_skills(
            matching_result["unmatched_required_skills"], skill_weights, role_type
        )
        
        return {
            "overall_score": round(total_skill_coverage, 1),
            "readiness_level": readiness_level.value,
            "total_possible_weight": round(total_possible_weight, 2),
            "achieved_weight": round(achieved_weight, 2),
            "skill_scores": skill_scores,
            "category_scores": weighted_category_scores,
            "missing_skills_analysis": missing_skills_analysis,
            "scoring_factors": {
                "role_type": role_type,
                "experience_level": experience_level,
                "total_required_skills": len(required_skills),
                "total_user_skills": len(user_skills),
                "match_distribution": matching_result["match_summary"]
            }
        }
    
    def determine_readiness_level(self, overall_score: float, category_coverage: Dict,
                                experience_level: str) -> ReadinessLevel:
        """
        Determine job readiness level based on scores and coverage.
        
        Args:
            overall_score: Overall skill coverage percentage
            category_coverage: Category-wise coverage data
            experience_level: Required experience level
            
        Returns:
            ReadinessLevel enum
        """
        # Adjust thresholds based on experience level
        if experience_level == "fresher":
            job_ready_threshold = 70
            interview_ready_threshold = 50
        elif experience_level == "junior":
            job_ready_threshold = 75
            interview_ready_threshold = 55
        else:  # mid-level, senior
            job_ready_threshold = 80
            interview_ready_threshold = 60
        
        # Check critical category coverage
        critical_categories = [
            SkillCategory.CORE_PROGRAMMING.value,
            SkillCategory.FRAMEWORKS.value,
            SkillCategory.DATABASES.value
        ]
        
        critical_coverage_good = True
        for cat_name in critical_categories:
            if cat_name in category_coverage:
                if category_coverage[cat_name]["coverage_percentage"] < 40:
                    critical_coverage_good = False
                    break
        
        # Determine level
        if overall_score >= job_ready_threshold and critical_coverage_good:
            return ReadinessLevel.JOB_READY
        elif overall_score >= interview_ready_threshold:
            return ReadinessLevel.INTERVIEW_READY
        else:
            return ReadinessLevel.BEGINNER
    
    def analyze_missing_skills(self, missing_skills: List[str], skill_weights: Dict,
                             role_type: str) -> List[Dict]:
        """
        Analyze missing skills and prioritize them.
        
        Args:
            missing_skills: List of missing required skills
            skill_weights: Dictionary of skill weights
            role_type: Type of role
            
        Returns:
            List of missing skills with priority analysis
        """
        missing_analysis = []
        
        for skill in missing_skills:
            if skill in skill_weights:
                skill_info = skill_weights[skill]
                
                # Determine priority based on weight and importance
                if skill_info["weight"] > 0.8:
                    priority = "High"
                elif skill_info["weight"] > 0.5:
                    priority = "Medium"
                else:
                    priority = "Low"
                
                # Estimate learning difficulty
                categories = skill_taxonomy.classify_skill(skill)
                primary_category = categories[0] if categories else SkillCategory.CORE_PROGRAMMING
                
                if primary_category in [SkillCategory.CORE_PROGRAMMING, SkillCategory.WEB_TECHNOLOGIES]:
                    difficulty = "Medium"
                    estimated_time = "2-4 weeks"
                elif primary_category in [SkillCategory.AI_ML_CORE, SkillCategory.ARCHITECTURE_DESIGN]:
                    difficulty = "Hard"
                    estimated_time = "4-8 weeks"
                else:
                    difficulty = "Easy"
                    estimated_time = "1-2 weeks"
                
                missing_analysis.append({
                    "skill": skill,
                    "priority": priority,
                    "weight": skill_info["weight"],
                    "importance": skill_info["importance"],
                    "category": skill_info["category"],
                    "difficulty": difficulty,
                    "estimated_learning_time": estimated_time,
                    "impact_on_score": round(skill_info["weight"] / sum(sw["weight"] for sw in skill_weights.values()) * 100, 1)
                })
        
        # Sort by priority (weight) descending
        missing_analysis.sort(key=lambda x: x["weight"], reverse=True)
        
        return missing_analysis

# Global instance for easy import
weighted_gap_scorer = WeightedGapScorer()