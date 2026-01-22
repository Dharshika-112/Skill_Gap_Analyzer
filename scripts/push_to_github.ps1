param(
    [string]$remote = $null,
    [string]$branch = "main"
)

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed or not in PATH. Install Git first: https://git-scm.com/downloads"
    exit 1
}

if (-not (Test-Path .git)) {
    git init
    Write-Host "Initialized new git repository."
}

git add --all
try {
    git commit -m "Initial import: Skill_Gap_Analyser" -q
    Write-Host "Committed files."
} catch {
    Write-Host "Nothing to commit or commit failed (maybe already committed). Continuing."
}

if (-not $remote) {
    Write-Host "No remote URL provided. Run this script with -remote 'https://github.com/username/repo.git' or set up your remote manually."
    exit 0
}

if (-not (git remote)) {
    git remote add origin $remote
    Write-Host "Added remote origin -> $remote"
} else {
    git remote set-url origin $remote
    Write-Host "Set origin -> $remote"
}

git branch -M $branch

Write-Host "Pushing to origin/$branch... Git may prompt for credentials or use your credential manager."
git push -u origin $branch
