"""
Skill Gap Analyzer - Step 6: Learning Roadmap Generator
CareerBoost AI - Intelligent Learning Path Creation

This module implements the sixth step of the 8-step skill gap analysis process:
- Automatically generates week-wise learning roadmaps
- Considers skill dependencies and prerequisites
- Provides learning outcomes and project suggestions
- Adapts to user's current skill level and learning pace
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum
from .skill_taxonomy import skill_taxonomy, SkillCategory
from .intelligent_skill_matcher import intelligent_skill_matcher

class LearningDifficulty(Enum):
    """Learning difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class LearningType(Enum):
    """Types of learning activities."""
    THEORY = "theory"
    PRACTICE = "practice"
    PROJECT = "project"
    REVIEW = "review"

class LearningRoadmapGenerator:
    def __init__(self):
        """Initialize the learning roadmap generator."""
        
        # Skill prerequisites and dependencies
        self.skill_prerequisites = {
            # Web Development Path
            "javascript": ["html", "css"],
            "react": ["javascript", "html", "css"],
            "angular": ["javascript", "typescript", "html", "css"],
            "vue": ["javascript", "html", "css"],
            "node.js": ["javascript"],
            "express.js": ["node.js", "javascript"],
            
            # Backend Development
            "django": ["python"],
            "flask": ["python"],
            "fastapi": ["python"],
            "spring boot": ["java"],
            "asp.net core": ["c#"],
            
            # Database
            "postgresql": ["sql"],
            "mysql": ["sql"],
            "mongodb": ["nosql concepts"],
            
            # DevOps
            "kubernetes": ["docker", "containerization"],
            "terraform": ["cloud basics"],
            "ansible": ["linux", "yaml"],
            
            # Data Science
            "pandas": ["python"],
            "numpy": ["python"],
            "matplotlib": ["python", "pandas"],
            "scikit-learn": ["python", "pandas", "numpy"],
            "tensorflow": ["python", "machine learning"],
            "pytorch": ["python", "machine learning"],
            
            # Mobile
            "react native": ["react", "javascript"],
            "flutter": ["dart"],
            "android studio": ["java", "kotlin"],
            
            # Testing
            "selenium": ["programming basics"],
            "jest": ["javascript"],
            "pytest": ["python"],
            "junit": ["java"],
        }
        
        # Learning time estimates (in hours)
        self.learning_time_estimates = {
            # Programming Languages
            "python": {"beginner": 40, "intermediate": 20, "advanced": 10},
            "javascript": {"beginner": 35, "intermediate": 18, "advanced": 8},
            "java": {"beginner": 45, "intermediate": 25, "advanced": 12},
            "c#": {"beginner": 40, "intermediate": 22, "advanced": 10},
            
            # Web Technologies
            "html": {"beginner": 15, "intermediate": 8, "advanced": 4},
            "css": {"beginner": 20, "intermediate": 12, "advanced": 6},
            "react": {"beginner": 30, "intermediate": 20, "advanced": 10},
            "angular": {"beginner": 35, "intermediate": 25, "advanced": 12},
            "vue": {"beginner": 25, "intermediate": 18, "advanced": 8},
            
            # Backend Frameworks
            "django": {"beginner": 25, "intermediate": 15, "advanced": 8},
            "flask": {"beginner": 20, "intermediate": 12, "advanced": 6},
            "node.js": {"beginner": 20, "intermediate": 15, "advanced": 8},
            "express.js": {"beginner": 15, "intermediate": 10, "advanced": 5},
            
            # Databases
            "sql": {"beginner": 25, "intermediate": 15, "advanced": 8},
            "mongodb": {"beginner": 20, "intermediate": 12, "advanced": 6},
            "postgresql": {"beginner": 15, "intermediate": 10, "advanced": 5},
            
            # DevOps & Cloud
            "docker": {"beginner": 20, "intermediate": 15, "advanced": 8},
            "kubernetes": {"beginner": 30, "intermediate": 20, "advanced": 12},
            "aws": {"beginner": 35, "intermediate": 25, "advanced": 15},
            "azure": {"beginner": 35, "intermediate": 25, "advanced": 15},
            
            # Data Science
            "machine learning": {"beginner": 50, "intermediate": 30, "advanced": 20},
            "pandas": {"beginner": 20, "intermediate": 12, "advanced": 6},
            "numpy": {"beginner": 15, "intermediate": 10, "advanced": 5},
            "tensorflow": {"beginner": 40, "intermediate": 25, "advanced": 15},
            "pytorch": {"beginner": 40, "intermediate": 25, "advanced": 15},
        }
        
        # Learning resources and activities
        self.learning_activities = {
            "theory": {
                "description": "Conceptual learning and documentation",
                "time_ratio": 0.3,  # 30% of total time
                "activities": ["Read documentation", "Watch tutorials", "Study concepts"]
            },
            "practice": {
                "description": "Hands-on coding and exercises",
                "time_ratio": 0.5,  # 50% of total time
                "activities": ["Code exercises", "Practice problems", "Mini challenges"]
            },
            "project": {
                "description": "Real-world project implementation",
                "time_ratio": 0.15,  # 15% of total time
                "activities": ["Build project", "Apply concepts", "Create portfolio"]
            },
            "review": {
                "description": "Review and reinforcement",
                "time_ratio": 0.05,  # 5% of total time
                "activities": ["Review notes", "Practice quiz", "Recap concepts"]
            }
        }
        
        # Project suggestions by skill
        self.project_suggestions = {
            "html": ["Personal portfolio website", "Landing page", "Blog template"],
            "css": ["Responsive design", "CSS animations", "Component library"],
            "javascript": ["Interactive calculator", "To-do app", "Weather app"],
            "react": ["Task manager", "E-commerce frontend", "Social media dashboard"],
            "python": ["Web scraper", "Data analyzer", "Automation script"],
            "django": ["Blog platform", "E-commerce site", "API backend"],
            "flask": ["REST API", "Microservice", "Web application"],
            "sql": ["Database design", "Data analysis queries", "Reporting system"],
            "machine learning": ["Prediction model", "Classification system", "Recommendation engine"],
            "docker": ["Containerized app", "Multi-service setup", "CI/CD pipeline"],
            "aws": ["Cloud deployment", "Serverless app", "Infrastructure setup"]
        }
    
    def assess_user_level(self, skill: str, user_skills: List[str]) -> LearningDifficulty:
        """
        Assess user's learning level for a specific skill.
        
        Args:
            skill: Target skill to learn
            user_skills: User's current skills
            
        Returns:
            Learning difficulty level
        """
        skill_lower = skill.lower().strip()
        
        # Check if user has prerequisites
        prerequisites = self.skill_prerequisites.get(skill_lower, [])
        met_prerequisites = 0
        
        for prereq in prerequisites:
            for user_skill in user_skills:
                if intelligent_skill_matcher.calculate_similarity(user_skill, prereq) > 0.8:
                    met_prerequisites += 1
                    break
        
        if not prerequisites:
            # No prerequisites defined, check related skills
            related_count = 0
            for user_skill in user_skills:
                similarity = intelligent_skill_matcher.calculate_similarity(user_skill, skill)
                if similarity > 0.3:
                    related_count += 1
            
            if related_count >= 3:
                return LearningDifficulty.INTERMEDIATE
            elif related_count >= 1:
                return LearningDifficulty.BEGINNER
            else:
                return LearningDifficulty.BEGINNER
        
        # Calculate prerequisite fulfillment ratio
        fulfillment_ratio = met_prerequisites / len(prerequisites) if prerequisites else 0
        
        if fulfillment_ratio >= 0.8:
            return LearningDifficulty.BEGINNER  # Easy to learn with good foundation
        elif fulfillment_ratio >= 0.5:
            return LearningDifficulty.INTERMEDIATE
        else:
            return LearningDifficulty.ADVANCED  # Hard without prerequisites
    
    def estimate_learning_time(self, skill: str, difficulty: LearningDifficulty) -> int:
        """
        Estimate learning time for a skill based on difficulty.
        
        Args:
            skill: Skill name
            difficulty: Learning difficulty level
            
        Returns:
            Estimated learning time in hours
        """
        skill_lower = skill.lower().strip()
        
        if skill_lower in self.learning_time_estimates:
            return self.learning_time_estimates[skill_lower][difficulty.value]
        
        # Default estimates based on skill category
        categories = skill_taxonomy.classify_skill(skill)
        primary_category = categories[0] if categories else SkillCategory.CORE_PROGRAMMING
        
        default_times = {
            SkillCategory.CORE_PROGRAMMING: {"beginner": 40, "intermediate": 25, "advanced": 15},
            SkillCategory.FRAMEWORKS: {"beginner": 25, "intermediate": 18, "advanced": 10},
            SkillCategory.DATABASES: {"beginner": 20, "intermediate": 15, "advanced": 8},
            SkillCategory.WEB_TECHNOLOGIES: {"beginner": 15, "intermediate": 10, "advanced": 6},
            SkillCategory.AI_ML_CORE: {"beginner": 50, "intermediate": 35, "advanced": 25},
            SkillCategory.DEVOPS_CLOUD: {"beginner": 30, "intermediate": 20, "advanced": 12},
            SkillCategory.SOFT_COGNITIVE: {"beginner": 10, "intermediate": 8, "advanced": 5}
        }
        
        category_times = default_times.get(primary_category, default_times[SkillCategory.CORE_PROGRAMMING])
        return category_times[difficulty.value]
    
    def create_weekly_plan(self, skill: str, total_hours: int, difficulty: LearningDifficulty) -> List[Dict]:
        """
        Create a weekly learning plan for a skill.
        
        Args:
            skill: Skill to learn
            total_hours: Total estimated learning hours
            difficulty: Learning difficulty level
            
        Returns:
            List of weekly learning activities
        """
        # Assume 10 hours per week study time
        hours_per_week = 10
        total_weeks = max(1, (total_hours + hours_per_week - 1) // hours_per_week)  # Ceiling division
        
        weekly_plan = []
        remaining_hours = total_hours
        
        for week in range(1, total_weeks + 1):
            week_hours = min(hours_per_week, remaining_hours)
            
            # Distribute time across activity types
            theory_hours = int(week_hours * self.learning_activities["theory"]["time_ratio"])
            practice_hours = int(week_hours * self.learning_activities["practice"]["time_ratio"])
            project_hours = int(week_hours * self.learning_activities["project"]["time_ratio"])
            review_hours = week_hours - theory_hours - practice_hours - project_hours
            
            # Adjust focus based on week and difficulty
            if week == 1:
                # First week: more theory
                theory_hours = int(week_hours * 0.5)
                practice_hours = int(week_hours * 0.4)
                project_hours = int(week_hours * 0.1)
            elif week == total_weeks and total_weeks > 1:
                # Last week: more project work
                theory_hours = int(week_hours * 0.2)
                practice_hours = int(week_hours * 0.3)
                project_hours = int(week_hours * 0.4)
                review_hours = week_hours - theory_hours - practice_hours - project_hours
            
            # Create week activities
            activities = []
            
            if theory_hours > 0:
                activities.append({
                    "type": "theory",
                    "hours": theory_hours,
                    "description": f"Study {skill} fundamentals and concepts",
                    "tasks": [
                        f"Read {skill} documentation",
                        f"Watch {skill} tutorial videos",
                        f"Understand {skill} core concepts"
                    ]
                })
            
            if practice_hours > 0:
                activities.append({
                    "type": "practice",
                    "hours": practice_hours,
                    "description": f"Hands-on {skill} coding practice",
                    "tasks": [
                        f"Complete {skill} exercises",
                        f"Solve {skill} coding challenges",
                        f"Practice {skill} syntax and patterns"
                    ]
                })
            
            if project_hours > 0:
                project_suggestions = self.project_suggestions.get(skill.lower(), 
                                                                 [f"Build a {skill} project"])
                activities.append({
                    "type": "project",
                    "hours": project_hours,
                    "description": f"Build a {skill} project",
                    "tasks": [
                        f"Plan {project_suggestions[0] if project_suggestions else 'project'}",
                        f"Implement core features using {skill}",
                        f"Test and refine the project"
                    ]
                })
            
            if review_hours > 0:
                activities.append({
                    "type": "review",
                    "hours": review_hours,
                    "description": f"Review and reinforce {skill} knowledge",
                    "tasks": [
                        f"Review {skill} notes and concepts",
                        f"Practice {skill} quick exercises",
                        f"Identify areas for improvement"
                    ]
                })
            
            weekly_plan.append({
                "week": week,
                "total_hours": week_hours,
                "focus": f"Week {week}: {skill} Learning",
                "learning_outcome": self.get_week_outcome(skill, week, total_weeks, difficulty),
                "activities": activities
            })
            
            remaining_hours -= week_hours
        
        return weekly_plan
    
    def get_week_outcome(self, skill: str, week: int, total_weeks: int, 
                        difficulty: LearningDifficulty) -> str:
        """
        Get expected learning outcome for a specific week.
        
        Args:
            skill: Skill being learned
            week: Current week number
            total_weeks: Total weeks in plan
            difficulty: Learning difficulty
            
        Returns:
            Expected learning outcome description
        """
        if week == 1:
            return f"Understand {skill} basics and setup development environment"
        elif week == total_weeks and total_weeks > 1:
            return f"Complete a {skill} project and demonstrate proficiency"
        elif week <= total_weeks // 2:
            return f"Master {skill} fundamentals and core concepts"
        else:
            return f"Apply {skill} in practical scenarios and build confidence"
    
    def generate_comprehensive_roadmap(self, missing_skills: List[str], user_skills: List[str],
                                     target_completion_weeks: int = 12) -> Dict:
        """
        Generate a comprehensive learning roadmap for multiple skills.
        
        Args:
            missing_skills: List of skills to learn
            user_skills: User's current skills
            target_completion_weeks: Target weeks to complete all skills
            
        Returns:
            Comprehensive learning roadmap
        """
        # Assess each skill and estimate time
        skill_assessments = []
        total_estimated_hours = 0
        
        for skill in missing_skills:
            difficulty = self.assess_user_level(skill, user_skills)
            estimated_hours = self.estimate_learning_time(skill, difficulty)
            
            skill_assessments.append({
                "skill": skill,
                "difficulty": difficulty.value,
                "estimated_hours": estimated_hours,
                "prerequisites": self.skill_prerequisites.get(skill.lower(), []),
                "projects": self.project_suggestions.get(skill.lower(), [f"{skill} project"])
            })
            
            total_estimated_hours += estimated_hours
        
        # Sort skills by prerequisites and difficulty
        sorted_skills = self.sort_skills_by_dependencies(skill_assessments, user_skills)
        
        # Create timeline
        roadmap_weeks = []
        current_week = 1
        
        for skill_info in sorted_skills:
            skill = skill_info["skill"]
            difficulty = LearningDifficulty(skill_info["difficulty"])
            hours = skill_info["estimated_hours"]
            
            # Create weekly plan for this skill
            skill_plan = self.create_weekly_plan(skill, hours, difficulty)
            
            # Add to roadmap with adjusted week numbers
            for week_plan in skill_plan:
                week_plan["absolute_week"] = current_week
                week_plan["skill"] = skill
                roadmap_weeks.append(week_plan)
                current_week += 1
        
        # Optimize timeline if it exceeds target
        if current_week - 1 > target_completion_weeks:
            roadmap_weeks = self.optimize_timeline(roadmap_weeks, target_completion_weeks)
        
        # Generate milestones
        milestones = self.generate_milestones(roadmap_weeks, sorted_skills)
        
        return {
            "total_skills": len(missing_skills),
            "total_estimated_hours": total_estimated_hours,
            "total_weeks": len(roadmap_weeks),
            "target_weeks": target_completion_weeks,
            "skill_assessments": skill_assessments,
            "learning_path": sorted_skills,
            "weekly_roadmap": roadmap_weeks,
            "milestones": milestones,
            "completion_date": (datetime.now() + timedelta(weeks=len(roadmap_weeks))).strftime("%Y-%m-%d"),
            "study_schedule": {
                "hours_per_week": 10,
                "recommended_pace": "Consistent daily practice",
                "flexibility": "Adjust based on your availability"
            }
        }
    
    def sort_skills_by_dependencies(self, skill_assessments: List[Dict], user_skills: List[str]) -> List[Dict]:
        """
        Sort skills based on prerequisites and dependencies.
        
        Args:
            skill_assessments: List of skill assessment data
            user_skills: User's current skills
            
        Returns:
            Sorted list of skills to learn in order
        """
        sorted_skills = []
        remaining_skills = skill_assessments.copy()
        learned_skills = set(skill.lower() for skill in user_skills)
        
        while remaining_skills:
            # Find skills with satisfied prerequisites
            ready_skills = []
            
            for skill_info in remaining_skills:
                skill = skill_info["skill"]
                prerequisites = self.skill_prerequisites.get(skill.lower(), [])
                
                # Check if all prerequisites are satisfied
                prerequisites_met = all(
                    any(intelligent_skill_matcher.calculate_similarity(learned, prereq) > 0.8 
                        for learned in learned_skills)
                    for prereq in prerequisites
                )
                
                if prerequisites_met:
                    ready_skills.append(skill_info)
            
            if not ready_skills:
                # If no skills are ready, take the one with fewest unmet prerequisites
                ready_skills = [min(remaining_skills, 
                                  key=lambda x: len(self.skill_prerequisites.get(x["skill"].lower(), [])))]
            
            # Sort ready skills by difficulty (easier first)
            difficulty_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
            ready_skills.sort(key=lambda x: difficulty_order[x["difficulty"]])
            
            # Add the first ready skill to sorted list
            next_skill = ready_skills[0]
            sorted_skills.append(next_skill)
            remaining_skills.remove(next_skill)
            learned_skills.add(next_skill["skill"].lower())
        
        return sorted_skills
    
    def optimize_timeline(self, roadmap_weeks: List[Dict], target_weeks: int) -> List[Dict]:
        """
        Optimize timeline to fit target completion weeks.
        
        Args:
            roadmap_weeks: Original weekly roadmap
            target_weeks: Target number of weeks
            
        Returns:
            Optimized weekly roadmap
        """
        if len(roadmap_weeks) <= target_weeks:
            return roadmap_weeks
        
        # Combine weeks or increase hours per week
        compression_ratio = len(roadmap_weeks) / target_weeks
        optimized_weeks = []
        
        current_week = 1
        i = 0
        
        while i < len(roadmap_weeks) and current_week <= target_weeks:
            # Combine multiple weeks if needed
            weeks_to_combine = min(int(compression_ratio), len(roadmap_weeks) - i)
            combined_week = {
                "week": current_week,
                "absolute_week": current_week,
                "total_hours": 0,
                "focus": "",
                "learning_outcome": "",
                "activities": [],
                "skills": []
            }
            
            for j in range(weeks_to_combine):
                if i + j < len(roadmap_weeks):
                    week_data = roadmap_weeks[i + j]
                    combined_week["total_hours"] += week_data["total_hours"]
                    combined_week["activities"].extend(week_data["activities"])
                    combined_week["skills"].append(week_data["skill"])
            
            # Update focus and outcome
            unique_skills = list(set(combined_week["skills"]))
            if len(unique_skills) == 1:
                combined_week["focus"] = f"Week {current_week}: {unique_skills[0]} Intensive"
                combined_week["learning_outcome"] = f"Master {unique_skills[0]} through intensive study"
            else:
                combined_week["focus"] = f"Week {current_week}: Multi-skill Learning"
                combined_week["learning_outcome"] = f"Progress in {', '.join(unique_skills)}"
            
            optimized_weeks.append(combined_week)
            i += weeks_to_combine
            current_week += 1
        
        return optimized_weeks
    
    def generate_milestones(self, roadmap_weeks: List[Dict], sorted_skills: List[Dict]) -> List[Dict]:
        """
        Generate learning milestones throughout the roadmap.
        
        Args:
            roadmap_weeks: Weekly roadmap
            sorted_skills: Sorted skills learning path
            
        Returns:
            List of milestone achievements
        """
        milestones = []
        
        # Skill completion milestones
        for i, skill_info in enumerate(sorted_skills):
            milestone_week = sum(
                len(self.create_weekly_plan(
                    s["skill"], 
                    s["estimated_hours"], 
                    LearningDifficulty(s["difficulty"])
                ))
                for s in sorted_skills[:i+1]
            )
            
            milestones.append({
                "week": milestone_week,
                "type": "skill_completion",
                "title": f"{skill_info['skill']} Mastery",
                "description": f"Complete learning {skill_info['skill']} with {skill_info['difficulty']} difficulty",
                "achievement": f"Can build projects using {skill_info['skill']}",
                "celebration": f"🎉 You've mastered {skill_info['skill']}!"
            })
        
        # Progress milestones (25%, 50%, 75%)
        total_weeks = len(roadmap_weeks)
        for percentage in [25, 50, 75]:
            milestone_week = int(total_weeks * percentage / 100)
            if milestone_week > 0:
                milestones.append({
                    "week": milestone_week,
                    "type": "progress",
                    "title": f"{percentage}% Complete",
                    "description": f"Reached {percentage}% of your learning journey",
                    "achievement": f"Consistent progress in skill development",
                    "celebration": f"🚀 {percentage}% of the way there!"
                })
        
        # Final completion milestone
        milestones.append({
            "week": total_weeks,
            "type": "completion",
            "title": "Learning Journey Complete",
            "description": "Successfully completed all planned skills",
            "achievement": "Ready for job applications and interviews",
            "celebration": "🏆 Congratulations! You're job-ready!"
        })
        
        return sorted(milestones, key=lambda x: x["week"])

# Global instance for easy import
learning_roadmap_generator = LearningRoadmapGenerator()