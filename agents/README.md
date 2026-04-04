# PlaybookPulse Multi-Agent Backend

**Production-ready FastAPI backend with multi-agent system for incident response playbook compliance analysis.**

---

## 🏗️ Architecture Overview

This backend implements a sophisticated multi-agent architecture using Claude (Anthropic) AI to analyze incident response processes:

### Agents (Member 1 Implementation)

1. **Orchestrator Agent** - Coordinates the entire workflow
2. **Playbook Parser Agent** - Extracts structured requirements from playbooks
3. **Incident Trail Agent** - Collects data from Slack, Jira, GitHub
4. **Adherence Checker Agent** - Compares actual vs expected actions
5. **Compliance Mapper Agent** - Maps findings to compliance frameworks (NIST, SOC2, ISO27001)

### Tech Stack

- **Framework**: FastAPI (async/await)
- **AI/LLM**: Anthropic Claude 3.5 Sonnet
- **Integrations**: Slack SDK, Jira API, PyGithub
- **Real-time**: WebSockets for progress updates
- **Data**: Pydantic models, optional SQLAlchemy
- **Reports**: ReportLab PDF generation

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Anthropic API Key** (required) - Get from [console.anthropic.com](https://console.anthropic.com/)
- **Optional**: Slack, Jira, GitHub tokens for integrations

### Installation

```bash
# Navigate to agents directory
cd agents

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Configuration

Edit `.env` file with your API keys:

```env
# REQUIRED
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# OPTIONAL (for integrations)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your-jira-api-token
GITHUB_TOKEN=ghp_your-github-token
```

### Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

Server starts at: **http://localhost:8000**

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Run with Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

---

## 📡 API Usage

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "playbook-pulse-agents",
  "version": "1.0.0",
  "environment": "development",
  "anthropic_configured": true,
  "slack_configured": false,
  "jira_configured": false,
  "github_configured": false
}
```

### 2. Start Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_content": "# Incident Response\n## Detection\n- Monitor alerts\n- Verify incident\n## Response\n- Create ticket\n- Notify team",
    "compliance_frameworks": ["nist_sp_800_61"]
  }'
```

Response:
```json
{
  "analysis_id": "analysis_abc123def456",
  "status": "pending",
  "message": "Analysis started successfully"
}
```

### 3. Get Analysis Results

```bash
curl http://localhost:8000/api/v1/analysis/analysis_abc123def456
```

### 4. WebSocket Connection (Real-time Updates)

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/client-123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

---

## 🧪 Testing

### Run Demo Analysis

```bash
python scripts/run_demo.py
```

This runs a complete analysis using the sample playbook in `app/data/fixtures/`.

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_agents/ -v
```

### Verify Setup

```bash
python scripts/setup_fixtures.py
```

---

## 📁 Project Structure

```
agents/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Settings & environment
│   ├── dependencies.py         # FastAPI dependencies
│   │
│   ├── agents/                 # 🤖 Multi-agent system
│   │   ├── base.py            # Base agent class
│   │   ├── orchestrator.py    # Main coordinator
│   │   ├── playbook_parser.py # Playbook analysis
│   │   ├── incident_trail.py  # Data collection
│   │   ├── adherence_checker.py # Compliance checking
│   │   └── compliance_mapper.py # Framework mapping
│   │
│   ├── api/v1/                 # 🌐 REST API
│   │   ├── analysis.py        # Analysis endpoints
│   │   ├── health.py          # Health checks
│   │   ├── websocket.py       # Real-time updates
│   │   └── router.py          # Main router
│   │
│   ├── integrations/           # 🔌 External services
│   │   ├── anthropic_client.py # Claude AI
│   │   ├── slack_client.py    # Slack
│   │   ├── jira_client.py     # Jira
│   │   └── github_client.py   # GitHub
│   │
│   ├── models/                 # 📊 Data models
│   │   ├── schemas.py         # Pydantic models
│   │   ├── enums.py           # Constants
│   │   └── database.py        # DB models (optional)
│   │
│   ├── services/               # 💼 Business logic
│   │   ├── analysis_service.py # Analysis orchestration
│   │   ├── websocket_manager.py # WebSocket management
│   │   ├── pdf_generator.py   # Report generation
│   │   └── pr_generator.py    # GitHub PR creation
│   │
│   ├── utils/                  # 🛠️ Utilities
│   │   ├── logger.py          # Logging
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── helpers.py         # Helper functions
│   │
│   └── data/                   # 📄 Static data
│       ├── compliance/        # Framework definitions
│       └── fixtures/          # Sample data
│
├── tests/                      # ✅ Test suites
├── scripts/                    # 🔧 Utility scripts
├── logs/                       # 📝 Log files
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── docker-compose.yml         # Docker orchestration
└── README.md                  # This file
```

