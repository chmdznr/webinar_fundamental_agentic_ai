# Git Guide for AgenKampus

## 📋 Quick Reference: What to Commit vs Ignore

### ✅ COMMIT THESE (Source Code & Docs)

**Python Source Files:**
```
✅ database/setup_database.py
✅ database/schema.sql
✅ mcp_utilitas/server.py
✅ mcp_akademik/server.py
✅ mcp_akademik/database.py
✅ rag/tool_retriever.py
✅ rag/tool_descriptions.json
✅ agent/orchestrator.py
✅ agent/config.py
✅ scripts/test_demo_scenarios.py
✅ scripts/run_interactive.sh
```

**Documentation:**
```
✅ README.md
✅ PROJECT_SUMMARY.md
✅ GIT_GUIDE.md (this file)
✅ database/README.md
✅ mcp_utilitas/README.md
✅ mcp_akademik/README.md
✅ rag/README.md
✅ agent/README.md
✅ docs/plans/2025-01-08-agenkampus-design.md
```

**Configuration Templates:**
```
✅ requirements.txt
✅ .env.example (template WITHOUT real keys)
✅ .gitignore
```

### ❌ NEVER COMMIT (Sensitive & Generated)

**SENSITIVE FILES (API Keys!):**
```
❌ .env (contains real API keys!)
❌ Any file with credentials
❌ *.pem, *.key files
```

**Generated Files (Will be recreated):**
```
❌ database/kampus.db (run setup_database.py to recreate)
❌ rag/chroma_db/ (run tool_retriever.py to recreate)
❌ __pycache__/ directories
❌ *.pyc, *.pyo files
```

**IDE & OS Files:**
```
❌ .vscode/
❌ .idea/
❌ .DS_Store
❌ *.swp, *.swo
```

## 🚀 Initial Git Setup

### 1. Initialize Repository

```bash
cd /Users/chmdznr/work/adinesia/webinar_fundamental_agentic_ai

# Initialize git
git init

# Check status
git status
```

### 2. Verify .gitignore is Working

```bash
# This should show ONLY source files and docs
git status

# Verify .env is ignored
git check-ignore .env
# Should output: .env

# Verify database is ignored
git check-ignore database/kampus.db
# Should output: database/kampus.db

# Verify chroma_db is ignored
git check-ignore rag/chroma_db/
# Should output: rag/chroma_db/
```

### 3. Stage and Commit

```bash
# Add all source files
git add .

# Check what will be committed
git status

# Should see:
# - All .py files
# - All .md files
# - requirements.txt
# - .env.example
# - .gitignore
# - schema.sql
# - tool_descriptions.json

# Should NOT see:
# - .env
# - kampus.db
# - chroma_db/
# - __pycache__/

# Commit
git commit -m "Initial commit: AgenKampus educational demo

Features:
- Database layer with SQLite
- 2 MCP servers (Utilitas & Akademik)
- RAG-for-Tools with ChromaDB
- Agent orchestrator with OpenAI GPT-4o-mini
- Complete documentation
- Test scripts

Ready for webinar demonstration!"
```

### 4. Add Remote (GitHub, GitLab, etc.)

```bash
# GitHub example
git remote add origin https://github.com/YOUR_USERNAME/agenkampus.git
git branch -M main
git push -u origin main
```

## 📝 For Students: Cloning & Setup

When students clone your repository:

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/agenkampus.git
cd agenkampus

# 2. Create conda environment
conda create -n agenkampus python=3.12 -y
conda activate agenkampus

# 3. Install dependencies
pip install uv
uv pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Setup database
cd database
python setup_database.py
cd ..

# 6. Initialize RAG (first run)
cd rag
python tool_retriever.py
cd ..

# 7. Test the system
python scripts/test_demo_scenarios.py --quick

# 8. Run interactive mode
cd agent
python orchestrator.py
```

## 🔐 Security Reminders

### CRITICAL: Never Commit .env

The `.env` file contains your API keys and should NEVER be committed!

**If you accidentally commit .env:**

```bash
# Remove from git history
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from git"

# IMPORTANT: Rotate your API keys!
# Go to OpenAI dashboard and regenerate keys
# The old keys are now compromised!
```

### Check Before Pushing

Always verify before pushing:

```bash
# Check what will be pushed
git diff origin/main..HEAD

# Verify .env is not staged
git status | grep .env
# Should output nothing or ".env" under "Untracked files"
```

## 📦 Recommended Git Workflow

### For Development

```bash
# Create feature branch
git checkout -b feature/new-tool

# Make changes
# ... edit files ...

# Stage changes
git add mcp_akademik/server.py

# Commit with descriptive message
git commit -m "Add get_gpa tool to Akademik MCP server

- Calculates student GPA from transcript
- Handles missing courses gracefully
- Added tests and documentation"

# Push to remote
git push origin feature/new-tool

# Create pull request on GitHub/GitLab
```

### For Webinar Updates

```bash
# Update documentation
git add README.md
git commit -m "Update README with troubleshooting section"

# Add new demo scenario
git add scripts/test_demo_scenarios.py
git commit -m "Add scenario 5: Multi-student query test"

# Push updates
git push origin main
```

## 📊 What Students Will See

When they clone your repo, they get:

✅ **Source Code**
- All .py files
- SQL schema
- Configuration templates

✅ **Documentation**
- README files
- Design documents
- API documentation

✅ **Setup Scripts**
- Database initialization
- Test scripts
- Launch scripts

❌ **NOT Included (They Generate Locally):**
- database/kampus.db → Run `setup_database.py`
- rag/chroma_db/ → Run `tool_retriever.py`
- .env → Copy from `.env.example` and add their keys

## 🎯 Best Practices

1. **Commit often** - Small, focused commits
2. **Descriptive messages** - Explain WHY, not just WHAT
3. **Test before commit** - Run `test_demo_scenarios.py`
4. **Never commit secrets** - Use `.env.example` template
5. **Keep .gitignore updated** - Add new generated files

## 📚 Common Git Commands

```bash
# Check status
git status

# View changes
git diff

# View commit history
git log --oneline

# Undo unstaged changes
git checkout -- file.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Create branch
git checkout -b branch-name

# Switch branch
git checkout main

# Merge branch
git merge feature-branch

# Pull latest changes
git pull origin main
```

## 🆘 Troubleshooting

### "I committed .env by mistake!"

```bash
# Remove from latest commit
git reset --soft HEAD~1
git restore --staged .env
git commit -m "Your commit message"

# If already pushed - ROTATE YOUR API KEYS IMMEDIATELY!
```

### "Database file shows as modified"

This is normal - `.gitignore` prevents tracking.
If it's showing as modified:

```bash
git status
# Should show "database/kampus.db" as untracked, not modified
```

### "Too many untracked files"

```bash
# Clean untracked files (careful!)
git clean -fd

# Preview what will be deleted
git clean -fd --dry-run
```

## ✅ Pre-Push Checklist

Before `git push`:

- [ ] Run tests: `python scripts/test_demo_scenarios.py --quick`
- [ ] Check git status: `git status`
- [ ] Verify .env not staged
- [ ] Verify no generated files staged
- [ ] Descriptive commit message
- [ ] Code is documented
- [ ] README updated if needed

---

**Ready to commit!** 🚀

```bash
git add .
git commit -m "Your descriptive message here"
git push origin main
```
