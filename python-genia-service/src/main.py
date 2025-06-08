"""
Aplicación principal FastAPI para integración con GenIA.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .models import QueryRequest, QueryResponse, HealthResponse, ErrorResponse, ServiceStatus
from .services import genia_service
import time
import logging

# Configurar logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="Servicio de integración con GenIA API usando Poetry",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especificar dominios exactos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

# Crear instancia de la aplicación
app = create_app()

@app.on_event("startup")
async def startup_event():
    """Eventos de inicio de la aplicación"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de cierre de la aplicación"""
    logger.info(f"Shutting down {settings.APP_NAME}")

@app.get("/", response_model=dict)
async def root():
    """Endpoint raíz con información básica"""
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.is_development else "disabled"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del servicio"""
    return HealthResponse(
        status=ServiceStatus.HEALTHY,
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=time.time()
    )

@app.get("/health/detailed", response_model=dict)
async def detailed_health_check():
    """Health check detallado incluyendo dependencias externas"""
    
    # Verificar GenIA API
    genia_healthy = await genia_service.health_check()
    
    overall_status = ServiceStatus.HEALTHY if genia_healthy else ServiceStatus.DEGRADED
    
    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
        "dependencies": {
            "genia_api": "healthy" if genia_healthy else "unhealthy"
        },
        "environment": settings.ENVIRONMENT
    }

@app.post("/query", response_model=QueryResponse)
async def query_genia(request: QueryRequest):
    """
    Procesa una consulta enviándola a GenIA API real
    
    Args:
        request: Datos de la consulta
        
    Returns:
        QueryResponse: Respuesta de GenIA
        
    Raises:
        HTTPException: En caso de error
    """
    logger.info(f"Processing real query: {request.prompt[:50]}...")
    
    try:
        response = await genia_service.query(request)
        logger.info("Real query processed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing real query: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="query_error",
                message=str(e),
                timestamp=time.time()
            ).dict()
        )

@app.post("/query/mock", response_model=QueryResponse)
async def query_mock(request: QueryRequest):
    """
    Endpoint mock para testing sin llamar a GenIA real
    
    Args:
        request: Datos de la consulta
        
    Returns:
        QueryResponse: Respuesta simulada
    """
    logger.info(f"Processing mock query: {request.prompt[:50]}...")
    
    try:
        response = await genia_service.query_mock(request)
        logger.info("Mock query processed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing mock query: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="mock_query_error",
                message=str(e),
                timestamp=time.time()
            ).dict()
        )

@app.get("/config", response_model=dict)
async def get_config():
    """
    Obtener configuración actual (solo para desarrollo)
    """
    if not settings.is_development:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "genia_api_url": settings.GENIA_API_URL,
        "api_timeout": settings.API_TIMEOUT,
        "max_retries": settings.MAX_RETRIES
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME} manually")
    
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development,
        log_level=settings.LOG_LEVEL.lower()
    )