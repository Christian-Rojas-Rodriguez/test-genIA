# 🐍 Python GenIA Service

Servicio FastAPI que integra con GenIA API, desarrollado con **Poetry** para gestión de dependencias.

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
# Con Poetry (recomendado)
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# O dentro del shell de Poetry
poetry shell
uvicorn src.main:app --reload

# Ejecutar directamente el main
poetry run python -m src.main
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
- `POST /query` - Consulta real a GenIA API
- `POST /query/mock` - Consulta mock para testing

### Desarrollo
- `GET /docs` - Documentación interactiva (solo dev)
- `GET /redoc` - Documentación alternativa (solo dev)
- `GET /config` - Configuración actual (solo dev)

## 🧪 Testing

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

## 🌍 Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# GenIA API
GENIA_API_URL=https://api.genia.example.com
GENIA_API_KEY=your-actual-api-key

# Aplicación
ENVIRONMENT=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Desarrollo
DEBUG=true
RELOAD=true
```

## 📊 Estructura del Proyecto

```bash
python-genia-service/
├── pyproject.toml # Configuración Poetry
├── poetry.lock # Lock file de dependencias
├── .env # Variables de entorno
├── Dockerfile # Container Docker
├── src/
│ ├── init.py
│ ├── main.py # Aplicación FastAPI
│ ├── config.py # Configuración
│ ├── models.py # Modelos Pydantic
│ └── services.py # Lógica de negocio
└── tests/
├── init.py
├── test_main.py # Tests de endpoints
└── test_services.py # Tests de servicios
```