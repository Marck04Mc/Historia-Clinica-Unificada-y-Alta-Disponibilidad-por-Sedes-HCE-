# Guía de Despliegue Exitoso - Sistema HCE

## ✅ Sistema Desplegado Correctamente

El sistema de Historia Clínica Electrónica Interoperable está ahora funcionando correctamente.

## 🚀 Servicios Activos

- **PostgreSQL**: `localhost:5432` (healthy)
- **HAPI FHIR**: `localhost:8080` (iniciando, puede tardar 1-2 minutos)
- **FastAPI Middleware**: `localhost:8000` (running)

## 🌐 Acceso al Sistema

Abre tu navegador y visita:

**http://localhost:8000**

## 👤 Credenciales de Prueba

### Médico (Bogotá)
- **Usuario**: `doctor1`
- **Contraseña**: `test123`

### Admisionista (Bogotá)
- **Usuario**: `admisionista1`
- **Contraseña**: `test123`

### Paciente (Bogotá)
- **Usuario**: `paciente1`
- **Contraseña**: `test123`

### Historificación (Bogotá)
- **Usuario**: `historificador1`
- **Contraseña**: `test123`

## 📱 Acceso desde Dispositivo Móvil

1. Obtén tu IP local:
   ```powershell
   ipconfig
   ```
   Busca "IPv4 Address" (ejemplo: 192.168.1.100)

2. Desde tu móvil en la misma red WiFi:
   ```
   http://TU-IP-LOCAL:8000
   ```
   Ejemplo: `http://192.168.1.100:8000`

## 🔧 Comandos Útiles

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Ver logs de un servicio específico
```bash
docker-compose logs -f middleware
docker-compose logs -f postgres
docker-compose logs -f hapi-fhir
```

### Reiniciar un servicio
```bash
docker-compose restart middleware
```

### Detener todo
```bash
docker-compose down
```

### Reiniciar todo
```bash
powershell -ExecutionPolicy Bypass -File start.ps1
```

## 🧪 Pruebas Recomendadas

### 1. Login y Navegación
- Inicia sesión con cada rol
- Verifica que el badge de sede muestre "Clínica Central Bogotá"
- Navega por las diferentes secciones

### 2. Funcionalidad por Rol

**Como Admisionista:**
- Registra un nuevo paciente
- Busca pacientes existentes

**Como Médico:**
- Selecciona un paciente
- Crea un encuentro clínico
- Registra observaciones (presión arterial, frecuencia cardíaca)
- Verifica que los códigos LOINC se muestren

**Como Paciente:**
- Ve tu historia clínica
- Descarga el PDF de tu historia

**Como Historificación:**
- Busca pacientes
- Exporta historias clínicas en PDF
- Visualiza bundles FHIR

### 3. Interoperabilidad FHIR

Abre en tu navegador:
```
http://localhost:8080/fhir/metadata
```

Deberías ver la metadata del servidor FHIR.

## ⚠️ Notas Importantes

1. **HAPI FHIR tarda en iniciar**: El servidor FHIR puede tardar 1-2 minutos en estar completamente operativo después de `docker-compose up`.

2. **Primera vez**: La primera vez que accedes, la base de datos se inicializa con datos de ejemplo.

3. **Cambios en código**: Si modificas el código del middleware, ejecuta:
   ```bash
   docker-compose up -d --build middleware
   ```

## 🎯 Endpoints de API

### Health Check
```bash
curl http://localhost:8000/health
```

### Autenticación
```bash
curl -X POST http://localhost:8000/auth/token \
  -d "username=doctor1&password=test123"
```

### Documentación Interactiva
```
http://localhost:8000/docs
```

## 📊 Verificación del Sistema

Ejecuta este comando para ver el estado de todos los servicios:
```bash
docker-compose ps
```

Todos los servicios deberían mostrar estado "Up" o "healthy".

## 🐛 Solución de Problemas

### El puerto 8000 no responde
```bash
docker logs hce-middleware
```

### Error de base de datos
```bash
docker logs hce-postgres
```

### HAPI FHIR no inicia
```bash
docker logs hce-hapi-fhir
```
(Es normal que tarde, espera 2-3 minutos)

### Reinicio completo
```bash
docker-compose down -v
powershell -ExecutionPolicy Bypass -File start.ps1
```

## ✨ Funcionalidades Implementadas

✅ Autenticación OAuth2 + JWT con contexto de sede  
✅ 4 interfaces diferenciadas por rol  
✅ Gestión de pacientes multisede  
✅ Registro de encuentros clínicos  
✅ Observaciones con códigos LOINC  
✅ Diagnósticos con ICD-10 y SNOMED CT  
✅ Exportación de historias clínicas a PDF  
✅ Adaptador FHIR bidireccional  
✅ Integración con HAPI FHIR  
✅ Historia clínica única multisede  
✅ Diseño responsivo para móviles  

## 🎉 ¡Listo para Usar!

El sistema está completamente funcional y listo para pruebas y demostración.
