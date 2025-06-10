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
        """Test valores por defecto de Settings (en ambiente de testing)"""
        # En ambiente de testing, conftest.py establece ciertas variables de entorno
        settings = Settings()
        
        assert settings.APP_NAME == "GenIA Service"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.HOST == "127.0.0.1"
        assert settings.PORT == 8000
        # Valores configurados por conftest.py:
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.ENVIRONMENT == "development"  # Configurado en conftest.py
        assert settings.DEBUG is True
        assert settings.RELOAD is True  # Configurado por conftest.py
        assert settings.API_TIMEOUT == 30
        assert settings.MAX_RETRIES == 3
    
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