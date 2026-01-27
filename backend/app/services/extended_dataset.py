"""
Dataset access layer.

This project supports TWO sources of dataset data:
- MongoDB collections created by `backend/scripts/init_dataset.py`:
  - dataset_skills
  - dataset_roles
- A built-in "extended" fallback dataset (hardcoded below) used when MongoDB
  is not initialized yet.

All API routes should call the functions in this module so the app automatically
uses the real Kaggle dataset when available.
"""

from typing import Any, Dict, List, Optional

from ..core.database import get_collection

EXTENDED_SKILLS_DATASET = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "C++", "C#", "PHP", "Ruby", "Go", "Rust", "Kotlin",
        "Swift", "Objective-C", "R", "MATLAB", "Scala", "Clojure", "Haskell", "TypeScript",
        "VB.NET", "Groovy", "Lua", "Perl", "Bash", "PowerShell", "SQL", "Solidity"
    ],
    "web_technologies": [
        "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask", "FastAPI",
        "Spring Boot", "ASP.NET", "Laravel", "WordPress", "HTML5", "CSS3", "SASS", "Bootstrap",
        "Tailwind CSS", "Next.js", "Nuxt.js", "Svelte", "Ember.js", "Backbone.js", "jQuery",
        "WebAssembly", "Progressive Web Apps", "REST API", "GraphQL"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Oracle",
        "SQL Server", "DynamoDB", "Firestore", "Firebase", "Memcached", "Neo4j", "Cosmos DB",
        "CouchDB", "MariaDB", "SQLite", "Hadoop", "Hive", "HBase", "Snowflake", "BigQuery",
        "Apache Spark", "Azure Data Lake", "Google Cloud Datastore"
    ],
    "cloud_platforms": [
        "AWS", "Azure", "Google Cloud Platform", "Heroku", "DigitalOcean", "Linode",
        "AWS Lambda", "Azure Functions", "Google Cloud Functions", "AWS EC2", "AWS S3",
        "Azure VM", "Kubernetes", "Docker", "OpenStack", "Alibaba Cloud"
    ],
    "devops_tools": [
        "Docker", "Kubernetes", "Jenkins", "GitLab CI/CD", "GitHub Actions", "CircleCI",
        "Travis CI", "Terraform", "Ansible", "Chef", "Puppet", "Vagrant", "Git", "SVN",
        "Prometheus", "Grafana", "ELK Stack", "Datadog", "New Relic", "Splunk",
        "AWS CodePipeline", "Azure DevOps", "CloudFormation"
    ],
    "ai_ml_tools": [
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "XGBoost", "LightGBM", "CatBoost",
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly", "OpenCV", "NLTK", "spaCy",
        "Hugging Face", "JAX", "MXNet", "ONNX", "MLflow", "Weights & Biases",
        "Deep Learning", "Machine Learning", "Natural Language Processing", "Computer Vision",
        "Reinforcement Learning", "Feature Engineering", "Data Preprocessing"
    ],
    "big_data": [
        "Apache Spark", "Apache Hadoop", "Hive", "Pig", "HBase", "Storm", "Kafka",
        "Apache Flink", "Apache Druid", "Presto", "Trino", "Drill", "PySpark", "Scala",
        "Data Warehouse", "ETL", "Data Lake", "Data Pipeline"
    ],
    "security_skills": [
        "OWASP", "Penetration Testing", "Network Security", "Cryptography", "SSL/TLS",
        "Firewalls", "Intrusion Detection", "Vulnerability Assessment", "Security Compliance",
        "GDPR", "HIPAA", "PCI-DSS", "SOC 2", "ISO 27001", "Two-Factor Authentication",
        "Identity Management", "Access Control", "Security Audit", "Threat Modeling",
        "Incident Response", "Ethical Hacking", "Malware Analysis"
    ],
    "mobile_development": [
        "React Native", "Flutter", "Xamarin", "Swift", "Kotlin", "Android Development",
        "iOS Development", "Cross-platform Development", "Mobile UI/UX", "Firebase",
        "Cordova", "Ionic", "NativeScript", "PWA"
    ],
    "business_skills": [
        "Project Management", "Agile", "Scrum", "Kanban", "Leadership", "Communication",
        "Business Analysis", "Data Analysis", "Strategic Planning", "Stakeholder Management",
        "Change Management", "Risk Management", "Budget Management", "ROI Analysis",
        "Product Management", "Market Research", "Customer Relations"
    ],
    "creative_skills": [
        "UI Design", "UX Design", "Graphic Design", "Web Design", "Mobile Design",
        "Wireframing", "Prototyping", "Design Thinking", "Figma", "Adobe XD", "Sketch",
        "Adobe Photoshop", "Adobe Illustrator", "Adobe Creative Suite", "Canva",
        "Animation", "Motion Graphics", "Video Editing", "3D Modeling", "Blender"
    ],
    "data_analytics": [
        "Data Analysis", "Business Intelligence", "Data Visualization", "Tableau", "Power BI",
        "Google Analytics", "Excel", "SQL", "Python", "R", "Statistics", "A/B Testing",
        "Dashboard Creation", "Report Generation", "Predictive Analytics"
    ],
    "emerging_technologies": [
        "Blockchain", "Cryptocurrency", "Web3", "NFTs", "Smart Contracts", "DeFi",
        "Ethereum", "Solana", "Metaverse", "Augmented Reality", "Virtual Reality",
        "Internet of Things (IoT)", "Edge Computing", "5G", "Quantum Computing",
        "Artificial Intelligence", "Generative AI", "ChatGPT", "LLMs"
    ],
    "soft_skills": [
        "Communication", "Teamwork", "Problem Solving", "Critical Thinking", "Creativity",
        "Adaptability", "Time Management", "Organization", "Attention to Detail",
        "Work Ethic", "Reliability", "Self-Motivation", "Continuous Learning",
        "Empathy", "Conflict Resolution", "Negotiation", "Presentation Skills"
    ]
}

