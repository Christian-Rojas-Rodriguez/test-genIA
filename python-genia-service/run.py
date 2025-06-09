#!/usr/bin/env python3
"""
Script de entrada para la aplicación GenIA Service
Resuelve el problema de importaciones relativas y configura logging
"""
import sys
import os

# Agregar el directorio src al path para las importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import uvicorn
    from config import settings
    from logging_config import configure_for_environment, get_logger
    
    # Configurar logging antes de iniciar la aplicación
    configure_for_environment(settings.ENVIRONMENT)
    logger = get_logger(__name__)
    
    # Información de inicio con logging
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📝 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔗 Model: gemini-1.5-flash")
    logger.info(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")
    
    if settings.is_development:
        logger.info(f"📚 Docs: http://{settings.HOST}:{settings.PORT}/docs")
    else:
        logger.info("📚 Docs: disabled (production)")
    
    # Configuración de uvicorn con logging deshabilitado (usamos el nuestro)
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development,
        log_level="critical",  # Deshabilitar logging de uvicorn, usamos el nuestro
        access_log=False      # Nuestro middleware maneja los access logs
    ) 