# 🚀 Quick Reference - PlaybookPulse Multi-Agent Backend

## ⚡ 5-Minute Setup

```bash
cd PlaybookPulse/agents
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Add ANTHROPIC_API_KEY=sk-ant-your-key
uvicorn app.main:app --reload
```

**Test:** `curl http://localhost:8000/health`  
**Docs:** http://localhost:8000/docs

---

## 📡 Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/analysis/start` | Start analysis |
| `GET` | `/api/v1/analysis/{id}` | Get results |
| `GET` | `/api/v1/analysis` | List all |
| `WS` | `/api/v1/ws/{client_id}` | Real-time updates |

---

## 🤖 Agents (Member 1's Core Work)

1. **OrchestratorAgent** - Coordinates workflow
2. **PlaybookParserAgent** - Extracts steps from playbooks
3. **IncidentTrailAgent** - Collects Slack/Jira/GitHub data
4. **AdherenceCheckerAgent** - Checks compliance
5. **ComplianceMapperAgent** - Maps to NIST/SOC2/ISO

---

## 🔧 Common Commands

```bash
# Start server
uvicorn app.main:app --reload

# Run demo
python scripts/run_demo.py

# Verify setup
python verify_setup.py

# Run tests
pytest

# Format code
black app/ && isort app/

# Docker
docker-compose up --build
```

---

## 📝 Example API Call

### Start Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_content": "# IR Playbook\n## Detection\n- Monitor",
    "compliance_frameworks": ["nist_sp_800_61"]
  }'
```

### Get Results

```bash
ANALYSIS_ID="analysis_abc123"
curl http://localhost:8000/api/v1/analysis/$ANALYSIS_ID | jq
```

### WebSocket (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/my-client');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "No module named 'app'" | Activate venv: `source venv/bin/activate` |
| "Port already in use" | Use different port: `--port 8001` |
| "API key invalid" | Check .env: `ANTHROPIC_API_KEY=sk-ant-...` |
| "Import error" | Reinstall: `pip install -r requirements.txt` |

---

## 📂 Important Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application |
| `app/agents/orchestrator.py` | Agent coordinator |
| `app/api/v1/analysis.py` | API endpoints |
| `.env` | Configuration (create from .env.example) |
| `requirements.txt` | Python dependencies |

---

## 📚 Documentation

- `README.md` - Full documentation (15KB)
- `SETUP_GUIDE.md` - Step-by-step setup (11KB)
- `API_DOCUMENTATION.md` - API reference (12KB)
- `DELIVERY.md` - Delivery summary (13KB)

---

## 🎯 Features

- ✅ Multi-agent AI system (5 agents)
- ✅ FastAPI REST API (12 endpoints)
- ✅ WebSocket real-time updates
- ✅ Anthropic Claude integration
- ✅ Slack/Jira/GitHub integrations
- ✅ 3 compliance frameworks
- ✅ Docker support
- ✅ Production-ready

---

## 🔑 Environment Variables

```env
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional
SLACK_BOT_TOKEN=xoxb-...
JIRA_URL=https://domain.atlassian.net
JIRA_EMAIL=email@domain.com
JIRA_API_TOKEN=...
GITHUB_TOKEN=ghp_...

# App Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 📊 Project Stats

- **Files:** 60+
- **Code:** ~7,000 lines
- **Docs:** 59KB
- **Agents:** 5
- **Endpoints:** 12
- **Integrations:** 4
- **Frameworks:** 3

---

## ✅ Verification

Run automated check:

```bash
python verify_setup.py
```

Expected: **10/11 checks pass** (only .env needs manual creation)

---

## 🚀 Next Steps

1. **Setup:**
   - Create `.env` from `.env.example`
   - Add your `ANTHROPIC_API_KEY`
   - Install dependencies
   - Start server

2. **Test:**
   - Run `python scripts/run_demo.py`
   - Check http://localhost:8000/docs
   - Try API endpoints

3. **Integrate:**
   - Connect frontend to API
   - Use WebSocket for real-time
   - Review `API_DOCUMENTATION.md`

---

## 🆘 Need Help?

1. Check logs: `tail -f logs/app.log`
2. Health check: `curl http://localhost:8000/health`
3. Debug mode: Set `LOG_LEVEL=DEBUG` in `.env`
4. Review: `SETUP_GUIDE.md` for detailed instructions

---

**Quick Links:**
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- WebSocket: ws://localhost:8000/api/v1/ws/{client_id}

---

**Status:** ✅ Production Ready | Member 1 Implementation Complete
