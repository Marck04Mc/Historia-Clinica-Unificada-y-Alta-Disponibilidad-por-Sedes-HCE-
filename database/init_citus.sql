-- =====================================================
-- CONFIGURACIÓN DE CITUS PARA DISTRIBUCIÓN DE DATOS
-- Sistema de Historia Clínica Electrónica
-- =====================================================

-- Crear extensión Citus
CREATE EXTENSION IF NOT EXISTS citus;

-- =====================================================
-- CONFIGURACIÓN DE TABLAS DISTRIBUIDAS
-- Distribuir por id_paciente para colocar todos los datos
-- de un paciente en el mismo nodo (colocation)
-- =====================================================

-- Tabla principal: pacientes
-- Esta es la tabla de distribución base
SELECT create_distributed_table('pacientes', 'id_paciente');

-- Tablas relacionadas: distribuir por id_paciente para colocation
SELECT create_distributed_table('encuentros_clinicos', 'id_paciente');
SELECT create_distributed_table('observaciones_clinicas', 'id_paciente');
SELECT create_distributed_table('diagnosticos', 'id_paciente');
SELECT create_distributed_table('medicamentos', 'id_paciente');
SELECT create_distributed_table('alergias', 'id_paciente');

-- =====================================================
-- CONFIGURACIÓN DE TABLAS DE REFERENCIA
-- Estas tablas se replican en todos los nodos
-- para permitir JOINs eficientes
-- =====================================================

SELECT create_reference_table('sedes');
SELECT create_reference_table('usuarios');

-- =====================================================
-- VERIFICACIÓN DE CONFIGURACIÓN
-- =====================================================

-- Ver todas las tablas distribuidas
SELECT * FROM citus_tables;

-- Ver la distribución de shards
SELECT * FROM citus_shards;

-- Ver los nodos workers activos
SELECT * FROM citus_get_active_worker_nodes();

-- =====================================================
-- CONFIGURACIÓN DE POLÍTICAS DE REBALANCEO
-- =====================================================

-- Habilitar rebalanceo automático de shards
ALTER SYSTEM SET citus.shard_replication_factor = 1;

-- Configurar el número de shards por tabla distribuida
-- (32 es un buen valor por defecto para escalabilidad)
ALTER SYSTEM SET citus.shard_count = 32;

-- =====================================================
-- NOTAS IMPORTANTES
-- =====================================================

-- 1. Todas las consultas que involucren pacientes deben incluir
--    id_paciente en la cláusula WHERE para aprovechar la distribución

-- 2. Las tablas de referencia (sedes, usuarios) están replicadas
--    en todos los nodos, por lo que los JOINs con estas tablas
--    son eficientes

-- 3. Para consultas multisede, el filtro por id_sede se aplica
--    después de la distribución, pero es eficiente gracias a los índices

-- 4. Ejemplo de consulta eficiente:
--    SELECT * FROM encuentros_clinicos 
--    WHERE id_paciente = 1 AND id_sede = 1;

-- 5. Ejemplo de consulta menos eficiente (requiere consultar todos los shards):
--    SELECT * FROM encuentros_clinicos 
--    WHERE id_sede = 1;
--    (Aún funciona, pero no aprovecha la distribución por paciente)
