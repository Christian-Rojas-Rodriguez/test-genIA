"""
Tests para los modelos Pydantic.
"""
import pytest
from pydantic import ValidationError
from models import (
    QueryRequest,
    QueryResponse, 
    HealthResponse,
    ErrorResponse,
    ServiceStatus,
    ModelCapabilities,
    ModelLimits,
    ModelInfo
)
import time


class TestQueryRequest:
    """Test suite para QueryRequest"""
    
    @pytest.mark.unit
    def test_valid_query_request_minimal(self):
        """Test request válido con parámetros mínimos"""
        request = QueryRequest(prompt="¿Qué es Python?")
        
        assert request.prompt == "¿Qué es Python?"
        assert request.max_tokens == 2048  # Default
        assert request.temperature == 0.7  # Default
        assert request.top_p is None  # Default
        assert request.top_k is None  # Default
    
    @pytest.mark.unit
    def test_valid_query_request_complete(self):
        """Test request válido con todos los parámetros"""
        request = QueryRequest(
            prompt="Explica machine learning",
            max_tokens=1000,
            temperature=0.8,
            top_p=0.9,
            top_k=40
        )
        
        assert request.prompt == "Explica machine learning"
        assert request.max_tokens == 1000
        assert request.temperature == 0.8
        assert request.top_p == 0.9
        assert request.top_k == 40
    
    @pytest.mark.unit
    def test_query_request_prompt_validation_empty(self):
        """Test validación de prompt vacío"""
        with pytest.raises(ValidationError) as excinfo:
            QueryRequest(prompt="")
        
        assert "String should have at least 1 character" in str(excinfo.value)
    
    @pytest.mark.unit
    def test_query_request_prompt_validation_whitespace(self):
        """Test validación de prompt solo con espacios"""
        with pytest.raises(ValidationError) as excinfo:
            QueryRequest(prompt="   ")
        
        assert "Prompt cannot be empty" in str(excinfo.value)
    
    @pytest.mark.unit
    def test_query_request_max_tokens_validation_too_high(self):
        """Test validación de max_tokens muy alto"""
        with pytest.raises(ValidationError) as excinfo:
            QueryRequest(prompt="Test", max_tokens=10000)
        
        # En Pydantic v2, la validación del Field constraint se ejecuta primero
        assert "Input should be less than or equal to 8192" in str(excinfo.value)
    
    @pytest.mark.unit
    def test_query_request_max_tokens_validation_zero(self):
        """Test validación de max_tokens cero"""
        with pytest.raises(ValidationError) as excinfo:
            QueryRequest(prompt="Test", max_tokens=0)
        
        assert "greater than or equal to 1" in str(excinfo.value)
    
    @pytest.mark.unit
    def test_query_request_temperature_validation_too_high(self):
        """Test validación de temperature muy alta"""
        with pytest.raises(ValidationError) as excinfo:
            QueryRequest(prompt="Test", temperature=3.0)
        
        assert "less than or equal to 2" in str(excinfo.value)
    
    @pytest.mark.unit
    def test_query_request_temperature_validation_negative(self):
        """Test validación de temperature negativa"""
        with pytest.raises(ValidationError) as excinfo:
            QueryRequest(prompt="Test", temperature=-0.1)
        
        assert "greater than or equal to 0" in str(excinfo.value)
    
    @pytest.mark.unit
    def test_query_request_top_p_validation(self):
        """Test validación de top_p"""
        # Válido
        request = QueryRequest(prompt="Test", top_p=0.9)
        assert request.top_p == 0.9
        
        # Inválido - muy alto
        with pytest.raises(ValidationError):
            QueryRequest(prompt="Test", top_p=1.5)
        
        # Inválido - negativo
        with pytest.raises(ValidationError):
            QueryRequest(prompt="Test", top_p=-0.1)
    
    @pytest.mark.unit
    def test_query_request_top_k_validation(self):
        """Test validación de top_k"""
        # Válido
        request = QueryRequest(prompt="Test", top_k=40)
        assert request.top_k == 40
        
        # Inválido - muy alto
        with pytest.raises(ValidationError):
            QueryRequest(prompt="Test", top_k=50)
        
        # Inválido - cero
        with pytest.raises(ValidationError):
            QueryRequest(prompt="Test", top_k=0)
    
    @pytest.mark.unit
    def test_query_request_prompt_strip(self):
        """Test que el prompt se hace strip automáticamente"""
        request = QueryRequest(prompt="  Test prompt  ")
        assert request.prompt == "Test prompt"


