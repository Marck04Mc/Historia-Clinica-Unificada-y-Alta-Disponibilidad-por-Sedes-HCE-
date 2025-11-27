-- Actualizar contraseñas con hash válido para test123
UPDATE usuarios SET password_hash = '$2b$12$HmoZkqgu0LlCd0bxWAOyX4u8m';

-- Verificar
SELECT username, rol, substring(password_hash, 1, 30) as hash_preview FROM usuarios LIMIT 5;
