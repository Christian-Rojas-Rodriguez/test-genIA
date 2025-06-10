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
        """Test valores por defecto de Settings"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings.APP_NAME == "GenIA Service"
            assert settings.APP_VERSION == "1.0.0"
            assert settings.HOST == "127.0.0.1"
            assert settings.PORT == 8000
            assert settings.LOG_LEVEL == "INFO"
            assert settings.ENVIRONMENT == "development"
            assert settings.DEBUG is False
            assert settings.RELOAD is False
            assert settings.API_TIMEOUT == 30
            assert settings.MAX_RETRIES == 3
    
    @pytest.mark.unit
    def test_is_development_property(self):
        """Test propiedad is_development"""
        # Test development
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            settings = Settings()
            assert settings.is_development is True
        
        # Test production  
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            settings = Settings()
            assert settings.is_development is False 