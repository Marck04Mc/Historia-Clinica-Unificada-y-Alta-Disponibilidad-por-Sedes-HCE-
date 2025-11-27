# Sistema de Historia Clínica Electrónica Interoperable

Sistema multisede de Historia Clínica Electrónica (HCE) con interoperabilidad FHIR, desarrollado con PostgreSQL+Citus, FastAPI, y Kubernetes.

## 🎯 Características Principales

- **Interoperabilidad FHIR**: Integración completa con servidor HAPI FHIR y recursos HL7 FHIR R4
- **Multisede**: Soporte para 3 sedes clínicas con historia clínica única unificada
- **Seguridad**: Autenticación OAuth2 + JWT con contexto de sede
- **Roles Diferenciados**: 4 interfaces especializadas (Paciente, Admisionista, Médico, Historificación)
- **Estándares Médicos**: Codificación con LOINC, SNOMED CT, ICD-10
- **Exportación PDF**: Generación de historias clínicas en PDF con datos FHIR
- **Escalabilidad**: Base de datos distribuida con PostgreSQL + Citus
- **Despliegue**: Contenedorización con Docker y orquestación con Kubernetes

## 📋 Requisitos Previos

- Docker Desktop (con Kubernetes habilitado) o Minikube
- Python 3.11+
- PostgreSQL 14+ con extensión Citus
- Git

## 🚀 Inicio Rápido

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd IDS-HCE
```

### 2. Despliegue con Docker Compose (Desarrollo)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Esperar a que los servicios estén listos (puede tomar 2-3 minutos)
docker-compose logs -f

# Verificar que todos los servicios estén corriendo
docker-compose ps
```

### 3. Acceder a la Aplicación

- **Frontend**: http://localhost:8000
- **HAPI FHIR**: http://localhost:8080/fhir
- **API Docs**: http://localhost:8000/docs

### 4. Credenciales de Prueba

| Rol | Usuario | Contraseña | Sede |
|-----|---------|------------|------|
| Paciente | paciente1 | test123 | Bogotá |
| Admisionista | admisionista1 | test123 | Bogotá |
| Médico | doctor1 | test123 | Bogotá |
| Historificación | historificador1 | test123 | Bogotá |

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Clientes (Web/Móvil)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              FastAPI Middleware (Kubernetes)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Auth Router  │  │ FHIR Adapter │  │  PDF Export  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────┬───────────────────────┬──────────────────────────┘
         │                       │
┌────────▼────────┐    ┌────────▼────────┐
│  PostgreSQL +   │    │   HAPI FHIR     │
│     Citus       │    │    Server       │
│  (Distribuido)  │    │   (R4 FHIR)     │
└─────────────────┘    └─────────────────┘
```

## 📁 Estructura del Proyecto

```
IDS-HCE/
├── database/
│   ├── schema.sql              # Esquema de base de datos
│   └── init_citus.sql          # Configuración Citus
├── middleware/
│   ├── routers/
│   │   ├── auth.py             # Autenticación OAuth2+JWT
│   │   ├── patients.py         # Gestión de pacientes
│   │   ├── encounters.py       # Encuentros clínicos
│   │   ├── observations.py     # Observaciones clínicas
│   │   ├── fhir_adapter.py     # Adaptador FHIR
│   │   └── pdf_export.py       # Exportación PDF
│   ├── templates/              # Templates Jinja2
│   ├── static/                 # CSS y JavaScript
│   ├── main.py                 # Aplicación principal
│   ├── models.py               # Modelos Pydantic
│   ├── database.py             # Conexión DB
│   ├── config.py               # Configuración
│   ├── Dockerfile              # Imagen Docker
│   └── requirements.txt        # Dependencias Python
├── k8s/
│   ├── deployment.yaml         # Deployment Kubernetes
│   ├── service.yaml            # Service Kubernetes
│   ├── configmap.yaml          # ConfigMap
│   └── secret.yaml             # Secrets
├── docs/                       # Documentación
└── docker-compose.yml          # Orquestación Docker
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en el directorio `middleware/`:

```env
DB_HOST=postgres-coordinator
DB_PORT=5432
DB_NAME=hce_db
DB_USER=postgres
DB_PASSWORD=postgres123
FHIR_SERVER_URL=http://hapi-fhir:8080/fhir
JWT_SECRET_KEY=tu-clave-secreta-cambiar-en-produccion
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
CORS_ORIGINS=*
```

## 🐳 Despliegue en Kubernetes (Minikube)

El proyecto incluye configuración completa para desplegarse en un clúster de Kubernetes local usando Minikube.

### ¿Por qué Kubernetes?
- **Escalabilidad**: Permite ejecutar múltiples réplicas de los servicios para manejar más tráfico.
- **Alta Disponibilidad**: Reinicia automáticamente los contenedores si fallan (self-healing).
- **Gestión de Configuración**: Manejo centralizado de variables de entorno y secretos.
- **Portabilidad**: La misma configuración funciona en local (Minikube) y en la nube (AWS, Azure, GCP).

### Prerrequisitos
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) instalado.
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado.

