"""
Configuración de la aplicación usando variables de entorno.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuraciones de la aplicación"""
    
    # Configuración de la aplicación
    APP_NAME: str = "GenIA Service"
    APP_VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Configuración de GenIA API
    GENIA_API_URL: str = os.getenv("GENIA_API_URL", "https://api.genia.example.com")
    GENIA_API_KEY: str = os.getenv("GENIA_API_KEY", "your-api-key-here")
    
    # Configuración de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Configuración de desarrollo
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"
    
    # Timeouts y límites
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    @property
    def is_development(self) -> bool:
        """Verifica si estamos en modo desarrollo"""
        return self.ENVIRONMENT.lower() in ["development", "dev"]
    
    @property
    def is_production(self) -> bool:
        """Verifica si estamos en modo producción"""
        return self.ENVIRONMENT.lower() in ["production", "prod"]

# Instancia global de configuración
settings = Settings()