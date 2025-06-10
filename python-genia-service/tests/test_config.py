"""
Tests para configuración de la aplicación.
"""
import pytest
import os
from unittest.mock import patch
from config import Settings


class TestSettings:
    """Test suite para Settings"""
    
    @pytest.mark.unit
    def test_settings_defaults(self):
        """Test valores básicos de Settings sin depender del entorno específico"""
        settings = Settings()
        
        # Valores que siempre deben ser consistentes:
        assert settings.APP_NAME == "GenIA Service"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.HOST == "127.0.0.1"
        assert settings.PORT == 8000
        assert settings.API_TIMEOUT == 30
        assert settings.MAX_RETRIES == 3
        
        # Valores que pueden variar según el entorno de testing:
        # LOG_LEVEL debe ser un nivel válido
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        # ENVIRONMENT debe ser un entorno válido (testing o development)
        assert settings.ENVIRONMENT in ["testing", "development", "production"]
        
        # DEBUG debe ser boolean
        assert isinstance(settings.DEBUG, bool)
        
        # RELOAD debe ser boolean
        assert isinstance(settings.RELOAD, bool)
    
    @pytest.mark.unit
    def test_is_development_property(self):
        """Test propiedad is_development"""
        # Test development - patcheamos directamente el atributo ENVIRONMENT
        test_settings = Settings()
        
        # Test con valor development
        test_settings.ENVIRONMENT = "development"
        assert test_settings.is_development is True
        
        # Test con valor dev  
        test_settings.ENVIRONMENT = "dev"
        assert test_settings.is_development is True
        
        # Test con valor production
        test_settings.ENVIRONMENT = "production"
        assert test_settings.is_development is False
        
        # Test con valor staging
        test_settings.ENVIRONMENT = "staging"
        assert test_settings.is_development is False 
    
    @pytest.mark.unit
    def test_settings_testing_environment(self):
        """Test específico para verificar configuración de testing"""
        settings = Settings()
        
        # Verificar que estamos en un entorno de testing válido
        # El ENVIRONMENT puede ser "testing" (CI/CD) o "development" (local)
        assert settings.ENVIRONMENT in ["testing", "development"]
        
        # En ambos casos, para testing necesitamos:
        assert settings.LOG_LEVEL == "DEBUG"  # Para debugging de tests
        assert settings.DEBUG is True  # Para obtener más información
        assert settings.HOST == "127.0.0.1"  # Para tests locales
        assert settings.PORT == 8000  # Puerto estándar
        
        # Verificar que tenemos una API key configurada (aunque sea de testing)
        assert settings.GENIA_API_KEY is not None
        assert len(settings.GENIA_API_KEY) > 0
        
        # Verificar properties derivadas
        if settings.ENVIRONMENT == "testing":
            # En testing, no debe ser considerado development
            assert settings.is_development is False
            assert settings.is_production is False
        elif settings.ENVIRONMENT == "development": 
            # En development local, debe ser considerado development
            assert settings.is_development is True
            assert settings.is_production is False 