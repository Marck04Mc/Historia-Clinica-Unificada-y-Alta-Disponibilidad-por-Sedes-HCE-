from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generar hash para test123
password = "test123"
hashed = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hash generado: {hashed}")
print(f"\nVerificación: {pwd_context.verify(password, hashed)}")