EXTENDED_ROLES_DATASET = {
    "software_development": [
        "Software Engineer", "Senior Software Engineer", "Full-stack Developer", "Backend Developer",
        "Frontend Developer", "iOS Developer", "Android Developer", "Mobile Developer",
        "React Developer", "Angular Developer", "Vue.js Developer", "Python Developer",
        "Java Developer", "C++ Developer", "Go Developer", "Rust Developer", "DevOps Engineer",
        "Solutions Architect", "Tech Lead", "Engineering Manager", "Staff Engineer"
    ],
    "data_science": [
        "Data Scientist", "Senior Data Scientist", "ML Engineer", "Machine Learning Engineer",
        "Deep Learning Engineer", "NLP Engineer", "Computer Vision Engineer", "Data Analyst",
        "Business Analyst", "BI Developer", "Analytics Engineer", "Data Engineer",
        "Big Data Engineer", "Analytics Manager"
    ],
    "cloud_infrastructure": [
        "Cloud Architect", "AWS Solutions Architect", "Azure Solutions Architect", "GCP Architect",
        "Cloud Engineer", "Cloud Security Engineer", "Infrastructure Engineer", "Systems Administrator",
        "Network Engineer", "Cloud Operations Engineer", "SRE (Site Reliability Engineer)"
    ],
    "security": [
        "Security Engineer", "Cybersecurity Specialist", "Security Architect", "Penetration Tester",
        "Information Security Analyst", "Security Operations Center (SOC) Analyst", "CISO",
        "Compliance Officer", "Threat Intelligence Analyst", "Security Consultant"
    ],
    "product_management": [
        "Product Manager", "Senior Product Manager", "Product Owner", "Technical Product Manager",
        "Interim Product Manager", "Associate Product Manager", "Product Strategist"
    ],
    "ux_design": [
        "UX Designer", "UI Designer", "UX/UI Designer", "Interaction Designer", "User Researcher",
        "Information Architect", "Design System Manager", "Design Lead", "Head of Design"
    ],
    "quality_assurance": [
        "QA Engineer", "Software Test Engineer", "Automation Test Engineer", "QA Lead",
        "Test Manager", "Performance Test Engineer", "Mobile QA Engineer"
    ],
    "emerging_roles": [
        "AI Engineer", "ML Ops Engineer", "Data Privacy Officer", "Blockchain Developer",
        "Web3 Developer", "Metaverse Developer", "AR/VR Developer", "Quantum Developer",
        "IoT Engineer", "Edge Computing Engineer", "LLM Engineer", "Prompt Engineer"
    ]
}

def _safe_list(col) -> List[dict]:
    try:
        return list(col.find({}))
    except Exception:
        return []

def get_dataset_skills() -> List[str]:
    """
    Return dataset skills.
    Prefers MongoDB (`dataset_skills`) if initialized; otherwise uses fallback list.
    """
    try:
        col = get_collection("dataset_skills")
        docs = _safe_list(col)
        skills = [d.get("skill") for d in docs if d.get("skill")]
        if skills:
            # Keep original casing from DB, but stable sort for UI
            return sorted(list({s.strip() for s in skills if str(s).strip()}), key=lambda x: x.lower())
    except Exception:
        pass

    # fallback
    all_skills: List[str] = []
    for _, skills in EXTENDED_SKILLS_DATASET.items():
        all_skills.extend(skills)
    return sorted(list(set(all_skills)), key=lambda x: x.lower())

