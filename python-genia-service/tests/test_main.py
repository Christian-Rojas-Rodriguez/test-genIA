"""
Tests para los endpoints principales.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_health_endpoint():
    """Test del health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_query_mock_endpoint():
    """Test del endpoint mock"""
    payload = {
        "prompt": "Test prompt",
        "max_tokens": 100,
        "temperature": 0.5
    }
    response = client.post("/query/mock", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "tokens_used" in data
    assert "model" in data

def test_query_mock_invalid_prompt():
    """Test con prompt inválido"""
    payload = {
        "prompt": "",  # Prompt vacío
        "max_tokens": 100
    }
    response = client.post("/query/mock", json=payload)
    assert response.status_code == 422  # Validation error

def test_query_mock_invalid_tokens():
    """Test con tokens inválidos"""
    payload = {
        "prompt": "Test prompt",
        "max_tokens": 5000  # Excede el límite
    }
    response = client.post("/query/mock", json=payload)
    assert response.status_code == 422  # Validation error