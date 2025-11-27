# 🚀 Inicio Rápido - Sistema HCE

## ✅ Sistema Listo

El sistema está completamente configurado y funcionando.

## 🌐 Acceso

**URL**: http://localhost:8000

## 👤 Credenciales (Todas usan contraseña: `test123`)

### Sede: Bogotá

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| 👨‍⚕️ Médico | `doctor1` | `test123` |
| 📋 Admisionista | `admisionista1` | `test123` |
| 🏥 Paciente | `paciente1` | `test123` |
| 📊 Historificación | `historificador1` | `test123` |

### Sede: Medellín

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| 👨‍⚕️ Médico | `doctor2` | `test123` |
| 📋 Admisionista | `admisionista2` | `test123` |
| 🏥 Paciente | `paciente2` | `test123` |
| 📊 Historificación | `historificador2` | `test123` |

### Sede: Cali

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| 👨‍⚕️ Médico | `doctor3` | `test123` |
| 📋 Admisionista | `admisionista3` | `test123` |
| 🏥 Paciente | `paciente3` | `test123` |
| 📊 Historificación | `historificador3` | `test123` |

## 🧪 Prueba Rápida

1. **Abre**: http://localhost:8000
2. **Login**: `doctor1` / `test123`
3. **Verifica**: Deberías ver el dashboard del médico con el badge "Clínica Central Bogotá"

## 📱 Funcionalidades por Rol

### 👨‍⚕️ Como Médico
- Buscar pacientes
- Crear encuentros clínicos
- Registrar observaciones (presión arterial, frecuencia cardíaca, etc.)
- Ver códigos LOINC en las observaciones

### 📋 Como Admisionista
- Registrar nuevos pacientes
- Buscar pacientes existentes
- Actualizar información de pacientes

### 🏥 Como Paciente
- Ver tu historia clínica completa
- Descargar historia clínica en PDF
- Ver encuentros de todas las sedes

### 📊 Como Historificación
- Buscar cualquier paciente
- Ver historias clínicas completas
- Exportar PDFs
- Generar bundles FHIR

## 🔧 Comandos Útiles

### Ver estado de servicios
```bash
docker-compose ps
```

### Ver logs en tiempo real
```bash
docker-compose logs -f middleware
```

### Reiniciar el sistema
```bash
powershell -ExecutionPolicy Bypass -File start.ps1
```

### Detener el sistema
```bash
docker-compose down
```

## 🌐 Endpoints Útiles

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **HAPI FHIR**: http://localhost:8080/fhir/metadata

## ❓ Solución de Problemas

### No puedo hacer login
Las contraseñas ya están actualizadas. Usa `test123` para todos los usuarios.

### El puerto 8000 no responde
```bash
docker logs hce-middleware
docker-compose restart middleware
```

### Página en blanco
Espera 30 segundos y recarga la página. Los servicios pueden tardar en iniciar.

## 📊 Datos de Ejemplo

La base de datos incluye:
- 12 usuarios (4 roles × 3 sedes)
- 3 sedes clínicas
- Datos de ejemplo listos para probar

## 🎯 Próximos Pasos

1. ✅ Login con diferentes roles
2. ✅ Probar funcionalidades de cada rol
3. ✅ Exportar PDF de historia clínica
4. ✅ Verificar códigos LOINC, ICD-10, SNOMED
5. ✅ Acceder desde dispositivo móvil (usa tu IP local)

---

**¿Necesitas ayuda?** Revisa [`DEPLOYMENT_GUIDE.md`](file:///C:/Users/lican/OneDrive/Documents/IDS-HCE/DEPLOYMENT_GUIDE.md) para más detalles.
