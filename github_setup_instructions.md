# GitHub Setup Instructions for ElectNepal

## Prerequisites Checklist
✅ `.gitignore` is properly configured (DONE)
✅ `.env` file is excluded from commits (VERIFIED)
✅ All sensitive data is protected (CONFIRMED)
✅ Local commits are ready (2 commits ready)

## Step-by-Step Commands

### 1. Add Remote Repository
Replace `YOUR_USERNAME` with your GitHub username:

```bash
# Using HTTPS (easier, works everywhere)
git remote add origin https://github.com/YOUR_USERNAME/electNepal.git

# OR using SSH (if you have SSH keys set up)
git remote add origin git@github.com:YOUR_USERNAME/electNepal.git
```

### 2. Verify Remote is Added
```bash
git remote -v
```

### 3. Push Your Code to GitHub
```bash
# Push main branch and set upstream
git push -u origin master

# If you get an error about branch names, use:
git branch -M main
git push -u origin main
```

### 4. If You Get Authentication Error (HTTPS)
GitHub now requires personal access tokens instead of passwords:

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a name like "electNepal-push"
4. Select scopes: `repo` (full control)
5. Generate token and COPY IT (you won't see it again)
6. Use this token as your password when git asks

### 5. If Using SSH (Recommended for Long-term)
```bash
# Check if you have SSH keys
ls -la ~/.ssh

# If no keys, generate new SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add SSH key to agent
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

## Verification Steps

### After Successful Push
1. Go to https://github.com/YOUR_USERNAME/electNepal
2. Verify all files are uploaded
3. Check that `.env` is NOT visible
4. Confirm `.gitignore` is present
5. Review commit history

### Files That SHOULD Be Visible
✅ Python files (*.py)
✅ HTML templates
✅ Static files (CSS, JS)
✅ Migration files
✅ Requirements.txt
✅ Documentation (*.md)
✅ .env.example

### Files That Should NOT Be Visible
❌ .env (contains passwords)
❌ .venv/ (virtual environment)
❌ __pycache__/ (compiled Python)
❌ *.pyc (compiled Python files)
❌ db.sqlite3 (if using SQLite)
❌ /media/ (user uploads)
❌ *.log (log files)

## Subsequent Pushes

After initial setup, pushing new changes is simple:

```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "Your descriptive message"

# Push to GitHub
git push
```

## Troubleshooting

### Error: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/electNepal.git
```

### Error: "Permission denied (publickey)"
Switch to HTTPS or set up SSH keys (see step 5)

### Error: "Large files detected"
```bash
# Find large files
find . -type f -size +100M

# Add to .gitignore if needed
echo "path/to/large/file" >> .gitignore
```

### Error: "Refusing to merge unrelated histories"
```bash
git pull origin master --allow-unrelated-histories
```

## Security Final Check

Before pushing, ensure:
1. ✅ No SECRET_KEY in committed files
2. ✅ No database passwords in code
3. ✅ No API keys hardcoded
4. ✅ No user data or personal information
5. ✅ .env.example has placeholder values only

## GitHub Repository Settings (After Push)

1. **Add Description**:
   "Django application for Nepal elections with bilingual support"

2. **Add Topics**:
   django, python, nepal, elections, bilingual, postgresql, i18n

3. **Create README** (optional):
   GitHub will show CLAUDE.md content

4. **Set up Branch Protection** (if public):
   - Settings → Branches
   - Add rule for main/master
   - Require pull request reviews

5. **Add License** (recommended):
   - MIT or Apache 2.0 for open source
   - Private license if commercial

## Collaboration Settings

If working with others:
1. Settings → Manage access → Invite collaborators
2. Set up branch protection rules
3. Create CONTRIBUTING.md guidelines
4. Set up issue templates

## Success Indicators

You know it worked when:
- ✅ GitHub shows your repository with all files
- ✅ Green checkmark on latest commit
- ✅ No sensitive data visible
- ✅ Clone works: `git clone https://github.com/YOUR_USERNAME/electNepal.git`

---

**Created**: 2025-01-15
**Project**: ElectNepal
**Security**: All sensitive data excluded