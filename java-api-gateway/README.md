# Java API Gateway

API Gateway en Spring Boot para el proyecto GenIA.

## 🚀 Ejecución Local

### Con Maven
```bash
# Compilar
mvn clean compile

# Ejecutar
mvn spring-boot:run

# Ejecutar con perfil específico
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

### Con Java directo
```bash
# Compilar
mvn clean package

# Ejecutar JAR
java -jar target/api-gateway-1.0.0.jar
```

## 🐳 Docker

```bash
# Construir imagen
docker build -t genia-gateway .

# Ejecutar container
docker run -p 8080:8080 \
  -e PYTHON_SERVICE_URL=http://python-service:8000 \
  genia-gateway
```

## 📋 Endpoints

### API Principal
- `POST /api/genia/query` - Consulta a GenIA (producción)
- `POST /api/genia/query/mock` - Consulta mock
- `GET /api/genia/health` - Health check
- `GET /api/genia/status` - Status detallado

### Actuator
- `GET /actuator/health` - Spring Boot health
- `GET /actuator/info` - Información de la aplicación
- `GET /actuator/metrics` - Métricas

## 🧪 Testing

```bash
# Ejecutar tests
mvn test

# Test con coverage
mvn test jacoco:report
```

## 📊 Ejemplo de Request

```bash
curl -X POST http://localhost:8080/api/genia/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explícame qué es la inteligencia artificial",
    "maxTokens": 150,
    "temperature": 0.7
  }'
```

## ⚙️ Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `PYTHON_SERVICE_URL` | URL del servicio Python | `http://localhost:8000` |
| `SERVER_PORT` | Puerto del gateway | `8080` |
| `LOGGING_LEVEL_COM_GENIA` | Level de logging | `DEBUG` |

## 🏗️ Estructura del Proyecto
```bash
src/
├── main/
│ ├── java/com/genia/gateway/
│ │ ├── Application.java # Main class
│ │ ├── controller/
│ │ │ └── GeniaController.java # REST controller
│ │ ├── model/
│ │ │ ├── QueryRequest.java # Request DTO
│ │ │ └── QueryResponse.java # Response DTO
│ │ └── service/
│ │ └── GeniaService.java # Business logic
│ └── resources/
│ └── application.yml # Configuration
└── test/ # Tests
```