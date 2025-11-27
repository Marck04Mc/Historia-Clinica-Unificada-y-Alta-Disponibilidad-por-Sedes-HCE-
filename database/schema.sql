-- =====================================================
-- SISTEMA DE HISTORIA CLÍNICA ELECTRÓNICA INTEROPERABLE
-- Base de datos PostgreSQL + Citus
-- Esquema multisede con soporte FHIR
-- =====================================================

-- Extensión para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLA: sedes
-- Información de las sedes clínicas
-- =====================================================
CREATE TABLE sedes (
    id_sede SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLA: usuarios
-- Usuarios del sistema con roles diferenciados
-- =====================================================
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('paciente', 'admisionista', 'medico', 'historificacion')),
    id_sede INTEGER REFERENCES sedes(id_sede),
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    email VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP
);

-- =====================================================
-- TABLA: pacientes
-- Información demográfica de pacientes
-- Tabla distribuida por id_paciente
-- =====================================================
CREATE TABLE pacientes (
    id_paciente SERIAL PRIMARY KEY,
    identificacion VARCHAR(20) UNIQUE NOT NULL,
    tipo_identificacion VARCHAR(10) NOT NULL CHECK (tipo_identificacion IN ('CC', 'TI', 'CE', 'PA', 'RC')),
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(1) CHECK (genero IN ('M', 'F', 'O')),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    ciudad VARCHAR(100),
    id_usuario INTEGER REFERENCES usuarios(id_usuario),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- TABLA: encuentros_clinicos
-- Registro de encuentros médicos (Encounter en FHIR)
-- Tabla distribuida por id_paciente
-- =====================================================
CREATE TABLE encuentros_clinicos (
    id_encuentro SERIAL,
    id_paciente INTEGER NOT NULL,
    id_sede INTEGER NOT NULL REFERENCES sedes(id_sede),
    id_doctor INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_encuentro VARCHAR(50) NOT NULL CHECK (tipo_encuentro IN ('consulta', 'urgencia', 'hospitalizacion', 'control', 'cirugia')),
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'finalizado', 'cancelado')),
    motivo_consulta TEXT,
    notas_clinicas TEXT,
    PRIMARY KEY (id_encuentro, id_paciente),
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente)
);

-- =====================================================
-- TABLA: observaciones_clinicas
-- Observaciones médicas (Observation en FHIR)
-- Incluye códigos LOINC para interoperabilidad
-- Tabla distribuida por id_paciente
-- =====================================================
CREATE TABLE observaciones_clinicas (
    id_observacion SERIAL,
    id_encuentro INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL,
    codigo_loinc VARCHAR(20),
    descripcion VARCHAR(255) NOT NULL,
    valor_numerico DECIMAL(10,2),
    valor_texto TEXT,
    unidad VARCHAR(50),
    rango_referencia VARCHAR(100),
    interpretacion VARCHAR(50),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_observacion, id_paciente),
    FOREIGN KEY (id_encuentro, id_paciente) REFERENCES encuentros_clinicos(id_encuentro, id_paciente)
);

-- =====================================================
-- TABLA: diagnosticos
-- Diagnósticos médicos (Condition en FHIR)
-- Incluye códigos ICD-10 y SNOMED CT
-- Tabla distribuida por id_paciente
-- =====================================================
CREATE TABLE diagnosticos (
    id_diagnostico SERIAL,
    id_encuentro INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL,
    codigo_icd10 VARCHAR(10),
    codigo_snomed VARCHAR(20),
    descripcion TEXT NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('principal', 'secundario', 'complicacion')),
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'resuelto', 'cronico')),
    fecha_diagnostico TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_diagnostico, id_paciente),
    FOREIGN KEY (id_encuentro, id_paciente) REFERENCES encuentros_clinicos(id_encuentro, id_paciente)
);

-- =====================================================
-- TABLA: medicamentos
-- Prescripciones médicas (MedicationRequest en FHIR)
-- Tabla distribuida por id_paciente
-- =====================================================
CREATE TABLE medicamentos (
    id_medicamento SERIAL,
    id_encuentro INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    principio_activo VARCHAR(255),
    dosis VARCHAR(100),
    frecuencia VARCHAR(100),
    duracion VARCHAR(50),
    via_administracion VARCHAR(50),
    indicaciones TEXT,
    fecha_prescripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'suspendido', 'completado')),
    PRIMARY KEY (id_medicamento, id_paciente),
    FOREIGN KEY (id_encuentro, id_paciente) REFERENCES encuentros_clinicos(id_encuentro, id_paciente)
);

