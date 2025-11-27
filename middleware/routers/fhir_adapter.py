"""
Adaptador FHIR bidireccional
Convierte entre recursos FHIR y modelo SQL
Integra con servidor HAPI FHIR
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import requests
from datetime import datetime

from database import db
from models import User
from routers.auth import get_current_user, require_role
from config import settings

router = APIRouter(prefix="/fhir", tags=["FHIR Interoperability"])


# =====================================================
# Funciones de conversión SQL → FHIR
# =====================================================

def sql_to_fhir_patient(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convertir paciente SQL a recurso FHIR Patient"""
    
    # Mapeo de género
    gender_map = {"M": "male", "F": "female", "O": "other"}
    
    fhir_patient = {
        "resourceType": "Patient",
        "id": str(patient_data["id_paciente"]),
        "identifier": [
            {
                "system": "http://hospital.com/identifiers/patient",
                "value": patient_data["identificacion"],
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": patient_data["tipo_identificacion"]
                        }
                    ]
                }
            }
        ],
        "name": [
            {
                "use": "official",
                "family": patient_data["apellidos"],
                "given": [patient_data["nombres"]]
            }
        ],
        "gender": gender_map.get(patient_data["genero"], "unknown"),
        "birthDate": patient_data["fecha_nacimiento"].isoformat() if patient_data.get("fecha_nacimiento") else None,
        "telecom": []
    }
    
    # Agregar teléfono si existe
    if patient_data.get("telefono"):
        fhir_patient["telecom"].append({
            "system": "phone",
            "value": patient_data["telefono"],
            "use": "mobile"
        })
    
    # Agregar email si existe
    if patient_data.get("email"):
        fhir_patient["telecom"].append({
            "system": "email",
            "value": patient_data["email"]
        })
    
    # Agregar dirección si existe
    if patient_data.get("direccion"):
        fhir_patient["address"] = [
            {
                "use": "home",
                "text": patient_data["direccion"],
                "city": patient_data.get("ciudad")
            }
        ]
    
    return fhir_patient


def sql_to_fhir_observation(obs_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convertir observación SQL a recurso FHIR Observation"""
    
    fhir_observation = {
        "resourceType": "Observation",
        "id": str(obs_data["id_observacion"]),
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
                    "code": obs_data.get("codigo_loinc", ""),
                    "display": obs_data["descripcion"]
                }
            ],
            "text": obs_data["descripcion"]
        },
        "subject": {
            "reference": f"Patient/{obs_data['id_paciente']}"
        },
        "encounter": {
            "reference": f"Encounter/{obs_data['id_encuentro']}"
        },
        "effectiveDateTime": obs_data["fecha_hora"].isoformat() if obs_data.get("fecha_hora") else None
    }
    
    # Agregar valor numérico si existe
    if obs_data.get("valor_numerico") is not None:
        fhir_observation["valueQuantity"] = {
            "value": float(obs_data["valor_numerico"]),
            "unit": obs_data.get("unidad", ""),
            "system": "http://unitsofmeasure.org",
            "code": obs_data.get("unidad", "")
        }
    
    # Agregar valor de texto si existe
    if obs_data.get("valor_texto"):
        fhir_observation["valueString"] = obs_data["valor_texto"]
    
    # Agregar rango de referencia si existe
    if obs_data.get("rango_referencia"):
        fhir_observation["referenceRange"] = [
            {
                "text": obs_data["rango_referencia"]
            }
        ]
    
    # Agregar interpretación si existe
    if obs_data.get("interpretacion"):
        fhir_observation["interpretation"] = [
            {
                "text": obs_data["interpretacion"]
            }
        ]
    
    return fhir_observation


def sql_to_fhir_encounter(encounter_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convertir encuentro SQL a recurso FHIR Encounter"""
    
    # Mapeo de tipo de encuentro
    class_map = {
        "consulta": "AMB",
        "urgencia": "EMER",
        "hospitalizacion": "IMP",
        "control": "AMB",
        "cirugia": "IMP"
    }
    
    fhir_encounter = {
        "resourceType": "Encounter",
        "id": str(encounter_data["id_encuentro"]),
        "status": encounter_data.get("estado", "finished"),
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": class_map.get(encounter_data["tipo_encuentro"], "AMB"),
            "display": encounter_data["tipo_encuentro"]
        },
        "subject": {
            "reference": f"Patient/{encounter_data['id_paciente']}"
        },
        "participant": [
            {
                "individual": {
                    "reference": f"Practitioner/{encounter_data['id_doctor']}"
                }
            }
        ],
        "period": {
            "start": encounter_data["fecha_hora"].isoformat() if encounter_data.get("fecha_hora") else None
        },
        "serviceProvider": {
            "reference": f"Organization/{encounter_data['id_sede']}"
        }
    }
    
    # Agregar motivo de consulta si existe
    if encounter_data.get("motivo_consulta"):
        fhir_encounter["reasonCode"] = [
            {
                "text": encounter_data["motivo_consulta"]
            }
        ]
    
    return fhir_encounter


