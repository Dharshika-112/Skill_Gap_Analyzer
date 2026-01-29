"""
Setup script for CareerBoost AI Roles Database
Creates skillgap database with roles collection and default data
"""

from pymongo import MongoClient
from datetime import datetime
import json

# MongoDB Configuration
MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "skillgap"

def setup_roles_database():
    """Setup the complete roles database"""
    print("🚀 Setting up CareerBoost AI Roles Database")
    print("=" * 60)
    
    # Connect to MongoDB
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Create collections
    roles_collection = db['roles']
    admin_collection = db['admin_users']
    
    print(f"✅ Connected to MongoDB: {MONGODB_URL}")
    print(f"📊 Database: {DATABASE_NAME}")
    
    # Clear existing data
    roles_collection.delete_many({})
    admin_collection.delete_many({})
    print("🗑️  Cleared existing data")
    
    # Default role data (10 important roles)
    default_roles = [
        {
            "roleId": "frontend-developer",
            "title": "Frontend Developer",
            "cardSubtitle": "Build user interfaces with React, Vue, Angular",
            "isActive": True,
            "order": 1,
            "overview": "Frontend developers create the visual and interactive elements of websites and web applications that users interact with directly. They work with HTML, CSS, JavaScript, and modern frameworks to build responsive, user-friendly interfaces.",
            "responsibilities": [
                "Develop responsive web applications using modern frameworks",
                "Collaborate with UI/UX designers to implement designs",
                "Optimize applications for maximum speed and scalability",
                "Ensure cross-browser compatibility and mobile responsiveness",
                "Write clean, maintainable, and well-documented code",
                "Participate in code reviews and team meetings"
            ],
            "mustHaveSkills": [
                "HTML5", "CSS3", "JavaScript (ES6+)", "React.js", "Git", 
                "Responsive Design", "REST APIs", "npm/yarn"
            ],
            "goodToHaveSkills": [
                "TypeScript", "Vue.js", "Angular", "Sass/SCSS", "Webpack", 
                "Testing (Jest, Cypress)", "GraphQL", "Progressive Web Apps"
            ],
            "tools": [
                "VS Code", "Chrome DevTools", "Figma", "Postman", 
                "GitHub", "Netlify/Vercel", "ESLint", "Prettier"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "backend-developer",
            "title": "Backend Developer",
            "cardSubtitle": "Build server-side logic with Node.js, Python, Java",
            "isActive": True,
            "order": 2,
            "overview": "Backend developers focus on server-side development, creating the logic, databases, and architecture that power web applications. They work with APIs, databases, and server technologies to ensure applications run smoothly and securely.",
            "responsibilities": [
                "Design and develop server-side applications and APIs",
                "Create and maintain database schemas and queries",
                "Implement authentication and authorization systems",
                "Optimize application performance and scalability",
                "Ensure data security and privacy compliance",
                "Deploy and maintain applications on cloud platforms"
            ],
            "mustHaveSkills": [
                "Python/Node.js/Java", "SQL", "REST APIs", "Git", 
                "Database Design", "Authentication", "Linux/Unix", "HTTP/HTTPS"
            ],
            "goodToHaveSkills": [
                "Docker", "Kubernetes", "GraphQL", "Redis", "Microservices", 
                "AWS/Azure/GCP", "CI/CD", "Message Queues"
            ],
            "tools": [
                "VS Code/IntelliJ", "Postman", "Docker", "AWS/Azure", 
                "MongoDB/PostgreSQL", "GitHub Actions", "Nginx", "Redis"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "full-stack-developer",
            "title": "Full Stack Developer",
            "cardSubtitle": "Master both frontend and backend development",
            "isActive": True,
            "order": 3,
            "overview": "Full stack developers work on both frontend and backend aspects of web applications. They have a comprehensive understanding of the entire web development process and can build complete applications from start to finish.",
            "responsibilities": [
                "Develop complete web applications from frontend to backend",
                "Design and implement database schemas",
                "Create responsive user interfaces and user experiences",
                "Build and integrate APIs and third-party services",
                "Deploy and maintain applications in production",
                "Collaborate with cross-functional teams"
            ],
            "mustHaveSkills": [
                "JavaScript", "React/Vue/Angular", "Node.js/Python", "SQL", 
                "Git", "REST APIs", "HTML/CSS", "Database Design"
            ],
            "goodToHaveSkills": [
                "TypeScript", "GraphQL", "Docker", "AWS/Azure", "Testing", 
                "DevOps", "Microservices", "Mobile Development"
            ],
            "tools": [
                "VS Code", "Git", "Docker", "Postman", "AWS/Heroku", 
                "MongoDB/PostgreSQL", "Figma", "Chrome DevTools"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "data-scientist",
            "title": "Data Scientist",
            "cardSubtitle": "Analyze data and build ML models with Python, R",
            "isActive": True,
            "order": 4,
            "overview": "Data scientists extract insights from large datasets using statistical analysis, machine learning, and data visualization. They help organizations make data-driven decisions and build predictive models.",
            "responsibilities": [
                "Collect, clean, and analyze large datasets",
                "Build and deploy machine learning models",
                "Create data visualizations and reports",
                "Collaborate with stakeholders to understand business needs",
                "Develop data pipelines and automation scripts",
                "Present findings to technical and non-technical audiences"
            ],
            "mustHaveSkills": [
                "Python/R", "SQL", "Statistics", "Machine Learning", 
                "Pandas/NumPy", "Data Visualization", "Git", "Jupyter"
            ],
            "goodToHaveSkills": [
                "Deep Learning", "TensorFlow/PyTorch", "Spark", "Docker", 
                "Cloud Platforms", "MLOps", "A/B Testing", "Big Data"
            ],
            "tools": [
                "Jupyter", "Python/R", "Tableau/PowerBI", "Git", 
                "AWS/GCP", "Docker", "Spark", "Airflow"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "devops-engineer",
            "title": "DevOps Engineer",
            "cardSubtitle": "Automate deployment and manage cloud infrastructure",
            "isActive": True,
            "order": 5,
            "overview": "DevOps engineers bridge the gap between development and operations, focusing on automation, continuous integration/deployment, and infrastructure management to improve software delivery speed and reliability.",
            "responsibilities": [
                "Design and maintain CI/CD pipelines",
                "Manage cloud infrastructure and deployments",
                "Implement monitoring and logging solutions",
                "Automate repetitive tasks and processes",
                "Ensure system security and compliance",
                "Collaborate with development teams on deployment strategies"
            ],
            "mustHaveSkills": [
                "Linux/Unix", "Docker", "Kubernetes", "CI/CD", 
                "AWS/Azure/GCP", "Git", "Scripting", "Monitoring"
            ],
            "goodToHaveSkills": [
                "Terraform", "Ansible", "Jenkins", "Prometheus", 
                "ELK Stack", "Security", "Networking", "Database Administration"
            ],
            "tools": [
                "Docker", "Kubernetes", "Jenkins", "Terraform", 
                "AWS/Azure", "Git", "Prometheus", "Grafana"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "mobile-developer",
            "title": "Mobile Developer",
            "cardSubtitle": "Create iOS and Android apps with React Native, Flutter",
            "isActive": True,
            "order": 6,
            "overview": "Mobile developers create applications for smartphones and tablets, working with native technologies or cross-platform frameworks to deliver engaging mobile experiences.",
            "responsibilities": [
                "Develop native or cross-platform mobile applications",
                "Implement mobile-specific UI/UX patterns",
                "Integrate with device features and APIs",
                "Optimize app performance and battery usage",
                "Publish apps to App Store and Google Play",
                "Maintain and update existing mobile applications"
            ],
            "mustHaveSkills": [
                "React Native/Flutter", "JavaScript/Dart", "Mobile UI/UX", 
                "Git", "API Integration", "App Store Guidelines", "Testing"
            ],
            "goodToHaveSkills": [
                "Native iOS/Android", "Swift/Kotlin", "Push Notifications", 
                "Analytics", "Performance Optimization", "Security", "CI/CD"
            ],
            "tools": [
                "VS Code/Xcode/Android Studio", "React Native/Flutter", 
                "Git", "Postman", "Firebase", "TestFlight", "Flipper"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "ui-ux-designer",
            "title": "UI/UX Designer",
            "cardSubtitle": "Design user interfaces and experiences with Figma, Adobe XD",
            "isActive": True,
            "order": 7,
            "overview": "UI/UX designers create intuitive and visually appealing user interfaces and experiences. They research user needs, create wireframes and prototypes, and ensure products are both functional and delightful to use.",
            "responsibilities": [
                "Conduct user research and usability testing",
                "Create wireframes, mockups, and prototypes",
                "Design user interfaces and interaction patterns",
                "Collaborate with developers on implementation",
                "Maintain design systems and style guides",
                "Analyze user feedback and iterate on designs"
            ],
            "mustHaveSkills": [
                "Figma/Sketch", "User Research", "Wireframing", "Prototyping", 
                "Design Systems", "HTML/CSS", "User Testing", "Adobe Creative Suite"
            ],
            "goodToHaveSkills": [
                "Animation", "Accessibility", "Front-end Development", 
                "Analytics", "A/B Testing", "Mobile Design", "Branding"
            ],
            "tools": [
                "Figma", "Sketch", "Adobe XD", "InVision", 
                "Principle", "Zeplin", "Miro", "Hotjar"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "cybersecurity-analyst",
            "title": "Cybersecurity Analyst",
            "cardSubtitle": "Protect systems from threats and vulnerabilities",
            "isActive": True,
            "order": 8,
            "overview": "Cybersecurity analysts protect organizations from digital threats by monitoring systems, investigating security incidents, and implementing security measures to prevent cyber attacks.",
            "responsibilities": [
                "Monitor networks and systems for security threats",
                "Investigate and respond to security incidents",
                "Implement security policies and procedures",
                "Conduct vulnerability assessments and penetration testing",
                "Maintain security tools and technologies",
                "Provide security awareness training"
            ],
            "mustHaveSkills": [
                "Network Security", "Incident Response", "Risk Assessment", 
                "Security Tools", "Linux/Windows", "Compliance", "Forensics"
            ],
            "goodToHaveSkills": [
                "Penetration Testing", "Malware Analysis", "Cloud Security", 
                "Scripting", "Threat Intelligence", "SIEM", "Cryptography"
            ],
            "tools": [
                "Wireshark", "Nmap", "Metasploit", "Splunk", 
                "Nessus", "Burp Suite", "SIEM Tools", "Kali Linux"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "product-manager",
            "title": "Product Manager",
            "cardSubtitle": "Define product strategy and roadmap",
            "isActive": True,
            "order": 9,
            "overview": "Product managers define product strategy, gather requirements, and coordinate with cross-functional teams to deliver products that meet user needs and business objectives.",
            "responsibilities": [
                "Define product vision and strategy",
                "Gather and prioritize product requirements",
                "Create and maintain product roadmaps",
                "Coordinate with engineering, design, and marketing teams",
                "Analyze market trends and user feedback",
                "Make data-driven product decisions"
            ],
            "mustHaveSkills": [
                "Product Strategy", "Market Research", "Analytics", 
                "Project Management", "Communication", "User Stories", "Agile/Scrum"
            ],
            "goodToHaveSkills": [
                "Technical Background", "A/B Testing", "SQL", 
                "Design Thinking", "Business Analysis", "Leadership", "Metrics"
            ],
            "tools": [
                "Jira", "Confluence", "Google Analytics", "Mixpanel", 
                "Figma", "Slack", "Roadmap Tools", "Survey Tools"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "roleId": "cloud-architect",
            "title": "Cloud Architect",
            "cardSubtitle": "Design scalable cloud infrastructure solutions",
            "isActive": True,
            "order": 10,
            "overview": "Cloud architects design and implement cloud computing strategies, ensuring scalable, secure, and cost-effective cloud infrastructure that meets business requirements.",
            "responsibilities": [
                "Design cloud architecture and migration strategies",
                "Evaluate and select appropriate cloud services",
                "Ensure security and compliance in cloud environments",
                "Optimize cloud costs and performance",
                "Lead cloud adoption initiatives",
                "Provide technical guidance to development teams"
            ],
            "mustHaveSkills": [
                "AWS/Azure/GCP", "Cloud Architecture", "Security", 
                "Networking", "Infrastructure as Code", "DevOps", "Cost Optimization"
            ],
            "goodToHaveSkills": [
                "Multi-cloud", "Serverless", "Containers", "Microservices", 
                "Disaster Recovery", "Compliance", "Automation", "Monitoring"
            ],
            "tools": [
                "AWS/Azure/GCP Console", "Terraform", "CloudFormation", 
                "Docker", "Kubernetes", "Monitoring Tools", "Cost Management Tools"
            ],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    ]
    
    # Insert default roles
    result = roles_collection.insert_many(default_roles)
    print(f"✅ Inserted {len(result.inserted_ids)} default roles")
    
    # Create default admin user
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    try:
        from backend.app.core.security import hash_password
    except ImportError:
        # Fallback hash function
        import hashlib
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()
    
    admin_user = {
        "email": "admin@careerboost.ai",
        "password_hash": hash_password("admin123"),
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    admin_result = admin_collection.insert_one(admin_user)
    print(f"✅ Created default admin user: admin@careerboost.ai")
    
    # Create indexes
    roles_collection.create_index("roleId", unique=True)
    roles_collection.create_index("order")
    roles_collection.create_index("isActive")
    admin_collection.create_index("email", unique=True)
    
    print("✅ Created database indexes")
    
    # Display summary
    print("\n📊 DATABASE SUMMARY")
    print("=" * 40)
    print(f"Database: {DATABASE_NAME}")
    print(f"Roles Collection: {roles_collection.count_documents({})} documents")
    print(f"Admin Collection: {admin_collection.count_documents({})} documents")
    
    print("\n🔑 DEFAULT ADMIN CREDENTIALS")
    print("=" * 40)
    print("Email: admin@careerboost.ai")
    print("Password: admin123")
    
    print("\n🎯 SAMPLE ROLES CREATED")
    print("=" * 40)
    for i, role in enumerate(default_roles[:5], 1):
        print(f"{i}. {role['title']} ({role['roleId']})")
    print(f"... and {len(default_roles)-5} more roles")
    
    print(f"\n✅ Database setup complete!")
    print(f"🌐 Access URLs:")
    print(f"   User Dashboard: http://localhost:3000/dashboard")
    print(f"   Admin Panel: http://localhost:3000/admin")
    
    return True

if __name__ == "__main__":
    setup_roles_database()