from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, events, users, attendees, sessions, ai, admin_chat
from app.infrastructure.database.connection import init_db

# app.infrastructure.database.connection.init_db is NOT needed here 
# because we use Alembic migrations for database schema management.

app = FastAPI(
    title="Mis Eventos API",
    description="API para la gestión de eventos corporativos",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(attendees.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(admin_chat.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Mis Eventos API"}
