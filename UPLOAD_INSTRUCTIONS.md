# Uploading this project to GitHub

Quick steps to push this workspace to a new GitHub repository.

1) Create an empty repository on GitHub (do NOT initialize with a README or .gitignore).
2) From this project's root run the PowerShell helper (Windows):

```powershell
cd "c:\Users\dsdha\OneDrive\Documents\Skill_Gap_Analyser"
.
\scripts\push_to_github.ps1 -remote "https://github.com/<your-username>/<your-repo>.git" -branch "main"
```

Or use the shell script on macOS / WSL / Linux:

```bash
cd "c:\Users\dsdha\OneDrive\Documents\Skill_Gap_Analyser"
./scripts/push_to_github.sh https://github.com/<your-username>/<your-repo>.git main
```

Notes:
- Git will prompt for credentials. For GitHub, use a Personal Access Token (PAT) if prompted for a password when using HTTPS.
- If you'd prefer SSH, use the SSH repo URL (git@github.com:username/repo.git) and ensure your SSH keys are configured.
- The helper scripts initialize a local repo, add all files, and create an "Initial import" commit if needed.
- If you already have a remote and want to push to a different branch name, pass `-branch` (PowerShell) or the second arg (shell script).

If you want me to run the push for you, provide the repository remote URL and confirm you want me to attempt pushing (this environment will prompt for credentials if needed). I cannot create GitHub repos on your behalf without a token or your confirmation.
