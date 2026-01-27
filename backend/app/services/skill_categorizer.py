"""
Skill Categorizer - Groups skills into categories for better UX
"""

from typing import List, Dict
from collections import defaultdict
from .extended_dataset import get_extended_skills

# Skill category mappings
SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "rust", "kotlin",
        "swift", "objective-c", "r", "matlab", "scala", "clojure", "haskell", "typescript",
        "vb.net", "groovy", "lua", "perl", "bash", "powershell", "sql", "solidity"
    ],
    "Web Technologies": [
        "react", "angular", "vue.js", "node.js", "express.js", "django", "flask", "fastapi",
        "spring boot", "asp.net", "laravel", "wordpress", "html5", "css3", "sass", "bootstrap",
        "tailwind css", "next.js", "nuxt.js", "svelte", "ember.js", "backbone.js", "jquery",
        "webassembly", "progressive web apps", "rest api", "graphql"
    ],
    "Databases": [
        "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "oracle",
        "sql server", "dynamodb", "firestore", "firebase", "memcached", "neo4j", "cosmos db",
        "couchdb", "mariadb", "sqlite", "hadoop", "hive", "hbase", "snowflake", "bigquery",
        "apache spark", "azure data lake", "google cloud datastore"
    ],
    "Cloud Platforms": [
        "aws", "azure", "google cloud platform", "heroku", "digitalocean", "linode",
        "aws lambda", "azure functions", "google cloud functions", "aws ec2", "aws s3",
        "azure vm", "kubernetes", "docker", "openstack", "alibaba cloud"
    ],
    "DevOps Tools": [
        "docker", "kubernetes", "jenkins", "gitlab ci/cd", "github actions", "circleci",
        "travis ci", "terraform", "ansible", "chef", "puppet", "vagrant", "git", "svn",
        "prometheus", "grafana", "elk stack", "datadog", "new relic", "splunk",
        "aws codepipeline", "azure devops", "cloudformation"
    ],
    "Machine Learning": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm", "catboost",
        "pandas", "numpy", "matplotlib", "seaborn", "plotly", "opencv", "nltk", "spacy",
        "hugging face", "jax", "mxnet", "onnx", "mlflow", "weights & biases",
        "deep learning", "machine learning", "natural language processing", "computer vision",
        "reinforcement learning", "feature engineering", "data preprocessing"
    ],
    "Big Data": [
        "apache spark", "apache hadoop", "hive", "pig", "hbase", "storm", "kafka",
        "apache flink", "apache druid", "presto", "trino", "drill", "pyspark", "scala",
        "data warehouse", "etl", "data lake", "data pipeline"
    ],
    "Security": [
        "owasp", "penetration testing", "network security", "cryptography", "ssl/tls",
        "firewalls", "intrusion detection", "vulnerability assessment", "security compliance",
        "gdpr", "hipaa", "pci-dss", "soc 2", "iso 27001", "two-factor authentication",
        "identity management", "access control", "security audit", "threat modeling",
        "incident response", "ethical hacking", "malware analysis"
    ],
    "Mobile Development": [
        "react native", "flutter", "xamarin", "swift", "kotlin", "android development",
        "ios development", "cross-platform development", "mobile ui/ux", "firebase",
        "cordova", "ionic", "nativescript", "pwa"
    ],
    "Business Skills": [
        "project management", "agile", "scrum", "kanban", "leadership", "communication",
        "business analysis", "data analysis", "strategic planning", "stakeholder management",
        "change management", "risk management", "budget management", "roi analysis",
        "product management", "market research", "customer relations"
    ],
    "Creative Skills": [
        "ui design", "ux design", "graphic design", "web design", "mobile design",
        "wireframing", "prototyping", "design thinking", "figma", "adobe xd", "sketch",
        "adobe photoshop", "adobe illustrator", "adobe creative suite", "canva",
        "animation", "motion graphics", "video editing", "3d modeling", "blender"
    ],
    "Data Analytics": [
        "data analysis", "business intelligence", "data visualization", "tableau", "power bi",
        "google analytics", "excel", "sql", "python", "r", "statistics", "a/b testing",
        "dashboard creation", "report generation", "predictive analytics"
    ],
    "Emerging Technologies": [
        "blockchain", "cryptocurrency", "web3", "nfts", "smart contracts", "defi",
        "ethereum", "solana", "metaverse", "augmented reality", "virtual reality",
        "internet of things (iot)", "edge computing", "5g", "quantum computing",
        "artificial intelligence", "generative ai", "chatgpt", "llms"
    ],
    "Soft Skills": [
        "communication", "teamwork", "problem solving", "critical thinking", "creativity",
        "adaptability", "time management", "organization", "attention to detail",
        "work ethic", "reliability", "self-motivation", "continuous learning",
        "empathy", "conflict resolution", "negotiation", "presentation skills"
    ],
    "Other": []  # Catch-all for unmatched skills
}

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Group skills into categories"""
    categorized = defaultdict(list)
    unmatched = []
    
    skills_lower_map = {s.lower(): s for s in skills}
    
    for category, keywords in SKILL_CATEGORIES.items():
        for keyword in keywords:
            if keyword in skills_lower_map:
                skill_name = skills_lower_map[keyword]
                if skill_name not in categorized[category]:
                    categorized[category].append(skill_name)
    
    # Find unmatched skills
    matched = set()
    for skills_list in categorized.values():
        matched.update(skills_list)
    
    for skill in skills:
        if skill not in matched:
            # Try fuzzy matching
            skill_lower = skill.lower()
            matched_category = None
            for category, keywords in SKILL_CATEGORIES.items():
                for keyword in keywords:
                    if keyword in skill_lower or skill_lower in keyword:
                        matched_category = category
                        break
                if matched_category:
                    break
            
            if matched_category:
                categorized[matched_category].append(skill)
            else:
                unmatched.append(skill)
    
    if unmatched:
        categorized["Other"].extend(unmatched)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}

def get_star_rating(match_percentage: float) -> int:
    """Convert match percentage to star rating (1-5)"""
    if match_percentage >= 90:
        return 5
    elif match_percentage >= 75:
        return 4
    elif match_percentage >= 60:
        return 3
    elif match_percentage >= 45:
        return 2
    else:
        return 1
