"""
Servicios de negocio para integración con Google Gemini API.
Implementación siguiendo la documentación oficial de Google.
"""
import time
import asyncio
from typing import Optional, Dict, Any
from config import settings
from models import QueryRequest, QueryResponse
import logging
from google import genai

# Configurar logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

class GeniaAPIService:
    """
    Servicio para interactuar con Google Gemini API
    Implementación oficial siguiendo: https://ai.google.dev/gemini-api/docs/quickstart
    """
    
    def __init__(self):
        self.api_key = settings.GENIA_API_KEY
        self.timeout = settings.API_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
        self.model_name = "gemini-1.5-flash"
        
        # Configurar el cliente oficial de Google Gemini
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Google Gemini client configured successfully with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to configure Google Gemini client: {e}")
                self.client = None
        else:
            logger.warning("No GENIA_API_KEY provided. Service will work in mock mode only.")
            self.client = None
    
    async def query(self, request: QueryRequest) -> QueryResponse:
        """
        Realizar consulta a Google Gemini API usando el SDK oficial
        
        Args:
            request: Datos de la consulta con prompt, max_tokens, temperature
            
        Returns:
            QueryResponse: Respuesta de Google Gemini
            
        Raises:
            Exception: Error en la comunicación con Google Gemini
        """
        if not self.client:
            raise Exception("Google Gemini client not configured. Check your GENIA_API_KEY.")
        
        start_time = time.time()
        
        try:
            logger.info(f"Calling Google Gemini API ({self.model_name}) with prompt: {request.prompt[:50]}...")
            
            # Preparar parámetros según la documentación oficial
            generation_config = self._build_generation_config(request)
            
            # Ejecutar la llamada en un thread pool para hacerla async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._generate_content_with_config, 
                request.prompt,
                generation_config
            )
            
            processing_time = time.time() - start_time
            
            logger.info(f"Google Gemini API responded successfully in {processing_time:.2f}s")
            
            return QueryResponse(
                response=response.text,
                tokens_used=self._estimate_tokens(response.text),
                model=self.model_name,
                processing_time=processing_time
            )
                
        except Exception as e:
            logger.error(f"Error calling Google Gemini API: {e}")
            # Incluir más detalles del error para debugging
            error_details = {
                "model": self.model_name,
                "prompt_length": len(request.prompt),
                "error_type": type(e).__name__
            }
            raise Exception(f"Google Gemini API error: {str(e)}. Details: {error_details}")
    
    def _build_generation_config(self, request: QueryRequest) -> Optional[Dict[str, Any]]:
        """
        Construir configuración de generación basada en los parámetros del request
        Soporta todos los parámetros de gemini-1.5-pro-002
        """
        config = {}
        
        # Mapear parámetros de nuestro modelo a los de Gemini
        if request.max_tokens is not None:
            config['max_output_tokens'] = request.max_tokens
        
        if request.temperature is not None:
            config['temperature'] = request.temperature
        
        if hasattr(request, 'top_p') and request.top_p is not None:
            config['top_p'] = request.top_p
        
        if hasattr(request, 'top_k') and request.top_k is not None:
            config['top_k'] = request.top_k
        
        # Parámetros por defecto optimizados para gemini-1.5-pro-002
        config.setdefault('max_output_tokens', 2048)
        config.setdefault('temperature', 0.7)
        
        return config if config else None
    
    def _generate_content_with_config(self, prompt: str, generation_config: Optional[Dict[str, Any]] = None):
        """
        Método sincrónico para generar contenido con configuración
        Siguiendo exactamente la documentación oficial de Google
        """
        # Implementación simplificada - exactamente como en la documentación oficial
        return self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimación de tokens más precisa para gemini-1.5-pro-002
        """
        # Gemini 1.5 Pro tiene tokenización más eficiente
        # Estimación mejorada: ~3.5 caracteres por token en promedio para español
        return max(1, len(text) // 4)
    
    async def query_mock(self, request: QueryRequest) -> QueryResponse:
        """
        Consulta mock para testing sin llamar a Google Gemini real
        
        Args:
            request: Datos de la consulta
            
        Returns:
            QueryResponse: Respuesta simulada
        """
        start_time = time.time()
        
        # Simular latencia de API real de Gemini
        await asyncio.sleep(0.3)  # Gemini 1.5 Pro es más rápido
        
        processing_time = time.time() - start_time
        
        logger.info(f"Mock query processed in {processing_time:.2f}s")
        
        # Respuesta mock más realista
        mock_response = (
            f"[MOCK GEMINI-1.5-PRO-002] Procesando consulta: '{request.prompt}'\n\n"
            f"Esta sería una respuesta generada por Google Gemini 1.5 Pro 002 "
            f"con temperatura={getattr(request, 'temperature', 0.7)} y "
            f"max_tokens={getattr(request, 'max_tokens', 2048)}.\n\n"
            f"El modelo gemini-1.5-pro-002 es conocido por su alta calidad en "
            f"generación de texto, razonamiento complejo y comprensión contextual avanzada."
        )
        
        return QueryResponse(
            response=mock_response,
            tokens_used=len(request.prompt.split()) * 2,  # Mock más realista
            model=f"mock-{self.model_name}",
            processing_time=processing_time
        )
    
    async def health_check(self) -> bool:
        """
        Verificar salud de Google Gemini API con una consulta simple
        
        Returns:
            bool: True si la API está disponible y funcionando
        """
        if not self.client:
            logger.warning("Health check failed: Client not configured")
            return False
            
        try:
            logger.info(f"Performing health check with {self.model_name}")
            
            # Consulta simple y rápida para verificar conectividad
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._generate_content_with_config,
                "Hello, respond with just 'OK'",
                {"max_output_tokens": 10, "temperature": 0.1}
            )
            
            # Verificar que la respuesta sea válida
            is_healthy = bool(response and response.text and len(response.text.strip()) > 0)
            
            if is_healthy:
                logger.info(f"Health check passed: {self.model_name} is healthy")
            else:
                logger.warning(f"Health check failed: Invalid response from {self.model_name}")
                
            return is_healthy
                
        except Exception as e:
            logger.warning(f"Google Gemini API health check failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtener información del modelo configurado
        """
        return {
            "model_name": self.model_name,
            "client_configured": bool(self.client),
            "api_key_set": bool(self.api_key),
            "capabilities": {
                "text_generation": True,
                "multimodal": True,  # gemini-1.5-pro-002 soporta imágenes
                "long_context": True,  # Hasta 1M tokens de contexto
                "function_calling": True,
                "json_mode": True
            },
            "limits": {
                "max_output_tokens": 8192,
                "context_window": 1048576,  # 1M tokens
                "temperature_range": [0.0, 2.0]
            }
        }

# Instancia global del servicio
genia_service = GeniaAPIService()