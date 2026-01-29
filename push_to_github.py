#!/usr/bin/env python3
"""
GitHub Push Script for CareerBoost AI
Automated script to push the cleaned project to GitHub
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def main():
    """Main function to push to GitHub."""
    print("🚀 CareerBoost AI - GitHub Push Script")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not a git repository. Initializing...")
        if not run_command("git init", "Initializing Git repository"):
            return False
    
    # Add remote origin (update with your repository URL)
    repo_url = "https://github.com/Dharshika-112/Skill_Gap_Analyzer.git"
    print(f"🔗 Setting remote origin to: {repo_url}")
    
    # Remove existing origin if it exists
    run_command("git remote remove origin", "Removing existing origin (if any)")
    
    # Add new origin
    if not run_command(f"git remote add origin {repo_url}", "Adding remote origin"):
        return False
    
    # Stage all files
    if not run_command("git add .", "Staging all files"):
        return False
    
    # Create commit
    commit_message = "feat: Complete CareerBoost AI with enhanced features\n\n" \
                    "- ✨ AI-powered skill gap analysis with 2,346+ skills\n" \
                    "- 📄 Advanced resume scoring with PDF processing\n" \
                    "- 🏢 218 career roles with detailed information\n" \
                    "- 🎨 Modern React UI with professional design\n" \
                    "- 🤖 Real ML algorithms (RandomForest + Neural Networks)\n" \
                    "- 🔒 Secure JWT authentication system\n" \
                    "- 📊 Comprehensive activity tracking\n" \
                    "- 🧪 Complete test suite with 96%+ accuracy\n" \
                    "- 📚 Professional documentation and setup guides\n\n" \
                    "Ready for production use! 🚀"
    
    if not run_command(f'git commit -m "{commit_message}"', "Creating commit"):
        return False
    
    # Push to GitHub
    if not run_command("git push -u origin main", "Pushing to GitHub"):
        # Try with master branch if main fails
        if not run_command("git push -u origin master", "Pushing to GitHub (master branch)"):
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Successfully pushed CareerBoost AI to GitHub!")
    print(f"🔗 Repository: {repo_url}")
    print("\n📋 What was pushed:")
    print("   ✅ Complete React frontend application")
    print("   ✅ Backend microservices (4 APIs)")
    print("   ✅ MongoDB database structure")
    print("   ✅ ML models and datasets")
    print("   ✅ Comprehensive documentation")
    print("   ✅ Setup and deployment scripts")
    print("   ✅ Professional README with images")
    print("\n🚀 Your project is now live on GitHub!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)