# 🚀 Quick Start Guide - Skill Gap Analyzer

## Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- Your Kaggle dataset CSV file

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Initialize Dataset

Place your Kaggle dataset CSV at: `backend/data/raw/job_dataset.csv`

Then run:
```bash
python scripts/init_dataset.py --dataset data/raw/job_dataset.csv
```

Expected output:
```
[OK] MongoDB connected
[OK] Loaded 1000+ job records
[OK] Found and normalized 500+ unique skills
[OK] Found 200+ roles across 5 experience levels
[OK] Dataset initialization complete!
```

## Step 3: Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend will be running at: `http://localhost:8000`

## Step 4: Start Frontend Server

Open a new terminal:
```bash
cd frontend
python server.py
```

Frontend will be running at: `http://localhost:3000`

## Step 5: Open Application

Open your browser and go to:
```
http://localhost:3000/index.html
```

## Features Available

✅ **User Authentication**
- Sign up with name, email, password
- Login with email/password
- Secure JWT token-based authentication

✅ **Manual Skill Entry**
- Searchable dropdown with all dataset skills
- Multi-select skills
- Add custom skills
- Remove selected skills
- Save to MongoDB

✅ **Resume Upload & Parsing**
- Upload PDF, DOCX, or TXT files
- Extract skills from Skills/Technical Skills section only
- Detect experience level (Internship, Fresher, Experienced)
- Filter skills against dataset
- Review and edit extracted skills

✅ **Role Matching Engine**
- Top 5 suitable roles with match percentage
- Star rating (⭐⭐⭐⭐⭐)
- Essential vs Overall skill match
- Experience weighting

✅ **Common vs Role-Specific Skills**
- Common Skills (appearing in many roles)
- Role-Specific Boosters (unique to role)
- TF-IDF style analysis

✅ **Grouped Skill Display**
- Missing skills grouped by category:
  - Programming Languages
  - Web Technologies
  - Databases
  - Cloud Platforms
  - DevOps Tools
  - Machine Learning
  - And more...

✅ **Role Override**
- Analyze another role instantly
- Dropdown to select different role
- Instant gap analysis

✅ **Report Generation**
- Export TXT report
- Export CSV (missing skills)
- Download matched skills list

## API Documentation

Interactive API docs available at:
```
http://localhost:8000/docs
```

## Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running: `mongod` (local) or check cloud connection string
- Update `backend/.env` with your MongoDB URL if needed

**Dataset Not Loading:**
- Check CSV file path: `backend/data/raw/job_dataset.csv`
- Verify CSV has columns: `Title`, `Skills`, `ExperienceLevel`

**Port Already in Use:**
- Backend: Change port in `uvicorn` command
- Frontend: Change `PORT` in `frontend/server.py`

## MongoDB Collections Created

- `users` - User accounts
- `user_skills` - User's skills with source
- `user_skill_gaps` - Analysis history
- `resumes` - Resume metadata
- `dataset_skills` - All skills from dataset
- `dataset_roles` - All roles with requirements

## Next Steps

1. Sign up for an account
2. Add your skills manually or upload resume
3. Select a target role
4. View your skill gap analysis
5. Export reports for your records

Enjoy analyzing your skill gaps! 🎓
