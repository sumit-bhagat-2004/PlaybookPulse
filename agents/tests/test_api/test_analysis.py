"""Analysis endpoint tests"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_start_analysis_minimal():
    """Test starting an analysis with minimal data"""
    response = client.post("/api/v1/analysis/start", json={
        "playbook_content": "# Test Playbook\n## Step 1: Detection\n- Monitor alerts\n- Identify incident"
    })
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["analysis_id"].startswith("analysis_")
    assert data["status"] in ["pending", "in_progress"]
    assert data["message"] == "Analysis started successfully"


def test_start_analysis_with_frameworks():
    """Test starting an analysis with compliance frameworks"""
    response = client.post("/api/v1/analysis/start", json={
        "playbook_content": "# Security Incident Playbook\n## Step 1\n- Action 1",
        "compliance_frameworks": ["nist_sp_800_61", "iso_27001_a16"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data


def test_list_analyses():
    """Test listing analyses"""
    response = client.get("/api/v1/analysis")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_analysis():
    """Test getting an analysis that doesn't exist"""
    response = client.get("/api/v1/analysis/nonexistent-id-12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_start_analysis_invalid_data():
    """Test starting an analysis with invalid data"""
    response = client.post("/api/v1/analysis/start", json={
        "invalid_field": "should fail"
    })
    assert response.status_code == 422  # Validation error


def test_report_for_incomplete_analysis():
    """Test generating report for incomplete analysis"""
    # First create an analysis
    create_response = client.post("/api/v1/analysis/start", json={
        "playbook_content": "# Test\n## Step 1\n- Action"
    })
    assert create_response.status_code == 200
    analysis_id = create_response.json()["analysis_id"]
    
    # Try to generate report immediately (should fail - not completed)
    report_response = client.post(f"/api/v1/analysis/{analysis_id}/report", json={
        "format": "pdf",
        "include_recommendations": True,
        "include_evidence": True
    })
    # Should return 400 because analysis is not completed
    assert report_response.status_code == 400
    assert "not completed" in report_response.json()["detail"].lower()
