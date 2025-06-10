"""
Configuración global de pytest y fixtures compartidas.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import tempfile
from fastapi.testclient import TestClient

# Agregar src al path para las importaciones
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configurar variables de entorno para testing ANTES de cualquier import
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("GENIA_API_KEY", "test-api-key-for-testing")
os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "8000")

# Ahora podemos importar nuestros módulos
from config import settings
from main import app
from services import GeniaAPIService
from models import QueryRequest, QueryResponse


@pytest.fixture(scope="session")
def test_settings():
    """Configuración de testing para toda la sesión"""
    return {
        "ENVIRONMENT": "testing",
        "LOG_LEVEL": "DEBUG",
        "DEBUG": True,
        "GENIA_API_KEY": "test-api-key-for-testing",
        "HOST": "127.0.0.1",
        "PORT": 8000
    }


@pytest.fixture
def client():
    """Cliente de testing para FastAPI"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_genia_service():
    """Mock del servicio GenIA para testing sin API real"""
    service = MagicMock(spec=GeniaAPIService)
    service.model_name = "mock-gemini-1.5-flash"
    service.api_key = "test-api-key"
    service.timeout = 30
    service.max_retries = 3
    
    # Mock query method
    async def mock_query(request: QueryRequest) -> QueryResponse:
        return QueryResponse(
            response=f"[MOCK] Respuesta para: {request.prompt[:50]}...",
            tokens_used=len(request.prompt.split()) * 2,
            model="mock-gemini-1.5-flash",
            processing_time=0.5,
            finish_reason="stop"
        )
    
    service.query = AsyncMock(side_effect=mock_query)
    
    # Mock query_mock method
    async def mock_query_mock(request: QueryRequest) -> QueryResponse:
        return QueryResponse(
            response=f"[MOCK] Mock response for: {request.prompt}",
            tokens_used=len(request.prompt.split()),
            model="mock-gemini-1.5-flash",
            processing_time=0.1,
            finish_reason="stop"
        )
    
    service.query_mock = AsyncMock(side_effect=mock_query_mock)
    
    # Mock health_check method
    service.health_check = AsyncMock(return_value=True)
    
    # Mock get_model_info method
    service.get_model_info = MagicMock(return_value={
        "model_name": "mock-gemini-1.5-flash",
        "client_configured": True,
        "api_key_set": True,
        "capabilities": {
            "text_generation": True,
            "multimodal": True,
            "long_context": True
        }
    })
    
    return service


@pytest.fixture
def sample_query_request():
    """Request de ejemplo para testing"""
    return QueryRequest(
        prompt="¿Qué es la inteligencia artificial?",
        max_tokens=100,
        temperature=0.7,
        top_p=0.9,
        top_k=40
    )


@pytest.fixture
def invalid_query_request():
    """Request inválido para testing de validación"""
    return {
        "prompt": "",  # Prompt vacío (inválido)
        "max_tokens": 10000,  # Excede límite
        "temperature": 3.0  # Fuera de rango
    }


@pytest.fixture
def temp_log_dir():
    """Directorio temporal para logs durante testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(autouse=True)
def setup_logging_for_tests(temp_log_dir):
    """Configurar logging para tests sin interferir con logs reales"""
    from logging_config import setup_logging
    
    # Configurar logging temporal para tests
    setup_logging(
        log_level="DEBUG",
        log_dir=str(temp_log_dir),
        enable_console=False,  # No spamear la consola durante tests
        enable_file=True,
        log_file="test.log"
    )


@pytest.fixture
def mock_google_client():
    """Mock del cliente de Google para testing sin llamadas reales"""
    mock_client = MagicMock()
    
    # Mock response object
    mock_response = MagicMock()
    mock_response.text = "Esta es una respuesta simulada de Google Gemini para testing."
    
    # Mock generate_content method
    mock_client.models.generate_content.return_value = mock_response
    
    return mock_client


# Configuración de markers para categorizar tests
def pytest_configure(config):
    """Configurar markers personalizados"""
    config.addinivalue_line("markers", "unit: marca tests como unitarios")
    config.addinivalue_line("markers", "integration: marca tests como de integración")
    config.addinivalue_line("markers", "slow: marca tests como lentos")
    config.addinivalue_line("markers", "api: marca tests que requieren API externa")


# Hook para ejecutar setup antes de todos los tests
def pytest_sessionstart(session):
    """Setup que se ejecuta al inicio de la sesión de testing"""
    print("\n🧪 Iniciando suite de tests para Genia Service")
    print(f"📁 Directorio de proyecto: {project_root}")
    print(f"🔧 Configuración: {settings.ENVIRONMENT}")


# Hook para cleanup después de todos los tests
def pytest_sessionfinish(session, exitstatus):
    """Cleanup que se ejecuta al final de la sesión de testing"""
    print(f"\n✅ Tests completados con código de salida: {exitstatus}")


# Función para generar datos de test
def generate_test_prompts():
    """Genera prompts de ejemplo para testing"""
    return [
        "¿Qué es la inteligencia artificial?",
        "Explica el concepto de machine learning",
        "¿Cómo funciona una red neuronal?",
        "Dame un ejemplo de uso de FastAPI",
        "¿Cuáles son las ventajas de Python?"
    ] 