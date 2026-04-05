"""
Quick test to verify incident data is being properly passed to agents
"""
import asyncio
import json
from pathlib import Path
from agents_bridge import AgentsBridge

async def test_analysis_with_fixtures():
    """Test analysis with fixture data"""
    
    # Load playbook
    playbook_path = Path(__file__).parent / "fixtures" / "playbook_comprehensive.md"
    with open(playbook_path) as f:
        playbook_content = f.read()
    
    # Load fixture incident data
    slack_fixture_path = Path(__file__).parent / "fixtures" / "slack_thread.json"
    jira_fixture_path = Path(__file__).parent / "fixtures" / "jira_ticket.json"
    
    with open(slack_fixture_path) as f:
        slack_messages = json.load(f)
        slack_data = {
            "messages": slack_messages,
            "participants": list(set(m.get("user") for m in slack_messages)),
            "timeline": [{"timestamp": m.get("timestamp"), "text": m.get("text")} for m in slack_messages]
        }
    
    with open(jira_fixture_path) as f:
        jira_ticket = json.load(f)
        jira_data = {
            "issue": jira_ticket,
            "comments": [],
            "timeline": jira_ticket.get("events", [])
        }
    
    print("=" * 60)
    print("Testing PlaybookPulse Analysis with Fixture Data")
    print("=" * 60)
    print(f"\n✅ Loaded playbook: {len(playbook_content)} characters")
    print(f"✅ Loaded {len(slack_messages)} Slack messages")
    print(f"✅ Loaded Jira ticket: {jira_ticket.get('ticket_id')}")
    
    # Run analysis
    print("\n🚀 Running multi-agent analysis...")
    bridge = AgentsBridge()
    
    result = await bridge.analyze_incident(
        playbook_content=playbook_content,
        slack_thread_data=slack_data,
        jira_ticket_data=jira_data,
        compliance_frameworks=["nist_sp_800_61"]
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    if result.get("status") == "error":
        print(f"\n❌ ERROR: {result.get('error')}")
        if result.get("traceback"):
            print(f"\nTraceback:\n{result.get('traceback')}")
        return
    
    print(f"\n✅ Status: {result.get('status')}")
    print(f"📊 Timestamp: {result.get('timestamp')}")
    
    # Playbook info
    playbook_info = result.get("playbook", {})
    print(f"\n📖 Playbook: {playbook_info.get('title')}")
    print(f"   Steps parsed: {playbook_info.get('total_steps')}")
    print(f"   Phases: {', '.join(playbook_info.get('phases', []))}")
    
    # Adherence results
    adherence = result.get("adherence", {})
    print(f"\n📈 Adherence Score: {adherence.get('overall_score', 0):.1f}%")
    print(f"   ✅ Full adherence: {adherence.get('full_adherence', 0)} steps")
    print(f"   ⚠️  Partial adherence: {adherence.get('partial_adherence', 0)} steps")
    print(f"   ❌ No adherence: {adherence.get('no_adherence', 0)} steps")
    
    # Check if incident data was used
    checks = adherence.get("checks", [])
    print(f"\n🔍 Adherence Checks: {len(checks)} total")
    
    if checks:
        # Show first few checks
        print("\n   Sample checks:")
        for i, check in enumerate(checks[:3], 1):
            step_id = check.get("step_id", "Unknown")
            level = check.get("adherence_level", "unknown")
            evidence = check.get("evidence", [])
            print(f"\n   {i}. {step_id}")
            print(f"      Level: {level}")
            print(f"      Evidence count: {len(evidence)}")
            if evidence:
                print(f"      Sample: {evidence[0][:80]}...")
    
    # Incident data status
    incident_info = result.get("incident_data", {})
    print(f"\n📦 Incident Data Sources:")
    print(f"   Slack: {'✅ Available' if incident_info.get('slack_available') else '❌ Not available'}")
    print(f"   Jira: {'✅ Available' if incident_info.get('jira_available') else '❌ Not available'}")
    print(f"   GitHub: {'✅ Available' if incident_info.get('github_available') else '❌ Not available'}")
    
    # Recommendations
    recommendations = result.get("recommendations", [])
    print(f"\n💡 Recommendations: {len(recommendations)}")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_analysis_with_fixtures())
