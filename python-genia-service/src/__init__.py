"""
Paquete principal del servicio GenIA.
"""
from .config import settings
from .models import QueryRequest, QueryResponse, HealthResponse
from .services import genia_service
from .main import app

__version__ = "1.0.0"
__all__ = ["settings", "QueryRequest", "QueryResponse", "HealthResponse", "genia_service", "app"]