"""
Simple startup verification - checks if app can start without errors
"""
import sys


def verify_imports():
    """Verify all critical imports work"""
    print("Verifying imports...")
    
    checks = [
        ("app.main", lambda: __import__("app.main")),
        ("app.config", lambda: __import__("app.config")),
        ("app.services.analysis_service", lambda: __import__("app.services.analysis_service")),
        ("app.agents.orchestrator", lambda: __import__("app.agents.orchestrator")),
        ("app.integrations.llm_client", lambda: __import__("app.integrations.llm_client")),
        ("app.integrations.gemini_client", lambda: __import__("app.integrations.gemini_client")),
        ("Async environment", lambda: __import__("asyncio")),
        ("FastAPI", lambda: __import__("fastapi")),
        ("Pydantic", lambda: __import__("pydantic")),
    ]
    
    failed = []
    for name, importer in checks:
        try:
            importer()
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            failed.append((name, str(e)))
    
    return len(failed) == 0, failed


def verify_config():
    """Verify configuration loads"""
    print("\nVerifying configuration...")
    
    try:
        from app.config import settings
        
        checks = {
            "Environment": settings.environment,
            "API Host": settings.api_host,
            "API Port": settings.api_port,
            "LLM Provider": settings.llm_provider,
            "Log Level": settings.log_level,
            "Agent Timeout": settings.agent_timeout,
            "Analysis Timeout": settings.analysis_timeout,
        }
        
        for name, value in checks.items():
            print(f"  ✓ {name}: {value}")
        
        # Check required keys
        if not settings.gemini_api_key and not settings.anthropic_api_key:
            print(f"  ⚠ Warning: No LLM API key configured")
            print(f"    - Set GEMINI_API_KEY or ANTHROPIC_API_KEY")
        
        return True, {}
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False, {"config": str(e)}


def verify_services():
    """Verify services initialize"""
    print("\nVerifying services...")
    
    try:
        from app.services.analysis_service import AnalysisService, _analyses_store
        print(f"  ✓ AnalysisService loaded")
        print(f"  ✓ Shared state (_analyses_store) available: {isinstance(_analyses_store, dict)}")
        
        from app.services.websocket_manager import WebSocketManager
        print(f"  ✓ WebSocketManager loaded")
        
        from app.services.pdf_generator import PDFGenerator
        print(f"  ✓ PDFGenerator loaded")
        
        return True, {}
    except Exception as e:
        print(f"  ✗ Service error: {e}")
        return False, {"services": str(e)}


def verify_agents():
    """Verify agents initialize"""
    print("\nVerifying agents...")
    
    agents = [
        "app.agents.base",
        "app.agents.playbook_parser",
        "app.agents.incident_trail",
        "app.agents.adherence_checker",
        "app.agents.compliance_mapper",
        "app.agents.orchestrator",
    ]
    
    failed = []
    for agent_module in agents:
        try:
            __import__(agent_module)
            agent_name = agent_module.split(".")[-1]
            print(f"  ✓ {agent_name} loaded")
        except Exception as e:
            agent_name = agent_module.split(".")[-1]
            print(f"  ✗ {agent_name}: {e}")
            failed.append((agent_module, str(e)))
    
    return len(failed) == 0, {k: v for k, v in failed}


def verify_app():
    """Verify FastAPI app initializes"""
    print("\nVerifying FastAPI app...")
    
    try:
        from app.main import app
        print(f"  ✓ FastAPI app created")
        print(f"  ✓ Routes available: {len(app.routes)}")
        
        # Check critical routes
        route_paths = {r.path for r in app.routes if hasattr(r, "path")}
        critical_paths = [
            "/api/v1/health",
            "/api/v1/analysis/start",
            "/api/v1/analysis/list",
        ]
        
        for path in critical_paths:
            if path in route_paths:
                print(f"  ✓ Route: {path}")
            else:
                print(f"  ✗ Route missing: {path}")
        
        return True, {}
    except Exception as e:
        print(f"  ✗ App error: {e}")
        return False, {"app": str(e)}


def main():
    """Run all verifications"""
    print("=" * 60)
    print("PlaybookPulse Startup Verification")
    print("=" * 60)
    
    results = []
    
    # Run checks
    results.append(("Imports", *verify_imports()))
    results.append(("Configuration", *verify_config()))
    results.append(("Services", *verify_services()))
    results.append(("Agents", *verify_agents()))
    results.append(("FastAPI App", *verify_app()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed, errors in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
        if errors:
            for error_key, error_msg in errors.items():
                print(f"       {error_key}: {error_msg[:50]}...")
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All checks passed! Server is ready to start.\n")
        print("To start the server:")
        print("  python -m uvicorn app.main:app --reload\n")
        print("To run agent tests:")
        print("  python test_agents_quick.py\n")
        print("To run API tests (with server running):")
        print("  python test_api_quick.py\n")
        return 0
    else:
        print("\n❌ Some checks failed. See details above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
