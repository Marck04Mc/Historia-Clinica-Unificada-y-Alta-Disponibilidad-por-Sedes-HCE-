"""
Script de migración para crear usuarios para pacientes existentes
Ejecutar desde el contenedor Docker: docker exec hce-middleware python /app/migrate_patient_users.py
"""
import asyncio
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, '/app')

from database import db
from routers.auth import get_password_hash


async def migrate_patient_users():
    """Crear usuarios para pacientes existentes sin cuenta"""
    
    # Conectar a la base de datos usando la configuración existente
    await db.connect()
    
    try:
        # Obtener una sede por defecto (la primera activa)
        sede_query = "SELECT id_sede FROM sedes WHERE activo = TRUE LIMIT 1"
        default_sede = await db.fetch_one(sede_query)
        
        if not default_sede:
            print("❌ Error: No hay sedes activas en el sistema")
            return
        
        default_sede_id = default_sede['id_sede']
        print(f"Usando sede por defecto: {default_sede_id}\n")
        
        # Obtener pacientes sin usuario
        query = """
            SELECT p.id_paciente, p.identificacion, p.nombres, p.apellidos, p.email
            FROM pacientes p
            LEFT JOIN usuarios u ON u.username = p.identificacion
            WHERE u.id_usuario IS NULL
            AND p.activo = TRUE
            ORDER BY p.nombres, p.apellidos
        """
        
        patients_without_users = await db.fetch_all(query)
        
        print(f"\n{'='*60}")
        print(f"Pacientes sin usuario encontrados: {len(patients_without_users)}")
        print(f"{'='*60}\n")
        
        if len(patients_without_users) == 0:
            print("✅ Todos los pacientes ya tienen usuario asignado.")
            return
        
        created_count = 0
        errors = []
        
        for patient in patients_without_users:
            try:
                # Generar contraseña temporal
                identificacion = patient['identificacion']
                temp_password = (identificacion[-4:] if len(identificacion) >= 4 
                                else identificacion) + "2024"
                password_hash = get_password_hash(temp_password)
                
                # Crear usuario
                insert_query = """
                    INSERT INTO usuarios (username, password_hash, rol, id_sede, 
                                        nombres, apellidos, email, activo)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE)
                    RETURNING id_usuario
                """
                
                result = await db.execute_returning(
                    insert_query,
                    identificacion,  # username
                    password_hash,
                    'paciente',  # rol
                    default_sede_id,  # usar sede por defecto
                    patient['nombres'],
                    patient['apellidos'],
                    patient['email']
                )
                
                created_count += 1
                print(f"✅ Usuario creado para: {patient['nombres']} {patient['apellidos']}")
                print(f"   Usuario: {identificacion} | Contraseña: {temp_password}")
                
            except Exception as e:
                error_msg = f"❌ Error creando usuario para {patient['nombres']} {patient['apellidos']}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        print(f"\n{'='*60}")
        print(f"Resumen de Migración:")
        print(f"  ✅ Usuarios creados: {created_count}")
        print(f"  ❌ Errores: {len(errors)}")
        print(f"{'='*60}\n")
        
        if errors:
            print("Detalles de errores:")
            for error in errors:
                print(f"  {error}")
        
        # Guardar credenciales en archivo
        if created_count > 0:
            with open('/app/credenciales_pacientes_migrados.txt', 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("CREDENCIALES DE PACIENTES MIGRADOS\n")
                f.write("="*60 + "\n\n")
                f.write("IMPORTANTE: Proporcione estas credenciales a los pacientes\n")
                f.write("Los pacientes deben cambiar su contraseña en el primer inicio de sesión\n\n")
                
                # Volver a obtener los pacientes migrados
                for patient in patients_without_users:
                    identificacion = patient['identificacion']
                    temp_password = (identificacion[-4:] if len(identificacion) >= 4 
                                    else identificacion) + "2024"
                    
                    f.write(f"Paciente: {patient['nombres']} {patient['apellidos']}\n")
                    f.write(f"Usuario: {identificacion}\n")
                    f.write(f"Contraseña Temporal: {temp_password}\n")
                    f.write("-"*60 + "\n")
            
            print(f"\n📄 Credenciales guardadas en: /app/credenciales_pacientes_migrados.txt")
            print(f"   Para copiar al host: docker cp hce-middleware:/app/credenciales_pacientes_migrados.txt .\n")
        
    finally:
        await db.disconnect()


if __name__ == "__main__":
    print("\n🔄 Iniciando migración de usuarios para pacientes existentes...\n")
    asyncio.run(migrate_patient_users())
    print("\n✅ Migración completada.\n")