-- =====================================================
-- TABLA: alergias
-- Registro de alergias del paciente (AllergyIntolerance en FHIR)
-- Tabla distribuida por id_paciente
-- =====================================================
CREATE TABLE alergias (
    id_alergia SERIAL,
    id_paciente INTEGER NOT NULL,
    sustancia VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) CHECK (tipo IN ('medicamento', 'alimento', 'ambiental', 'otro')),
    severidad VARCHAR(20) CHECK (severidad IN ('leve', 'moderada', 'severa')),
    reaccion TEXT,
    fecha_identificacion DATE,
    activo BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (id_alergia, id_paciente),
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente)
);

-- =====================================================
-- ÍNDICES para optimización de consultas
-- =====================================================
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_rol_sede ON usuarios(rol, id_sede);
CREATE INDEX idx_pacientes_identificacion ON pacientes(identificacion);
CREATE INDEX idx_encuentros_paciente ON encuentros_clinicos(id_paciente);
CREATE INDEX idx_encuentros_sede ON encuentros_clinicos(id_sede);
CREATE INDEX idx_encuentros_doctor ON encuentros_clinicos(id_doctor);
CREATE INDEX idx_encuentros_fecha ON encuentros_clinicos(fecha_hora);
CREATE INDEX idx_observaciones_encuentro ON observaciones_clinicas(id_encuentro, id_paciente);
CREATE INDEX idx_observaciones_loinc ON observaciones_clinicas(codigo_loinc);
CREATE INDEX idx_diagnosticos_encuentro ON diagnosticos(id_encuentro, id_paciente);
CREATE INDEX idx_diagnosticos_icd10 ON diagnosticos(codigo_icd10);
CREATE INDEX idx_diagnosticos_snomed ON diagnosticos(codigo_snomed);
CREATE INDEX idx_medicamentos_encuentro ON medicamentos(id_encuentro, id_paciente);
CREATE INDEX idx_alergias_paciente ON alergias(id_paciente);

-- =====================================================
-- DATOS DE EJEMPLO: Sedes
-- =====================================================
INSERT INTO sedes (nombre, ciudad, direccion, telefono, email) VALUES
('Clínica Central Bogotá', 'Bogotá', 'Calle 100 # 15-20', '+57 1 6000000', 'contacto@clinicabogota.com'),
('Clínica del Valle Medellín', 'Medellín', 'Carrera 43A # 1-50', '+57 4 4000000', 'contacto@clinicamedellin.com'),
('Clínica del Pacífico Cali', 'Cali', 'Avenida 6N # 28-50', '+57 2 3000000', 'contacto@clinicacali.com');

