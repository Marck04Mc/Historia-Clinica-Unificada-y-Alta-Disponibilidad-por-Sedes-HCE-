"""
Script para actualizar contraseñas de usuarios de prueba
"""
import asyncio
from passlib.context import CryptContext
import asyncpg

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def update_passwords():
    # Conectar a la base de datos
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        database='hce_db',
        user='postgres',
        password='postgres123'
    )
    
    # Generar hash para "test123"
    password_hash = pwd_context.hash("test123")
    print(f"Hash generado para 'test123': {password_hash}")
    
    # Actualizar todos los usuarios
    await conn.execute(
        "UPDATE usuarios SET password_hash = $1",
        password_hash
    )
    
    print("✅ Contraseñas actualizadas correctamente")
    
    # Verificar
    users = await conn.fetch("SELECT username, rol FROM usuarios")
    print("\n📋 Usuarios en la base de datos:")
    for user in users:
        print(f"  - {user['username']} ({user['rol']})")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(update_passwords())