def get_dataset_roles() -> List[Dict[str, Any]]:
    """
    Return dataset roles.
    Prefers MongoDB (`dataset_roles`) if initialized; otherwise uses fallback roles.

    MongoDB format:
      {_id: "<title>_<level>", title: "...", level: "...", skills: [...]}
    """
    try:
        col = get_collection("dataset_roles")
        docs = _safe_list(col)
        roles: List[Dict[str, Any]] = []
        for d in docs:
            roles.append(
                {
                    "id": str(d.get("_id")),
                    "title": d.get("title"),
                    "level": d.get("level"),
                }
            )
        # If mongo has data, return it
        if any(r.get("title") for r in roles):
            roles = [r for r in roles if r.get("title")]
            return sorted(roles, key=lambda r: (str(r.get("title")).lower(), str(r.get("level") or "").lower()))
    except Exception:
        pass

    # fallback: flatten the built-in list
    all_roles: List[str] = []
    for _, roles in EXTENDED_ROLES_DATASET.items():
        all_roles.extend(roles)
    return [{"id": r.lower().replace(" ", "_"), "title": r, "level": "unknown"} for r in sorted(list(set(all_roles)), key=lambda x: x.lower())]

def get_role_requirements(role_ref: str) -> List[str]:
    """
    Get required skills for a role.

    `role_ref` can be:
    - a MongoDB role document id (preferred): "<title>_<level>"
    - a role title (fallback)
    """
    # 1) Try Mongo by _id
    try:
        col = get_collection("dataset_roles")
        doc = col.find_one({"_id": role_ref})
        if doc and doc.get("skills"):
            return [s for s in doc.get("skills", []) if s]
    except Exception:
        pass

    # 2) Try Mongo by title
    try:
        col = get_collection("dataset_roles")
        doc = col.find_one({"title": {"$regex": f"^{role_ref}$", "$options": "i"}})
        if doc and doc.get("skills"):
            return [s for s in doc.get("skills", []) if s]
    except Exception:
        pass

    # 3) Fallback mapping (built-in)
    role_name_lower = (role_ref or "").lower()

    role_skill_mapping = {
        "software engineer": EXTENDED_SKILLS_DATASET["programming_languages"]
        + EXTENDED_SKILLS_DATASET["web_technologies"]
        + EXTENDED_SKILLS_DATASET["devops_tools"][:5]
        + ["Git", "REST API", "SQL"],
        "data scientist": EXTENDED_SKILLS_DATASET["ai_ml_tools"]
        + EXTENDED_SKILLS_DATASET["data_analytics"]
        + ["Python", "SQL", "Statistics"],
        "cloud architect": EXTENDED_SKILLS_DATASET["cloud_platforms"]
        + EXTENDED_SKILLS_DATASET["devops_tools"]
        + ["Kubernetes", "Terraform", "Networking"],
        "security engineer": EXTENDED_SKILLS_DATASET["security_skills"] + ["Python", "Networking", "Linux", "Windows"],
        "ux designer": EXTENDED_SKILLS_DATASET["creative_skills"] + EXTENDED_SKILLS_DATASET["business_skills"][:3] + ["User Research", "Accessibility"],
        "ai engineer": EXTENDED_SKILLS_DATASET["ai_ml_tools"] + EXTENDED_SKILLS_DATASET["programming_languages"][:5] + ["Deep Learning", "Data Engineering"],
    }

    for role, skills in role_skill_mapping.items():
        if role in role_name_lower:
            return skills

    return EXTENDED_SKILLS_DATASET["programming_languages"][:5] + EXTENDED_SKILLS_DATASET["soft_skills"][:5]

def get_dataset_summary():
    """Return summary; prefers MongoDB stats if available."""
    # Prefer dataset_stats collection if present
    try:
        stats_col = get_collection("ml_models")  # not ideal; keep backward compatibility
    except Exception:
        stats_col = None

    try:
        # init_dataset stores stats in `dataset_stats` directly (not in COLLECTIONS)
        db = get_collection("users").database  # reuse existing connection
        stats_doc = db["dataset_stats"].find_one({"_id": "main"})
        if stats_doc:
            return {
                "source": "mongodb",
                "total_skills": stats_doc.get("total_skills"),
                "total_roles": stats_doc.get("total_roles"),
                "common_skills": stats_doc.get("common_skills", [])[:20],
                "roles_by_level": stats_doc.get("roles_by_level", {}),
            }
    except Exception:
        pass

    # fallback summary
    return {
        "source": "fallback",
        "total_skills": len(get_dataset_skills()),
        "total_roles": len(get_dataset_roles()),
        "skill_categories": len(EXTENDED_SKILLS_DATASET),
        "role_categories": len(EXTENDED_ROLES_DATASET),
        "categories": {"skills": list(EXTENDED_SKILLS_DATASET.keys()), "roles": list(EXTENDED_ROLES_DATASET.keys())},
    }

# Backwards-compatible names used throughout the repo
def get_extended_skills() -> List[str]:
    return get_dataset_skills()

def get_extended_roles():
    # Old code expects List[str]; keep for compatibility but prefer the new structured list in API.
    roles = get_dataset_roles()
    return [r["title"] for r in roles if r.get("title")]
