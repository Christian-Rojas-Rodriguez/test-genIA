"""
Inicialización del paquete src.
Expone los componentes principales para facilitar las importaciones.
"""

# Importar configuraciones
from config import settings

# Importar modelos principales
from models import QueryRequest, QueryResponse, HealthResponse

# Importar servicios
from services import genia_service

# Importar aplicación principal
from main import app

# Definir qué se exporta cuando se hace 'from src import *'
__all__ = ["settings", "QueryRequest", "QueryResponse", "HealthResponse", "genia_service", "app"]
