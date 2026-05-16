#!/bin/bash
set -e

echo "🚀 Iniciando proceso de arranque..."

# 1. Esperar a que la base de datos esté lista (si es necesario)
# En docker-compose ya usamos healthchecks, pero esto añade robustez

# 2. Correr migraciones
echo "📝 Aplicando migraciones de base de datos..."
alembic upgrade head

# 3. Cargar datos semilla
echo "🌱 Cargando datos semilla (seed)..."
python scripts/seed_users.py
python scripts/seed_events.py

# 4. Iniciar la aplicación
echo "✨ Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