class TestQueryResponse:
    """Test suite para QueryResponse"""
    
    @pytest.mark.unit
    def test_valid_query_response_minimal(self):
        """Test response válido mínimo"""
        response = QueryResponse(response="Esta es una respuesta")
        
        assert response.response == "Esta es una respuesta"
        assert response.tokens_used == 0  # Default
        assert response.model == "gemini-1.5-pro-002"  # Default
        assert response.processing_time is None  # Default
        assert response.finish_reason is None  # Default
    
    @pytest.mark.unit
    def test_valid_query_response_complete(self):
        """Test response válido completo"""
        response = QueryResponse(
            response="Respuesta completa",
            tokens_used=150,
            model="gemini-1.5-flash",
            processing_time=1.5,
            finish_reason="stop"
        )
        
        assert response.response == "Respuesta completa"
        assert response.tokens_used == 150
        assert response.model == "gemini-1.5-flash"
        assert response.processing_time == 1.5
        assert response.finish_reason == "stop"
    
    @pytest.mark.unit
    def test_query_response_tokens_validation_negative(self):
        """Test validación de tokens_used negativo"""
        with pytest.raises(ValidationError):
            QueryResponse(response="Test", tokens_used=-1)


class TestHealthResponse:
    """Test suite para HealthResponse"""
    
    @pytest.mark.unit
    def test_valid_health_response(self):
        """Test health response válido"""
        timestamp = time.time()
        response = HealthResponse(
            status="healthy",
            service="test-service",
            version="1.0.0",
            timestamp=timestamp
        )
        
        assert response.status == "healthy"
        assert response.service == "test-service"
        assert response.version == "1.0.0"
        assert response.timestamp == timestamp
    
    @pytest.mark.unit
    def test_health_response_defaults(self):
        """Test valores por defecto de HealthResponse"""
        timestamp = time.time()
        response = HealthResponse(timestamp=timestamp)
        
        assert response.status == "healthy"
        assert response.service == "genia-service"
        assert response.version == "1.0.0"


class TestErrorResponse:
    """Test suite para ErrorResponse"""
    
    @pytest.mark.unit
    def test_valid_error_response_minimal(self):
        """Test error response mínimo"""
        timestamp = time.time()
        response = ErrorResponse(
            error="validation_error",
            message="Error de validación",
            timestamp=timestamp
        )
        
        assert response.error == "validation_error"
        assert response.message == "Error de validación"
        assert response.timestamp == timestamp
        assert response.details is None
        assert response.model is None
    
    @pytest.mark.unit
    def test_valid_error_response_complete(self):
        """Test error response completo"""
        timestamp = time.time()
        details = {"field": "prompt", "issue": "too_short"}
        
        response = ErrorResponse(
            error="api_error",
            message="Error en la API",
            timestamp=timestamp,
            details=details,
            model="gemini-1.5-flash"
        )
        
        assert response.error == "api_error"
        assert response.message == "Error en la API"
        assert response.details == details
        assert response.model == "gemini-1.5-flash"


class TestServiceStatus:
    """Test suite para ServiceStatus enum"""
    
    @pytest.mark.unit
    def test_service_status_values(self):
        """Test valores del enum ServiceStatus"""
        assert ServiceStatus.HEALTHY == "healthy"
        assert ServiceStatus.UNHEALTHY == "unhealthy"
        assert ServiceStatus.DEGRADED == "degraded"
    
    @pytest.mark.unit
    def test_service_status_usage(self):
        """Test uso del enum en HealthResponse"""
        timestamp = time.time()
        response = HealthResponse(
            status=ServiceStatus.HEALTHY,
            timestamp=timestamp
        )
        assert response.status == "healthy"


class TestModelCapabilities:
    """Test suite para ModelCapabilities"""
    
    @pytest.mark.unit
    def test_model_capabilities_defaults(self):
        """Test valores por defecto de ModelCapabilities"""
        capabilities = ModelCapabilities()
        
        assert capabilities.text_generation is True
        assert capabilities.multimodal is True
        assert capabilities.long_context is True
        assert capabilities.function_calling is True
        assert capabilities.json_mode is True
        assert capabilities.code_generation is True
        assert capabilities.reasoning is True
    
    @pytest.mark.unit
    def test_model_capabilities_custom(self):
        """Test ModelCapabilities personalizado"""
        capabilities = ModelCapabilities(
            text_generation=True,
            multimodal=False,
            long_context=True,
            function_calling=False,
            json_mode=True,
            code_generation=True,
            reasoning=False
        )
        
        assert capabilities.text_generation is True
        assert capabilities.multimodal is False
        assert capabilities.function_calling is False
        assert capabilities.reasoning is False


