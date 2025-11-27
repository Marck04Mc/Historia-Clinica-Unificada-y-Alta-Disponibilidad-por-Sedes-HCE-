"""
Router de estadísticas generales
"""
from fastapi import APIRouter, Depends
from database import db
from models import User
from routers.auth import get_current_user, require_role

router = APIRouter(prefix="/api/stats", tags=["Estadísticas"])

@router.get("/general")
async def get_general_stats(
    current_user: User = Depends(require_role(["historificacion", "admin"]))
):
    """
    Obtener estadísticas generales del sistema
    """
    # Total pacientes
    total_patients = await db.fetch_val("SELECT COUNT(*) FROM pacientes WHERE activo = TRUE")
    
    # Total encuentros
    total_encounters = await db.fetch_val("SELECT COUNT(*) FROM encuentros_clinicos")
    
    # Total observaciones
    total_observations = await db.fetch_val("SELECT COUNT(*) FROM observaciones_clinicas")
    
    # Total usuarios
    total_users = await db.fetch_val("SELECT COUNT(*) FROM usuarios WHERE activo = TRUE")

    return {
        "pacientes": total_patients,
        "encuentros": total_encounters,
        "observaciones": total_observations,
        "usuarios": total_users
    }