def sql_to_fhir_condition(diag_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convertir diagnóstico SQL a recurso FHIR Condition"""
    
    fhir_condition = {
        "resourceType": "Condition",
        "id": str(diag_data["id_diagnostico"]),
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active" if diag_data.get("estado") == "activo" else "resolved"
                }
            ]
        },
        "code": {
            "coding": [],
            "text": diag_data["descripcion"]
        },
        "subject": {
            "reference": f"Patient/{diag_data['id_paciente']}"
        },
        "encounter": {
            "reference": f"Encounter/{diag_data['id_encuentro']}"
        },
        "recordedDate": diag_data["fecha_diagnostico"].isoformat() if diag_data.get("fecha_diagnostico") else None
    }
    
    # Agregar código ICD-10 si existe
    if diag_data.get("codigo_icd10"):
        fhir_condition["code"]["coding"].append({
            "system": "http://hl7.org/fhir/sid/icd-10",
            "code": diag_data["codigo_icd10"],
            "display": diag_data["descripcion"]
        })
    
    # Agregar código SNOMED CT si existe
    if diag_data.get("codigo_snomed"):
        fhir_condition["code"]["coding"].append({
            "system": "http://snomed.info/sct",
            "code": diag_data["codigo_snomed"],
            "display": diag_data["descripcion"]
        })
    
    return fhir_condition


# =====================================================
# Endpoints FHIR
# =====================================================

@router.get("/Patient/{patient_id}")
async def get_fhir_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener paciente en formato FHIR
    """
    query = "SELECT * FROM pacientes WHERE id_paciente = $1"
    patient = await db.fetch_one(query, patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    return sql_to_fhir_patient(patient)


@router.get("/Observation/{observation_id}")
async def get_fhir_observation(
    observation_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener observación en formato FHIR
    """
    query = "SELECT * FROM observaciones_clinicas WHERE id_observacion = $1"
    observation = await db.fetch_one(query, observation_id)
    
    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observación no encontrada"
        )
    
    return sql_to_fhir_observation(observation)


@router.get("/Encounter/{encounter_id}")
async def get_fhir_encounter(
    encounter_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener encuentro en formato FHIR
    """
    query = "SELECT * FROM encuentros_clinicos WHERE id_encuentro = $1"
    encounter = await db.fetch_one(query, encounter_id)
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encuentro no encontrado"
        )
    
    return sql_to_fhir_encounter(encounter)


@router.get("/Condition/{condition_id}")
async def get_fhir_condition(
    condition_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener diagnóstico en formato FHIR Condition
    """
    query = "SELECT * FROM diagnosticos WHERE id_diagnostico = $1"
    condition = await db.fetch_one(query, condition_id)
    
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico no encontrado"
        )
    
    return sql_to_fhir_condition(condition)


@router.post("/Patient/{patient_id}/sync")
async def sync_patient_to_hapi(
    patient_id: int,
    current_user: User = Depends(require_role(["medico", "historificacion"]))
):
    """
    Sincronizar paciente con servidor HAPI FHIR
    """
    # Obtener paciente
    query = "SELECT * FROM pacientes WHERE id_paciente = $1"
    patient = await db.fetch_one(query, patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Convertir a FHIR
    fhir_patient = sql_to_fhir_patient(patient)
    
    # Enviar a HAPI FHIR
    try:
        response = requests.put(
            f"{settings.FHIR_SERVER_URL}/Patient/{patient_id}",
            json=fhir_patient,
            headers={"Content-Type": "application/fhir+json"}
        )
        response.raise_for_status()
        
        return {
            "message": "Paciente sincronizado exitosamente",
            "fhir_resource": response.json()
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar con HAPI FHIR: {str(e)}"
        )


@router.get("/Patient/{patient_id}/bundle")
async def get_patient_bundle(
    patient_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener bundle FHIR completo de un paciente
    Incluye: Patient, Encounters, Observations, Conditions
    """
    # Obtener paciente
    patient = await db.fetch_one(
        "SELECT * FROM pacientes WHERE id_paciente = $1",
        patient_id
    )
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Obtener encuentros
    encounters = await db.fetch_all(
        "SELECT * FROM encuentros_clinicos WHERE id_paciente = $1",
        patient_id
    )
    
    # Obtener observaciones
    observations = await db.fetch_all(
        "SELECT * FROM observaciones_clinicas WHERE id_paciente = $1",
        patient_id
    )
    
    # Obtener diagnósticos
    conditions = await db.fetch_all(
        "SELECT * FROM diagnosticos WHERE id_paciente = $1",
        patient_id
    )
    
    # Crear bundle
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }
    
    # Agregar paciente
    bundle["entry"].append({
        "resource": sql_to_fhir_patient(patient)
    })
    
    # Agregar encuentros
    for encounter in encounters:
        bundle["entry"].append({
            "resource": sql_to_fhir_encounter(encounter)
        })
    
    # Agregar observaciones
    for observation in observations:
        bundle["entry"].append({
            "resource": sql_to_fhir_observation(observation)
        })
    
    # Agregar diagnósticos
    for condition in conditions:
        bundle["entry"].append({
            "resource": sql_to_fhir_condition(condition)
        })
    
    return bundle