### Pasos para Desplegar (Automático)

1. **Ejecutar Script de Despliegue:**
   Hemos incluido un script de PowerShell que automatiza todo el proceso:
   ```powershell
   .\deploy_minikube.ps1
   ```
   Este script se encargará de:
   - Iniciar Minikube si no está corriendo.
   - Configurar el entorno Docker de Minikube.
   - Construir la imagen del middleware dentro del clúster.
   - Aplicar todos los manifiestos de Kubernetes (`k8s/`).
   - Mostrar la URL de acceso final.

2. **Acceder al Dashboard:**
   El script mostrará la URL al finalizar. También puedes obtenerla con:
   ```bash
   minikube service hce-middleware --url
   ```

### Pasos para Desplegar (Manual)

Si prefieres hacerlo paso a paso:

1. **Iniciar Minikube:**
   ```bash
   minikube start
   ```

2. **Configurar Docker:**
   ```powershell
   & minikube -p minikube docker-env --shell powershell | Invoke-Expression
   ```

3. **Construir Imagen:**
   ```bash
   docker build -t middleware-citus:1.0 ./middleware
   ```

4. **Aplicar Manifiestos:**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/schema-configmap.yaml
   kubectl apply -f k8s/postgres-deployment.yaml
   kubectl apply -f k8s/hapi-fhir-deployment.yaml
   kubectl apply -f k8s/middleware-deployment.yaml
   ```

### Solución de Problemas

- **Error de Imagen (ErrImageNeverPull):**
  Si ves este error, significa que la imagen no se construyó dentro de Minikube. Ejecuta el script de reparación:
  ```powershell
  .\build_middleware.ps1
  ```

- **Ver Estado:**
  ```bash
  kubectl get pods
  minikube dashboard
  ```

## 📊 Endpoints de la API

### Autenticación

- `POST /auth/token` - Obtener token JWT
- `GET /auth/me` - Información del usuario actual
- `GET /auth/sede` - Información de la sede

### Pacientes

- `GET /api/patients` - Listar pacientes (filtrado por sede/rol)
- `POST /api/patients` - Crear paciente (admisionista)
- `GET /api/patients/{id}` - Obtener paciente
- `PUT /api/patients/{id}` - Actualizar paciente

### Encuentros Clínicos

- `GET /api/encounters` - Listar encuentros
- `POST /api/encounters` - Crear encuentro (médico)
- `GET /api/encounters/{id}` - Detalle de encuentro

### Observaciones

- `POST /api/observations` - Crear observación (médico)
- `GET /api/observations/{encounter_id}` - Observaciones de un encuentro

### FHIR

- `GET /fhir/Patient/{id}` - Paciente en formato FHIR
- `GET /fhir/Observation/{id}` - Observación en formato FHIR
- `GET /fhir/Encounter/{id}` - Encuentro en formato FHIR
- `GET /fhir/Patient/{id}/bundle` - Bundle FHIR completo

### Exportación

- `GET /api/pdf/patient/{id}` - Descargar historia clínica en PDF

## 🧪 Pruebas

### Pruebas Manuales

1. **Login**: Acceder con diferentes roles
2. **Paciente**: Ver historia clínica y descargar PDF
3. **Admisionista**: Registrar nuevo paciente
4. **Médico**: Crear encuentro y registrar observaciones
5. **Historificación**: Buscar pacientes y ver historias

### Pruebas de API

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/auth/token \
  -d "username=doctor1&password=test123"

# Listar pacientes (con token)
curl http://localhost:8000/api/patients \
  -H "Authorization: Bearer <TOKEN>"
```

## 🌐 Acceso desde Dispositivos Móviles

1. Obtener IP local del servidor:
   ```bash
   ipconfig  # Windows
   ifconfig  # Linux/Mac
   ```

2. Desde dispositivo móvil en la misma red:
   ```
   http://<IP-LOCAL>:8000
   ```

## 📱 Sedes Configuradas

1. **Clínica Central Bogotá** (Sede 1)
   - Color: Rojo
   - Ciudad: Bogotá

2. **Clínica del Valle Medellín** (Sede 2)
   - Color: Azul
   - Ciudad: Medellín

3. **Clínica del Pacífico Cali** (Sede 3)
   - Color: Verde
   - Ciudad: Cali

## 🔒 Seguridad

- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración de 30 minutos
- Contexto de sede en cada token
- Validación de roles en cada endpoint
- CORS configurado
- SQL preparado para prevenir inyección

## 📚 Documentación Adicional

- [Arquitectura del Sistema](docs/ARCHITECTURE.md)
- [Mapeo FHIR](docs/FHIR_MAPPING.md)
- [Estrategia Multisede](docs/MULTISITE_STRATEGY.md)

## 🤝 Contribución

Este es un proyecto académico desarrollado para el curso de Interoperabilidad en Sistemas de Salud.

## 📄 Licencia

Proyecto académico - Universidad XYZ - 2024

## 👥 Autores

- Equipo de desarrollo IDS-HCE

## 📞 Soporte

Para preguntas o problemas, contactar al equipo de desarrollo.
