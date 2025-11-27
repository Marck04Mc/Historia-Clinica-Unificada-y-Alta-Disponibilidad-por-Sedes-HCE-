"""
Router de observaciones clínicas
Gestión de observaciones con códigos LOINC
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from database import db
from models import ObservacionClinica, ObservacionClinicaCreate, User
from routers.auth import get_current_user, require_role

router = APIRouter(prefix="/api/observations", tags=["Observaciones Clínicas"])


@router.get("/{encounter_id}", response_model=List[ObservacionClinica])
async def get_observations(
    encounter_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener todas las observaciones de un encuentro clínico
    """
    # Verificar que el encuentro existe
    encounter = await db.fetch_one(
        "SELECT id_paciente FROM encuentros_clinicos WHERE id_encuentro = $1",
        encounter_id
    )
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encuentro no encontrado"
        )
    
    query = """
        SELECT * FROM observaciones_clinicas
        WHERE id_encuentro = $1 AND id_paciente = $2
        ORDER BY fecha_hora DESC
    """
    
    observations = await db.fetch_all(query, encounter_id, encounter["id_paciente"])
    return observations


@router.post("", response_model=ObservacionClinica, status_code=status.HTTP_201_CREATED)
async def create_observation(
    observation: ObservacionClinicaCreate,
    current_user: User = Depends(require_role(["medico"]))
):
    """
    Crear una nueva observación clínica
    Solo médicos pueden crear observaciones
    """
    # Verificar que el encuentro existe y pertenece al médico
    encounter = await db.fetch_one(
        """
        SELECT id_paciente, id_doctor FROM encuentros_clinicos
        WHERE id_encuentro = $1
        """,
        observation.id_encuentro
    )
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encuentro no encontrado"
        )
    
    # Verificar que el id_paciente coincide
    if encounter["id_paciente"] != observation.id_paciente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El paciente no coincide con el encuentro"
        )
    
    # Insertar observación
    query = """
        INSERT INTO observaciones_clinicas (
            id_encuentro, id_paciente, codigo_loinc, descripcion,
            valor_numerico, valor_texto, unidad, rango_referencia, interpretacion
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
    """
    
    new_observation = await db.execute_returning(
        query,
        observation.id_encuentro,
        observation.id_paciente,
        observation.codigo_loinc,
        observation.descripcion,
        observation.valor_numerico,
        observation.valor_texto,
        observation.unidad,
        observation.rango_referencia,
        observation.interpretacion
    )
    
    return new_observation


@router.get("/patient/{patient_id}", response_model=List[dict])
async def get_patient_observations(
    patient_id: int,
    loinc_code: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener todas las observaciones de un paciente
    Opcionalmente filtrar por código LOINC
    """
    if loinc_code:
        query = """
            SELECT o.*, e.fecha_hora as encuentro_fecha, s.nombre as sede_nombre
            FROM observaciones_clinicas o
            JOIN encuentros_clinicos e ON o.id_encuentro = e.id_encuentro
            JOIN sedes s ON e.id_sede = s.id_sede
            WHERE o.id_paciente = $1 AND o.codigo_loinc = $2
            ORDER BY o.fecha_hora DESC
        """
        observations = await db.fetch_all(query, patient_id, loinc_code)
    else:
        query = """
            SELECT o.*, e.fecha_hora as encuentro_fecha, s.nombre as sede_nombre
            FROM observaciones_clinicas o
            JOIN encuentros_clinicos e ON o.id_encuentro = e.id_encuentro
            JOIN sedes s ON e.id_sede = s.id_sede
            WHERE o.id_paciente = $1
            ORDER BY o.fecha_hora DESC
        """
        observations = await db.fetch_all(query, patient_id)
    
    return observations
