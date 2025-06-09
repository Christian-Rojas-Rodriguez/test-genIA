"""
Configuración centralizada de logging siguiendo las mejores prácticas de Python.
Basado en: https://docs.python.org/3/library/logging.html
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from config import settings

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    Configura el sistema de logging de la aplicación siguiendo las mejores prácticas.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nombre del archivo de log (opcional)
        log_dir: Directorio donde guardar los logs
        max_bytes: Tamaño máximo por archivo de log
        backup_count: Número de archivos de backup a mantener
        enable_console: Si mostrar logs en consola
        enable_file: Si guardar logs en archivo
    
    Returns:
        Logger: Logger raíz configurado
    """
    
    # Obtener el logger raíz
    root_logger = logging.getLogger()
    
    # Limpiar handlers existentes para evitar duplicados
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configurar nivel de logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Formato detallado para logs
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formato simple para consola
    console_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler para consola (stdout)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Handler para archivo con rotación
    if enable_file:
        # Crear directorio de logs si no existe
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Nombre del archivo de log
        if not log_file:
            log_file = f"{settings.APP_NAME.lower().replace(' ', '-')}.log"
        
        log_file_path = log_path / log_file
        
        # RotatingFileHandler para manejo automático de archivos
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Logger específico para requests HTTP (opcional)
    http_logger = logging.getLogger('httpx')
    http_logger.setLevel(logging.WARNING)  # Solo errores HTTP
    
    # Logger específico para uvicorn (servidor)
    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.setLevel(logging.INFO)
    
    # Configurar propagación para evitar duplicados
    root_logger.propagate = False
    
    # Log inicial confirmando configuración
    root_logger.info(f"Logging configurado - Nivel: {log_level}, Archivo: {enable_file}, Consola: {enable_console}")
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.
    Siguiendo la práctica recomendada de usar __name__ del módulo.
    
    Args:
        name: Nombre del logger (típicamente __name__)
    
    Returns:
        Logger: Logger configurado para el módulo
    """
    return logging.getLogger(name)

def log_function_call(func_name: str, args: dict = None, level: str = "DEBUG"):
    """
    Utility para loggear llamadas a funciones con sus argumentos.
    
    Args:
        func_name: Nombre de la función
        args: Argumentos de la función
        level: Nivel de log
    """
    logger = get_logger(__name__)
    log_method = getattr(logger, level.lower(), logger.debug)
    
    if args:
        log_method(f"Calling {func_name} with args: {args}")
    else:
        log_method(f"Calling {func_name}")

def log_api_call(method: str, url: str, status_code: int = None, response_time: float = None):
    """
    Utility específica para loggear llamadas a APIs.
    
    Args:
        method: Método HTTP (GET, POST, etc.)
        url: URL de la API
        status_code: Código de respuesta HTTP
        response_time: Tiempo de respuesta en segundos
    """
    logger = get_logger('api_calls')
    
    message = f"{method} {url}"
    if status_code:
        message += f" - Status: {status_code}"
    if response_time:
        message += f" - Time: {response_time:.3f}s"
    
    if status_code and status_code >= 400:
        logger.error(message)
    elif status_code and status_code >= 300:
        logger.warning(message)
    else:
        logger.info(message)

def log_performance(operation: str, duration: float, details: dict = None):
    """
    Utility para loggear métricas de performance.
    
    Args:
        operation: Nombre de la operación
        duration: Duración en segundos
        details: Detalles adicionales
    """
    logger = get_logger('performance')
    
    message = f"{operation} completed in {duration:.3f}s"
    if details:
        message += f" - Details: {details}"
    
    # Clasificar por tiempo de respuesta
    if duration > 5.0:
        logger.warning(f"SLOW: {message}")
    elif duration > 2.0:
        logger.info(f"MEDIUM: {message}")
    else:
        logger.debug(f"FAST: {message}")

# Configuración específica para diferentes entornos
def configure_for_environment(environment: str = "development"):
    """
    Configura logging según el entorno de ejecución.
    
    Args:
        environment: Entorno (development, staging, production)
    """
    if environment.lower() in ["development", "dev"]:
        # Desarrollo: logs detallados en consola y archivo
        setup_logging(
            log_level="DEBUG",
            enable_console=True,
            enable_file=True
        )
    elif environment.lower() in ["staging", "test"]:
        # Staging: logs de info en adelante
        setup_logging(
            log_level="INFO",
            enable_console=True,
            enable_file=True
        )
    elif environment.lower() in ["production", "prod"]:
        # Producción: solo warnings y errores, principalmente a archivo
        setup_logging(
            log_level="WARNING",
            enable_console=False,
            enable_file=True,
            max_bytes=50 * 1024 * 1024,  # 50MB en producción
            backup_count=10
        )
    else:
        # Default: configuración balanceada
        setup_logging(
            log_level="INFO",
            enable_console=True,
            enable_file=True
        )

# Inicialización automática basada en configuración
if __name__ != "__main__":
    # Auto-configurar cuando se importa el módulo
    configure_for_environment(settings.ENVIRONMENT) 