# API Documentation - PlaybookPulse Multi-Agent Backend

**Complete REST API reference for the multi-agent incident response compliance system.**

Base URL: `http://localhost:8000`

---

## 🔐 Authentication

Currently, authentication is not implemented (planned for future releases).  
All endpoints are publicly accessible in development mode.

---

## 📡 Endpoints

### Health & Status

#### GET `/health`

Root health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "playbook-pulse-agents",
  "version": "1.0.0",
  "environment": "development"
}
```

---

#### GET `/api/v1/health`

Detailed health check with integration status.

**Response:**
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

---

#### GET `/api/v1/ping`

Simple ping endpoint for uptime monitoring.

**Response:**
```json
{
  "message": "pong"
}
```

---

### Analysis Operations

#### POST `/api/v1/analysis/start`

Start a new incident response analysis.

**Request Body:**
```json
{
  "playbook_content": "# Incident Response Playbook\n## Detection\n...",
  "slack_thread_id": "C01ABC:1640000000.123456",
  "jira_ticket_id": "INC-123",
  "github_repo": "myorg/myrepo",
  "compliance_frameworks": ["nist_sp_800_61", "soc2_cc7"]
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `playbook_content` | string | ✅ Yes | Markdown content of the incident response playbook |
| `slack_thread_id` | string | No | Slack thread ID (format: `CHANNEL:THREAD_TS`) |
| `jira_ticket_id` | string | No | Jira ticket ID (e.g., `INC-123`) |
| `github_repo` | string | No | GitHub repository (format: `org/repo`) |
| `compliance_frameworks` | array | No | List of frameworks to check against |

**Compliance Frameworks:**
- `nist_sp_800_61` - NIST SP 800-61 Rev. 2
- `soc2_cc7` - SOC 2 CC7 (System Operations)
- `iso_27001_a16` - ISO 27001 A.16

**Response:** `200 OK`
```json
{
  "analysis_id": "analysis_abc123def456",
  "status": "pending",
  "message": "Analysis started successfully",
  "result": null
}
```

**Status Codes:**
- `200` - Analysis started successfully
- `400` - Invalid request body
- `500` - Server error

---

#### GET `/api/v1/analysis/{analysis_id}`

Get analysis status and results.

**Path Parameters:**
- `analysis_id` (string) - The analysis ID returned from start endpoint

**Response:** `200 OK`
```json
{
  "analysis_id": "analysis_abc123def456",
  "status": "completed",
  "message": "Analysis retrieved successfully",
  "result": {
    "analysis_id": "analysis_abc123def456",
    "status": "completed",
    "playbook_steps": [...],
    "incident_data": {...},
    "adherence_checks": [...],
    "compliance_mappings": [...],
    "overall_score": 85.5,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:05:00Z",
    "completed_at": "2024-01-15T10:05:00Z"
  }
}
```

**Analysis Statuses:**
- `pending` - Analysis queued
- `in_progress` - Currently running
- `completed` - Finished successfully
- `failed` - Error occurred

**Status Codes:**
- `200` - Analysis found
- `404` - Analysis not found
- `500` - Server error

---

#### GET `/api/v1/analysis`

List all analyses with pagination.

**Query Parameters:**
- `limit` (integer, default: 10) - Maximum number of results
- `offset` (integer, default: 0) - Offset for pagination

**Example:** `GET /api/v1/analysis?limit=20&offset=0`

**Response:** `200 OK`
```json
[
  {
    "analysis_id": "analysis_abc123",
    "status": "completed",
    "message": "",
    "result": {...}
  },
  {
    "analysis_id": "analysis_def456",
    "status": "in_progress",
    "message": "",
    "result": null
  }
]
```

---

#### POST `/api/v1/analysis/{analysis_id}/report`

Generate a downloadable report for completed analysis.

**Path Parameters:**
- `analysis_id` (string) - The analysis ID

**Request Body:**
```json
{
  "format": "pdf",
  "include_recommendations": true,
  "include_evidence": true
}
```

**Parameters:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | string | `pdf` | Report format (`pdf`, `json`, `html`) |
| `include_recommendations` | boolean | `true` | Include recommendations section |
| `include_evidence` | boolean | `true` | Include evidence details |

**Response:** `200 OK`
```json
{
  "analysis_id": "analysis_abc123",
  "format": "pdf",
  "generated_at": "2024-01-15T10:10:00Z",
  "download_url": "/reports/analysis_abc123.pdf"
}
```

**Status Codes:**
- `200` - Report generated successfully
- `400` - Analysis not completed
- `404` - Analysis not found
- `500` - Server error

---

#### DELETE `/api/v1/analysis/{analysis_id}`

Delete an analysis.

**Path Parameters:**
- `analysis_id` (string) - The analysis ID

**Response:** `200 OK`
```json
{
  "message": "Analysis deleted successfully"
}
```

**Status Codes:**
- `200` - Deleted successfully
- `404` - Analysis not found
- `500` - Server error

---

### WebSocket

#### WS `/api/v1/ws/{client_id}`

WebSocket endpoint for real-time updates.

**Path Parameters:**
- `client_id` (string) - Unique client identifier

**Message Types:**

1. **Connection (from server):**
```json
{
  "type": "connection",
  "message": "Connected to PlaybookPulse Agents",
  "client_id": "my-client-123",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

2. **Ping (from client):**
```json
{
  "type": "ping",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

3. **Pong (from server):**
```json
{
  "type": "pong",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

4. **Subscribe (from client):**
```json
{
  "type": "subscribe",
  "analysis_id": "analysis_abc123"
}
```

5. **Subscribed (from server):**
```json
{
  "type": "subscribed",
  "analysis_id": "analysis_abc123",
  "message": "Subscribed to analysis analysis_abc123",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

6. **Analysis Update (from server):**
```json
{
  "type": "analysis_update",
  "analysis_id": "analysis_abc123",
  "status": "in_progress",
  "progress": 50,
  "message": "Checking adherence to playbook steps",
  "timestamp": "2024-01-15T10:02:30Z"
}
```

7. **Agent Status (from server):**
```json
{
  "type": "agent_status",
  "analysis_id": "analysis_abc123",
  "agent_name": "playbook_parser",
  "status": "completed",
  "message": "Parsed 12 playbook steps",
  "timestamp": "2024-01-15T10:01:15Z"
}
```

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/my-client-123');

ws.onopen = () => {
  // Subscribe to analysis
  ws.send(JSON.stringify({
    type: 'subscribe',
    analysis_id: 'analysis_abc123'
  }));
  
  // Send heartbeat
  setInterval(() => {
    ws.send(JSON.stringify({
      type: 'ping',
      timestamp: new Date().toISOString()
    }));
  }, 30000);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  switch (data.type) {
    case 'analysis_update':
      console.log(`Progress: ${data.progress}%`);
      break;
    case 'agent_status':
      console.log(`Agent ${data.agent_name}: ${data.status}`);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

---

#### GET `/api/v1/ws/status`

Get WebSocket server status.

**Response:** `200 OK`
```json
{
  "active_connections": 5,
  "status": "operational"
}
```

---

## 📊 Data Models

### PlaybookStep

```json
{
  "step_id": "step_1",
  "phase": "Detection",
  "description": "Monitor system alerts for anomalies",
  "required_actions": [
    "Check monitoring dashboard",
    "Verify alert severity"
  ],
  "responsible_roles": [
    "On-call Engineer",
    "SRE Team"
  ]
}
```

### AdherenceCheck

```json
{
  "step_id": "step_1",
  "adherence_level": "full",
  "evidence": [
    "Slack message at 10:00 AM confirming alert review",
    "Jira ticket created at 10:02 AM"
  ],
  "gaps": [],
  "recommendations": []
}
```

**Adherence Levels:**
- `full` - Step fully completed as expected
- `partial` - Step partially completed
- `none` - Step not completed or no evidence

### ComplianceMapping

```json
{
  "framework": "nist_sp_800_61",
  "control_id": "IR-4",
  "control_title": "Incident Handling",
  "adherence_level": "full",
  "supporting_evidence": [
    "All incident handling steps documented",
    "Response team properly notified"
  ]
}
```

### IncidentData

```json
{
  "slack_messages": [...],
  "jira_comments": [...],
  "github_events": [...],
  "slack_participants": ["U01ABC", "U02DEF"],
  "slack_timeline": [...],
  "jira_issue": {...},
  "github_prs": [...]
}
```

---

## 🔧 Error Responses

All errors follow this format:

```json
{
  "error": "Error category",
  "message": "Detailed error message",
  "detail": "Additional context (in development mode)"
}
```

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `400` | Bad Request | Invalid request body, missing required fields |
| `404` | Not Found | Analysis ID doesn't exist |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error, check logs |
| `503` | Service Unavailable | Temporary service issue |

---

## 📈 Rate Limits

Current implementation has no rate limiting.

**Recommended for production:**
- 100 requests per minute per IP
- 10 concurrent analyses per user
- WebSocket: 100 concurrent connections

---

## 🧪 Example Workflows

### Workflow 1: Complete Analysis

```bash
# 1. Start analysis
ANALYSIS_ID=$(curl -X POST http://localhost:8000/api/v1/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_content": "# IR Playbook\n## Detection\n- Monitor alerts",
    "compliance_frameworks": ["nist_sp_800_61"]
  }' | jq -r '.analysis_id')

# 2. Poll for completion
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/analysis/$ANALYSIS_ID | jq -r '.result.status')
  echo "Status: $STATUS"
  [ "$STATUS" = "completed" ] && break
  sleep 5
done

# 3. Get results
curl http://localhost:8000/api/v1/analysis/$ANALYSIS_ID | jq

# 4. Generate report
curl -X POST http://localhost:8000/api/v1/analysis/$ANALYSIS_ID/report \
  -H "Content-Type: application/json" \
  -d '{"format": "pdf", "include_recommendations": true}'
```

### Workflow 2: Real-time Monitoring

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/client-123');

// Start analysis
const response = await fetch('http://localhost:8000/api/v1/analysis/start', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    playbook_content: '# IR Playbook\n...',
    compliance_frameworks: ['nist_sp_800_61']
  })
});

const {analysis_id} = await response.json();

// Subscribe to updates
ws.send(JSON.stringify({
  type: 'subscribe',
  analysis_id
}));

// Listen for progress
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'analysis_update') {
    console.log(`Progress: ${data.progress}%`);
    if (data.status === 'completed') {
      // Fetch final results
      fetch(`http://localhost:8000/api/v1/analysis/${analysis_id}`)
        .then(r => r.json())
        .then(console.log);
    }
  }
};
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Request/response bodies use JSON format
- Maximum playbook size: 100,000 characters
- Analysis typically completes in 30-120 seconds depending on complexity
- WebSocket connections timeout after 5 minutes of inactivity

---

**For interactive API testing, visit:** `http://localhost:8000/docs`
