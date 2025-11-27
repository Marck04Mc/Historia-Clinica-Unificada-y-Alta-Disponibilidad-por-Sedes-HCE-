# Mapeo FHIR y Estándares de Interoperabilidad

## Introducción

Este documento describe el mapeo entre el modelo relacional de la base de datos y los recursos HL7 FHIR R4, así como el uso de terminologías estándar (LOINC, SNOMED CT, ICD-10).

## Recursos FHIR Implementados

### 1. Patient (Paciente)

**Mapeo SQL → FHIR:**

| Campo SQL | Campo FHIR | Transformación |
|-----------|------------|----------------|
| `id_paciente` | `id` | String |
| `identificacion` | `identifier[0].value` | String |
| `tipo_identificacion` | `identifier[0].type.coding[0].code` | String |
| `nombres` | `name[0].given[0]` | String |
| `apellidos` | `name[0].family` | String |
| `genero` | `gender` | M→male, F→female, O→other |
| `fecha_nacimiento` | `birthDate` | ISO 8601 |
| `telefono` | `telecom[0].value` | String (system=phone) |
| `email` | `telecom[1].value` | String (system=email) |
| `direccion` | `address[0].text` | String |
| `ciudad` | `address[0].city` | String |

**Ejemplo de Recurso FHIR:**

```json
{
  "resourceType": "Patient",
  "id": "1",
  "identifier": [
    {
      "system": "http://hospital.com/identifiers/patient",
      "value": "1234567890",
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "CC"
          }
        ]
      }
    }
  ],
  "name": [
    {
      "use": "official",
      "family": "Rodríguez",
      "given": ["Pedro"]
    }
  ],
  "gender": "male",
  "birthDate": "1985-03-15",
  "telecom": [
    {
      "system": "phone",
      "value": "3001234567",
      "use": "mobile"
    },
    {
      "system": "email",
      "value": "prodriguez@email.com"
    }
  ],
  "address": [
    {
      "use": "home",
      "text": "Calle 100 # 15-20",
      "city": "Bogotá"
    }
  ]
}
```

### 2. Observation (Observación Clínica)

**Mapeo SQL → FHIR:**

| Campo SQL | Campo FHIR | Transformación |
|-----------|------------|----------------|
| `id_observacion` | `id` | String |
| `codigo_loinc` | `code.coding[0].code` | LOINC code |
| `descripcion` | `code.text` | String |
| `valor_numerico` | `valueQuantity.value` | Number |
| `unidad` | `valueQuantity.unit` | String |
| `valor_texto` | `valueString` | String |
| `fecha_hora` | `effectiveDateTime` | ISO 8601 |
| `id_paciente` | `subject.reference` | Patient/{id} |
| `id_encuentro` | `encounter.reference` | Encounter/{id} |

**Códigos LOINC Utilizados:**

| Código LOINC | Descripción | Unidad Típica |
|--------------|-------------|---------------|
| 8480-6 | Presión Arterial Sistólica | mmHg |
| 8462-4 | Presión Arterial Diastólica | mmHg |
| 8867-4 | Frecuencia Cardíaca | lpm |
| 8310-5 | Temperatura Corporal | °C |
| 29463-7 | Peso Corporal | kg |
| 8302-2 | Estatura | cm |
| 2339-0 | Glucosa en Sangre | mg/dL |
| 2571-8 | Triglicéridos | mg/dL |
| 2093-3 | Colesterol Total | mg/dL |

**Ejemplo de Recurso FHIR:**

```json
{
  "resourceType": "Observation",
  "id": "1",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "vital-signs",
          "display": "Vital Signs"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "8480-6",
        "display": "Presión Arterial Sistólica"
      }
    ],
    "text": "Presión Arterial Sistólica"
  },
  "subject": {
    "reference": "Patient/1"
  },
  "encounter": {
    "reference": "Encounter/1"
  },
  "effectiveDateTime": "2024-11-25T10:30:00Z",
  "valueQuantity": {
    "value": 130,
    "unit": "mmHg",
    "system": "http://unitsofmeasure.org",
    "code": "mm[Hg]"
  },
  "referenceRange": [
    {
      "text": "90-120"
    }
  ]
}
```

### 3. Encounter (Encuentro Clínico)

**Mapeo SQL → FHIR:**

| Campo SQL | Campo FHIR | Transformación |
|-----------|------------|----------------|
| `id_encuentro` | `id` | String |
| `estado` | `status` | activo→in-progress, finalizado→finished |
| `tipo_encuentro` | `class.code` | Mapeo a ActCode |
| `fecha_hora` | `period.start` | ISO 8601 |
| `id_paciente` | `subject.reference` | Patient/{id} |
| `id_doctor` | `participant[0].individual.reference` | Practitioner/{id} |
| `id_sede` | `serviceProvider.reference` | Organization/{id} |
| `motivo_consulta` | `reasonCode[0].text` | String |

**Mapeo de Tipos de Encuentro:**

| Tipo SQL | Código ActCode | Display |
|----------|----------------|---------|
| consulta | AMB | Ambulatory |
| urgencia | EMER | Emergency |
| hospitalizacion | IMP | Inpatient |
| control | AMB | Ambulatory |
| cirugia | IMP | Inpatient |

### 4. Condition (Diagnóstico)

**Mapeo SQL → FHIR:**

