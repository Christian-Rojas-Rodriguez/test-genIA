# 📮 Postman Testing Collection

Esta colección contiene todos los tests necesarios para probar la integración GenIA.

## 🚀 Setup

1. **Importar colección**: Importa `GenIA-Integration.postman_collection.json`
2. **Importar environment**: Importa `GenIA-Environment.postman_environment.json`
3. **Seleccionar environment**: Activa el environment en Postman

## 🧪 Tests Incluidos

### Health Checks
- ✅ Java Gateway Health
- ✅ Java Gateway Status  
- ✅ Python Service Health (directo)

### GenIA Queries
- ✅ Query Mock (testing)
- ✅ Query Producción (real GenIA API)
- ✅ Query con parámetros personalizados

### Error Testing
- ❌ Request con prompt vacío
- ❌ Request con maxTokens excedido
- ❌ Request malformado

## 🌍 Environments

| Environment | Java Gateway | Python Service | Uso |
|-------------|--------------|----------------|-----|
| **Local** | `localhost:8080` | `localhost:8000` | Desarrollo local |
| **Docker** | `localhost:8080` | `localhost:8000` | Docker Compose |
| **Production** | `api.company.com` | N/A | Producción |

## 📋 Ejemplo de Request

```json
{
  "prompt": "Explícame qué es la inteligencia artificial",
  "maxTokens": 150,
  "temperature": 0.7
}
```

## 🔄 Flujo de Testing

1. **Start Services**: `docker-compose up -d`
2. **Health Checks**: Verificar que servicios están up
3. **Mock Tests**: Probar con endpoints mock
4. **Production Tests**: Probar con GenIA real (si tienes API key)
5. **Error Tests**: Verificar manejo de errores