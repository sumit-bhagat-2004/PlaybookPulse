# Incident Data Flow Fix

## Problem
The PlaybookPulse agents were performing adherence checks but showing "No incident data available" for all checks, resulting in 0% adherence scores and meaningless output.

## Root Cause
The issue had two parts:

1. **Data Flow Mismatch**: The `IncidentTrailAgent` only accepted thread IDs/ticket IDs for fetching data from APIs, but didn't support pre-fetched/raw incident data being passed directly.

2. **Missing Fixture Loading**: When running tests or demos without live integrations, the system wasn't loading the sample fixture data that already existed in `backend/fixtures/`.

## Changes Made

### 1. Updated `agents/app/agents/incident_trail.py`
- Added support for pre-fetched data via `slack_data`, `jira_data`, and `github_events` parameters
- Agent now checks for raw data first before attempting to fetch from APIs
- Prevents duplicate fetching if data is already provided

### 2. Updated `backend/slack_app.py`
- Added automatic fixture loading when no live Slack thread is available
- Loads both Slack and Jira fixture data for demo/testing scenarios
- Passes `jira_ticket_data` to the analysis (was missing before)

### 3. Updated `backend/main.py` (`/analyze` endpoint)
- Added automatic fixture loading when no incident data is provided in the request
- Ensures demo/test requests always have data to analyze

### 4. Fixed Unicode Issues in `backend/agents_bridge.py`
- Removed emoji characters that caused encoding errors on Windows
- Changed warning symbols (⚠️, 🔗) to text equivalents

## Testing

### Simple Verification Test
```bash
cd backend
python test_incident_data_simple.py
```

Expected output:
```
[OK] Loaded Slack Data:
   - Messages: 10
   - Participants: ['bob_secops', 'U12345_PagerDuty', 'alice_oncall']

[OK] Loaded Jira Data:
   - Ticket ID: SEC-1234
   - Title: Production credential leaked in public GitHub repository
   - Events: 4
```

### Full Analysis Test (if agents are available)
```bash
cd backend
python test_analysis_with_fixtures.py
```

This will run the complete multi-agent analysis with fixture data and show adherence scores.

### API Test
```bash
# Start the backend server
cd backend
uvicorn main:api --reload

# In another terminal, test the analyze endpoint
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"use_sample_playbook": true}'
```

The response should now show adherence checks with actual evidence from the Slack and Jira fixtures, not "No incident data available".

## Fixture Data Available

Located in `backend/fixtures/`:

- **playbook_comprehensive.md** - Detailed incident response playbook
- **slack_thread.json** - 10 messages simulating an incident response
- **jira_ticket.json** - Ticket with status changes and timeline
- **github_commits.json** - Commits related to the incident

## Expected Behavior After Fix

### Before:
```json
{
  "adherence_level": "none",
  "evidence": [
    "No incident data was available to assess whether..."
  ],
  "gaps": [
    "Inability to confirm ... due to lack of data."
  ]
}
```

### After:
```json
{
  "adherence_level": "partial",  // or "full"
  "evidence": [
    "Slack message at 14:05 shows alice_oncall acknowledged the alert",
    "JIRA ticket SEC-1234 shows status change to 'In Progress' at 14:10"
  ],
  "gaps": [
    "Step requires creating incident channel - no evidence found",
    "Legal notification occurred 3 hours late (at 17:05 vs expected 14:00)"
  ]
}
```

## Next Steps

1. **Test with Live Data**: Configure Slack/Jira credentials and test with real incident threads
2. **Verify Agents Service**: Ensure the agents service can start and process the data correctly
3. **UI Testing**: Run the frontend and verify adherence scores display properly

## Files Modified

- `agents/app/agents/incident_trail.py` - Added pre-fetched data support
- `backend/slack_app.py` - Added fixture loading
- `backend/main.py` - Added fixture loading for API endpoint
- `backend/agents_bridge.py` - Fixed unicode encoding issues
- `backend/test_incident_data_simple.py` (new) - Simple verification test
- `backend/test_analysis_with_fixtures.py` (new) - Full analysis test

## Dependencies
Ensure all dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

Note: There may be Python 3.14 compatibility issues with pydantic. If you encounter DLL errors, consider using Python 3.11 or 3.12 instead.