---

## 🔑 Key Features

### ✅ Member 1 Tasks Implemented

1. **Multi-Agent Architecture**
   - Base agent class with LLM integration
   - 5 specialized agents with distinct responsibilities
   - Orchestrator for workflow coordination

2. **FastAPI REST API**
   - Complete CRUD operations for analyses
   - Health check endpoints
   - Background task processing
   - Proper error handling

3. **Real-time Updates**
   - WebSocket support for live progress
   - Connection management
   - Heartbeat/ping-pong

4. **External Integrations**
   - Anthropic Claude AI (required)
   - Slack (optional)
   - Jira (optional)
   - GitHub (optional)

5. **Compliance Frameworks**
   - NIST SP 800-61
   - SOC 2 CC7
   - ISO 27001 A.16

6. **Production Ready**
   - Comprehensive logging (JSON format)
   - Error handling & retry logic
   - Environment-based configuration
   - Docker support
   - CORS middleware

---

## 🌐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | Claude API key from Anthropic |
| `ENVIRONMENT` | No | `development` or `production` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `API_HOST` | No | Host to bind (default: `0.0.0.0`) |
| `API_PORT` | No | Port to bind (default: `8000`) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
| `MAX_CONCURRENT_AGENTS` | No | Max parallel agents (default: `5`) |
| `SLACK_BOT_TOKEN` | No | Slack bot token for integration |
| `JIRA_URL` | No | Jira instance URL |
| `JIRA_EMAIL` | No | Jira account email |
| `JIRA_API_TOKEN` | No | Jira API token |
| `GITHUB_TOKEN` | No | GitHub personal access token |

---

## 🎯 Usage Examples

### Example 1: Analyze Playbook Only

```python
import httpx

response = httpx.post("http://localhost:8000/api/v1/analysis/start", json={
    "playbook_content": """
    # Incident Response Playbook
    ## 1. Detection
    - Monitor alerts
    - Verify incident severity
    ## 2. Response
    - Create Jira ticket
    - Notify on-call engineer
    - Start Slack thread
    """
})

analysis_id = response.json()["analysis_id"]
print(f"Analysis started: {analysis_id}")
```

### Example 2: Full Analysis with Integrations

```python
response = httpx.post("http://localhost:8000/api/v1/analysis/start", json={
    "playbook_content": "...",
    "slack_thread_id": "C01ABC:1640000000.123456",
    "jira_ticket_id": "INC-789",
    "github_repo": "myorg/myapp",
    "compliance_frameworks": ["nist_sp_800_61", "soc2_cc7"]
})
```

### Example 3: Monitor Progress via WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/my-client-id');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    analysis_id: 'analysis_abc123'
  }));
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.type === 'analysis_update') {
    console.log(`Progress: ${update.progress}%`);
  }
};
```

---

## 🐛 Common Failure Cases & Solutions

### 1. **Missing Anthropic API Key**

**Symptom:**
```
IntegrationException: Anthropic API key not configured
```

**Solution:**
```bash
# Add to .env file
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Verify it's set
python -c "from app.config import settings; print(settings.anthropic_api_key[:10])"
```

### 2. **Module Import Errors**

**Symptom:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Solution:**
```bash
# Ensure venv is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt

