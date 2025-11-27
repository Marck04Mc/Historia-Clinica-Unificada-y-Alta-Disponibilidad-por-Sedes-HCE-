import asyncio
import asyncpg
from passlib.context import CryptContext
import os

# Configuración de seguridad idéntica a auth.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def fix_password():
    print("🔄 Iniciando reparación de contraseñas...")
    
    # 1. Generar hash válido
    password = "test123"
    hashed_password = pwd_context.hash(password)
    print(f"🔑 Contraseña: {password}")
    print(f"🔒 Hash generado: {hashed_password}")
    print(f"📏 Longitud del hash: {len(hashed_password)}")
    
    if len(hashed_password) != 60:
        print("❌ ERROR: El hash generado no tiene 60 caracteres. Algo está mal con la librería bcrypt.")
        return

    # 2. Conectar a la base de datos
    try:
        conn = await asyncpg.connect(
            host='postgres',  # Nombre del servicio en docker-compose
            port=5432,
            database='hce_db',
            user='postgres',
            password='postgres123'
        )
        print("✅ Conexión a base de datos exitosa")
    except Exception as e:
        print(f"❌ Error conectando a la BD: {e}")
        return

    # 3. Actualizar usuarios
    try:
        # Actualizamos todos los usuarios para asegurarnos
        result = await conn.execute(
            "UPDATE usuarios SET password_hash = $1",
            hashed_password
        )
        print(f"✅ Base de datos actualizada: {result}")
    except Exception as e:
        print(f"❌ Error actualizando BD: {e}")
        await conn.close()
        return

    # 4. Verificar actualización
    try:
        row = await conn.fetchrow("SELECT password_hash FROM usuarios WHERE username = 'doctor1'")
        db_hash = row['password_hash']
        print(f"📖 Hash leído de BD: {db_hash}")
        
        if db_hash == hashed_password:
            print("✅ El hash en la BD coincide exactamente con el generado.")
        else:
            print("❌ ADVERTENCIA: El hash en la BD es diferente.")
            
        # 5. Verificar validez
        is_valid = pwd_context.verify(password, db_hash)
        print(f"🕵️ Verificación final (passlib.verify): {'✅ ÉXITO' if is_valid else '❌ FALLÓ'}")
        
    except Exception as e:
        print(f"❌ Error verificando: {e}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_password())
