from passlib.context import CryptContext

# Misma configuración que en auth.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generar hash para "test123"
password = "test123"
hashed = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hash: {hashed}")
print(f"\nSQL para actualizar:")
print(f"UPDATE usuarios SET password_hash = '{hashed}';")
