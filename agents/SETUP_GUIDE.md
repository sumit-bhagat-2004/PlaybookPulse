# Setup Guide - PlaybookPulse Multi-Agent Backend

**Complete step-by-step setup instructions for Member 1's backend implementation.**

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] pip (Python package manager)
- [ ] Git installed
- [ ] Anthropic API account (free tier available)
- [ ] Text editor or IDE (VS Code recommended)
- [ ] Terminal/Command Prompt access

**Optional (for full features):**
- [ ] Docker Desktop (for containerized deployment)
- [ ] Slack workspace access (for Slack integration)
- [ ] Jira account (for Jira integration)
- [ ] GitHub account (for GitHub integration)

---

## 🚀 Installation Steps

### Step 1: Navigate to Directory

```bash
cd PlaybookPulse/agents
```

### Step 2: Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (web framework)
- Anthropic SDK (Claude AI)
- Pydantic (data validation)
- Integration SDKs (Slack, Jira, GitHub)
- Utilities (logging, PDF generation, etc.)

**Expected output:**
```
Successfully installed fastapi-0.109.0 anthropic-0.18.1 ...
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Windows (if cp doesn't work):
copy .env.example .env
```

### Step 5: Get Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

### Step 6: Edit .env File

Open `.env` in your text editor and add your API key:

```env
# REQUIRED - Get from console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-your-actual-key-paste-it-here

# Optional - can leave as defaults
ENVIRONMENT=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

**Save the file!**

### Step 7: Verify Setup

```bash
python scripts/setup_fixtures.py
```

**Expected output:**
```
Checking compliance framework data...
✓ nist_sp_800_61.json: NIST SP 800-61 Rev. 2 loaded
✓ soc2_cc7.json: SOC 2 CC7 loaded
✓ iso_27001_a16.json: ISO/IEC 27001:2013 Annex A.16 loaded

Compliance data check complete!
```

### Step 8: Start the Server

```bash
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 9: Test the API

Open another terminal and run:

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "playbook-pulse-agents",
  "version": "1.0.0",
  "environment": "development",
  "anthropic_configured": true
}
```

### Step 10: Access API Documentation

Open your browser and go to:

**http://localhost:8000/docs**

You should see the interactive Swagger UI with all API endpoints.

---

## ✅ Verification Tests

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Should return status "healthy"

### Test 2: API Version

```bash
curl http://localhost:8000/api/v1/health
```

Should show all integration statuses

### Test 3: Run Demo Analysis

In a new terminal (with venv activated):

```bash
python scripts/run_demo.py
```

This runs a full analysis with the sample playbook. Should complete in 30-60 seconds.

**Check the generated file:**
```bash
# Should create demo_analysis_result.json
cat demo_analysis_result.json  # Linux/Mac
type demo_analysis_result.json  # Windows
```

---

## 🔌 Optional: Setup Integrations

### Slack Integration (Optional)

1. **Create Slack App:**
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click "Create New App" → "From scratch"
   - Name it "PlaybookPulse" and select your workspace

2. **Add Bot Token Scopes:**
   - OAuth & Permissions → Bot Token Scopes
   - Add: `channels:history`, `channels:read`, `users:read`

3. **Install to Workspace:**
   - Install App → Install to Workspace
   - Copy "Bot User OAuth Token" (starts with `xoxb-`)

4. **Add to .env:**
   ```env
   SLACK_BOT_TOKEN=xoxb-your-token-here
   ```

5. **Test:**
   ```bash
   curl -H "Authorization: Bearer xoxb-your-token" \
     https://slack.com/api/auth.test
   ```

### Jira Integration (Optional)

1. **Generate API Token:**
   - Go to [id.atlassian.com/manage/api-tokens](https://id.atlassian.com/manage/api-tokens)
   - Click "Create API token"
   - Copy the token

2. **Add to .env:**
   ```env
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@domain.com
   JIRA_API_TOKEN=your-token-here
   ```

3. **Test:**
   ```bash
   curl -u "your-email:your-token" \
     https://your-domain.atlassian.net/rest/api/3/myself
   ```

### GitHub Integration (Optional)

1. **Create Personal Access Token:**
   - Go to Settings → Developer settings → Personal access tokens
   - Generate new token (classic)
   - Select scopes: `repo`, `read:org`
   - Copy the token

2. **Add to .env:**
   ```env
   GITHUB_TOKEN=ghp_your-token-here
   GITHUB_ORG=your-org-name
   ```

3. **Test:**
   ```bash
   curl -H "Authorization: token ghp-your-token" \
     https://api.github.com/user
   ```

---

## 🐳 Docker Setup (Alternative)

### Step 1: Ensure Docker is Running

```bash
docker --version
docker-compose --version
```

### Step 2: Create .env File

Same as Step 6 above - Docker will use this file.

### Step 3: Build and Run

```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

