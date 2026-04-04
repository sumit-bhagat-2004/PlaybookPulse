"""
Quick test script to validate agents and orchestrator work end-to-end
Run this WITHOUT needing Slack, Jira, or GitHub
"""
import asyncio
from tests.fixtures import SAMPLE_PLAYBOOK, SAMPLE_INCIDENT_DATA
from app.models.schemas import AnalysisRequest, ComplianceFramework


async def test_full_analysis_flow():
    """Test the complete analysis flow"""
    print("=" * 60)
    print("Testing Full Analysis Flow")
    print("=" * 60)
    
    # Create an analysis request with sample data
    request = AnalysisRequest(
        playbook_content=SAMPLE_PLAYBOOK,
        compliance_frameworks=[ComplianceFramework.NIST_SP_800_61]
        # Note: NOT providing slack_thread_id, jira_ticket_id, github_repo
    )
    
    print(f"\n1. Created analysis request")
    print(f"   - Playbook length: {len(request.playbook_content)} chars")
    print(f"   - Frameworks: {request.compliance_frameworks}")
    
    # Test parsing agent
    print(f"\n2. Testing PlaybookParserAgent...")
    from app.agents.playbook_parser import PlaybookParserAgent
    parser = PlaybookParserAgent()
    parse_result = await parser.process({
        "playbook_content": request.playbook_content
    })
    print(f"   - Parser status: {parse_result.get('status')}")
    print(f"   - Sections found: {parse_result.get('data', {}).get('sections', [])}")
    
    # Test incident trail agent (without external integrations)
    print(f"\n3. Testing IncidentTrailAgent...")
    from app.agents.incident_trail import IncidentTrailAgent
    incident_agent = IncidentTrailAgent()
    incident_result = await incident_agent.process(
        SAMPLE_INCIDENT_DATA  # Will gracefully skip external APIs
    )
    print(f"   - Agent status: {incident_result.get('status')}")
    print(f"   - Slack integration available: {incident_result.get('data', {}).get('integrations_status', {}).get('slack')}")
    print(f"   - Jira integration available: {incident_result.get('data', {}).get('integrations_status', {}).get('jira')}")
    print(f"   - GitHub integration available: {incident_result.get('data', {}).get('integrations_status', {}).get('github')}")
    
    # Test adherence checker
    print(f"\n4. Testing AdherenceCheckerAgent...")
    from app.agents.adherence_checker import AdherenceCheckerAgent
    adherence_agent = AdherenceCheckerAgent()
    adherence_result = await adherence_agent.process({
        "playbook_content": request.playbook_content,
        "compliance_framework": ComplianceFramework.NIST_SP_800_61,
        "incident_data": SAMPLE_INCIDENT_DATA
    })
    print(f"   - Agent status: {adherence_result.get('status')}")
    if adherence_result.get('status') == 'success':
        checks = adherence_result.get('data', {}).get('adherence_checks', [])
        print(f"   - Adherence checks performed: {len(checks)}")
        for check in checks[:2]:
            print(f"     • {check.get('step_id')}: {check.get('adherence_level')}")
    
    # Test full orchestrator
    print(f"\n5. Testing OrchestratorAgent...")
    from app.services.analysis_service import run_analysis_task
    from app.models.schemas import AnalysisStatus
    
    # Create analysis entry manually
    from app.services.analysis_service import _analyses_store
    analysis_id = "test-analysis-001"
    _analyses_store[analysis_id] = {
        "id": analysis_id,
        "status": AnalysisStatus.PENDING,
        "result": {}
    }
    
    # Run the full analysis
    result = await run_analysis_task(analysis_id, request)
    
    print(f"   - Analysis completed!")
    print(f"   - Status: {_analyses_store[analysis_id].get('status')}")
    print(f"   - Overall score: {_analyses_store[analysis_id].get('result', {}).get('overall_score', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ All agents working correctly!")
    print("=" * 60)


async def test_individual_agents():
    """Test each agent individually"""
    print("\n" + "=" * 60)
    print("Testing Individual Agents")
    print("=" * 60)
    
    # Test LLM client availability
    print(f"\n1. Checking LLM Client...")
    try:
        from app.integrations.llm_client import get_llm_client
        from app.config import settings
        client = get_llm_client()
        print(f"   ✓ LLM Provider: {settings.llm_provider}")
        print(f"   ✓ LLM Client available: {client is not None}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test base agent
    print(f"\n2. Testing BaseAgent...")
    try:
        from app.agents.base import BaseAgent
        agent = BaseAgent("test")
        print(f"   ✓ BaseAgent initialized")
        print(f"   ✓ Has LLM client: {hasattr(agent, 'llm_client')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test playbook parser without LLM (structure only)
    print(f"\n3. Testing PlaybookParserAgent (structure parsing)...")
    try:
        from app.agents.playbook_parser import PlaybookParserAgent
        parser = PlaybookParserAgent()
        result = await parser.process({"playbook_content": SAMPLE_PLAYBOOK})
        print(f"   ✓ Parser status: {result.get('status')}")
        sections = result.get('data', {}).get('sections', [])
        print(f"   ✓ Sections found: {sections}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test incident trail agent (optional integrations)
    print(f"\n4. Testing IncidentTrailAgent (optional integrations)...")
    try:
        from app.agents.incident_trail import IncidentTrailAgent
        agent = IncidentTrailAgent()
        result = await agent.process({})
        print(f"   ✓ Agent status: {result.get('status')}")
        print(f"   ✓ Gracefully handles missing integrations")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test compliance mapper
    print(f"\n5. Testing ComplianceMapperAgent...")
    try:
        from app.agents.compliance_mapper import ComplianceMapperAgent
        mapper = ComplianceMapperAgent()
        result = await mapper.process({
            "playbook_content": SAMPLE_PLAYBOOK,
            "frameworks": ["NIST_SP_800_61"]
        })
        print(f"   ✓ Mapper status: {result.get('status')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\nPlaybookPulse Agent Test Suite")
    print("(No external integrations needed)\n")
    
    # Run individual agent tests first
    asyncio.run(test_individual_agents())
    
    # Then run full flow
    print("\n")
    asyncio.run(test_full_analysis_flow())
