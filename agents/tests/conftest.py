"""Test configuration and fixtures"""
import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_playbook_content():
    """Sample playbook content for testing"""
    return """# Test Incident Response Playbook
    
## Detection
- Monitor alerts
- Verify incident

## Response
- Create ticket
- Notify team
- Start investigation
"""


@pytest.fixture
def sample_analysis_request():
    """Sample analysis request"""
    return {
        "playbook_content": "# Test Playbook\n## Step 1\n- Action A",
        "slack_thread_id": "C123:1640000000.123456",
        "jira_ticket_id": "INC-123",
        "github_repo": "org/repo"
    }
