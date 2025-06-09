"""
Aplicación principal FastAPI para integración con Google Gemini API.
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models import QueryRequest, QueryResponse, HealthResponse, ErrorResponse, ServiceStatus
from services import genia_service
import time
from logging_config import get_logger, log_api_call, log_performance
import logging

# Obtener logger específico para este módulo
logger = get_logger(__name__)

def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="Servicio de integración con Google Gemini API (gemini-1.5-pro-002) usando Poetry",
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para loggear todas las requests HTTP"""
    start_time = time.time()
    
    # Log request inicial
    logger.info(f"🌐 Incoming request: {request.method} {request.url.path}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log respuesta exitosa
        log_api_call(
            method=request.method,
            url=str(request.url.path),
            status_code=response.status_code,
            response_time=process_time
        )
        
        # Agregar tiempo de procesamiento al header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ Request failed: {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.3f}s")
        raise

@app.on_event("startup")
async def startup_event():
    """Eventos de inicio de la aplicación"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🐛 Debug mode: {settings.DEBUG}")
    logger.info(f"🤖 Google Gemini model: {genia_service.model_name}")
    logger.info(f"🌐 Server will be available at: http://{settings.HOST}:{settings.PORT}")
    
    # Log configuración importante
    logger.debug(f"Configuration details:")
    logger.debug(f"  - API Timeout: {settings.API_TIMEOUT}s")
    logger.debug(f"  - Max Retries: {settings.MAX_RETRIES}")
    logger.debug(f"  - Log Level: {settings.LOG_LEVEL}")
    
    # Verificar configuración crítica
    if not settings.GENIA_API_KEY:
        logger.critical("⚠️  GENIA_API_KEY not configured - API calls will fail!")
    
@app.on_event("shutdown") 
async def shutdown_event():
    """Eventos de cierre de la aplicación"""
    logger.info(f"🛑 Shutting down {settings.APP_NAME}")
    logging.shutdown()  # Cerrar todos los handlers

@app.get("/", response_model=dict)
async def root():
    """Endpoint raíz con información básica"""
    logger.info("📋 Root endpoint accessed")
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "model": genia_service.model_name,
        "docs_url": "/docs" if settings.is_development else "disabled"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del servicio"""
    logger.debug("❤️  Health check requested")
    
    health_response = HealthResponse(
        status=ServiceStatus.HEALTHY,
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=time.time()
    )
    
    logger.debug(f"Health status: {health_response.status}")
    return health_response

@app.get("/health/detailed", response_model=dict)
async def detailed_health_check():
    """Health check detallado incluyendo dependencias externas"""
    start_time = time.time()
    logger.info("🔍 Detailed health check started")
    
    try:
        # Verificar Google Gemini API
        logger.debug("Checking Google Gemini API health...")
        gemini_healthy = await genia_service.health_check()
        
        overall_status = ServiceStatus.HEALTHY if gemini_healthy else ServiceStatus.DEGRADED
        
        health_details = {
            "status": overall_status,
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "timestamp": time.time(),
            "dependencies": {
                "google_gemini": "healthy" if gemini_healthy else "unhealthy"
            },
            "environment": settings.ENVIRONMENT,
            "model": genia_service.model_name
        }
        
        # Log performance del health check
        check_duration = time.time() - start_time
        log_performance("detailed_health_check", check_duration, {"gemini_healthy": gemini_healthy})
        
        if gemini_healthy:
            logger.info(f"✅ Detailed health check passed - Status: {overall_status}")
        else:
            logger.warning(f"⚠️  Detailed health check degraded - Gemini API unhealthy")
        
        return health_details
        
    except Exception as e:
        check_duration = time.time() - start_time
        logger.error(f"❌ Detailed health check failed: {str(e)} - Duration: {check_duration:.3f}s")
        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                error="health_check_failed",
                message=str(e),
                timestamp=time.time()
            ).dict()
        )

@app.get("/model/info", response_model=dict)
async def get_model_info():
    """
    Obtener información detallada del modelo Google Gemini configurado
    """
    try:
        model_info = genia_service.get_model_info()
        return {
            "success": True,
            "data": model_info,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="model_info_error",
                message=str(e),
                timestamp=time.time()
            ).dict()
        )

@app.post("/query", response_model=QueryResponse)
async def query_gemini(request: QueryRequest):
    """
    Procesa una consulta enviándola a Google Gemini API (gemini-1.5-pro-002)
    
    Args:
        request: Datos de la consulta con prompt, max_tokens, temperature
        
    Returns:
        QueryResponse: Respuesta de Google Gemini
        
    Raises:
        HTTPException: En caso de error
    """
    start_time = time.time()
    request_id = f"query_{int(start_time * 1000)}"  # ID único para tracking
    
    logger.info(f"🤖 [{request_id}] Processing Gemini query - Prompt: '{request.prompt[:50]}...'")
    logger.debug(f"[{request_id}] Query parameters: max_tokens={request.max_tokens}, temperature={request.temperature}")
    
    try:
        response = await genia_service.query(request)
        
        # Log performance metrics
        processing_time = time.time() - start_time
        log_performance(
            f"gemini_query_{request_id}", 
            processing_time, 
            {
                "prompt_length": len(request.prompt),
                "tokens_used": response.tokens_used,
                "model": response.model
            }
        )
        
        logger.info(f"✅ [{request_id}] Gemini query successful - Tokens: {response.tokens_used}, Time: {processing_time:.3f}s")
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ [{request_id}] Gemini query failed: {str(e)} - Time: {processing_time:.3f}s")
        logger.debug(f"[{request_id}] Error details: {type(e).__name__}")
        
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="query_error",
                message=str(e),
                timestamp=time.time(),
                details={"request_id": request_id, "processing_time": processing_time}
            ).dict()
        )

@app.post("/query/mock", response_model=QueryResponse)
async def query_mock(request: QueryRequest):
    """
    Endpoint mock para testing sin llamar a Google Gemini real
    
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
        "google_gemini_configured": bool(settings.GENIA_API_KEY),
        "model": genia_service.model_name,
        "api_timeout": settings.API_TIMEOUT,
        "max_retries": settings.MAX_RETRIES,
        "api_key_preview": f"{settings.GENIA_API_KEY[:10]}...{settings.GENIA_API_KEY[-10:]}" if settings.GENIA_API_KEY else "None"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME} manually")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development,
        log_level=settings.LOG_LEVEL.lower()
    )