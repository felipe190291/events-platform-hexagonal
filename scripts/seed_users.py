import sys
import os

# Añadir el directorio raíz al path para poder importar la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session
from app.infrastructure.database.connection import engine
from app.infrastructure.database.models import UserModel
from app.infrastructure.security.jwt_handler import hash_password
from app.domain.enums import UserRole

def seed_users():
    users_to_create = []
    
    # 1. Admin
    users_to_create.append(UserModel(
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        full_name="Administrador del Sistema",
        role=UserRole.ADMIN,
        is_active=True
    ))
    
    # 2. Organizadores
    for i in range(1, 3):
        users_to_create.append(UserModel(
            email=f"organizer{i}@example.com",
            hashed_password=hash_password("password123"),
            full_name=f"Organizador {i}",
            role=UserRole.ORGANIZER,
            is_active=True
        ))
        
    # 3. Asistentes (usuarios comunes)
    nombres = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Elena", "Pedro", "Sofia", "Diego", "Laura", "Miguel", "Lucia", "Roberto", "Carmen", "Fernando", "Isabel", "Gabriel"]
    for i, nombre in enumerate(nombres, 1):
        users_to_create.append(UserModel(
            email=f"user{i}@example.com",
            hashed_password=hash_password("password123"),
            full_name=f"{nombre} Pérez",
            role=UserRole.ATTENDEE,
            is_active=True
        ))

    print(f"🚀 Iniciando seed de {len(users_to_create)} usuarios...")
    
    with Session(engine) as session:
        # Limpiar usuarios anteriores (opcional, cuidado en prod)
        # session.query(UserModel).delete() 
        
        for user in users_to_create:
            # Verificar si ya existe para no duplicar
            existing = session.query(UserModel).filter(UserModel.email == user.email).first()
            if not existing:
                session.add(user)
        
        session.commit()
        print("✅ Seed completado con éxito.")

if __name__ == "__main__":
    seed_users()
