"""
Modelos de datos usando Pydantic v2 para validación y serialización.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from enum import Enum
import time


class QueryRequest(BaseModel):
    """Modelo para las consultas a Google Gemini API"""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=32000,
        description="Texto del prompt para Google Gemini"
    )
    max_tokens: int = Field(
        default=2048,
        ge=1,
        le=8192,
        description="Número máximo de tokens en la respuesta"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Creatividad del modelo (0.0-2.0)"
    )
    top_p: Optional[float] = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    top_k: Optional[int] = Field(
        default=40,
        ge=1,
        le=100,
        description="Top-k sampling parameter"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        """Validar que el prompt no esté vacío después de strip"""
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty or only whitespace")
        return v.strip()

    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        """Validar límites de tokens"""
        if v > 8192:
            raise ValueError("max_tokens cannot exceed 8192")
        return v


class QueryResponse(BaseModel):
    """Modelo para las respuestas de Google Gemini API"""

    response: str = Field(..., description="Respuesta generada por el modelo")
    tokens_used: int = Field(..., ge=0, description="Tokens utilizados en la respuesta")
    model: str = Field(..., description="Modelo utilizado")
    processing_time: float = Field(..., ge=0.0, description="Tiempo de procesamiento en segundos")
    finish_reason: str = Field(default="stop", description="Razón de finalización")
    timestamp: float = Field(default_factory=time.time, description="Timestamp de la respuesta")

    @field_validator('tokens_used')
    @classmethod
    def validate_tokens_used(cls, v):
        """Validar que tokens_used sea positivo"""
        if v < 0:
            raise ValueError("tokens_used must be non-negative")
        return v


class HealthResponse(BaseModel):
    """Modelo para respuestas de health check"""

    status: str = Field(..., description="Estado del servicio")
    service: str = Field(..., description="Nombre del servicio")
    version: str = Field(..., description="Versión del servicio")
    timestamp: float = Field(default_factory=time.time, description="Timestamp del health check")


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""

    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje descriptivo del error")
    timestamp: float = Field(default_factory=time.time, description="Timestamp del error")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Detalles adicionales del error")


class ServiceStatus(str, Enum):
    """Estados posibles del servicio"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ModelCapabilities(BaseModel):
    """Capacidades del modelo Google Gemini"""

    text_generation: bool = Field(default=True, description="Capacidad de generación de texto")
    multimodal: bool = Field(default=True, description="Soporte multimodal")
    long_context: bool = Field(default=True, description="Soporte para contexto largo")
    function_calling: bool = Field(default=False, description="Capacidad de llamar funciones")
    code_generation: bool = Field(default=True, description="Generación de código")


class ModelLimits(BaseModel):
    """Límites del modelo Google Gemini"""

    max_input_tokens: int = Field(default=30720, description="Máximo de tokens de entrada")
    max_output_tokens: int = Field(default=8192, description="Máximo de tokens de salida")
    max_temperature: float = Field(default=2.0, description="Temperatura máxima")


class ModelInfo(BaseModel):
    """Información completa del modelo"""

    model_name: str = Field(..., description="Nombre del modelo")
    client_configured: bool = Field(..., description="Si el cliente está configurado")
    api_key_set: bool = Field(..., description="Si la API key está configurada")
    capabilities: ModelCapabilities = Field(..., description="Capacidades del modelo")
    limits: ModelLimits = Field(..., description="Límites del modelo")

    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v):
        """Validar que el nombre del modelo no esté vacío"""
        if not v or not v.strip():
            raise ValueError("model_name cannot be empty")
        return v.strip()

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow"
    )
