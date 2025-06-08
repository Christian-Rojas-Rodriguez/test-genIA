"""
Tests para los servicios.
"""
import pytest
from src.services import GeniaAPIService
from src.models import QueryRequest

@pytest.fixture
def genia_service():
    """Fixture para el servicio GenIA"""
    return GeniaAPIService()

@pytest.fixture
def sample_request():
    """Fixture para request de ejemplo"""
    return QueryRequest(
        prompt="Test prompt",
        max_tokens=100,
        temperature=0.7
    )

@pytest.mark.asyncio
async def test_query_mock(genia_service, sample_request):
    """Test del método mock"""
    response = await genia_service.query_mock(sample_request)
    
    assert response.response is not None
    assert "[MOCK]" in response.response
    assert response.tokens_used > 0
    assert response.model == "mock-genia"
    assert response.processing_time is not None

@pytest.mark.asyncio
async def test_health_check(genia_service):
    """Test del health check"""
    # Este test podría fallar si no hay conectividad real
    # En un entorno de CI/CD, podrías usar mocks
    result = await genia_service.health_check()
    assert isinstance(result, bool)