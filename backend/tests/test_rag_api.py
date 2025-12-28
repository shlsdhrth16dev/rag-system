import pytest
from fastapi.testclient import TestClient

def test_read_stats(client: TestClient):
    """Test the stats endpoint returns 200 and expected structure"""
    response = client.get("/api/v1/rag/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "embedding_model" in data

def test_query_no_input(client: TestClient):
    """Test query endpoint with empty input returns error or valid response"""
    # Depending on validation, this might be 422 or handled
    response = client.post("/api/v1/rag/query", json={"query": ""})
    # Pydantic validation should catch empty string if constrained, or app logic
    # Assuming validation or handled. If constrained: 422.
    # Let's verify it doesn't crash 500.
    assert response.status_code in [200, 422, 400]

def test_upload_no_file(client: TestClient):
    """Test upload without file fails"""
    response = client.post("/api/v1/rag/upload")
    assert response.status_code == 422 # Missing form data

# Note: Integration tests with real DB/OpenAI would require mocking or a live env.
# For now, we test basic reachability and validation.
