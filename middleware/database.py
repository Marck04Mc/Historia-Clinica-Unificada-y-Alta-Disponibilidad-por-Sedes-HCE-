"""
Conexión y operaciones con la base de datos PostgreSQL
"""
import asyncpg
from typing import Optional, List, Dict, Any
from config import settings


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Crear pool de conexiones"""
        self.pool = await asyncpg.create_pool(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            min_size=5,
            max_size=20
        )
        print(f"✓ Conectado a PostgreSQL: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    async def disconnect(self):
        """Cerrar pool de conexiones"""
        if self.pool:
            await self.pool.close()
            print("✓ Desconectado de PostgreSQL")
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Ejecutar query y retornar un registro"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Ejecutar query y retornar todos los registros"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def execute(self, query: str, *args) -> str:
        """Ejecutar query de modificación (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def execute_returning(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Ejecutar query y retornar el registro insertado/actualizado"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None


# Instancia global
db = Database()
