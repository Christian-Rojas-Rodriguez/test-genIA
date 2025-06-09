# 🐍 Python GenIA Service

Servicio FastAPI profesional que integra con **Google Gemini API**, desarrollado con **Poetry** siguiendo patrones de arquitectura limpia y mejores prácticas de desarrollo.

## 🏗️ **Arquitectura y Patrones de Diseño**

Este proyecto implementa una arquitectura robusta siguiendo principios SOLID y patrones reconocidos en la industria.

### **🎯 Patrones Arquitectónicos Implementados**

#### **1. Clean Architecture / Hexagonal Architecture**
```python
# Separación clara de responsabilidades:
- Entities (models.py)        → Modelos de dominio y DTOs
- Use Cases (services.py)     → Lógica de negocio pura
- Controllers (main.py)       → API endpoints y HTTP concerns
- Configuration (config.py)   → Infraestructura y settings
```

#### **2. Dependency Injection Pattern**
```python
# config.py - Singleton de configuración
settings = Settings()  # Una sola instancia global

# services.py - Inyección de dependencias
genia_service = GeniaAPIService()  # Servicio global

# main.py - Uso del servicio inyectado
response = await genia_service.query(request)
```

#### **3. Factory Pattern**
```python
# main.py
def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI"""
    app = FastAPI(...)
    app.add_middleware(...)
    return app

app = create_app()  # Patrón Factory
```

### **📁 Estructura del Proyecto y Filosofía**

```
python-genia-service/
├── pyproject.toml        # 📦 Gestión moderna de dependencias (Poetry)
├── run.py               # 🚀 Punto de entrada (resolver imports)
├── src/                 # 📂 Código fuente (separación clara)
│   ├── main.py         # 🎯 Aplicación FastAPI y rutas
│   ├── config.py       # ⚙️  Configuración centralizada
│   ├── models.py       # 📋 Modelos Pydantic (validación)
│   ├── services.py     # 🔧 Lógica de negocio
│   └── __init__.py     # 📝 Inicialización de módulo
├── tests/              # 🧪 Pruebas unitarias
└── .env                # 🔐 Variables de entorno
```

## 🔍 **Justificación de Cada Archivo**

### **🚀 `run.py` - ¿Por qué NO usar `main.py` directamente?**

**El problema que resuelve:**
```python
# Sin run.py → Error de imports relativos
# ImportError: attempted relative import with no known parent package

# run.py soluciona esto agregando src/ al path:
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

**¿Por qué necesitamos esto?**
1. **Estructura modular**: `src/` separa código fuente de archivos de configuración
2. **Imports absolutos**: Python puede encontrar los módulos sin problemas
3. **Punto de entrada claro**: Un solo archivo para ejecutar toda la app
4. **Debugging**: Información útil al iniciar (versión, modelo, URLs)

### **⚙️ `config.py` - Configuración Centralizada**

**Patrón:** Settings Pattern + Environment Variables Pattern

```python
class Settings:
    # Todas las configuraciones en UN lugar
    GENIA_API_KEY: str = os.getenv("GENIA_API_KEY")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() in ["development", "dev"]

settings = Settings()  # Singleton global
```

**¿Por qué este patrón?**
- **12-Factor App**: Configuración por variables de entorno
- **Type Safety**: Validación automática de tipos
- **Centralization**: Un solo lugar para toda la configuración
- **Environment Aware**: Diferentes comportamientos según entorno

### **📋 `models.py` - Modelos Pydantic (Data Transfer Objects)**

**Patrón:** DTO (Data Transfer Object) + Validation Pattern

```python
class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000000)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()
```

**¿Por qué Pydantic?**
- **Automatic Validation**: Valida datos de entrada automáticamente
- **Type Conversion**: Convierte tipos automáticamente (str → int)
- **Documentation**: Genera documentación OpenAPI automática
- **Error Handling**: Mensajes de error claros y estructurados

### **🔧 `services.py` - Capa de Servicios (Business Logic)**

**Patrón:** Service Layer + Adapter Pattern

```python
class GeniaAPIService:
    def __init__(self):
        # Configuración del cliente externo
        self.client = genai.Client(api_key=self.api_key)
    
    async def query(self, request: QueryRequest) -> QueryResponse:
        # Lógica de negocio pura
        # Transformación de datos
        # Manejo de errores
        pass
```

**¿Por qué esta separación?**
- **Single Responsibility**: Solo maneja comunicación con Gemini
- **Testability**: Fácil de testear con mocks
- **Abstraction**: FastAPI no necesita saber CÓMO funciona Gemini
- **Flexibility**: Fácil cambiar a otro proveedor de IA

### **🎯 `main.py` - FastAPI Application (Presentation Layer)**

**Patrón:** Controller Pattern + Middleware Pattern

```python
@app.post("/query", response_model=QueryResponse)
async def query_gemini(request: QueryRequest):
    """Solo coordina - NO contiene lógica de negocio"""
    try:
        response = await genia_service.query(request)  # Delega al servicio
        return response
    except Exception as e:
        raise HTTPException(...)  # Manejo de HTTP errors