-- =====================================================
-- DATOS DE EJEMPLO: Usuarios
-- Password: test123 (hashed con bcrypt)
-- Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu
-- =====================================================
INSERT INTO usuarios (username, password_hash, rol, id_sede, nombres, apellidos, email) VALUES
-- Admisionistas
('admisionista1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'admisionista', 1, 'María', 'González', 'mgonzalez@clinicabogota.com'),
('admisionista2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'admisionista', 2, 'Carlos', 'Ramírez', 'cramirez@clinicamedellin.com'),
('admisionista3', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'admisionista', 3, 'Ana', 'López', 'alopez@clinicacali.com'),

-- Médicos
('doctor1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'medico', 1, 'Dr. Juan', 'Pérez', 'jperez@clinicabogota.com'),
('doctor2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'medico', 2, 'Dra. Laura', 'Martínez', 'lmartinez@clinicamedellin.com'),
('doctor3', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'medico', 3, 'Dr. Roberto', 'Sánchez', 'rsanchez@clinicacali.com'),

-- Historificación
('historificador1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'historificacion', 1, 'Patricia', 'Torres', 'ptorres@clinicabogota.com'),
('historificador2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'historificacion', 2, 'Miguel', 'Vargas', 'mvargas@clinicamedellin.com');

-- =====================================================
-- DATOS DE EJEMPLO: Pacientes
-- =====================================================
INSERT INTO pacientes (identificacion, tipo_identificacion, nombres, apellidos, fecha_nacimiento, genero, telefono, email, ciudad) VALUES
('1234567890', 'CC', 'Pedro', 'Rodríguez', '1985-03-15', 'M', '3001234567', 'prodriguez@email.com', 'Bogotá'),
('9876543210', 'CC', 'Sofía', 'Hernández', '1990-07-22', 'F', '3109876543', 'shernandez@email.com', 'Medellín'),
('5555555555', 'CC', 'Luis', 'Gómez', '1978-11-30', 'M', '3205555555', 'lgomez@email.com', 'Cali'),
('1111111111', 'CC', 'Carmen', 'Díaz', '1995-05-10', 'F', '3151111111', 'cdiaz@email.com', 'Bogotá');

-- Crear usuarios para los pacientes (para que puedan acceder al sistema)
INSERT INTO usuarios (username, password_hash, rol, id_sede, nombres, apellidos, email) VALUES
('paciente1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'paciente', 1, 'Pedro', 'Rodríguez', 'prodriguez@email.com'),
('paciente2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'paciente', 2, 'Sofía', 'Hernández', 'shernandez@email.com'),
('paciente3', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'paciente', 3, 'Luis', 'Gómez', 'lgomez@email.com'),
('paciente4', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvniu', 'paciente', 1, 'Carmen', 'Díaz', 'cdiaz@email.com');

-- Vincular usuarios con pacientes
UPDATE pacientes SET id_usuario = 9 WHERE identificacion = '1234567890';
UPDATE pacientes SET id_usuario = 10 WHERE identificacion = '9876543210';
UPDATE pacientes SET id_usuario = 11 WHERE identificacion = '5555555555';
UPDATE pacientes SET id_usuario = 12 WHERE identificacion = '1111111111';

-- =====================================================
-- DATOS DE EJEMPLO: Encuentros Clínicos
-- =====================================================
INSERT INTO encuentros_clinicos (id_paciente, id_sede, id_doctor, tipo_encuentro, motivo_consulta, notas_clinicas, estado) VALUES
(1, 1, 4, 'consulta', 'Control de presión arterial', 'Paciente con hipertensión controlada. Se mantiene tratamiento.', 'finalizado'),
(1, 2, 5, 'control', 'Seguimiento de tratamiento', 'Paciente viajó a Medellín. Control de rutina realizado.', 'finalizado'),
(2, 2, 5, 'consulta', 'Dolor abdominal', 'Se solicitan exámenes de laboratorio.', 'activo'),
(3, 3, 6, 'urgencia', 'Trauma en pierna derecha', 'Fractura de tibia. Se inmoviliza y remite a ortopedia.', 'finalizado'),
(4, 1, 4, 'consulta', 'Chequeo general', 'Paciente en buen estado de salud general.', 'finalizado');

-- =====================================================
-- DATOS DE EJEMPLO: Observaciones Clínicas
-- Códigos LOINC estándar
-- =====================================================
INSERT INTO observaciones_clinicas (id_encuentro, id_paciente, codigo_loinc, descripcion, valor_numerico, unidad, rango_referencia) VALUES
(1, 1, '8480-6', 'Presión arterial sistólica', 130, 'mmHg', '90-120'),
(1, 1, '8462-4', 'Presión arterial diastólica', 85, 'mmHg', '60-80'),
(1, 1, '8867-4', 'Frecuencia cardíaca', 72, 'lpm', '60-100'),
(2, 1, '8480-6', 'Presión arterial sistólica', 125, 'mmHg', '90-120'),
(2, 1, '8462-4', 'Presión arterial diastólica', 80, 'mmHg', '60-80'),
(3, 2, '8310-5', 'Temperatura corporal', 37.2, '°C', '36.5-37.5'),
(4, 3, '8867-4', 'Frecuencia cardíaca', 95, 'lpm', '60-100'),
(5, 4, '29463-7', 'Peso corporal', 65, 'kg', NULL),
(5, 4, '8302-2', 'Estatura', 165, 'cm', NULL);

-- =====================================================
-- DATOS DE EJEMPLO: Diagnósticos
-- Códigos ICD-10 y SNOMED CT
-- =====================================================
INSERT INTO diagnosticos (id_encuentro, id_paciente, codigo_icd10, codigo_snomed, descripcion, tipo, estado) VALUES
(1, 1, 'I10', '38341003', 'Hipertensión arterial esencial', 'principal', 'cronico'),
(3, 2, 'R10.4', '21522001', 'Dolor abdominal no especificado', 'principal', 'activo'),
(4, 3, 'S82.2', '413294005', 'Fractura de tibia', 'principal', 'activo');

-- =====================================================
-- DATOS DE EJEMPLO: Medicamentos
-- =====================================================
INSERT INTO medicamentos (id_encuentro, id_paciente, nombre, principio_activo, dosis, frecuencia, via_administracion, indicaciones) VALUES
(1, 1, 'Losartán', 'Losartán potásico', '50mg', 'Una vez al día', 'Oral', 'Tomar en ayunas'),
(3, 2, 'Omeprazol', 'Omeprazol', '20mg', 'Dos veces al día', 'Oral', 'Antes de las comidas'),
(4, 3, 'Ibuprofeno', 'Ibuprofeno', '400mg', 'Cada 8 horas', 'Oral', 'Tomar con alimentos');

-- =====================================================
-- DATOS DE EJEMPLO: Alergias
-- =====================================================
INSERT INTO alergias (id_paciente, sustancia, tipo, severidad, reaccion, fecha_identificacion) VALUES
(2, 'Penicilina', 'medicamento', 'severa', 'Reacción anafiláctica', '2015-03-10'),
(3, 'Maní', 'alimento', 'moderada', 'Urticaria', '2010-06-15');
