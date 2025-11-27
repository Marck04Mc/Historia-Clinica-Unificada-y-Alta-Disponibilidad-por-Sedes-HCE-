"""
Router de encuentros clínicos
Gestión de consultas médicas con contexto de sede
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from database import db
from models import EncuentroClinico, EncuentroClinicoCreate, User
from routers.auth import get_current_user, require_role

router = APIRouter(prefix="/api/encounters", tags=["Encuentros Clínicos"])


@router.get("", response_model=List[dict])
async def list_encounters(
    patient_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """
    Listar encuentros clínicos
    - Médicos: ven encuentros de su sede o que ellos crearon
    - Historificación: ven todos los encuentros
    - Pacientes: solo ven sus propios encuentros
    - Admisionistas: ven encuentros de su sede
    """
    
    if current_user.rol == "paciente":
        # Obtener id_paciente del usuario
        paciente = await db.fetch_one(
            "SELECT id_paciente FROM pacientes WHERE id_usuario = $1",
            current_user.id_usuario
        )
        if not paciente:
            return []
        
        query = """
            SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
                   u.nombres || ' ' || u.apellidos as doctor_nombre
            FROM encuentros_clinicos e
            JOIN sedes s ON e.id_sede = s.id_sede
            JOIN usuarios u ON e.id_doctor = u.id_usuario
            WHERE e.id_paciente = $1
            ORDER BY e.fecha_hora DESC
            LIMIT $2 OFFSET $3
        """
        encounters = await db.fetch_all(query, paciente["id_paciente"], limit, skip)
    
    elif current_user.rol == "historificacion":
        # Ver todos los encuentros
        if patient_id:
            query = """
                SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
                       u.nombres || ' ' || u.apellidos as doctor_nombre
                FROM encuentros_clinicos e
                JOIN sedes s ON e.id_sede = s.id_sede
                JOIN usuarios u ON e.id_doctor = u.id_usuario
                WHERE e.id_paciente = $1
                ORDER BY e.fecha_hora DESC
                LIMIT $2 OFFSET $3
            """
            encounters = await db.fetch_all(query, patient_id, limit, skip)
        else:
            query = """
                SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
                       u.nombres || ' ' || u.apellidos as doctor_nombre
                FROM encuentros_clinicos e
                JOIN sedes s ON e.id_sede = s.id_sede
                JOIN usuarios u ON e.id_doctor = u.id_usuario
                ORDER BY e.fecha_hora DESC
                LIMIT $1 OFFSET $2
            """
            encounters = await db.fetch_all(query, limit, skip)
    
    elif current_user.rol == "medico":
        # Ver encuentros de su sede o que ellos crearon
        if patient_id:
            # Si se busca por paciente, ver TODOS sus encuentros (historia clínica completa)
            query = """
                SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
                       u.nombres || ' ' || u.apellidos as doctor_nombre
                FROM encuentros_clinicos e
                JOIN sedes s ON e.id_sede = s.id_sede
                JOIN usuarios u ON e.id_doctor = u.id_usuario
                WHERE e.id_paciente = $1
                ORDER BY e.fecha_hora DESC
                LIMIT $2 OFFSET $3
            """
            encounters = await db.fetch_all(query, patient_id, limit, skip)
        else:
            query = """
                SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
                       u.nombres || ' ' || u.apellidos as doctor_nombre
                FROM encuentros_clinicos e
                JOIN sedes s ON e.id_sede = s.id_sede
                JOIN usuarios u ON e.id_doctor = u.id_usuario
                WHERE e.id_sede = $1 OR e.id_doctor = $2
                ORDER BY e.fecha_hora DESC
                LIMIT $3 OFFSET $4
            """
            encounters = await db.fetch_all(
                query, current_user.id_sede, current_user.id_usuario, limit, skip
            )
    
    else:  # admisionista
        # Ver encuentros de su sede
        if patient_id:
            query = """
                SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
                       u.nombres || ' ' || u.apellidos as doctor_nombre
                FROM encuentros_clinicos e
                JOIN sedes s ON e.id_sede = s.id_sede
                JOIN usuarios u ON e.id_doctor = u.id_usuario
                WHERE e.id_paciente = $1 AND e.id_sede = $2
                ORDER BY e.fecha_hora DESC
                LIMIT $3 OFFSET $4
            """
            encounters = await db.fetch_all(query, patient_id, current_user.id_sede, limit, skip)
        else:
            query = """
                SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
                       u.nombres || ' ' || u.apellidos as doctor_nombre
                FROM encuentros_clinicos e
                JOIN sedes s ON e.id_sede = s.id_sede
                JOIN usuarios u ON e.id_doctor = u.id_usuario
                WHERE e.id_sede = $1
                ORDER BY e.fecha_hora DESC
                LIMIT $2 OFFSET $3
            """
            encounters = await db.fetch_all(query, current_user.id_sede, limit, skip)
    
    return encounters


@router.get("/{encounter_id}", response_model=dict)
async def get_encounter(
    encounter_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Obtener detalle de un encuentro clínico con observaciones, diagnósticos y medicamentos
    """
    # Obtener encuentro
    query = """
        SELECT e.*, s.nombre as sede_nombre, s.ciudad as sede_ciudad,
               u.nombres || ' ' || u.apellidos as doctor_nombre,
               p.nombres || ' ' || p.apellidos as paciente_nombre,
               p.identificacion as paciente_identificacion
        FROM encuentros_clinicos e
        JOIN sedes s ON e.id_sede = s.id_sede
        JOIN usuarios u ON e.id_doctor = u.id_usuario
        JOIN pacientes p ON e.id_paciente = p.id_paciente
        WHERE e.id_encuentro = $1
    """
    encounter = await db.fetch_one(query, encounter_id)
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encuentro no encontrado"
        )
    
    # Obtener observaciones
    obs_query = """
        SELECT * FROM observaciones_clinicas
        WHERE id_encuentro = $1 AND id_paciente = $2
        ORDER BY fecha_hora DESC
    """
    observations = await db.fetch_all(obs_query, encounter_id, encounter["id_paciente"])
    
    # Obtener diagnósticos
    diag_query = """
        SELECT * FROM diagnosticos
        WHERE id_encuentro = $1 AND id_paciente = $2
        ORDER BY fecha_diagnostico DESC
    """
    diagnostics = await db.fetch_all(diag_query, encounter_id, encounter["id_paciente"])
    
    # Obtener medicamentos
    med_query = """
        SELECT * FROM medicamentos
        WHERE id_encuentro = $1 AND id_paciente = $2
        ORDER BY fecha_prescripcion DESC
    """
    medications = await db.fetch_all(med_query, encounter_id, encounter["id_paciente"])
    
    return {
        **encounter,
        "observaciones": observations,
        "diagnosticos": diagnostics,
        "medicamentos": medications
    }


