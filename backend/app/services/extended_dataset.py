"""
Enhanced Dataset Manager with multiple data sources
Includes IT, Business, Creative, and Emerging Tech skills
"""

import json
from pathlib import Path

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

def get_extended_skills():
    """Return all extended skills organized by category"""
    all_skills = []
    for category, skills in EXTENDED_SKILLS_DATASET.items():
        all_skills.extend(skills)
    return sorted(list(set(all_skills)))

def get_extended_roles():
    """Return all extended roles organized by category"""
    all_roles = []
    for category, roles in EXTENDED_ROLES_DATASET.items():
        all_roles.extend(roles)
    return sorted(list(set(all_roles)))

def get_role_requirements(role_name):
    """Get required skills for a specific role"""
    role_name_lower = role_name.lower()
    
    role_skill_mapping = {
        "software engineer": EXTENDED_SKILLS_DATASET["programming_languages"] + 
                            EXTENDED_SKILLS_DATASET["web_technologies"] +
                            EXTENDED_SKILLS_DATASET["devops_tools"][:5] +
                            ["Git", "REST API", "SQL"],
        
        "data scientist": EXTENDED_SKILLS_DATASET["ai_ml_tools"] +
                         EXTENDED_SKILLS_DATASET["data_analytics"] +
                         ["Python", "SQL", "Statistics"],
        
        "cloud architect": EXTENDED_SKILLS_DATASET["cloud_platforms"] +
                          EXTENDED_SKILLS_DATASET["devops_tools"] +
                          ["Kubernetes", "Terraform", "Networking"],
        
        "security engineer": EXTENDED_SKILLS_DATASET["security_skills"] +
                            ["Python", "Networking", "Linux", "Windows"],
        
        "ux designer": EXTENDED_SKILLS_DATASET["creative_skills"] +
                      EXTENDED_SKILLS_DATASET["business_skills"][:3] +
                      ["User Research", "Accessibility"],
        
        "ai engineer": EXTENDED_SKILLS_DATASET["ai_ml_tools"] +
                      EXTENDED_SKILLS_DATASET["programming_languages"][:5] +
                      ["Deep Learning", "Data Engineering"],
    }
    
    # Default skills for any role
    for role, skills in role_skill_mapping.items():
        if role in role_name_lower:
            return skills
    
    # Return generic skills if role not specifically mapped
    return EXTENDED_SKILLS_DATASET["programming_languages"][:5] + \
           EXTENDED_SKILLS_DATASET["soft_skills"][:5]

def get_dataset_summary():
    """Return summary of available datasets"""
    return {
        "total_skills": len(get_extended_skills()),
        "total_roles": len(get_extended_roles()),
        "skill_categories": len(EXTENDED_SKILLS_DATASET),
        "role_categories": len(EXTENDED_ROLES_DATASET),
        "categories": {
            "skills": list(EXTENDED_SKILLS_DATASET.keys()),
            "roles": list(EXTENDED_ROLES_DATASET.keys())
        }
    }
