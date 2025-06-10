"""
Tests para los servicios de negocio.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from services import GeniaAPIService
from models import QueryRequest, QueryResponse
import asyncio


class TestGeniaAPIService:
    """Test suite para GeniaAPIService"""
    
    @pytest.fixture
    def service_with_api_key(self):
        """Servicio configurado con API key"""
        with patch('config.settings.GENIA_API_KEY', 'test-api-key'):
            return GeniaAPIService()
    
    @pytest.fixture
    def service_without_api_key(self):
        """Servicio sin API key configurada"""
        with patch('config.settings.GENIA_API_KEY', None):
            return GeniaAPIService()
    
    @pytest.mark.unit
    def test_service_initialization_with_api_key(self, service_with_api_key):
        """Test inicialización del servicio con API key"""
        assert service_with_api_key.api_key == 'test-api-key'
        assert service_with_api_key.model_name == "gemini-1.5-flash"
        assert service_with_api_key.timeout == 30
        assert service_with_api_key.max_retries == 3
    
    @pytest.mark.unit
    def test_service_initialization_without_api_key(self, service_without_api_key):
        """Test inicialización del servicio sin API key"""
        assert service_without_api_key.api_key is None
        assert service_without_api_key.client is None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_query_mock_basic(self, service_with_api_key, sample_query_request):
        """Test del método query_mock básico"""
        response = await service_with_api_key.query_mock(sample_query_request)
        
        assert isinstance(response, QueryResponse)
        assert response.response is not None
        assert "[MOCK" in response.response
        assert response.tokens_used > 0
        assert response.model.startswith("mock-")
        assert response.processing_time is not None
        assert response.processing_time > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_query_mock_different_prompts(self, service_with_api_key):
        """Test query_mock con diferentes prompts"""
        prompts = [
            "Pregunta corta",
            "Esta es una pregunta mucho más larga que debería generar una respuesta diferente",
            "¿Cómo funciona la inteligencia artificial en el contexto de machine learning?"
        ]
        
        for prompt in prompts:
            request = QueryRequest(prompt=prompt, max_tokens=100, temperature=0.7)
            response = await service_with_api_key.query_mock(request)
            
            assert prompt in response.response
            assert response.tokens_used > 0
            assert response.processing_time > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_query_without_client_fails(self, service_without_api_key, sample_query_request):
        """Test que query falla sin cliente configurado"""
        with pytest.raises(Exception) as excinfo:
            await service_without_api_key.query(sample_query_request)
        
        assert "not configured" in str(excinfo.value)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('services.GeniaAPIService._generate_content_with_config')
    async def test_query_success(self, mock_generate, service_with_api_key, sample_query_request, mock_google_client):
        """Test query exitoso con mock"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = "Esta es una respuesta de prueba de Gemini"
        mock_generate.return_value = mock_response
        
        # Setup mock client
        service_with_api_key.client = mock_google_client
        
        # Execute query
        response = await service_with_api_key.query(sample_query_request)
        
        # Assertions
        assert isinstance(response, QueryResponse)
        assert response.response == "Esta es una respuesta de prueba de Gemini"
        assert response.tokens_used > 0
        assert response.model == "gemini-1.5-flash"
        assert response.processing_time > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('services.GeniaAPIService._generate_content_with_config')
    async def test_query_api_error(self, mock_generate, service_with_api_key, sample_query_request, mock_google_client):
        """Test query con error de API"""
        # Setup mock to raise exception
        mock_generate.side_effect = Exception("API timeout")
        service_with_api_key.client = mock_google_client
        
        with pytest.raises(Exception) as excinfo:
            await service_with_api_key.query(sample_query_request)
        
        assert "Google Gemini API error" in str(excinfo.value)
        assert "API timeout" in str(excinfo.value)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_without_client(self, service_without_api_key):
        """Test health check sin cliente configurado"""
        result = await service_without_api_key.health_check()
        assert result is False
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('services.GeniaAPIService._generate_content_with_config')
    async def test_health_check_success(self, mock_generate, service_with_api_key, mock_google_client):
        """Test health check exitoso"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = "OK"
        mock_generate.return_value = mock_response
        
        service_with_api_key.client = mock_google_client
        
        result = await service_with_api_key.health_check()
        assert result is True
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('services.GeniaAPIService._generate_content_with_config')
    async def test_health_check_failure(self, mock_generate, service_with_api_key, mock_google_client):
        """Test health check con fallo"""
        mock_generate.side_effect = Exception("Connection failed")
        service_with_api_key.client = mock_google_client
        
        result = await service_with_api_key.health_check()
        assert result is False
    
    @pytest.mark.unit
    def test_build_generation_config(self, service_with_api_key):
        """Test construcción de configuración de generación"""
        request = QueryRequest(
            prompt="Test",
            max_tokens=100,
            temperature=0.8,
            top_p=0.9,
            top_k=40
        )
        
        config = service_with_api_key._build_generation_config(request)
        
        assert config['max_output_tokens'] == 100
        assert config['temperature'] == 0.8
        assert config.get('top_p') == 0.9
        assert config.get('top_k') == 40
    
    @pytest.mark.unit
    def test_build_generation_config_defaults(self, service_with_api_key):
        """Test configuración con valores por defecto"""
        request = QueryRequest(prompt="Test")
        
        config = service_with_api_key._build_generation_config(request)
        
        assert config['max_output_tokens'] == 2048  # Default
        assert config['temperature'] == 0.7  # Default
    
    @pytest.mark.unit
    def test_estimate_tokens(self, service_with_api_key):
        """Test estimación de tokens"""
        # Test con texto corto
        short_text = "Hola mundo"
        tokens = service_with_api_key._estimate_tokens(short_text)
        assert tokens >= 1
        assert tokens < 10
        
        # Test con texto largo
        long_text = "Esta es una respuesta mucho más larga que debería generar más tokens " * 10
        tokens_long = service_with_api_key._estimate_tokens(long_text)
        assert tokens_long > tokens
    
    @pytest.mark.unit
    def test_get_model_info_with_client(self, service_with_api_key):
        """Test obtener información del modelo con cliente configurado"""
        info = service_with_api_key.get_model_info()
        
        assert info['model_name'] == "gemini-1.5-flash"
        assert info['client_configured'] is True
        assert info['api_key_set'] is True
        assert 'capabilities' in info
        assert 'limits' in info
    
    @pytest.mark.unit
    def test_get_model_info_without_client(self, service_without_api_key):
        """Test obtener información del modelo sin cliente"""
        info = service_without_api_key.get_model_info()
        
        assert info['model_name'] == "gemini-1.5-flash"
        assert info['client_configured'] is False
        assert info['api_key_set'] is False


class TestGeniaAPIServiceIntegration:
    """Tests de integración para GeniaAPIService"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_full_workflow_mock(self):
        """Test del workflow completo usando solo mocks"""
        service = GeniaAPIService()
        
        request = QueryRequest(
            prompt="¿Qué es la inteligencia artificial?",
            max_tokens=150,
            temperature=0.7
        )
        
        # Test mock query
        response = await service.query_mock(request)
        assert response.response is not None
        assert response.tokens_used > 0
        
        # Test health check sin cliente real
        health = await service.health_check()
        assert isinstance(health, bool)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_mock_queries(self):
        """Test queries concurrentes usando mock"""
        service = GeniaAPIService()
        
        requests = [
            QueryRequest(prompt=f"Pregunta {i}", max_tokens=50, temperature=0.5)
            for i in range(5)
        ]
        
        # Ejecutar queries concurrentemente
        tasks = [service.query_mock(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        # Verificar todas las respuestas
        assert len(responses) == 5
        for i, response in enumerate(responses):
            assert f"Pregunta {i}" in response.response
            assert response.tokens_used > 0