@router.post("", response_model=EncuentroClinico, status_code=status.HTTP_201_CREATED)
async def create_encounter(
    encounter: EncuentroClinicoCreate,
    current_user: User = Depends(require_role(["medico"]))
):
    """
    Crear un nuevo encuentro clínico
    Solo médicos pueden crear encuentros
    El id_sede y id_doctor se toman del token JWT
    """
    # Verificar que el paciente existe
    patient = await db.fetch_one(
        "SELECT id_paciente FROM pacientes WHERE id_paciente = $1 AND activo = TRUE",
        encounter.id_paciente
    )
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Insertar encuentro con sede y doctor del usuario actual
    query = """
        INSERT INTO encuentros_clinicos (
            id_paciente, id_sede, id_doctor, tipo_encuentro,
            motivo_consulta, notas_clinicas
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
    """
    
    new_encounter = await db.execute_returning(
        query,
        encounter.id_paciente,
        current_user.id_sede,  # Sede del médico
        current_user.id_usuario,  # ID del médico
        encounter.tipo_encuentro,
        encounter.motivo_consulta,
        encounter.notas_clinicas
    )
    
    return new_encounter


@router.put("/{encounter_id}", response_model=EncuentroClinico)
async def update_encounter(
    encounter_id: int,
    encounter: EncuentroClinicoCreate,
    current_user: User = Depends(require_role(["medico"]))
):
    """
    Actualizar un encuentro clínico
    Solo el médico que creó el encuentro puede actualizarlo
    """
    # Verificar que existe y que el médico actual es el creador
    existing = await db.fetch_one(
        "SELECT id_doctor FROM encuentros_clinicos WHERE id_encuentro = $1",
        encounter_id
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encuentro no encontrado"
        )
    
    if existing["id_doctor"] != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el médico que creó el encuentro puede actualizarlo"
        )
    
    # Actualizar
    query = """
        UPDATE encuentros_clinicos
        SET tipo_encuentro = $1, motivo_consulta = $2, notas_clinicas = $3
        WHERE id_encuentro = $4
        RETURNING *
    """
    
    updated_encounter = await db.execute_returning(
        query,
        encounter.tipo_encuentro,
        encounter.motivo_consulta,
        encounter.notas_clinicas,
        encounter_id
    )
    
    return updated_encounter


@router.patch("/{encounter_id}/finalize")
async def finalize_encounter(
    encounter_id: int,
    current_user: User = Depends(require_role(["medico"]))
):
    """
    Finalizar un encuentro clínico (cambiar estado a 'finalizado')
    """
    result = await db.execute_returning(
        """
        UPDATE encuentros_clinicos
        SET estado = 'finalizado'
        WHERE id_encuentro = $1 AND id_doctor = $2
        RETURNING *
        """,
        encounter_id,
        current_user.id_usuario
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encuentro no encontrado o no tiene permisos"
        )
    
    return result