# Or specific package
pip install anthropic
```

### 3. **Port Already in Use**

**Symptom:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8000
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

### 4. **Rate Limit Errors (Claude API)**

**Symptom:**
```
RateLimitException: Claude API rate limit exceeded
```

**Solution:**
- Wait a few minutes before retrying
- Reduce `MAX_CONCURRENT_AGENTS` in `.env`
- The system has automatic retry logic with exponential backoff
- Check your Anthropic API tier limits

### 5. **JSON Parse Errors from Claude**

**Symptom:**
```
json.JSONDecodeError: Expecting value
```

**Solution:**
- This is handled automatically by the code
- Check logs for `raw_response` field
- The system falls back gracefully
- May need to adjust prompts in agent files

### 6. **Slack Integration Fails**

**Symptom:**
```
SlackApiError: invalid_auth
```

**Solution:**
```bash
# Test token
curl -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  https://slack.com/api/auth.test

# Required scopes:
# - channels:history
# - channels:read
# - users:read

# Format thread_id correctly: "CHANNEL_ID:THREAD_TS"
# Example: "C01ABC123:1640000000.123456"
```

### 7. **Jira Authentication Issues**

**Symptom:**
```
JIRAError: 401 Unauthorized
```

**Solution:**
```bash
# Generate API token: https://id.atlassian.com/manage/api-tokens

# Test connection
curl -u "email@domain.com:API_TOKEN" \
  https://your-domain.atlassian.net/rest/api/3/myself

# Ensure JIRA_URL doesn't have trailing slash
```

### 8. **Database File Locked (SQLite)**

**Symptom:**
```
OperationalError: database is locked
```

**Solution:**
```bash
# Close other connections
# Or switch to PostgreSQL for production

# In .env:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
```

### 9. **CORS Errors from Frontend**

**Symptom:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
```bash
# Add frontend URL to .env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Restart server
```

### 10. **Docker Build Failures**

**Symptom:**
```
ERROR [internal] load metadata for docker.io/library/python:3.11-slim
```

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker-compose build --no-cache

# Check Docker is running
docker info
```

---

## 🔍 Debugging Tips

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# Restart server
```

### Check Health Status

```bash
curl http://localhost:8000/health | jq
```

### View Real-time Logs

```bash
# Local
tail -f logs/app.log

# Docker
docker-compose logs -f app
```

### Test Individual Agents

```python
from app.agents.playbook_parser import PlaybookParserAgent
import asyncio

async def test():
    agent = PlaybookParserAgent()
    result = await agent.process({
        "playbook_content": "# Test\n## Step 1\n- Action"
    })
    print(result)

asyncio.run(test())
```

---

## 📊 Performance & Scaling

### Current Limitations
- In-memory storage (not persistent across restarts)
- Single instance (no horizontal scaling yet)
- Synchronous database operations

### Production Recommendations
1. **Use PostgreSQL** instead of SQLite
2. **Add Redis** for caching and session management
3. **Deploy with Gunicorn** + Uvicorn workers
4. **Add rate limiting** (e.g., slowapi)
5. **Implement request queuing** (e.g., Celery + RabbitMQ)
6. **Add monitoring** (Prometheus + Grafana)
7. **Use secrets manager** (AWS Secrets Manager, HashiCorp Vault)

---

## 🚀 Next Steps

- [ ] Add authentication (JWT tokens)
- [ ] Implement database persistence
- [ ] Add more unit tests
- [ ] Create CI/CD pipeline
- [ ] Add Prometheus metrics
- [ ] Implement request queuing
- [ ] Add API rate limiting
- [ ] Create admin dashboard

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

This is Member 1's implementation focusing on:
- ✅ Multi-agent architecture
- ✅ FastAPI REST API
- ✅ Claude AI integration
- ✅ External service integrations
- ✅ Real-time WebSocket updates
- ✅ Production-ready error handling

For questions or issues, please create a GitHub issue.

---

**Built with ❤️ using FastAPI & Claude AI**