| Campo SQL | Campo FHIR | Transformación |
|-----------|------------|----------------|
| `id_diagnostico` | `id` | String |
| `codigo_icd10` | `code.coding[0].code` | ICD-10 code |
| `codigo_snomed` | `code.coding[1].code` | SNOMED CT code |
| `descripcion` | `code.text` | String |
| `estado` | `clinicalStatus.coding[0].code` | activo→active, resuelto→resolved |
| `fecha_diagnostico` | `recordedDate` | ISO 8601 |
| `id_paciente` | `subject.reference` | Patient/{id} |
| `id_encuentro` | `encounter.reference` | Encounter/{id} |

**Códigos ICD-10 Comunes:**

| Código ICD-10 | Descripción |
|---------------|-------------|
| I10 | Hipertensión Arterial Esencial |
| E11 | Diabetes Mellitus Tipo 2 |
| J06.9 | Infección Aguda de Vías Respiratorias Superiores |
| K21.9 | Enfermedad por Reflujo Gastroesofágico |
| M54.5 | Dolor Lumbar |
| R10.4 | Dolor Abdominal |
| S82.2 | Fractura de Tibia |

**Códigos SNOMED CT Correspondientes:**

| Código SNOMED | Descripción |
|---------------|-------------|
| 38341003 | Hipertensión Arterial |
| 44054006 | Diabetes Mellitus Tipo 2 |
| 54150009 | Infección Respiratoria Superior |
| 235595009 | Enfermedad por Reflujo Gastroesofágico |
| 279039007 | Dolor Lumbar |
| 21522001 | Dolor Abdominal |
| 413294005 | Fractura de Tibia |

## Interoperabilidad Sintáctica

### Formatos Soportados

1. **JSON**: Formato principal para API REST
2. **XML**: Soportado por HAPI FHIR (futuro)

### Content Types

- `application/json` - JSON estándar
- `application/fhir+json` - JSON FHIR
- `application/fhir+xml` - XML FHIR (futuro)

## Interoperabilidad Semántica

### Sistemas de Codificación

| Sistema | URI | Uso |
|---------|-----|-----|
| LOINC | http://loinc.org | Observaciones clínicas y laboratorio |
| SNOMED CT | http://snomed.info/sct | Procedimientos y diagnósticos |
| ICD-10 | http://hl7.org/fhir/sid/icd-10 | Diagnósticos |
| UCUM | http://unitsofmeasure.org | Unidades de medida |
| ActCode | http://terminology.hl7.org/CodeSystem/v3-ActCode | Tipos de encuentro |

### Extensiones Personalizadas

Actualmente no se utilizan extensiones personalizadas. Todos los datos se mapean a elementos estándar de FHIR R4.

## Bundles FHIR

### Bundle de Historia Clínica Completa

El endpoint `/fhir/Patient/{id}/bundle` genera un Bundle de tipo `collection` que incluye:

1. Recurso Patient
2. Todos los Encounters del paciente
3. Todas las Observations del paciente
4. Todas las Conditions del paciente

**Ejemplo de Bundle:**

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "1",
        ...
      }
    },
    {
      "resource": {
        "resourceType": "Encounter",
        "id": "1",
        ...
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "1",
        ...
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "id": "1",
        ...
      }
    }
  ]
}
```

## Sincronización con HAPI FHIR

### Endpoint de Sincronización

`POST /fhir/Patient/{id}/sync`

**Proceso:**
1. Obtener datos del paciente desde PostgreSQL
2. Convertir a recurso FHIR Patient
3. Enviar a HAPI FHIR mediante PUT
4. Retornar recurso FHIR creado/actualizado

### Estrategia de Sincronización

Actualmente la sincronización es **manual** mediante llamada explícita al endpoint. En el futuro se puede implementar:

- Sincronización automática en cada creación/actualización
- Sincronización por lotes (batch)
- Sincronización bidireccional (FHIR → SQL)

## Validación de Recursos

### Validación en Backend

- Validación de estructura mediante Pydantic
- Validación de códigos LOINC, SNOMED, ICD-10 (básica)
- Validación de referencias entre recursos

### Validación en HAPI FHIR

- Validación completa contra perfiles FHIR R4
- Validación de terminologías
- Validación de cardinalidad y tipos de datos

## Búsqueda FHIR

### Parámetros de Búsqueda Soportados

**Patient:**
- `identifier` - Búsqueda por identificación
- `name` - Búsqueda por nombre
- `birthdate` - Búsqueda por fecha de nacimiento

**Observation:**
- `patient` - Observaciones de un paciente
- `code` - Observaciones por código LOINC
- `date` - Observaciones por fecha

**Encounter:**
- `patient` - Encuentros de un paciente
- `date` - Encuentros por fecha

## Consideraciones de Implementación

### Rendimiento

- Conversión FHIR realizada en memoria (rápida)
- Cache de recursos FHIR frecuentes (futuro)
- Paginación en búsquedas

### Consistencia

- Transacciones en PostgreSQL garantizan consistencia
- Sincronización FHIR eventual (no inmediata)
- Reconciliación manual en caso de inconsistencias

### Privacidad

- Recursos FHIR respetan permisos de acceso
- No se exponen datos sensibles sin autenticación
- Logs de auditoría de acceso a recursos FHIR

## Referencias

- [HL7 FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [LOINC Database](https://loinc.org/)
- [SNOMED CT Browser](https://browser.ihtsdotools.org/)
- [ICD-10 Codes](https://www.who.int/standards/classifications/classification-of-diseases)
- [HAPI FHIR Documentation](https://hapifhir.io/)
