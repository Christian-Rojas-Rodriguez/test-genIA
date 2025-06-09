#!/bin/bash

echo "🚀 Configurando dependencias para GenIA + Gemini 1.5 Pro"
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: No se encuentra pyproject.toml"
    echo "Ejecuta este script desde el directorio python-genia-service/"
    exit 1
fi

echo "📦 Agregando dependencias de producción..."

# Dependencias principales de Google Gemini
echo "🤖 Agregando Google Generative AI..."
poetry add google-generativeai

# Dependencias adicionales para Data Science
echo "🧠 Agregando herramientas de Data Science..."
poetry add pandas numpy

# Dependencias para procesamiento de texto
echo "📝 Agregando herramientas de NLP..."
poetry add tiktoken  # Para contar tokens
poetry add langdetect  # Para detectar idioma

# Dependencias para manejo de archivos y datos
echo "📊 Agregando herramientas de manejo de datos..."
poetry add openpyxl  # Para Excel
poetry add aiofiles  # Para manejo asíncrono de archivos

# Dependencias para monitoring y logging
echo "📈 Agregando herramientas de monitoring..."
poetry add structlog  # Logging estructurado
poetry add prometheus-client  # Métricas

# Dependencias para validación y serialización
echo "✅ Agregando herramientas de validación..."
poetry add email-validator  # Validación de emails
poetry add phonenumbers  # Validación de teléfonos

echo ""
echo "🧪 Agregando dependencias de desarrollo..."

# Testing
poetry add --group dev pytest
poetry add --group dev pytest-asyncio
poetry add --group dev pytest-cov
poetry add --group dev pytest-mock
poetry add --group dev httpx  # Para testing de APIs

# Code Quality
poetry add --group dev black  # Formateo de código
poetry add --group dev isort  # Ordenar imports
poetry add --group dev flake8  # Linting
poetry add --group dev mypy  # Type checking

# Development tools
poetry add --group dev pre-commit  # Git hooks
poetry add --group dev bandit  # Security linting
poetry add --group dev safety  # Dependency security check

# Jupyter para experimentación
poetry add --group dev jupyter
poetry add --group dev ipykernel

# Performance profiling
poetry add --group dev memory-profiler
poetry add --group dev line-profiler

echo ""
echo "📋 Instalando todas las dependencias..."
poetry install

echo ""
echo "✅ ¡Dependencias instaladas exitosamente!"
echo ""
echo "📊 Resumen de dependencias agregadas:"
echo "=================================="
echo "🤖 IA & ML:"
echo "  - google-generativeai (Gemini 1.5 Pro)"
echo "  - pandas, numpy (Data Science basics)"
echo "  - tiktoken (Token counting)"
echo "  - langdetect (Language detection)"
echo ""
echo "🔧 Utilities:"
echo "  - aiofiles (Async file handling)"
echo "  - openpyxl (Excel support)"
echo "  - structlog (Structured logging)"
echo "  - prometheus-client (Metrics)"
echo ""
echo "🧪 Development:"
echo "  - pytest suite (Testing)"
echo "  - black, isort, flake8 (Code quality)"
echo "  - mypy (Type checking)"
echo "  - jupyter (Experimentation)"
echo "  - pre-commit (Git hooks)"
echo ""
echo "🚀 Próximos pasos:"
echo "1. Configurar tu API key de Gemini en .env"
echo "2. Ejecutar: poetry run uvicorn src.main:app --reload"
echo "3. Abrir: http://localhost:8000/docs"
echo ""
echo "💡 Comandos útiles:"
echo "poetry show                    # Ver todas las dependencias"
echo "poetry run pytest             # Ejecutar tests"
echo "poetry run black src/         # Formatear código"
echo "poetry run jupyter lab        # Abrir Jupyter"
