"""
Script para depurar el estado de la base de datos
Verifica la vinculación entre usuarios y pacientes
Ejecutar desde el contenedor Docker: docker exec hce-middleware python /app/debug_db.py
"""
import asyncio
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, '/app')

from database import db


async def debug_database():
    """Verificar estado de usuarios y pacientes"""
    
    await db.connect()
    
    try:
        username = "1234567890"
        print(f"\nDepurando usuario: {username}")
        
        # 1. Verificar usuario
        user_query = "SELECT * FROM usuarios WHERE username = $1"
        user = await db.fetch_one(user_query, username)
        
        if user:
            print(f"✅ Usuario encontrado:")
            print(f"   ID: {user['id_usuario']}")
            print(f"   Rol: {user['rol']}")
            print(f"   Activo: {user['activo']}")
            
            user_id = user['id_usuario']
            
            # 2. Verificar paciente vinculado
            patient_query = "SELECT * FROM pacientes WHERE id_usuario = $1"
            patient = await db.fetch_one(patient_query, user_id)
            
            if patient:
                print(f"✅ Paciente vinculado encontrado:")
                print(f"   ID: {patient['id_paciente']}")
                print(f"   Nombre: {patient['nombres']} {patient['apellidos']}")
                print(f"   Identificación: {patient['identificacion']}")
            else:
                print(f"❌ NO se encontró paciente vinculado al usuario ID {user_id}")
                
                # 3. Buscar paciente por identificación
                p_ident_query = "SELECT * FROM pacientes WHERE identificacion = $1"
                p_ident = await db.fetch_one(p_ident_query, username)
                
                if p_ident:
                    print(f"⚠️ Paciente encontrado por identificación, pero no vinculado:")
                    print(f"   ID: {p_ident['id_paciente']}")
                    print(f"   ID Usuario actual: {p_ident['id_usuario']}")
                else:
                    print(f"❌ Tampoco se encontró paciente con identificación {username}")
        else:
            print(f"❌ Usuario {username} no encontrado")
            
        # Verificar quién es el usuario 9
        print("\nVerificando usuario ID 9:")
        user9 = await db.fetch_one("SELECT * FROM usuarios WHERE id_usuario = 9")
        if user9:
            print(f"   Username: {user9['username']}")
            print(f"   Rol: {user9['rol']}")
            print(f"   Activo: {user9['activo']}")
        else:
            print("   ❌ Usuario ID 9 NO existe")

            
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(debug_database())
