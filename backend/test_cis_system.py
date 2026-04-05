"""
Test CIS-Only Compliance System

Tests both pre-PR and post-merge endpoints.
"""
import asyncio
import sys
from pathlib import Path

# Add parent dirs to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

async def test_cis_system():
    """Test the CIS-only compliance system"""
    from agents_bridge import AgentsBridge
    import json
    
    print("=" * 60)
    print("PlaybookPulse CIS-Only Compliance System Test")
    print("=" * 60)
    
    # Initialize bridge
    bridge = AgentsBridge()
    
    # Load test playbook
    playbook_path = Path(__file__).parent / "fixtures" / "playbook_comprehensive.md"
    if playbook_path.exists():
        with open(playbook_path) as f:
            playbook_content = f.read()
    else:
        playbook_content = """# Test Playbook
## Detection Phase
- Alert acknowledgment within 15 minutes
- Incident commander assigned
## Containment Phase  
- Isolate affected systems
- Block malicious IPs
"""
    
    # Load test incident data
    slack_data = None
    jira_data = None
    
    slack_path = Path(__file__).parent / "fixtures" / "slack_thread.json"
    if slack_path.exists():
        with open(slack_path) as f:
            messages = json.load(f)
            slack_data = {"messages": messages}
    
    jira_path = Path(__file__).parent / "fixtures" / "jira_ticket.json"
    if jira_path.exists():
        with open(jira_path) as f:
            jira_data = json.load(f)
    
    # ============ Test 1: Pre-PR Static Check ============
    print("\n" + "=" * 60)
    print("TEST 1: Pre-PR Static CIS Compliance Check")
    print("=" * 60)
    
    pre_pr_result = await bridge.check_pre_pr(
        playbook_content=playbook_content
    )
    
    print(f"\nStatus: {pre_pr_result.get('overall_status', 'N/A')}")
    print(f"Compliance Score: {pre_pr_result.get('compliance_score', 'N/A')}%")
    print(f"Controls Checked: {len(pre_pr_result.get('controls_checked', []))}")
    print(f"Blocking Issues: {len(pre_pr_result.get('blocking_issues', []))}")
    print(f"Warnings: {len(pre_pr_result.get('warnings', []))}")
    
    if pre_pr_result.get('blocking_issues'):
        print("\nBlocking Issues:")
        for issue in pre_pr_result['blocking_issues'][:3]:
            print(f"  - {issue}")
    
    # ============ Test 2: Post-Merge Dynamic Check ============
    print("\n" + "=" * 60)
    print("TEST 2: Post-Merge Dynamic CIS Compliance Check")
    print("=" * 60)
    
    post_merge_result = await bridge.check_post_merge(
        playbook_content=playbook_content,
        slack_thread_data=slack_data,
        jira_ticket_data=jira_data
    )
    
    print(f"\nStatus: {post_merge_result.get('overall_status', 'N/A')}")
    print(f"Compliance Score: {post_merge_result.get('compliance_score', 'N/A')}%")
    print(f"Controls Checked: {len(post_merge_result.get('controls_checked', []))}")
    print(f"Violations: {len(post_merge_result.get('violations', []))}")
    
    # SLA compliance
    sla = post_merge_result.get('sla_compliance', {})
    print(f"\nSLA Compliance:")
    print(f"  Status: {sla.get('status', 'N/A')}")
    print(f"  Checks: {sla.get('total_checks', 0)}")
    print(f"  Violations: {sla.get('violations', 0)}")
    
    # ============ Test 3: Full Analysis ============
    print("\n" + "=" * 60)
    print("TEST 3: Full Incident Analysis (CIS Controls v8)")
    print("=" * 60)
    
    analysis_result = await bridge.analyze_incident(
        playbook_content=playbook_content,
        slack_thread_data=slack_data,
        jira_ticket_data=jira_data
    )
    
    print(f"\nStatus: {analysis_result.get('status', 'N/A')}")
    print(f"Framework: {analysis_result.get('framework', 'N/A')}")
    
    adherence = analysis_result.get('adherence', {})
    print(f"\nAdherence:")
    print(f"  Overall Score: {adherence.get('overall_score', 'N/A')}%")
    print(f"  Full: {adherence.get('full_adherence', 0)}")
    print(f"  Partial: {adherence.get('partial_adherence', 0)}")
    print(f"  None: {adherence.get('no_adherence', 0)}")
    
    cis = analysis_result.get('cis_compliance', {})
    if cis:
        print(f"\nCIS Compliance:")
        print(f"  Framework: {cis.get('framework', 'N/A')}")
        print(f"  Mappings: {len(cis.get('mappings', []))}")
        
        dynamic = cis.get('dynamic_analysis', {})
        if dynamic:
            print(f"  Dynamic Score: {dynamic.get('compliance_score', 'N/A')}%")
    
    recs = analysis_result.get('recommendations', [])
    if recs:
        print(f"\nRecommendations ({len(recs)}):")
        for rec in recs[:5]:
            print(f"  - {rec[:100]}...")
    
    # ============ Summary ============
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Pre-PR Check: {'PASS' if pre_pr_result.get('overall_status') == 'pass' else 'FAIL/WARN'}")
    print(f"Post-Merge Check: {'COMPLIANT' if post_merge_result.get('overall_status') == 'compliant' else 'NON-COMPLIANT'}")
    print(f"Full Analysis: {'COMPLETED' if analysis_result.get('status') == 'completed' else 'ERROR'}")
    print("=" * 60)
    
    return {
        "pre_pr": pre_pr_result,
        "post_merge": post_merge_result,
        "analysis": analysis_result
    }


if __name__ == "__main__":
    results = asyncio.run(test_cis_system())
    
    # Save results
    import json
    output_path = Path(__file__).parent / "test_cis_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")