### Step 4: Run in Background

```bash
docker-compose up -d
```

### Step 5: View Logs

```bash
docker-compose logs -f app
```

### Step 6: Stop

```bash
docker-compose down
```

---

## 🧪 Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

Open `htmlcov/index.html` in your browser to see coverage report.

---

## 🔧 Development Workflow

### 1. Start Development Server

```bash
uvicorn app.main:app --reload --log-level debug
```

The `--reload` flag enables auto-reload on code changes.

### 2. Make Code Changes

Edit files in the `app/` directory. Server will auto-reload.

### 3. Test Your Changes

```bash
# Quick test
curl -X POST http://localhost:8000/api/v1/analysis/start \
  -H "Content-Type: application/json" \
  -d '{"playbook_content": "# Test\n## Step 1\n- Action"}'
```

### 4. Check Logs

```bash
tail -f logs/app.log
```

### 5. Format Code

```bash
black app/
isort app/
```

---

## 📊 Monitoring & Debugging

### View Logs

```bash
# Real-time
tail -f logs/app.log

# Last 100 lines
tail -100 logs/app.log

# Search for errors
grep "ERROR" logs/app.log
```

### Enable Debug Mode

In `.env`:
```env
LOG_LEVEL=DEBUG
```

### Test Individual Components

```python
# Test Anthropic client
python -c "from app.integrations.anthropic_client import get_anthropic_client; client = get_anthropic_client(); print('OK')"

# Test agent
python -c "from app.agents.playbook_parser import PlaybookParserAgent; agent = PlaybookParserAgent(); print('Agent created')"
```

---

## 🚨 Troubleshooting

### Issue: "No module named 'app'"

**Solution:**
```bash
# Make sure you're in the agents/ directory
pwd  # Should end with '/agents'

# Activate venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Verify Python path
python -c "import sys; print(sys.executable)"
# Should point to venv Python
```

### Issue: "Address already in use"

**Solution:**
```bash
# Use different port
uvicorn app.main:app --port 8001

# Or kill existing process
# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "API key invalid"

**Solution:**
1. Check key format: should start with `sk-ant-`
2. No extra spaces in .env file
3. Regenerate key at console.anthropic.com
4. Restart server after changing .env

### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker Desktop
# Then verify:
docker info
```

---

## 📚 Next Steps

After successful setup:

1. **Explore API:**
   - Visit http://localhost:8000/docs
   - Try different endpoints
   - Check request/response schemas

2. **Run Demo:**
   ```bash
   python scripts/run_demo.py
   ```

3. **Read Code:**
   - Start with `app/main.py`
   - Explore `app/agents/orchestrator.py`
   - Check `app/api/v1/analysis.py`

4. **Customize:**
   - Modify agent prompts
   - Add new compliance frameworks
   - Create custom endpoints

5. **Integrate Frontend:**
   - API is ready at http://localhost:8000
   - WebSocket at ws://localhost:8000/api/v1/ws/{client_id}
   - CORS already configured for localhost:3000 and localhost:5173

---

## ✨ Quick Reference

### Common Commands

```bash
# Activate venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/ && isort app/

# Check compliance data
python scripts/setup_fixtures.py

# Run demo
python scripts/run_demo.py

# Reset environment
python scripts/reset_demo_env.py
```

### Important URLs

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- WebSocket: ws://localhost:8000/api/v1/ws/{client_id}

### File Locations

- Logs: `logs/app.log`
- Config: `.env`
- Sample data: `app/data/fixtures/`
- Compliance: `app/data/compliance/`

---

## 🆘 Getting Help

1. **Check Logs:** `tail -f logs/app.log`
2. **Test Health:** `curl http://localhost:8000/health`
3. **Debug Mode:** Set `LOG_LEVEL=DEBUG` in `.env`
4. **Review README:** See main README.md for feature details
5. **Check Issues:** Review common failure cases in README

---

**You're all set! 🎉**

The multi-agent backend is now running and ready to analyze incident response playbooks.
