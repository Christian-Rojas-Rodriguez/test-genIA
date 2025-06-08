"""
Servicios de negocio para integración con GenIA API.
"""
import httpx
import time
from typing import Optional
from .config import settings
from .models import QueryRequest, QueryResponse
import logging

# Configurar logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

class GeniaAPIService:
    """Servicio para interactuar con GenIA API"""
    
    def __init__(self):
        self.base_url = settings.GENIA_API_URL
        self.api_key = settings.GENIA_API_KEY
        self.timeout = settings.API_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
    
    async def query(self, request: QueryRequest) -> QueryResponse:
        """
        Realizar consulta real a GenIA API
        
        Args:
            request: Datos de la consulta
            
        Returns:
            QueryResponse: Respuesta de GenIA
            
        Raises:
            httpx.HTTPError: Error en la comunicación con GenIA
            Exception: Error general
        """
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"{settings.APP_NAME}/{settings.APP_VERSION}"
            }
            
            payload = {
                "prompt": request.prompt,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            }
            
            logger.info(f"Calling GenIA API: {self.base_url}/generate")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                processing_time = time.time() - start_time
                
                logger.info(f"GenIA API responded successfully in {processing_time:.2f}s")
                
                return QueryResponse(
                    response=data.get("text", "No response from GenIA"),
                    tokens_used=data.get("tokens_used", 0),
                    model=data.get("model", "genia-api"),
                    processing_time=processing_time
                )
                
        except httpx.TimeoutException as e:
            logger.error(f"GenIA API timeout: {e}")
            raise Exception("GenIA API timeout")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"GenIA API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"GenIA API error: {e.response.status_code}")
            
        except httpx.RequestError as e:
            logger.error(f"GenIA API connection error: {e}")
            raise Exception("GenIA API connection error")
            
        except Exception as e:
            logger.error(f"Unexpected error calling GenIA API: {e}")
            raise Exception(f"Unexpected error: {str(e)}")
    
    async def query_mock(self, request: QueryRequest) -> QueryResponse:
        """
        Consulta mock para testing sin llamar a GenIA real
        
        Args:
            request: Datos de la consulta
            
        Returns:
            QueryResponse: Respuesta simulada
        """
        start_time = time.time()
        
        # Simular latencia de API real
        import asyncio
        await asyncio.sleep(0.5)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Mock query processed in {processing_time:.2f}s")
        
        return QueryResponse(
            response=f"[MOCK] Respuesta simulada para: '{request.prompt}'. "
                    f"En un sistema real, esto sería procesado por GenIA API con "
                    f"max_tokens={request.max_tokens} y temperature={request.temperature}.",
            tokens_used=len(request.prompt.split()),
            model="mock-genia",
            processing_time=processing_time
        )
    
    async def health_check(self) -> bool:
        """
        Verificar salud de GenIA API
        
        Returns:
            bool: True si la API está disponible
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"{settings.APP_NAME}/{settings.APP_VERSION}"
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=headers
                )
                return response.status_code == 200
                
        except Exception as e:
            logger.warning(f"GenIA API health check failed: {e}")
            return False

# Instancia global del servicio
genia_service = GeniaAPIService()