"""
Configuración de la aplicación
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Base de datos
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "hce_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres123"
    
    # FHIR Server
    FHIR_SERVER_URL: str = "http://localhost:8080/fhir"
    
    # JWT
    JWT_SECRET_KEY: str = "tu-clave-secreta-super-segura-cambiar-en-produccion-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
