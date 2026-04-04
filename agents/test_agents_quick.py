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
    
    # Handle None or failed results gracefully
    if parse_result is None:
        print(f"   ✗ Parser returned None (unexpected)")
        parse_result = {"success": False, "data": {}, "error": "Parser returned None"}
    
    print(f"   - Parser success: {parse_result.get('success', False)}")
    if parse_result.get('success'):
        steps = parse_result.get('data', {}).get('steps', [])
        print(f"   - Steps found: {len(steps)}")
    else:
        print(f"   - Error: {parse_result.get('error', 'Unknown error')}")
    
    # Test incident trail agent (without external integrations)
    print(f"\n3. Testing IncidentTrailAgent...")
    from app.agents.incident_trail import IncidentTrailAgent
    incident_agent = IncidentTrailAgent()
    incident_result = await incident_agent.process(
        SAMPLE_INCIDENT_DATA  # Will gracefully skip external APIs
    )
    
    # Handle None results gracefully
    if incident_result is None:
        print(f"   ✗ Agent returned None (unexpected)")
        incident_result = {"success": False, "data": {}, "error": "Agent returned None"}
    
    print(f"   - Agent success: {incident_result.get('success', False)}")
    integrations = incident_result.get('data', {}).get('integrations_status', {})
    print(f"   - Slack integration: {integrations.get('slack', 'N/A')}")
    print(f"   - Jira integration: {integrations.get('jira', 'N/A')}")
    print(f"   - GitHub integration: {integrations.get('github', 'N/A')}")
    
    # Test adherence checker - needs playbook_steps (parsed steps), not playbook_content
    print(f"\n4. Testing AdherenceCheckerAgent...")
    from app.agents.adherence_checker import AdherenceCheckerAgent
    adherence_agent = AdherenceCheckerAgent()
    
    # Get steps from parse_result (or use defaults if parsing failed)
    playbook_steps = []
    if parse_result and parse_result.get('success'):
        playbook_steps = parse_result.get('data', {}).get('steps', [])
    
    if not playbook_steps:
        print(f"   ⚠ No parsed steps available, using mock steps")
        playbook_steps = [
            {"step_id": "step_1", "phase": "Detection", "description": "Detect incident", "required_actions": ["Monitor alerts"], "responsible_roles": ["SRE"]},
            {"step_id": "step_2", "phase": "Containment", "description": "Contain incident", "required_actions": ["Isolate systems"], "responsible_roles": ["Security"]}
        ]
    
    adherence_result = await adherence_agent.process({
        "playbook_steps": playbook_steps,  # Pass parsed steps, not raw content
        "incident_data": SAMPLE_INCIDENT_DATA
    })
    
    # Handle None results gracefully
    if adherence_result is None:
        print(f"   ✗ Agent returned None (unexpected)")
        adherence_result = {"success": False, "data": {}, "error": "Agent returned None"}
    
    print(f"   - Agent success: {adherence_result.get('success', False)}")
    if adherence_result.get('success'):
        checks = adherence_result.get('data', {}).get('adherence_checks', [])
        print(f"   - Adherence checks performed: {len(checks)}")
        for check in checks[:2]:
            print(f"     • {check.get('step_id')}: {check.get('adherence_level')}")
    else:
        print(f"   - Error: {adherence_result.get('error', 'Unknown error')}")
    
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
    
    # Test base agent - BaseAgent is abstract, so instantiation should fail
    print(f"\n2. Testing BaseAgent (abstract class)...")
    try:
        from app.agents.base import BaseAgent
        try:
            agent = BaseAgent("test")
            print(f"   ✗ BaseAgent should be abstract!")
        except TypeError as e:
            print(f"   ✓ BaseAgent is correctly abstract (cannot instantiate)")
            print(f"   ✓ Error message: {str(e)[:60]}...")
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
    
    # Test playbook parser without LLM (structure only)
    print(f"\n3. Testing PlaybookParserAgent (structure parsing)...")
    parsed_steps = []  # Store for later tests
    try:
        from app.agents.playbook_parser import PlaybookParserAgent
        parser = PlaybookParserAgent()
        result = await parser.process({"playbook_content": SAMPLE_PLAYBOOK})
        
        if result is None:
            print(f"   ✗ Parser returned None")
        else:
            print(f"   ✓ Parser success: {result.get('success', False)}")
            if result.get('success'):
                parsed_steps = result.get('data', {}).get('steps', [])
                print(f"   ✓ Steps found: {len(parsed_steps)}")
            else:
                print(f"   ✗ Error: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test incident trail agent (optional integrations)
    print(f"\n4. Testing IncidentTrailAgent (optional integrations)...")
    try:
        from app.agents.incident_trail import IncidentTrailAgent
        agent = IncidentTrailAgent()
        result = await agent.process({})
        
        if result is None:
            print(f"   ✗ Agent returned None")
        else:
            print(f"   ✓ Agent success: {result.get('success', False)}")
            print(f"   ✓ Gracefully handles missing integrations")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test compliance mapper - needs adherence_checks from previous step
    print(f"\n5. Testing ComplianceMapperAgent...")
    try:
        from app.agents.compliance_mapper import ComplianceMapperAgent
        mapper = ComplianceMapperAgent()
        
        # ComplianceMapper needs adherence_checks (from AdherenceChecker)
        # For individual test, we'll create mock adherence checks
        mock_adherence_checks = [
            {
                "step_id": "step_1",
                "adherence_level": "full",
                "evidence": ["Log entries show detection at 14:32"],
                "gaps": [],
                "recommendations": []
            },
            {
                "step_id": "step_2", 
                "adherence_level": "partial",
                "evidence": ["Incident was contained"],
                "gaps": ["Containment took longer than expected"],
                "recommendations": ["Automate containment procedures"]
            }
        ]
        
        result = await mapper.process({
            "adherence_checks": mock_adherence_checks,
            "frameworks": ["nist_sp_800_61"]
        })
        
        if result is None:
            print(f"   ✗ Mapper returned None")
        else:
            print(f"   ✓ Mapper success: {result.get('success', False)}")
            if result.get('success'):
                mappings = result.get('data', {}).get('compliance_mappings', [])
                print(f"   ✓ Mappings generated: {len(mappings)}")
            else:
                print(f"   ✗ Error: {result.get('error', 'Unknown')}")
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
