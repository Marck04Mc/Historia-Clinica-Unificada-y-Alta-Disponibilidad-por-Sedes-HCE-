"""
Router de autenticación OAuth2 + JWT
Gestiona login y generación de tokens con contexto de sede
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from database import db
from models import Token, TokenData, User, UserInDB
from config import settings

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    try:
        if not plain_password or not hashed_password:
            return False
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verificando contraseña: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """Hashear contraseña"""
    return pwd_context.hash(password)


async def get_user(username: str) -> Optional[UserInDB]:
    """Obtener usuario de la base de datos"""
    query = """
        SELECT id_usuario, username, password_hash, rol, id_sede, 
               nombres, apellidos, email, activo
        FROM usuarios
        WHERE username = $1 AND activo = TRUE
    """
    user_data = await db.fetch_one(query, username)
    
    if user_data:
        return UserInDB(**user_data)
    return None


async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Autenticar usuario"""
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Obtener usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(
            username=username,
            rol=payload.get("rol"),
            id_sede=payload.get("id_sede"),
            id_usuario=payload.get("id_usuario")
        )
    except JWTError:
        raise credentials_exception
    
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(**user.dict())


def require_role(allowed_roles: list):
    """Dependencia para verificar roles permitidos"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos. Se requiere uno de estos roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login OAuth2
    Retorna un token JWT con información del usuario y sede
    """
    # Validar que username y password no estén vacíos
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario y contraseña son requeridos",
        )
    
    # Validar que password no sea demasiado corto
    if len(form_data.password) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña inválida",
        )
    
    try:
        user = await authenticate_user(form_data.username, form_data.password)
    except Exception as e:
        print(f"Error en autenticación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el servidor: {str(e)}",
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Actualizar último acceso
    await db.execute(
        "UPDATE usuarios SET ultimo_acceso = $1 WHERE id_usuario = $2",
        datetime.utcnow(),
        user.id_usuario
    )
    
    # Crear token con información de usuario y sede
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "rol": user.rol,
            "id_sede": user.id_sede,
            "id_usuario": user.id_usuario
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Obtener información del usuario actual
    """
    return current_user


@router.get("/sede")
async def get_sede_info(current_user: User = Depends(get_current_user)):
    """
    Obtener información de la sede del usuario actual
    """
    if not current_user.id_sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no tiene sede asignada"
        )
    
    query = """
        SELECT id_sede, nombre, ciudad, direccion, telefono, email
        FROM sedes
        WHERE id_sede = $1
    """
    sede = await db.fetch_one(query, current_user.id_sede)
    
    if not sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sede no encontrada"
        )
    
    return sede


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user)
):
    current_password = request.current_password
    new_password = request.new_password
    """
    Cambiar contraseña del usuario actual
    """
    # Verificar contraseña actual
    user_in_db = await get_user(current_user.username)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not verify_password(current_password, user_in_db.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # Validar nueva contraseña
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Validar que contenga mayúscula, minúscula y número
    if not any(c.isupper() for c in new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos una letra mayúscula"
        )
    
    if not any(c.islower() for c in new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos una letra minúscula"
        )
    
    if not any(c.isdigit() for c in new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos un número"
        )
    
    # Actualizar contraseña
    new_password_hash = get_password_hash(new_password)
    
    query = """
        UPDATE usuarios
        SET password_hash = $1
        WHERE id_usuario = $2
    """
    await db.execute(query, new_password_hash, current_user.id_usuario)
    
    return {"message": "Contraseña cambiada exitosamente"}
