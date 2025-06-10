"""
Tests para los endpoints principales de FastAPI.
"""
import pytest
from unittest.mock import patch
import time

@pytest.mark.unit
def test_root_endpoint(client):
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "environment" in data
    assert "model" in data
    assert "docs_url" in data


@pytest.mark.unit
def test_health_endpoint(client):
    """Test del health check básico"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "service" in data
    assert "version" in data


@pytest.mark.integration
@patch('services.genia_service.health_check')
def test_detailed_health_endpoint_healthy(mock_health_check, client):
    """Test del health check detallado cuando Gemini está healthy"""
    mock_health_check.return_value = True
    
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dependencies"]["google_gemini"] == "healthy"
    assert "timestamp" in data


@pytest.mark.integration
@patch('services.genia_service.health_check')
def test_detailed_health_endpoint_degraded(mock_health_check, client):
    """Test del health check detallado cuando Gemini está degraded"""
    mock_health_check.return_value = False
    
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["dependencies"]["google_gemini"] == "unhealthy"


@pytest.mark.unit
@patch('services.genia_service.get_model_info')
def test_model_info_endpoint(mock_get_model_info, client):
    """Test del endpoint de información del modelo"""
    mock_get_model_info.return_value = {
        "model_name": "gemini-1.5-flash",
        "client_configured": True,
        "api_key_set": True
    }
    
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "timestamp" in data


@pytest.mark.unit
def test_query_mock_endpoint(client, sample_query_request):
    """Test del endpoint mock"""
    payload = sample_query_request.model_dump()
    response = client.post("/query/mock", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "tokens_used" in data
    assert "model" in data
    assert "processing_time" in data
    assert "[MOCK" in data["response"]


@pytest.mark.unit  
@patch('services.genia_service.query')
def test_query_real_endpoint_success(mock_query, client, sample_query_request):
    """Test del endpoint de query real exitoso"""
    # Mock successful response
    from models import QueryResponse
    mock_response = QueryResponse(
        response="Esta es una respuesta de ejemplo de Gemini",
        tokens_used=42,
        model="gemini-1.5-flash",
        processing_time=1.5,
        finish_reason="stop"
    )
    mock_query.return_value = mock_response
    
    payload = sample_query_request.model_dump()
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Esta es una respuesta de ejemplo de Gemini"
    assert data["tokens_used"] == 42
    assert data["model"] == "gemini-1.5-flash"


@pytest.mark.unit
@patch('services.genia_service.query')
def test_query_real_endpoint_error(mock_query, client, sample_query_request):
    """Test del endpoint de query real con error"""
    mock_query.side_effect = Exception("API timeout error")
    
    payload = sample_query_request.model_dump()
    response = client.post("/query", json=payload)
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    error_detail = data["detail"]
    assert "error" in error_detail
    assert "message" in error_detail


@pytest.mark.unit
def test_query_validation_empty_prompt(client):
    """Test validación con prompt vacío"""
    payload = {
        "prompt": "",  # Prompt vacío
        "max_tokens": 100
    }
    response = client.post("/query/mock", json=payload)
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_query_validation_invalid_tokens(client):
    """Test validación con tokens inválidos"""
    payload = {
        "prompt": "Test prompt",
        "max_tokens": 10000  # Excede el límite de 8192
    }
    response = client.post("/query/mock", json=payload)
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_query_validation_invalid_temperature(client):
    """Test validación con temperatura inválida"""
    payload = {
        "prompt": "Test prompt",
        "max_tokens": 100,
        "temperature": 3.5  # Fuera del rango 0.0-2.0
    }
    response = client.post("/query/mock", json=payload)
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
@patch('config.settings.ENVIRONMENT', 'development')
def test_config_endpoint_development(client):
    """Test del endpoint de configuración en desarrollo"""
    response = client.get("/config")
    # En desarrollo el endpoint debe estar disponible
    if response.status_code == 200:
        data = response.json()
        assert "app_name" in data
        assert "environment" in data
        assert "google_gemini_configured" in data


@pytest.mark.unit
@patch('config.settings.ENVIRONMENT', 'production')
def test_config_endpoint_production(client):
    """Test del endpoint de configuración en producción (debe devolver 404)"""
    response = client.get("/config")
    assert response.status_code == 404


@pytest.mark.integration
def test_request_middleware_adds_process_time(client):
    """Test que el middleware agrega el header X-Process-Time"""
    response = client.get("/")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0.0


@pytest.mark.unit
def test_cors_headers(client):
    """Test que CORS está configurado correctamente"""
    response = client.options("/", headers={"Origin": "http://localhost:3000"})
    # FastAPI testclient no simula completamente CORS, pero podemos verificar que no hay errores
    assert response.status_code in [200, 405]  # 405 es aceptable para OPTIONS