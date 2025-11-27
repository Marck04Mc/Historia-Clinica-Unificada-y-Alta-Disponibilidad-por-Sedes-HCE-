"""
Script para vincular pacientes con sus usuarios
Corrige el problema donde se crearon usuarios pero no se actualizó la tabla pacientes
Ejecutar desde el contenedor Docker: docker exec hce-middleware python /app/link_patients_users.py
"""
import asyncio
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, '/app')

from database import db


async def link_patients_users():
    """Vincular pacientes con sus usuarios correspondientes"""
    
    # Conectar a la base de datos
    await db.connect()
    
    try:
        # Buscar pacientes donde la identificación coincide con el username
        # y el id_usuario es diferente (o nulo)
        query = """
            SELECT p.id_paciente, p.nombres, p.apellidos, u.id_usuario, u.username, p.id_usuario as current_user_id
            FROM pacientes p
            INNER JOIN usuarios u ON u.username = p.identificacion
            WHERE p.id_usuario IS NULL OR p.id_usuario != u.id_usuario
        """
        
        patients_to_link = await db.fetch_all(query)
        
        print(f"\n{'='*60}")
        print(f"Pacientes pendientes de vincular: {len(patients_to_link)}")
        print(f"{'='*60}\n")
        
        if len(patients_to_link) == 0:
            print("✅ Todos los pacientes están correctamente vinculados.")
            return
        
        updated_count = 0
        errors = []
        
        for patient in patients_to_link:
            try:
                update_query = """
                    UPDATE pacientes 
                    SET id_usuario = $1 
                    WHERE id_paciente = $2
                """
                
                await db.execute(update_query, patient['id_usuario'], patient['id_paciente'])
                
                updated_count += 1
                print(f"✅ Vinculado: {patient['nombres']} {patient['apellidos']} -> Usuario ID: {patient['id_usuario']}")
                
            except Exception as e:
                error_msg = f"❌ Error vinculando {patient['nombres']} {patient['apellidos']}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        print(f"\n{'='*60}")
        print(f"Resumen de Vinculación:")
        print(f"  ✅ Pacientes actualizados: {updated_count}")
        print(f"  ❌ Errores: {len(errors)}")
        print(f"{'='*60}\n")
        
    finally:
        await db.disconnect()


if __name__ == "__main__":
    print("\n🔄 Iniciando vinculación de pacientes con usuarios...\n")
    asyncio.run(link_patients_users())
    print("\n✅ Proceso completado.\n")
