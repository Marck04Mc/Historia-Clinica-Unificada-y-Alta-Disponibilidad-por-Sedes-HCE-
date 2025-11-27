-- Script para actualizar contraseñas de usuarios
-- Password: test123
-- Hash generado con bcrypt rounds=12

UPDATE usuarios SET password_hash = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW';

-- Verificar usuarios
SELECT username, rol, id_sede FROM usuarios ORDER BY id_usuario;