class TestModelLimits:
    """Test suite para ModelLimits"""
    
    @pytest.mark.unit
    def test_model_limits_defaults(self):
        """Test valores por defecto de ModelLimits"""
        limits = ModelLimits()
        
        assert limits.max_output_tokens == 8192
        assert limits.context_window == 1048576
        assert limits.temperature_range == [0.0, 2.0]
        assert limits.requests_per_minute is None
    
    @pytest.mark.unit
    def test_model_limits_custom(self):
        """Test ModelLimits personalizado"""
        limits = ModelLimits(
            max_output_tokens=4096,
            context_window=524288,
            temperature_range=[0.0, 1.0],
            requests_per_minute=100
        )
        
        assert limits.max_output_tokens == 4096
        assert limits.context_window == 524288
        assert limits.temperature_range == [0.0, 1.0]
        assert limits.requests_per_minute == 100


class TestModelInfo:
    """Test suite para ModelInfo"""
    
    @pytest.mark.unit
    def test_model_info_complete(self):
        """Test ModelInfo completo"""
        capabilities = ModelCapabilities()
        limits = ModelLimits()
        
        model_info = ModelInfo(
            model_name="gemini-1.5-flash",
            client_configured=True,
            api_key_set=True,
            capabilities=capabilities,
            limits=limits
        )
        
        assert model_info.model_name == "gemini-1.5-flash"
        assert model_info.client_configured is True
        assert model_info.api_key_set is True
        assert isinstance(model_info.capabilities, ModelCapabilities)
        assert isinstance(model_info.limits, ModelLimits)
    
    @pytest.mark.unit
    def test_model_info_validation(self):
        """Test validación de ModelInfo"""
        with pytest.raises(ValidationError):
            ModelInfo(
                # Faltan campos requeridos
                model_name="test"
            )


class TestModelsSerialization:
    """Test suite para serialización/deserialización de modelos"""
    
    @pytest.mark.unit
    def test_query_request_json_serialization(self):
        """Test serialización JSON de QueryRequest"""
        request = QueryRequest(
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.8
        )
        
        json_data = request.model_dump()
        assert json_data["prompt"] == "Test prompt"
        assert json_data["max_tokens"] == 100
        assert json_data["temperature"] == 0.8
    
    @pytest.mark.unit
    def test_query_response_json_serialization(self):
        """Test serialización JSON de QueryResponse"""
        response = QueryResponse(
            response="Test response",
            tokens_used=50,
            model="test-model",
            processing_time=1.0
        )
        
        json_data = response.model_dump()
        assert json_data["response"] == "Test response"
        assert json_data["tokens_used"] == 50
        assert json_data["model"] == "test-model"
        assert json_data["processing_time"] == 1.0
    
    @pytest.mark.unit
    def test_model_info_json_serialization(self):
        """Test serialización JSON de ModelInfo"""
        model_info = ModelInfo(
            model_name="test-model",
            client_configured=True,
            api_key_set=False,
            capabilities=ModelCapabilities(),
            limits=ModelLimits()
        )
        
        json_data = model_info.model_dump()
        assert json_data["model_name"] == "test-model"
        assert json_data["client_configured"] is True
        assert json_data["api_key_set"] is False
        assert "capabilities" in json_data
        assert "limits" in json_data


class TestModelsValidationEdgeCases:
    """Test cases para casos extremos de validación"""
    
    @pytest.mark.unit
    def test_query_request_very_long_prompt(self):
        """Test con prompt muy largo (cerca del límite)"""
        # Gemini 1.5 soporta hasta 1M tokens, esto debería ser válido
        long_prompt = "Test " * 10000  # ~50K caracteres
        request = QueryRequest(prompt=long_prompt)
        assert len(request.prompt) > 40000
    
    @pytest.mark.unit
    def test_query_request_edge_values(self):
        """Test con valores en los límites"""
        # Valores mínimos válidos
        request = QueryRequest(
            prompt="A",
            max_tokens=1,
            temperature=0.0,
            top_p=0.0,
            top_k=1
        )
        assert request.max_tokens == 1
        assert request.temperature == 0.0
        
        # Valores máximos válidos
        request = QueryRequest(
            prompt="Test",
            max_tokens=8192,
            temperature=2.0,
            top_p=1.0,
            top_k=40
        )
        assert request.max_tokens == 8192
        assert request.temperature == 2.0
    
    @pytest.mark.unit
    def test_response_models_with_special_characters(self):
        """Test modelos con caracteres especiales"""
        # Texto con emojis y caracteres especiales
        special_text = "¡Hola! 🚀 Esto es una prueba con acentos y ñ"
        
        response = QueryResponse(response=special_text)
        assert response.response == special_text
        
        error = ErrorResponse(
            error="special_chars",
            message=special_text,
            timestamp=time.time()
        )
        assert error.message == special_text 