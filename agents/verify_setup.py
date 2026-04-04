#!/usr/bin/env python3
"""
Verification script for PlaybookPulse Multi-Agent Backend
Checks that all components are properly set up
"""
import os
import sys
import json
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: NOT FOUND - {filepath}")
        return False


def check_directory_structure():
    """Verify directory structure"""
    print("\n=== Checking Directory Structure ===\n")
    
    dirs = [
        ("app", "Main application directory"),
        ("app/agents", "Multi-agent system"),
        ("app/api/v1", "API v1 endpoints"),
        ("app/integrations", "External integrations"),
        ("app/models", "Data models"),
        ("app/services", "Business logic services"),
        ("app/utils", "Utilities"),
        ("app/data/compliance", "Compliance frameworks"),
        ("app/data/fixtures", "Sample data"),
        ("tests", "Test suite"),
        ("scripts", "Utility scripts"),
        ("logs", "Log files")
    ]
    
    all_ok = True
    for dir_path, description in dirs:
        if os.path.isdir(dir_path):
            print(f"✓ {description}: {dir_path}/")
        else:
            print(f"✗ {description}: NOT FOUND - {dir_path}/")
            all_ok = False
    
    return all_ok


def check_core_files():
    """Check core application files"""
    print("\n=== Checking Core Application Files ===\n")
    
    files = [
        ("app/__init__.py", "App package init"),
        ("app/main.py", "FastAPI application"),
        ("app/config.py", "Configuration"),
        ("app/dependencies.py", "Dependencies"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok


def check_agents():
    """Check multi-agent system files"""
    print("\n=== Checking Multi-Agent System ===\n")
    
    files = [
        ("app/agents/__init__.py", "Agents package"),
        ("app/agents/base.py", "Base agent class"),
        ("app/agents/orchestrator.py", "Orchestrator agent"),
        ("app/agents/playbook_parser.py", "Playbook parser agent"),
        ("app/agents/incident_trail.py", "Incident trail agent"),
        ("app/agents/adherence_checker.py", "Adherence checker agent"),
        ("app/agents/compliance_mapper.py", "Compliance mapper agent"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok


def check_api():
    """Check API files"""
    print("\n=== Checking API Layer ===\n")
    
    files = [
        ("app/api/__init__.py", "API package"),
        ("app/api/v1/__init__.py", "API v1 package"),
        ("app/api/v1/router.py", "Main router"),
        ("app/api/v1/health.py", "Health endpoints"),
        ("app/api/v1/analysis.py", "Analysis endpoints"),
        ("app/api/v1/websocket.py", "WebSocket endpoints"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok


def check_integrations():
    """Check integration files"""
    print("\n=== Checking Integrations ===\n")
    
    files = [
        ("app/integrations/__init__.py", "Integrations package"),
        ("app/integrations/anthropic_client.py", "Anthropic/Claude client"),
        ("app/integrations/slack_client.py", "Slack client"),
        ("app/integrations/jira_client.py", "Jira client"),
        ("app/integrations/github_client.py", "GitHub client"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok


def check_compliance_data():
    """Check compliance framework data"""
    print("\n=== Checking Compliance Framework Data ===\n")
    
    files = [
        ("app/data/compliance/nist_sp_800_61.json", "NIST SP 800-61"),
        ("app/data/compliance/soc2_cc7.json", "SOC 2 CC7"),
        ("app/data/compliance/iso_27001_a16.json", "ISO 27001 A.16"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if check_file_exists(filepath, description):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    print(f"  → Loaded: {data.get('name', 'Unknown')}")
            except json.JSONDecodeError:
                print(f"  → WARNING: Invalid JSON in {filepath}")
                all_ok = False
        else:
            all_ok = False
    
    return all_ok


def check_fixtures():
    """Check sample data fixtures"""
    print("\n=== Checking Sample Fixtures ===\n")
    
    files = [
        ("app/data/fixtures/playbook_sample.md", "Sample playbook"),
        ("app/data/fixtures/slack_thread.json", "Sample Slack thread"),
        ("app/data/fixtures/jira_ticket.json", "Sample Jira ticket"),
        ("app/data/fixtures/github_events.json", "Sample GitHub events"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok


def check_config_files():
    """Check configuration files"""
    print("\n=== Checking Configuration Files ===\n")
    
    files = [
        ("requirements.txt", "Python dependencies"),
        (".env.example", "Environment template"),
        (".gitignore", "Git ignore rules"),
        ("setup.py", "Package setup"),
        ("Dockerfile", "Docker image definition"),
        ("docker-compose.yml", "Docker Compose config"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok


def check_documentation():
    """Check documentation files"""
    print("\n=== Checking Documentation ===\n")
    
    files = [
        ("README.md", "Main README"),
        ("SETUP_GUIDE.md", "Setup instructions"),
        ("API_DOCUMENTATION.md", "API reference"),
        ("IMPLEMENTATION_SUMMARY.md", "Implementation summary"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if check_file_exists(filepath, description):
            size = os.path.getsize(filepath)
            print(f"  → Size: {size:,} bytes")
        else:
            all_ok = False
    
    return all_ok


def check_scripts():
    """Check utility scripts"""
    print("\n=== Checking Utility Scripts ===\n")
    
    files = [
        ("scripts/setup_fixtures.py", "Setup fixtures"),
        ("scripts/run_demo.py", "Run demo"),
        ("scripts/reset_demo_env.py", "Reset environment"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok


def check_environment():
    """Check environment configuration"""
    print("\n=== Checking Environment Configuration ===\n")
    
    if os.path.exists(".env"):
        print("✓ .env file exists")
        try:
            with open(".env", 'r') as f:
                content = f.read()
                if "ANTHROPIC_API_KEY" in content:
                    if "your-api-key" in content or "sk-ant-your" in content:
                        print("  ⚠ WARNING: ANTHROPIC_API_KEY needs to be set to actual key")
                        return False
                    else:
                        print("  ✓ ANTHROPIC_API_KEY appears to be configured")
                        return True
                else:
                    print("  ✗ ANTHROPIC_API_KEY not found in .env")
                    return False
        except Exception as e:
            print(f"  ✗ Error reading .env: {e}")
            return False
    else:
        print("⚠ .env file not found (copy from .env.example)")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("PlaybookPulse Multi-Agent Backend - Verification Check")
    print("=" * 60)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Core Files", check_core_files),
        ("Multi-Agent System", check_agents),
        ("API Layer", check_api),
        ("Integrations", check_integrations),
        ("Compliance Data", check_compliance_data),
        ("Sample Fixtures", check_fixtures),
        ("Configuration Files", check_config_files),
        ("Documentation", check_documentation),
        ("Utility Scripts", check_scripts),
        ("Environment", check_environment),
    ]
    
    results = []
    
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60 + "\n")
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Backend is ready to use.")
        print("\nNext steps:")
        print("1. Ensure .env has your ANTHROPIC_API_KEY")
        print("2. Activate virtual environment: source venv/bin/activate")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Start server: uvicorn app.main:app --reload")
        print("5. Visit http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠ Some checks failed. Review the output above.")
        print("\nRefer to SETUP_GUIDE.md for detailed setup instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
