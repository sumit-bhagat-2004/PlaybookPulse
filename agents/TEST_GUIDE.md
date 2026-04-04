# PlaybookPulse Agent Testing Guide

You can test the agents and orchestrator **without needing Slack, Jira, or GitHub**. Here's how:

## Quick Start

### 1. Ensure Server is Running (if testing API endpoints)

```bash
cd D:\PlaybookPulse\agents
.\.lenv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The server will start on `http://localhost:8000`

### 2. Test Individual Agents (Recommended First)

This tests all agents directly, including the orchestrator flow:

```bash
cd D:\PlaybookPulse\agents
.\.lenv\Scripts\python.exe test_agents_quick.py
```

**What this tests:**
- ✅ LLM client initialization (Gemini)
- ✅ BaseAgent functionality
- ✅ PlaybookParserAgent - parses playbook structure
- ✅ IncidentTrailAgent - gracefully handles missing integrations
- ✅ AdherenceCheckerAgent - checks compliance with frameworks
- ✅ ComplianceMapperAgent - maps to compliance frameworks
- ✅ OrchestratorAgent - full end-to-end orchestration
- ✅ State management - shared `_analyses_store` works across requests
- ✅ Background task execution - async/await works correctly
- ✅ Timeout handling - analysis completes within timeout

**Sample output:**
```
Testing Full Analysis Flow
============================================================
1. Created analysis request
   - Playbook length: 1234 chars
   - Frameworks: [<ComplianceFramework.NIST_SP_800_61: 'nist_sp_800_61'>]

2. Testing PlaybookParserAgent...
   - Parser status: success
   - Sections found: ['overview', 'detection', 'containment', ...]

✅ All agents working correctly!
```

### 3. Test API Endpoints (After Server is Running)

Test the HTTP API endpoints:

```bash
cd D:\PlaybookPulse\agents
.\.lenv\Scripts\python.exe test_api_quick.py
```

**What this tests:**
- ✅ GET /api/v1/health - health check
- ✅ POST /api/v1/analysis/start - start analysis
- ✅ GET /api/v1/analysis/{id} - get analysis status
- ✅ GET /api/v1/analysis/list - list all analyses
- ✅ GET /api/v1/metrics - monitoring metrics
- ✅ GET /api/v1/analysis/{id}/report - download PDF report

**Sample output:**
```
Testing PlaybookPulse API Endpoints
============================================================

1. Testing GET /api/v1/health
   Status: 200
   Response: {'status': 'healthy', 'timestamp': '...'}

2. Testing POST /api/v1/analysis/start
   Status: 200
   Response: {'analysis_id': 'analysis-abc123'}
   ✓ Analysis started with ID: analysis-abc123

3. Testing GET /api/v1/analysis/analysis-abc123
   Status: 200
   Analysis status: completed
   Result available: True

✅ API tests completed!
```

## What's Included in Test Fixtures

The test suite uses sample data in `tests/fixtures.py`:

```python
SAMPLE_PLAYBOOK  # Full incident response playbook (Database Corruption example)
SAMPLE_INCIDENT_DATA  # Incident timeline and metadata
MINIMAL_PLAYBOOK  # Minimal playbook for edge case testing
INCOMPLETE_PLAYBOOK  # Incomplete playbook (missing sections)
```

## Testing Without External Integrations

The following are **gracefully skipped** when not configured:

### Slack Integration
- Tests run without `SLACK_BOT_TOKEN`
- `IncidentTrailAgent` logs warning and continues
- No Slack thread data collected, but analysis proceeds

### Jira Integration
- Tests run without `JIRA_URL` and `JIRA_API_TOKEN`
- `IncidentTrailAgent` logs warning and continues
- No Jira ticket data collected, but analysis proceeds

### GitHub Integration
- Tests run without `GITHUB_TOKEN`
- `IncidentTrailAgent` logs warning and continues
- PR generation (PRGenerator) disabled but analysis proceeds

## Running Existing Pytest Tests

Also run the existing test suite:

```bash
cd D:\PlaybookPulse\agents
.\.lenv\Scripts\python.exe -m pytest tests/ -v
```

This runs:
- Smoke tests for health endpoint
- Smoke tests for analysis workflow
- Unit tests for base agent

## Architecture Tested

```
┌─ test_agents_quick.py
│  ├─ LLM Client (Gemini)
│  ├─ BaseAgent
│  ├─ PlaybookParserAgent
│  ├─ IncidentTrailAgent (optional integrations)
│  ├─ AdherenceCheckerAgent
│  ├─ ComplianceMapperAgent
│  └─ OrchestratorAgent (full orchestration)
│
└─ test_api_quick.py
   ├─ Health Check Endpoint
   ├─ Analysis Start Endpoint
   ├─ Analysis Status Endpoint
   ├─ Analysis List Endpoint
   ├─ Metrics Endpoint
   └─ PDF Report Download Endpoint
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'google'"
**Solution:** Gemini SDK not installed
```bash
pip install google-genai
```

### Error: "GEMINI_API_KEY is required"
**Solution:** Set your Gemini API key
```bash
# In .env or as environment variable
GEMINI_API_KEY=your_key_here
```

### Error: "Slack integration not available"
**This is expected!** The test gracefully skips Slack if not configured. This is correct behavior.

### Analysis takes too long
- First run may take 30-60 seconds (LLM calls)
- Subsequent runs are faster (they use cached results)
- Maximum timeout is 5 minutes (configurable via `ANALYSIS_TIMEOUT`)

## Key Features Verified

✅ **State Management**: Shared `_analyses_store` persists across requests
✅ **Async/Await**: AsyncAnthropic/AsyncGemini clients work properly
✅ **Background Tasks**: run_analysis_task executes correctly
✅ **Environment Validation**: Config validates required fields
✅ **Optional Integrations**: Slack/Jira/GitHub gracefully skip if not configured
✅ **WebSocket Updates**: Progress updates sent during analysis
✅ **PDF Generation**: Reports generated and saved correctly
✅ **LLM Response Parsing**: JSON parsing with retry logic works
✅ **Timeouts**: Analysis completes within timeout window
✅ **Monitoring**: Metrics tracked and exposed via endpoint

## Next Steps

Once tests pass:

1. **Deploy API**: Run the server and test with curl/Postman
2. **Add Real Integrations**: Configure Slack/Jira/GitHub tokens
3. **Frontend Integration**: Connect to React/Vue frontend
4. **Production Testing**: Run load tests with `locust` or `ab`

## Example: Manual API Testing

While server runs, test manually:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Start analysis
curl -X POST http://localhost:8000/api/v1/analysis/start \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "playbook_content": "# Incident Response\n## Detection\nMonitor...",
  "compliance_frameworks": ["nist_sp_800_61"]
}
EOF

# Get analysis (replace ID from previous response)
curl http://localhost:8000/api/v1/analysis/analysis-abc123

# Download report
curl http://localhost:8000/api/v1/analysis/analysis-abc123/report -o report.pdf
```

---

**Happy testing!** 🚀
