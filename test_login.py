import asyncio
import asyncpg

async def test_login():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        database='hce_db',
        user='postgres',
        password='postgres123'
    )
    
    # Obtener usuario
    user = await conn.fetchrow(
        "SELECT username, password_hash FROM usuarios WHERE username = 'doctor1'"
    )
    
    print(f"Usuario: {user['username']}")
    print(f"Hash en DB: {user['password_hash']}")
    
    # Probar verificación
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    password = "test123"
    result = pwd_context.verify(password, user['password_hash'])
    
    print(f"\nPassword: {password}")
    print(f"Verificación: {result}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(test_login())
