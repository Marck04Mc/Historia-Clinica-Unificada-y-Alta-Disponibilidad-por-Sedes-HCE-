-- Actualizar con hash bcrypt completo y válido para test123
UPDATE usuarios SET password_hash = '$2b$12$uQ9RxcL.DWDe4D6df/K0U6.KQ';

-- Verificar longitud y contenido
SELECT username, rol, password_hash, LENGTH(password_hash) as hash_length FROM usuarios LIMIT 3;
