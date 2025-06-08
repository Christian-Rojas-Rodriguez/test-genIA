"""
Modelos de datos usando Pydantic para validación automática.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

class QueryRequest(BaseModel):
    """Modelo para requests de consulta a GenIA"""
    
    prompt: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="Texto de la consulta para GenIA"
    )
    max_tokens: int = Field(
        default=150,
        ge=1,
        le=2000,
        description="Número máximo de tokens a generar"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Creatividad de la respuesta (0-2)"
    )
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validar que el prompt no esté vacío después de strip"""
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Explícame qué es la inteligencia artificial",
                "max_tokens": 150,
                "temperature": 0.7
            }
        }

class QueryResponse(BaseModel):
    """Modelo para respuestas de GenIA"""
    
    response: str = Field(..., description="Respuesta generada por GenIA")
    tokens_used: int = Field(default=0, ge=0, description="Tokens utilizados")
    model: str = Field(default="genia-api", description="Modelo utilizado")
    processing_time: Optional[float] = Field(default=None, description="Tiempo de procesamiento en segundos")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "La inteligencia artificial es...",
                "tokens_used": 75,
                "model": "genia-api",
                "processing_time": 1.23
            }
        }

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
    details: Optional[dict] = Field(default=None, description="Detalles adicionales del error")
    timestamp: float = Field(..., description="Timestamp del error")

class ServiceStatus(str, Enum):
    """Estados posibles del servicio"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"