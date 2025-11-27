"""
Router de gestión de pacientes
Endpoints para CRUD de pacientes con filtrado por sede
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from database import db
from models import Paciente, PacienteCreate, User
from routers.auth import get_current_user, require_role, get_password_hash

router = APIRouter(prefix="/api/patients", tags=["Pacientes"])

@router.get("", response_model=List[Paciente])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Listar pacientes según rol.
    - admisionista/medico: pacientes de su sede
    - historificacion: todos
    - paciente: solo él mismo
    """
    if current_user.rol == "paciente":
        query = """
            SELECT * FROM pacientes WHERE id_usuario = $1
        """
        patients = await db.fetch_all(query, current_user.id_usuario)
    elif current_user.rol in ["historificacion", "medico"]:
        if search:
            query = """
                SELECT * FROM pacientes
                WHERE (nombres ILIKE $1 OR apellidos ILIKE $1 OR identificacion ILIKE $1)
                  AND activo = TRUE
                ORDER BY apellidos, nombres
                LIMIT $2 OFFSET $3
            """
            patients = await db.fetch_all(query, f"%{search}%", limit, skip)
        else:
            query = """
                SELECT * FROM pacientes WHERE activo = TRUE
                ORDER BY apellidos, nombres
                LIMIT $1 OFFSET $2
            """
            patients = await db.fetch_all(query, limit, skip)
    else:
        # admisionista
        if search:
            query = """
                SELECT DISTINCT p.* FROM pacientes p
                LEFT JOIN encuentros_clinicos e ON p.id_paciente = e.id_paciente
                WHERE (p.nombres ILIKE $1 OR p.apellidos ILIKE $1 OR p.identificacion ILIKE $1)
                  AND (e.id_sede = $2 OR e.id_sede IS NULL)
                  AND p.activo = TRUE
                ORDER BY p.apellidos, p.nombres
                LIMIT $3 OFFSET $4
            """
            patients = await db.fetch_all(query, f"%{search}%", current_user.id_sede, limit, skip)
        else:
            query = """
                SELECT DISTINCT p.* FROM pacientes p
                LEFT JOIN encuentros_clinicos e ON p.id_paciente = e.id_paciente
                WHERE (e.id_sede = $1 OR e.id_sede IS NULL)
                  AND p.activo = TRUE
                ORDER BY p.apellidos, p.nombres
                LIMIT $2 OFFSET $3
            """
            patients = await db.fetch_all(query, current_user.id_sede, limit, skip)
    return patients

@router.get("/{patient_id}", response_model=Paciente)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user)
):
    """Obtener información de un paciente específico."""
    query = "SELECT * FROM pacientes WHERE id_paciente = $1"
    patient = await db.fetch_one(query, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    if current_user.rol == "paciente" and patient["id_usuario"] != current_user.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para ver este paciente")
    return patient

@router.post("", response_model=Paciente, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PacienteCreate,
    current_user: User = Depends(require_role(["admisionista"]))
):
    """Crear un nuevo paciente y una cuenta de usuario asociada."""
    existing = await db.fetch_one(
        "SELECT id_paciente FROM pacientes WHERE identificacion = $1",
        patient.identificacion
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un paciente con esta identificación")
    query = """
        INSERT INTO pacientes (
            identificacion, tipo_identificacion, nombres, apellidos,
            fecha_nacimiento, genero, telefono, email, direccion, ciudad
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING *
    """
    new_patient = await db.execute_returning(
        query,
        patient.identificacion,
        patient.tipo_identificacion,
        patient.nombres,
        patient.apellidos,
        patient.fecha_nacimiento,
        patient.genero,
        patient.telefono,
        patient.email,
        patient.direccion,
        patient.ciudad
    )
    # crear usuario asociado
    temp_password = (patient.identificacion[-4:] if len(patient.identificacion) >= 4 else patient.identificacion) + "2024"
    password_hash = get_password_hash(temp_password)
    user_query = """
        INSERT INTO usuarios (username, password_hash, rol, id_sede, nombres, apellidos, email)
        VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id_usuario
    """
    await db.execute_returning(
        user_query,
        patient.identificacion,
        password_hash,
        "paciente",
        current_user.id_sede,
        patient.nombres,
        patient.apellidos,
        patient.email
    )
    return new_patient

@router.put("/{patient_id}", response_model=Paciente)
async def update_patient(
    patient_id: int,
    patient: PacienteCreate,
    current_user: User = Depends(require_role(["admisionista"]))
):
    """Actualizar información de un paciente y su usuario asociado."""
    existing = await db.fetch_one("SELECT id_paciente FROM pacientes WHERE id_paciente = $1", patient_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    query = """
        UPDATE pacientes SET
            identificacion = $1, tipo_identificacion = $2, nombres = $3,
            apellidos = $4, fecha_nacimiento = $5, genero = $6,
            telefono = $7, email = $8, direccion = $9, ciudad = $10
        WHERE id_paciente = $11 RETURNING *
    """
    updated_patient = await db.execute_returning(
        query,
        patient.identificacion,
        patient.tipo_identificacion,
        patient.nombres,
        patient.apellidos,
        patient.fecha_nacimiento,
        patient.genero,
        patient.telefono,
        patient.email,
        patient.direccion,
        patient.ciudad,
        patient_id
    )
    # actualizar datos de usuario si existe
    user_update = """
        UPDATE usuarios SET nombres = $1, apellidos = $2, email = $3
        WHERE username = $4
    """
    await db.execute(
        user_update,
        patient.nombres,
        patient.apellidos,
        patient.email,
        patient.identificacion
    )
    return updated_patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    current_user: User = Depends(require_role(["admisionista"]))
):
    """Desactivar (soft delete) un paciente."""
    result = await db.execute("UPDATE pacientes SET activo = FALSE WHERE id_paciente = $1", patient_id)
    if result == "UPDATE 0":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return None
