import sys
import os
from datetime import datetime, timedelta
import random

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlalchemy as sa
from sqlmodel import Session, select
from app.infrastructure.database.connection import engine
from app.infrastructure.database.models import UserModel, EventModel
from app.domain.enums import EventStatus, UserRole

def seed_events():
    with Session(engine) as session:
        # 1. Verificar si ya existen eventos para no duplicar en cada reinicio
        existing_count = session.exec(select(sa.func.count(EventModel.id))).one()
        if existing_count > 0:
            print(f"ℹ️ La base de datos ya tiene {existing_count} eventos. Saltando seed de eventos.")
            return

        # 2. Buscar un organizador para asignar los eventos
        statement = select(UserModel).where(UserModel.role == UserRole.ORGANIZER)
        organizer = session.exec(statement).first()
        
        if not organizer:
            # Si no hay organizador, buscamos un admin
            statement = select(UserModel).where(UserModel.role == UserRole.ADMIN)
            organizer = session.exec(statement).first()
            
        if not organizer:
            print("❌ Error: No se encontró ningún usuario Organizador o Admin para asignar los eventos.")
            return

        print(f"👤 Asignando eventos al usuario: {organizer.full_name} ({organizer.email})")

        # 3. Listas para generar datos variados
        temas = ["Tecnología", "IA", "Diseño", "Marketing", "Negocios", "Startup", "Blockchain", "Cloud", "Data Science", "UX/UI"]
        formatos = ["Conferencia", "Workshop", "Seminario", "Meetup", "Webinar", "Cumbre"]
        ciudades = ["Madrid", "Barcelona", "Bogotá", "Ciudad de México", "Buenos Aires", "Remoto", "Valencia", "Lima", "Santiago"]
        imagenes = [
            "https://images.unsplash.com/photo-1540575861501-7ad05823c9f5?w=800",
            "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=800",
            "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800",
            "https://images.unsplash.com/photo-1475721027185-39a12947c048?w=800",
            "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800"
        ]

        events_created = 0
        now = datetime.now()

        for i in range(1, 31):
            tema = random.choice(temas)
            formato = random.choice(formatos)
            titulo = f"{formato} de {tema} {2024 + (i % 2)}"
            
            # Fechas variadas (algunas pasadas, algunas futuras)
            dias_offset = random.randint(-60, 120)
            start_date = now + timedelta(days=dias_offset, hours=random.randint(9, 18))
            end_date = start_date + timedelta(hours=random.randint(2, 8))
            
            # Estado basado en la fecha
            if start_date < now:
                status = EventStatus.COMPLETED
            else:
                status = random.choice([EventStatus.PUBLISHED, EventStatus.PUBLISHED, EventStatus.DRAFT])

            event = EventModel(
                title=titulo,
                description=f"Únete a nosotros en este increíble {formato.lower()} sobre {tema.lower()}. Aprenderás las últimas tendencias y harás networking con expertos del sector. No te pierdas la oportunidad de expandir tus conocimientos en {tema}.",
                location=random.choice(ciudades),
                start_date=start_date,
                end_date=end_date,
                capacity=random.choice([50, 100, 200, 500]),
                status=status,
                organizer_id=organizer.id,
                image_url=random.choice(imagenes)
            )
            
            session.add(event)
            events_created += 1

        session.commit()
        print(f"✅ Seed completado: se han creado {events_created} eventos.")

if __name__ == "__main__":
    seed_events()
