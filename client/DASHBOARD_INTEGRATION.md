# Dashboard Integration Guide

## Overview

The PlaybookPulse dashboard has been updated to integrate with both the **Agents API** (port 8001) and **Backend Integration API** (port 8000), providing real-time incident response compliance monitoring.

## Architecture

### API Endpoints

#### Agents API (Port 8001) - Primary API

- **Base URL**: `http://localhost:8001/api/v1`
- **Endpoints**:
  - `POST /analysis/start` - Start a new analysis
  - `GET /analysis` - List all analyses
  - `GET /analysis/{id}` - Get specific analysis result
  - `POST /analysis/{id}/report` - Generate compliance report
  - `GET /health` - Health check
  - `WebSocket /ws/{client_id}` - Real-time updates

#### Backend Integration API (Port 8000) - Supporting API

- **Base URL**: `http://localhost:8000`
- **Endpoints**:
  - `POST /analyze` - Quick analysis with fixtures
  - `GET /playbooks` - List available playbooks
  - `GET /playbooks/{id}` - Get playbook content

### Data Flow

#### Analysis Lifecycle

1. **Start Analysis**
   - Dashboard sends `AnalysisRequest` with playbook content and compliance frameworks
   - Agents API returns `analysis_id` immediately
   - Status is set to `PENDING`

2. **Background Processing**
   - Multi-agent system processes incident:
     - Playbook Parser extracts steps
     - Incident Trail collects data
     - Adherence Checker verifies step compliance
     - Compliance Mapper maps to frameworks

3. **Real-time Updates**
   - WebSocket broadcasts progress updates
   - Dashboard receives and displays:
     - Adherence check results
     - Compliance mappings
     - Overall compliance score

## Dashboard Components

### 1. Main Dashboard View (`app/dashboard/page.tsx`)

**Features:**

- Real-time health status monitoring
- List of previous analyses
- Selected analysis details:
  - Compliance score with progress bar
  - Adherence tracking grid
  - Compliance frameworks breakdown
  - Detail panel for specific steps

### 2. Supporting Components

#### AdherenceGrid (`components/AdherenceGrid.tsx`)

- Displays playbook steps with status indicators
- Status colors:
  - 🟢 FOLLOWED - Adherent
  - 🟡 DELAYED - Partial adherence
  - 🔴 MISSED - Non-adherent
  - ⚫ PENDING - Not yet evaluated

#### ComplianceDetailPanel (`components/ComplianceDetailPanel.tsx`)

- Side panel showing:
  - Step-level adherence details
  - Evidence supporting compliance
  - Gaps identified
  - Recommendations for improvement
  - PDF report download option

### 3. API Utilities (`lib/api.ts`)

Centralized API calls for:

- `checkHealth()` - Verify agent API availability
- `startAnalysis()` - Initiate new analysis
- `listAnalyses()` - Fetch analysis history
- `getAnalysis()` - Get detailed analysis result
- `downloadReport()` - Generate PDF report
- `listPlaybooks()` - Get available playbooks
- `quickAnalysis()` - Backend quick analysis

### 4. Constants (`lib/constants.ts`)

Configuration for:

- `AGENTS_API` - Main API endpoint
- `AGENTS_WS` - WebSocket endpoint
- `BACKEND_URL` - Integration API endpoint
- Organized endpoint mappings

## Data Models

### Analysis Request

```typescript
{
  playbook_content: string;
  slack_thread_id?: string;
  jira_ticket_id?: string;
  github_repo?: string;
  compliance_frameworks?: string[];
}
```

### Analysis Result

```typescript
{
  analysis_id: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  playbook_steps: PlaybookStep[];
  adherence_checks: AdherenceCheck[];
  compliance_mappings: ComplianceMapping[];
  overall_score: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}
```

### Adherence Check

```typescript
{
  step_id: string;
  adherence_level: "full" | "partial" | "none";
  evidence: string[]; // Supporting evidence
  gaps: string[]; // Identified gaps
  recommendations: string[]; // Improvement recommendations
}
```

### Compliance Mapping

```typescript
{
  framework: string; // "nist_sp_800_61" | "soc2_cc7" | "iso_27001_a16"
  control_id: string;
  control_title: string;
  adherence_level: "full" | "partial" | "none";
  supporting_evidence: string[];
}
```

## Features

### ✅ Real-time Monitoring

- Live health status indicator
- Auto-refresh analyses every 10 seconds
- WebSocket updates during analysis processing

### ✅ Analysis Management

- View analysis history
- Select and inspect individual analyses
- Filter by completion status
- Download PDF reports

### ✅ Compliance Visualization

- Overall compliance score with progress bar
- Per-framework adherence levels
- Control-level mapping display
- Visual status indicators and color coding

### ✅ Adherence Tracking

- Step-by-step progress grid
- Color-coded status badges
- Click to view detailed gap analysis
- Evidence and recommendations display

### ✅ Performance

- Efficient API calls with error handling
- Debounced health checks (5s interval)
- Auto-refresh with configurable intervals (10s default)
- Hydration-safe SSR compatibility

## Running the Dashboard

### Prerequisites

1. **Backend running** on port 8000:

   ```bash
   cd backend && uvicorn main:app --reload --port 8000
   ```

2. **Agents API running** on port 8001:

   ```bash
   cd agents && uvicorn app.main:app --reload --port 8001
   ```

3. **Client dev server** on port 3000:
   ```bash
   cd client && npm run dev
   ```

### Access

- Dashboard: `http://localhost:3000/dashboard`
- Agents API Docs: `http://localhost:8001/docs`
- Backend API Docs: `http://localhost:8000/docs`

## Configuration

### Environment Variables

```env
# client/.env or client/.env.local
REACT_APP_AGENTS_API=http://localhost:8001/api/v1
REACT_APP_BACKEND_URL=http://localhost:8000
```

## Future Enhancements

1. **Export Capabilities**
   - CSV export of adherence data
   - JSON export of full analysis
   - Email report distribution

2. **Advanced Filtering**
   - Filter analyses by framework
   - Filter by adherence level
   - Filter by date range

3. **Comparison Tools**
   - Compare multiple analyses
   - Trend analysis over time
   - Compliance drift detection

4. **Integration Features**
   - Slack notifications
   - Jira issue creation
   - GitHub PR comments

5. **Custom Playbooks**
   - Upload custom playbooky forms
   - Template library
   - Version control

## Troubleshooting

### Dashboard shows "Offline"

- Check agents API is running: `curl http://localhost:8001/api/v1/health`
- Verify CORS settings in agents API config
- Check browser console for connection errors

### Analyses not loading

- Verify database connectivity in agents API
- Check API logs for error messages
- Ensure analyses exist in database (run test analysis first)

### WebSocket not updating

- Check browser Network tab for WebSocket connection
- Verify client_id is being sent correctly
- Check agents API WebSocket implementation

### Report download fails

- Verify PDF generation dependencies are installed
- Check file write permissions
- Review API logs for generation errors
