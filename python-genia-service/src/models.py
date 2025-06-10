"""
Modelos de datos usando Pydantic para validación automática.
Optimizados para Google Gemini API (gemini-1.5-pro-002).
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum

class QueryRequest(BaseModel):
    """Modelo para requests de consulta a Google Gemini API"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Explícame qué es la inteligencia artificial en términos simples",
                "max_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }
    )
    
    prompt: str = Field(
        ..., 
        min_length=1, 
        max_length=1000000,  # gemini-1.5-pro-002 soporta hasta 1M tokens
        description="Texto de la consulta para Google Gemini"
    )
    max_tokens: Optional[int] = Field(
        default=2048,
        ge=1,
        le=8192,  # Límite de gemini-1.5-pro-002
        description="Número máximo de tokens a generar (gemini-1.5-pro-002: max 8192)"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Creatividad de la respuesta (0.0-2.0). Valores más bajos son más deterministas"
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling. Controla la diversidad de la respuesta"
    )
    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        le=40,
        description="Top-k sampling. Número de tokens más probables a considerar"
    )
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        """Validar que el prompt no esté vacío después de strip"""
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        """Validar límites específicos de gemini-1.5-pro-002"""
        if v and v > 8192:
            raise ValueError('max_tokens cannot exceed 8192 for gemini-1.5-pro-002')
        return v

class QueryResponse(BaseModel):
    """Modelo para respuestas de Google Gemini API"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana...",
                "tokens_used": 125,
                "model": "gemini-1.5-pro-002",
                "processing_time": 1.23,
                "finish_reason": "stop"
            }
        }
    )
    
    response: str = Field(..., description="Respuesta generada por Google Gemini")
    tokens_used: int = Field(default=0, ge=0, description="Tokens utilizados (estimación)")
    model: str = Field(default="gemini-1.5-pro-002", description="Modelo utilizado")
    processing_time: Optional[float] = Field(default=None, description="Tiempo de procesamiento en segundos")
    finish_reason: Optional[str] = Field(default=None, description="Razón por la que terminó la generación")

class HealthResponse(BaseModel):
    """Modelo para respuesta de health check"""
    
    status: str = Field(default="healthy", description="Estado del servicio")
    service: str = Field(default="genia-service", description="Nombre del servicio")
    version: str = Field(default="1.0.0", description="Versión del servicio")
    timestamp: float = Field(..., description="Timestamp del check")
    
class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Detalles adicionales del error")
    timestamp: float = Field(..., description="Timestamp del error")
    model: Optional[str] = Field(default=None, description="Modelo que causó el error")

class ServiceStatus(str, Enum):
    """Estados posibles del servicio"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"

class ModelCapabilities(BaseModel):
    """Modelo para las capacidades del modelo Gemini"""
    
    text_generation: bool = Field(default=True, description="Generación de texto")
    multimodal: bool = Field(default=True, description="Soporte para imágenes y otros medios")
    long_context: bool = Field(default=True, description="Contexto largo (hasta 1M tokens)")
    function_calling: bool = Field(default=True, description="Llamadas a funciones")
    json_mode: bool = Field(default=True, description="Modo JSON estructurado")
    code_generation: bool = Field(default=True, description="Generación de código")
    reasoning: bool = Field(default=True, description="Razonamiento complejo")

class ModelLimits(BaseModel):
    """Modelo para los límites del modelo Gemini"""
    
    max_output_tokens: int = Field(default=8192, description="Tokens máximos de salida")
    context_window: int = Field(default=1048576, description="Ventana de contexto (tokens)")
    temperature_range: List[float] = Field(default=[0.0, 2.0], description="Rango de temperatura")
    requests_per_minute: Optional[int] = Field(default=None, description="Límite de requests por minuto")

class ModelInfo(BaseModel):
    """Modelo completo de información del modelo"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model_name": "gemini-1.5-pro-002",
                "client_configured": True,
                "api_key_set": True,
                "capabilities": {
                    "text_generation": True,
                    "multimodal": True,
                    "long_context": True,
                    "function_calling": True,
                    "json_mode": True,
                    "code_generation": True,
                    "reasoning": True
                },
                "limits": {
                    "max_output_tokens": 8192,
                    "context_window": 1048576,
                    "temperature_range": [0.0, 2.0]
                }
            }
        }
    )
    
    model_name: str = Field(..., description="Nombre del modelo")
    client_configured: bool = Field(..., description="Si el cliente está configurado")
    api_key_set: bool = Field(..., description="Si la API key está configurada")
    capabilities: ModelCapabilities = Field(..., description="Capacidades del modelo")
    limits: ModelLimits = Field(..., description="Límites del modelo")