```

**¿Por qué esta estructura?**
- **Thin Controllers**: Solo coordinan, no contienen lógica
- **HTTP Concerns**: Solo maneja aspectos HTTP (status codes, headers)
- **Dependency Injection**: Usa servicios inyectados
- **Middleware**: CORS, logging, etc.

## 🏛️ **Principios SOLID Aplicados**

### **S - Single Responsibility Principle**
- `config.py`: Solo configuración
- `models.py`: Solo validación y DTOs
- `services.py`: Solo lógica de negocio
- `main.py`: Solo HTTP endpoints

### **O - Open/Closed Principle**
- Fácil agregar nuevos modelos IA sin cambiar código existente
- Nuevos endpoints sin modificar servicios

### **D - Dependency Inversion Principle**
- `main.py` depende de abstracción (`genia_service`)
- No depende de implementación concreta de Google API

## 🚀 Setup con Poetry

### Instalación inicial
```bash
# Instalar Poetry (si no lo tienes)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependencias del proyecto
poetry install

# Activar el entorno virtual
poetry shell
```

### Agregar dependencias
```bash
# Dependencias de producción
poetry add nueva-dependencia

# Dependencias de desarrollo
poetry add --group dev pytest black flake8

# Ver dependencias actuales
poetry show
```

## 🏃‍♂️ Ejecución

### Desarrollo local
```bash
# Usar run.py (RECOMENDADO - resuelve imports)
poetry run python run.py

# Con Poetry y uvicorn directamente
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# O dentro del shell de Poetry
poetry shell
python run.py
```

### Con Docker
```bash
# Construir imagen
docker build -t genia-python-service .

# Ejecutar container
docker run -p 8000:8000 \
  -e GENIA_API_KEY=your-key \
  genia-python-service
```

## 📋 Endpoints

### API Principal
- `GET /` - Información básica del servicio
- `GET /health` - Health check simple
- `GET /health/detailed` - Health check con dependencias
- `POST /query` - Consulta real a Google Gemini API
- `POST /query/mock` - Consulta mock para testing
- `GET /model/info` - Información del modelo Gemini configurado

### Desarrollo
- `GET /docs` - Documentación interactiva (solo dev)
- `GET /redoc` - Documentación alternativa (solo dev)
- `GET /config` - Configuración actual (solo dev)

## 🧪 Testing Strategy

```bash
# Ejecutar todos los tests
poetry run pytest

# Tests con coverage
poetry run pytest --cov=src

# Tests específicos
poetry run pytest tests/test_main.py

# Tests en modo verbose
poetry run pytest -v
```

**Patrón:** Test Pyramid
- **Unit Tests**: Servicios individuales
- **Integration Tests**: Endpoints + servicios
- **Mocks**: Para APIs externas

## 🌍 Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Google Gemini API
GENIA_API_KEY=your-actual-google-gemini-api-key

# Aplicación
ENVIRONMENT=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Desarrollo
DEBUG=true
RELOAD=true

# Timeouts y límites
API_TIMEOUT=30
MAX_RETRIES=3
```

## 🔄 **Flujo de Datos (Request/Response Cycle)**

1. **Client HTTP Request** → FastAPI main.py
2. **Pydantic Validation** → models.py valida automáticamente
3. **Business Logic** → services.py procesa la lógica
4. **Google Gemini API** → Llamada externa
5. **Response Transformation** → services.py transforma respuesta
6. **Pydantic Response** → models.py estructura la salida
7. **HTTP Response** → main.py devuelve al cliente

## 🚀 **Ventajas de Esta Arquitectura**

1. **Maintainability**: Código fácil de mantener y modificar
2. **Testability**: Cada capa se puede testear independientemente
3. **Scalability**: Fácil agregar nuevas funcionalidades
4. **Separation of Concerns**: Cada archivo tiene una responsabilidad clara
5. **Type Safety**: Pydantic + Python typing previene errores
6. **Documentation**: OpenAPI automática con ejemplos
7. **Error Handling**: Manejo consistente de errores en cada capa

## 🎯 **¿Por qué NO un monolito en `main.py`?**

❌ **Antipattern (lo que NO hicimos):**
```python
# main.py - TODO EN UN ARCHIVO (MAL)
@app.post("/query")
async def query_gemini(prompt: str):  # Sin validación
    api_key = os.getenv("API_KEY")    # Configuración mezclada
    client = genai.Client(api_key)    # Lógica de negocio mezclada
    response = client.generate(prompt) # Sin manejo de errores
    return {"response": response}     # Sin tipo de respuesta
```

✅ **Nuestro approach (correcto):**
- Separación clara de responsabilidades
- Validación automática con Pydantic
- Configuración centralizada
- Manejo de errores estructurado
- Testing independiente de cada capa

## 📦 **Gestión de Dependencias (Poetry)**

```toml
# pyproject.toml - Archivo de configuración moderno
[project]
dependencies = [
    "fastapi (>=0.115.12,<0.116.0)",    # Framework web
    "google-genai (>=1.19.0,<2.0.0)",   # SDK oficial Google
    "pydantic (>=2.11.5,<3.0.0)",       # Validación de datos
]
```

**¿Por qué Poetry?**
- **Dependency Resolution**: Resuelve conflictos automáticamente
- **Lock File**: Versiones exactas para reproducibilidad
- **Virtual Environment**: Aislamiento automático
- **Build System**: Empaquetado moderno

## 🔧 **Tecnologías Utilizadas**

- **FastAPI**: Framework web moderno y rápido
- **Google Gemini API**: Modelo de IA generativa
- **Pydantic**: Validación de datos y serialización
- **Poetry**: Gestión moderna de dependencias
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Python 3.9+**: Lenguaje base con type hints

## 📚 **Recursos y Documentación**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Poetry Documentation](https://python-poetry.org/docs/)

---

**Desarrollado siguiendo principios de Clean Architecture y mejores prácticas de desarrollo Python** 🐍✨