# Gestión Segura de API Keys y Secrets

## 🔐 Para Desarrollo Local

### 1. Configurar tu API Key

```bash
# 1. Copia el template
cp python-genia-service/.env.example python-genia-service/.env

# 2. Edita el archivo .env y reemplaza tu API key real
# GENIA_API_KEY=tu-api-key-real-aqui
```

### 2. Variables de Entorno Disponibles

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `GENIA_API_KEY` | Tu API key de Gemini 1.5 Pro | `AIzaSyC...` |
| `GENIA_API_URL` | URL base de la API | `https://generativelanguage.googleapis.com` |
| `ENVIRONMENT` | Entorno de ejecución | `development`, `testing`, `production` |
| `DEBUG` | Modo debug | `true`, `false` |
| `LOG_LEVEL` | Nivel de logging | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## 🚀 Para GitHub Actions (CI/CD)

### 1. Configurar GitHub Secrets

En tu repositorio de GitHub:
1. Ve a **Settings** → **Secrets and variables** → **Actions**
2. Crea estos secrets:

| Secret | Valor |
|--------|-------|
| `GENIA_API_KEY` | Tu API key de Gemini 1.5 Pro |
| `GENIA_API_URL` | `https://generativelanguage.googleapis.com` |

### 2. Los Secrets se usan automáticamente

El workflow de GitHub Actions (`.github/workflows/ci.yml`) ya está configurado para usar estos secrets automáticamente.

## 🔒 Mejores Prácticas de Seguridad

### ✅ SÍ hacer:
- **Usar archivos `.env`** para desarrollo local
- **Usar GitHub Secrets** para CI/CD
- **Nunca commitear** archivos `.env` (ya está en `.gitignore`)
- **Rotar API keys** periódicamente
- **Usar diferentes keys** para diferentes entornos

### ❌ NO hacer:
- **Nunca hardcodear** API keys en el código
- **Nunca subir** archivos `.env` a GitHub
- **Nunca compartir** API keys por email/chat
- **Nunca usar** la misma key para todos los entornos

## 🛠️ Para Producción

### Docker/Kubernetes
```yaml
# docker-compose.prod.yml
environment:
  - GENIA_API_KEY=${GENIA_API_KEY}
  - ENVIRONMENT=production
```

### Variables de Entorno del Sistema
```bash
export GENIA_API_KEY="tu-key-aqui"
export ENVIRONMENT="production"
```

## 🧪 Para Testing

Para los tests, puedes usar:
```bash
# En tu .env para testing
GENIA_API_KEY=test-key-mock
ENVIRONMENT=testing
```

## 📞 Soporte

Si tu API key se compromete:
1. **Revoca inmediatamente** la key en Google Cloud Console
2. **Genera una nueva** API key
3. **Actualiza** todos los entornos con la nueva key
4. **Revisa logs** para detectar uso no autorizado 