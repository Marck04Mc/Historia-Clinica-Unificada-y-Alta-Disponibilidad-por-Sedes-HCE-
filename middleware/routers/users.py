"""
Router de gestión de usuarios (admisionistas y médicos)
Endpoints para CRUD de usuarios - solo accesible por rol admin
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from database import db
from models import User
from routers.auth import get_current_user, get_password_hash

router = APIRouter(prefix="/api/users", tags=["Usuarios"])


# Modelos Pydantic
class UserCreate(BaseModel):
    identificacion: str
    nombres: str
    apellidos: str
    email: EmailStr
    rol: str  # admisionista, medico
    id_sede: int


class UserUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    id_sede: Optional[int] = None
    activo: Optional[bool] = None


class UserResponse(BaseModel):
    id_usuario: int
    username: str
    nombres: str
    apellidos: str
    email: str
    rol: str
    id_sede: int
    activo: bool
    temp_password: Optional[str] = None  # Solo en creación


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verificar que el usuario actual sea admin"""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a este recurso"
        )
    return current_user


def generate_temp_password(identificacion: str) -> str:
    """Generar contraseña temporal basada en identificación"""
    # Últimos 4 dígitos + "2024"
    last_digits = identificacion[-4:] if len(identificacion) >= 4 else identificacion
    return f"{last_digits}2024"


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin)
):
    """
    Crear nuevo usuario (admisionista o médico)
    Solo accesible por administradores
    """
    # Validar rol
    if user_data.rol not in ["admisionista", "medico"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol debe ser 'admisionista' o 'medico'"
        )
    
    # Verificar que la sede existe
    sede_query = "SELECT id_sede FROM sedes WHERE id_sede = $1 AND activo = TRUE"
    sede = await db.fetch_one(sede_query, user_data.id_sede)
    if not sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sede no encontrada o inactiva"
        )
    
    # Verificar que el username (identificación) no exista
    username_check = "SELECT id_usuario FROM usuarios WHERE username = $1"
    existing_user = await db.fetch_one(username_check, user_data.identificacion)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con esta identificación"
        )
    
    # Verificar que el email no exista
    email_check = "SELECT id_usuario FROM usuarios WHERE email = $1"
    existing_email = await db.fetch_one(email_check, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este email"
        )
    
    # Generar contraseña temporal
    temp_password = generate_temp_password(user_data.identificacion)
    password_hash = get_password_hash(temp_password)
    
    # Crear usuario
    insert_query = """
        INSERT INTO usuarios (username, password_hash, rol, id_sede, 
                            nombres, apellidos, email, activo)
        VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE)
        RETURNING id_usuario, username, nombres, apellidos, email, rol, id_sede, activo
    """
    
    new_user = await db.execute_returning(
        insert_query,
        user_data.identificacion,  # username
        password_hash,
        user_data.rol,
        user_data.id_sede,
        user_data.nombres,
        user_data.apellidos,
        user_data.email
    )
    
    # Retornar usuario con contraseña temporal
    return {
        **new_user,
        "temp_password": temp_password
    }


@router.get("", response_model=List[dict])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    rol: Optional[str] = None,
    id_sede: Optional[int] = None,
    activo: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    """
    Listar usuarios con filtros opcionales
    Solo accesible por administradores
    """
    # Construir query dinámicamente
    conditions = []
    params = []
    param_count = 0
    
    if rol:
        param_count += 1
        conditions.append(f"u.rol = ${param_count}")
        params.append(rol)
    
    if id_sede is not None:
        param_count += 1
        conditions.append(f"u.id_sede = ${param_count}")
        params.append(id_sede)
    
    if activo is not None:
        param_count += 1
        conditions.append(f"u.activo = ${param_count}")
        params.append(activo)
    
    if search:
        param_count += 1
        conditions.append(f"(u.nombres ILIKE ${param_count} OR u.apellidos ILIKE ${param_count} OR u.username ILIKE ${param_count})")
        params.append(f"%{search}%")
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
        SELECT u.id_usuario, u.username, u.nombres, u.apellidos, u.email, 
               u.rol, u.id_sede, u.activo, s.nombre as sede_nombre
        FROM usuarios u
        LEFT JOIN sedes s ON u.id_sede = s.id_sede
        {where_clause}
        ORDER BY u.nombres, u.apellidos
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    params.extend([limit, skip])
    
    users = await db.fetch_all(query, *params)
    return users


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin)
):
    """
    Obtener detalles de un usuario específico
    Solo accesible por administradores
    """
    query = """
        SELECT u.id_usuario, u.username, u.nombres, u.apellidos, u.email, 
               u.rol, u.id_sede, u.activo, s.nombre as sede_nombre
        FROM usuarios u
        LEFT JOIN sedes s ON u.id_sede = s.id_sede
        WHERE u.id_usuario = $1
    """
    user = await db.fetch_one(query, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin)
):
    """
    Actualizar información de un usuario
    Solo accesible por administradores
    """
    # Verificar que el usuario existe
    check_query = "SELECT id_usuario FROM usuarios WHERE id_usuario = $1"
    existing = await db.fetch_one(check_query, user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Construir update dinámicamente
    updates = []
    params = []
    param_count = 0
    
    if user_data.nombres is not None:
        param_count += 1
        updates.append(f"nombres = ${param_count}")
        params.append(user_data.nombres)
    
    if user_data.apellidos is not None:
        param_count += 1
        updates.append(f"apellidos = ${param_count}")
        params.append(user_data.apellidos)
    
    if user_data.email is not None:
        param_count += 1
        updates.append(f"email = ${param_count}")
        params.append(user_data.email)
    
    if user_data.rol is not None:
        if user_data.rol not in ["admisionista", "medico", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido"
            )
        param_count += 1
        updates.append(f"rol = ${param_count}")
        params.append(user_data.rol)
    
    if user_data.id_sede is not None:
        param_count += 1
        updates.append(f"id_sede = ${param_count}")
        params.append(user_data.id_sede)
    
    if user_data.activo is not None:
        param_count += 1
        updates.append(f"activo = ${param_count}")
        params.append(user_data.activo)
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay campos para actualizar"
        )
    
    param_count += 1
    params.append(user_id)
    
    update_query = f"""
        UPDATE usuarios
        SET {", ".join(updates)}
        WHERE id_usuario = ${param_count}
        RETURNING id_usuario, username, nombres, apellidos, email, rol, id_sede, activo
    """
    
    updated_user = await db.execute_returning(update_query, *params)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin)
):
    """
    Desactivar un usuario (soft delete)
    Solo accesible por administradores
    """
    query = """
        UPDATE usuarios
        SET activo = FALSE
        WHERE id_usuario = $1
        RETURNING id_usuario
    """
    
    result = await db.execute_returning(query, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {"message": "Usuario desactivado exitosamente", "id_usuario": user_id}
