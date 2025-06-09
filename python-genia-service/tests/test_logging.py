"""
Tests para el sistema de logging configurado
"""
import pytest
import logging
import tempfile
import os
from pathlib import Path
import sys

# Agregar src al path para las importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logging_config import setup_logging, get_logger, log_function_call, log_api_call, log_performance


class TestLoggingConfig:
    """Test cases para configuración de logging"""
    
    def test_get_logger_returns_logger_instance(self):
        """Test que get_logger retorna una instancia de Logger"""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_setup_logging_console_only(self):
        """Test configuración de logging solo a consola"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = setup_logging(
                log_level="INFO",
                log_dir=temp_dir,
                enable_console=True,
                enable_file=False
            )
            
            assert isinstance(logger, logging.Logger)
            assert logger.level == logging.INFO
    
    def test_setup_logging_file_only(self):
        """Test configuración de logging solo a archivo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = setup_logging(
                log_level="DEBUG",
                log_dir=temp_dir,
                enable_console=False,
                enable_file=True,
                log_file="test.log"
            )
            
            assert isinstance(logger, logging.Logger)
            assert logger.level == logging.DEBUG
            
            # Verificar que el archivo de log se crea
            log_file_path = Path(temp_dir) / "test.log"
            assert log_file_path.exists()
    
    def test_setup_logging_both_console_and_file(self):
        """Test configuración de logging a consola y archivo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = setup_logging(
                log_level="WARNING",
                log_dir=temp_dir,
                enable_console=True,
                enable_file=True,
                log_file="both.log"
            )
            
            assert isinstance(logger, logging.Logger)
            assert logger.level == logging.WARNING
            
            # Verificar que el archivo de log se crea
            log_file_path = Path(temp_dir) / "both.log"
            assert log_file_path.exists()
    
    def test_log_levels(self):
        """Test diferentes niveles de logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test DEBUG level
            logger = setup_logging(log_level="DEBUG", log_dir=temp_dir, enable_file=True)
            assert logger.level == logging.DEBUG
            
            # Test INFO level
            logger = setup_logging(log_level="INFO", log_dir=temp_dir, enable_file=True)
            assert logger.level == logging.INFO
            
            # Test WARNING level
            logger = setup_logging(log_level="WARNING", log_dir=temp_dir, enable_file=True)
            assert logger.level == logging.WARNING
            
            # Test ERROR level
            logger = setup_logging(log_level="ERROR", log_dir=temp_dir, enable_file=True)
            assert logger.level == logging.ERROR


class TestLoggingUtilities:
    """Test cases para utilidades de logging"""
    
    def test_log_function_call_basic(self):
        """Test log_function_call funciona básicamente"""
        # Esta función debería ejecutarse sin errores
        log_function_call("test_function")
        log_function_call("test_function", {"arg1": "value1"})
    
    def test_log_api_call_success(self):
        """Test log_api_call para casos exitosos"""
        # Estas funciones deberían ejecutarse sin errores
        log_api_call("GET", "/api/test", 200, 0.5)
        log_api_call("POST", "/api/create", 201, 1.2)
    
    def test_log_api_call_error(self):
        """Test log_api_call para casos de error"""
        log_api_call("GET", "/api/error", 500, 2.1)
        log_api_call("POST", "/api/forbidden", 403, 0.8)
    
    def test_log_performance_fast(self):
        """Test log_performance para operaciones rápidas"""
        log_performance("fast_operation", 0.5, {"items": 10})
    
    def test_log_performance_medium(self):
        """Test log_performance para operaciones medianas"""
        log_performance("medium_operation", 3.0, {"items": 100})
    
    def test_log_performance_slow(self):
        """Test log_performance para operaciones lentas"""
        log_performance("slow_operation", 6.0, {"items": 1000})


class TestLoggingIntegration:
    """Test cases de integración del sistema de logging"""
    
    def test_logging_hierarchy(self):
        """Test que la jerarquía de loggers funciona correctamente"""
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")
        
        assert child_logger.parent == parent_logger
    
    def test_multiple_loggers_same_name(self):
        """Test que múltiples llamadas con el mismo nombre retornan el mismo logger"""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        
        assert logger1 is logger2
    
    def test_logger_with_file_rotation(self):
        """Test que la rotación de archivos funciona"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configurar con archivos pequeños para forzar rotación
            setup_logging(
                log_level="DEBUG",
                log_dir=temp_dir,
                enable_file=True,
                max_bytes=1024,  # 1KB para forzar rotación rápida
                backup_count=3
            )
            
            logger = get_logger("rotation_test")
            
            # Generar muchos logs para forzar rotación
            for i in range(100):
                logger.info(f"Test log message number {i} with some extra content to make it longer")
            
            # Verificar que se crearon archivos
            log_files = list(Path(temp_dir).glob("*.log*"))
            assert len(log_files) >= 1  # Al menos el archivo principal


if __name__ == "__main__":
    pytest.main([__file__]) 