"""
Quick test to verify CIS compliance is working after fixes
"""
import sys
import os

print("=" * 70)
print("CIS Compliance Fix Verification")
print("=" * 70)

# Test 1: Check python-dateutil
print("\n[TEST 1] Checking python-dateutil dependency...")
try:
    import dateutil
    print(f"  [OK] python-dateutil is installed: version {dateutil.__version__}")
except ImportError as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

# Test 2: Check timestamp analyzer
print("\n[TEST 2] Loading TimestampAnalyzer...")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))
try:
    from app.compliance.timestamp_analyzer import TimestampAnalyzer
    analyzer = TimestampAnalyzer()
    print(f"  [OK] TimestampAnalyzer loaded successfully")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check CIS framework
print("\n[TEST 3] Loading CIS Framework...")
try:
    from app.compliance.cis_framework import (
        get_cis_requirements_for_step,
        calculate_sla_violation_severity,
        SLAViolationSeverity
    )
    
    # Test getting requirements
    req = get_cis_requirements_for_step("detection", "Detection")
    print(f"  [OK] CIS framework loaded")
    print(f"    - Phase: {req['cis_phase']}")
    print(f"    - SLA: {req['sla_minutes']} minutes")
    print(f"    - Controls: {req['cis_controls']}")
    
    # Test SLA calculation
    severity = calculate_sla_violation_severity(15, 185)
    print(f"  [OK] SLA violation severity: {severity.value} (185min vs 15min expected)")
    
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check CIS Compliance Agent
print("\n[TEST 4] Loading CIS Compliance Agent...")
try:
    from app.compliance.cis_compliance_agent import CISComplianceAgent
    
    # Initialize without API key (will use fallback mode)
    agent = CISComplianceAgent(google_api_key=None, use_langchain=False)
    print(f"  [OK] CIS Compliance Agent loaded (fallback mode)")
    print(f"    - Using LangChain: {agent.use_langchain}")
    
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test timestamp extraction
print("\n[TEST 5] Testing timestamp extraction from fixture data...")
try:
    import json
    from pathlib import Path
    
    # Load fixture data
    fixtures_dir = Path(__file__).parent / "fixtures"
    slack_path = fixtures_dir / "slack_thread.json"
    
    if not slack_path.exists():
        print(f"  [WARN] Fixture not found: {slack_path}")
    else:
        with open(slack_path) as f:
            slack_messages = json.load(f)
        
        # Create incident data structure
        incident_data = {
            "slack_messages": slack_messages,
            "jira_timeline": [],
            "github_events": []
        }
        
        # Extract timeline
        analyzer = TimestampAnalyzer()
        timeline = analyzer.extract_timeline_from_incident_data(incident_data)
        
        print(f"  [OK] Extracted {len(timeline)} timeline events")
        if timeline:
            print(f"    - Incident start: {analyzer.incident_start_time}")
            print(f"    - First event: {timeline[0]['action'][:50]}...")
            print(f"    - Last event: {timeline[-1]['action'][:50]}...")
    
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("[OK] ALL TESTS PASSED")
print("=" * 70)
print("\nCIS Compliance is ready to use!")
print("\nNext steps:")
print("1. Restart your API server if it's running")
print("2. Test the /analyze endpoint:")
print("   curl -X POST http://localhost:8000/analyze \\")
print("     -H 'Content-Type: application/json' \\")
print("     -d '{\"use_sample_playbook\": true}'")
print("3. Look for 'cis_compliance' in the response")
