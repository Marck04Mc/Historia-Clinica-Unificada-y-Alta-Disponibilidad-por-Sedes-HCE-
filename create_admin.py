"""
Script para crear usuario administrador inicial
Ejecutar desde el contenedor Docker: docker exec hce-middleware python /app/create_admin.py
"""
import asyncio
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, '/app')

from database import db
from routers.auth import get_password_hash


async def create_admin_user():
    """Crear usuario administrador si no existe"""
    
    await db.connect()
    
    try:
        # Verificar si ya existe un admin
        check_query = "SELECT id_usuario FROM usuarios WHERE rol = 'admin' LIMIT 1"
        existing_admin = await db.fetch_one(check_query)
        
        if existing_admin:
            print("✅ Ya existe un usuario administrador en el sistema.")
            print(f"   ID: {existing_admin['id_usuario']}")
            return
        
        # Obtener la primera sede activa
        sede_query = "SELECT id_sede FROM sedes WHERE activo = TRUE LIMIT 1"
        sede = await db.fetch_one(sede_query)
        
        if not sede:
            print("❌ Error: No hay sedes activas en el sistema")
            return
        
        # Datos del admin
        username = "admin"
        password = "admin2024"  # Contraseña temporal
        password_hash = get_password_hash(password)
        
        # Crear admin
        insert_query = """
            INSERT INTO usuarios (username, password_hash, rol, id_sede, 
                                nombres, apellidos, email, activo)
            VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE)
            RETURNING id_usuario
        """
        
        result = await db.execute_returning(
            insert_query,
            username,
            password_hash,
            'admin',
            sede['id_sede'],
            'Administrador',
            'Sistema',
            'admin@hce.com'
        )
        
        print("\n" + "="*60)
        print("✅ Usuario Administrador Creado Exitosamente")
        print("="*60)
        print(f"\n   Usuario: {username}")
        print(f"   Contraseña: {password}")
        print(f"   ID: {result['id_usuario']}")
        print("\n⚠️  IMPORTANTE: Cambie esta contraseña después del primer inicio de sesión")
        print("="*60 + "\n")
        
    finally:
        await db.disconnect()


if __name__ == "__main__":
    print("\n🔄 Creando usuario administrador...\n")
    asyncio.run(create_admin_user())
