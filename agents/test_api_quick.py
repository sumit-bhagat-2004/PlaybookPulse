"""
Test the API endpoints using the test client
No external integrations needed
"""
import asyncio
import json
from httpx import AsyncClient
from tests.fixtures import SAMPLE_PLAYBOOK
from app.main import app
from app.models.schemas import ComplianceFramework


async def test_api_endpoints():
    """Test all major API endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        print("=" * 60)
        print("Testing PlaybookPulse API Endpoints")
        print("=" * 60)
        
        # 1. Health check
        print("\n1. Testing GET /api/v1/health")
        response = await client.get("/api/v1/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # 2. Start analysis
        print("\n2. Testing POST /api/v1/analysis/start")
        request_data = {
            "playbook_content": SAMPLE_PLAYBOOK,
            "compliance_frameworks": ["nist_sp_800_61"]
        }
        response = await client.post(
            "/api/v1/analysis/start",
            json=request_data
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        if response.status_code == 200:
            analysis_id = data.get("analysis_id")
            print(f"   ✓ Analysis started with ID: {analysis_id}")
            
            # Wait a bit for analysis to start
            await asyncio.sleep(2)
            
            # 3. Get analysis status
            print(f"\n3. Testing GET /api/v1/analysis/{analysis_id}")
            response = await client.get(f"/api/v1/analysis/{analysis_id}")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Analysis status: {data.get('status')}")
            print(f"   Result available: {'result' in data and bool(data['result'])}")
            
            # 4. List analyses
            print(f"\n4. Testing GET /api/v1/analysis/list")
            response = await client.get("/api/v1/analysis/list")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Total analyses: {len(data.get('analyses', []))}")
            
        # 5. Metrics endpoint
        print(f"\n5. Testing GET /api/v1/metrics")
        response = await client.get("/api/v1/metrics")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Metrics available: {bool(data)}")
        if data:
            print(f"   - Total analyses: {data.get('total_analyses_completed')}")
            print(f"   - Avg duration: {data.get('average_analysis_duration_ms', 0):.1f}ms")
        
        print("\n" + "=" * 60)
        print("✅ API tests completed!")
        print("=" * 60)


async def test_analysis_download():
    """Test PDF report download (if analysis completes)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        print("\n" + "=" * 60)
        print("Testing PDF Report Download")
        print("=" * 60)
        
        # Start analysis
        print("\n1. Starting analysis...")
        request_data = {
            "playbook_content": SAMPLE_PLAYBOOK,
            "compliance_frameworks": ["nist_sp_800_61"]
        }
        response = await client.post(
            "/api/v1/analysis/start",
            json=request_data
        )
        
        if response.status_code == 200:
            analysis_id = response.json().get("analysis_id")
            print(f"   ✓ Analysis ID: {analysis_id}")
            
            # Wait for analysis to complete
            print(f"\n2. Waiting for analysis to complete...")
            max_wait = 30
            for i in range(max_wait):
                await asyncio.sleep(1)
                status_response = await client.get(f"/api/v1/analysis/{analysis_id}")
                status = status_response.json().get("status")
                if status == "completed":
                    print(f"   ✓ Analysis completed after {i+1}s")
                    break
                elif i % 5 == 0:
                    print(f"   Waiting... ({status}) - {i+1}s elapsed")
            
            # Try to download report
            print(f"\n3. Testing GET /api/v1/analysis/{analysis_id}/report")
            response = await client.get(f"/api/v1/analysis/{analysis_id}/report")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✓ Report downloaded ({len(response.content)} bytes)")
            else:
                print(f"   Note: {response.status_code} - {response.text[:100]}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\nPlaybookPulse API Test Suite\n")
    
    # Test endpoints
    asyncio.run(test_api_endpoints())
    
    # Test PDF download
    asyncio.run(test_analysis_download())
