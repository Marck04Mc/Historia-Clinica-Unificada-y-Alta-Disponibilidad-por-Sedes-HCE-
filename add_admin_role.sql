-- Agregar rol 'admin' a la restricción CHECK de usuarios
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS usuarios_rol_check;

ALTER TABLE usuarios ADD CONSTRAINT usuarios_rol_check 
CHECK (rol IN ('paciente', 'admisionista', 'medico', 'historificacion', 'admin'));
