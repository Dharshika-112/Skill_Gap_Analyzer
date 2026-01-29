# 🗄️ CareerBoost AI - Database Structure

## 📊 **Database Overview**

**Database Name:** `skillgap`  
**MongoDB URL:** `mongodb://localhost:27017/`  
**Collections:** 2 main collections

---

## 🎯 **Collection 1: roles**

### **Purpose:** Store all job role information for the dashboard

### **Schema Structure:**
```json
{
  "_id": "ObjectId",
  "roleId": "frontend-developer",           // Unique string for URLs
  "title": "Frontend Developer",           // Display title
  "cardSubtitle": "Build user interfaces with React, Vue, Angular",
  "isActive": true,                        // Show/hide role
  "order": 1,                             // Dashboard display order
  "overview": "Frontend developers create...", // Detailed description
  "responsibilities": [                    // Array of responsibilities
    "Develop responsive web applications",
    "Collaborate with UI/UX designers",
    "..."
  ],
  "mustHaveSkills": [                     // Required skills
    "HTML5", "CSS3", "JavaScript", "React.js", "..."
  ],
  "goodToHaveSkills": [                   // Nice-to-have skills
    "TypeScript", "Vue.js", "Angular", "..."
  ],
  "tools": [                              // Tools and technologies
    "VS Code", "Chrome DevTools", "Figma", "..."
  ],
  "createdAt": "2026-01-28T...",
  "updatedAt": "2026-01-28T..."
}
```

### **Sample Data Created (10 Roles):**
1. **Frontend Developer** (`frontend-developer`)
2. **Backend Developer** (`backend-developer`)
3. **Full Stack Developer** (`full-stack-developer`)
4. **Data Scientist** (`data-scientist`)
5. **DevOps Engineer** (`devops-engineer`)
6. **Mobile Developer** (`mobile-developer`)
7. **UI/UX Designer** (`ui-ux-designer`)
8. **Cybersecurity Analyst** (`cybersecurity-analyst`)
9. **Product Manager** (`product-manager`)
10. **Cloud Architect** (`cloud-architect`)

---

## 🔐 **Collection 2: admin_users**

### **Purpose:** Store admin user credentials for role management

### **Schema Structure:**
```json
{
  "_id": "ObjectId",
  "email": "admin@careerboost.ai",
  "password_hash": "hashed_password_string",
  "created_at": "2026-01-28T...",
  "is_active": true
}
```

### **Default Admin User:**
- **Email:** `admin@careerboost.ai`
- **Password:** `admin123`
- **Status:** Active

---

## 📋 **Database Indexes Created:**

### **roles collection:**
- `roleId` (unique) - For fast URL lookups
- `order` - For dashboard sorting
- `isActive` - For filtering active roles

### **admin_users collection:**
- `email` (unique) - For admin authentication

---

## 🎯 **Role Data Examples:**

### **Frontend Developer Role:**
```json
{
  "roleId": "frontend-developer",
  "title": "Frontend Developer",
  "cardSubtitle": "Build user interfaces with React, Vue, Angular",
  "isActive": true,
  "order": 1,
  "overview": "Frontend developers create the visual and interactive elements...",
  "responsibilities": [
    "Develop responsive web applications using modern frameworks",
    "Collaborate with UI/UX designers to implement designs",
    "Optimize applications for maximum speed and scalability"
  ],
  "mustHaveSkills": [
    "HTML5", "CSS3", "JavaScript (ES6+)", "React.js", "Git"
  ],
  "goodToHaveSkills": [
    "TypeScript", "Vue.js", "Angular", "Sass/SCSS", "Webpack"
  ],
  "tools": [
    "VS Code", "Chrome DevTools", "Figma", "Postman", "GitHub"
  ]
}
```

### **Data Scientist Role:**
```json
{
  "roleId": "data-scientist",
  "title": "Data Scientist",
  "cardSubtitle": "Analyze data and build ML models with Python, R",
  "isActive": true,
  "order": 4,
  "overview": "Data scientists extract insights from large datasets...",
  "responsibilities": [
    "Collect, clean, and analyze large datasets",
    "Build and deploy machine learning models",
    "Create data visualizations and reports"
  ],
  "mustHaveSkills": [
    "Python/R", "SQL", "Statistics", "Machine Learning", "Pandas/NumPy"
  ],
  "goodToHaveSkills": [
    "Deep Learning", "TensorFlow/PyTorch", "Spark", "Docker"
  ],
  "tools": [
    "Jupyter", "Python/R", "Tableau/PowerBI", "Git", "AWS/GCP"
  ]
}
```

---

## 🔄 **How the System Works:**

### **User Dashboard:**
1. Fetches roles from MongoDB where `isActive = true`
2. Sorts by `order` field
3. Displays as cards with `title`, `cardSubtitle`, and top skills
4. Cards link to `/role/{roleId}` for detailed view

### **Role Detail Pages:**
1. Uses `roleId` from URL to fetch specific role
2. Displays all role information from database
3. Shows overview, responsibilities, skills, tools

### **Admin Panel:**
1. Admin logs in with email/password
2. Can view all roles (active and inactive)
3. Can add, edit, delete, activate/deactivate roles
4. Changes are immediately reflected on user dashboard

---

## 📊 **Database Statistics:**
- **Total Roles:** 10 default roles created
- **Active Roles:** 10 (all active by default)
- **Admin Users:** 1 default admin
- **Collections:** 2 main collections
- **Indexes:** 4 indexes for performance

---

## 🚀 **Ready for Customization!**

The database is now fully set up and ready for:
- ✅ Dynamic role management through admin panel
- ✅ Real-time dashboard updates
- ✅ Role-based career guidance
- ✅ Scalable role addition/modification
- ✅ Professional role detail pages

**Next Steps:** Implement the backend APIs and frontend components to interact with this database structure.