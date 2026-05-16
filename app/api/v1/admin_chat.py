import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any
import os
import logging
import json
from sqlalchemy import text
from app.infrastructure.database.connection import get_session
from app.api.dependencies import get_current_admin
from app.domain.entities.user import UserEntity
from sqlalchemy.orm import Session

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/admin/chat", tags=["Admin Intelligence"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sql: str | None = None
    data: Any | None = None

DB_SCHEMA = """
ESTRUCTURA DE LA BASE DE DATOS (IMPORTANTE):
- Tabla 'users': (id, email, full_name, role ['ADMIN', 'ORGANIZER', 'ATTENDEE'])
- Tabla 'events': (id, title, status ['PUBLISHED', 'DRAFT', 'CANCELLED'])
- Tabla 'attendees': (id, user_id, event_id, status ['REGISTERED', 'CANCELLED'])
- Tabla 'sessions': (id, title, speaker_name, event_id)

RELACIONES:
- 'attendees.event_id' se une con 'events.id'
- 'attendees.user_id' se une con 'users.id'
"""

@router.post("", response_model=ChatResponse)
async def admin_chat(
    request: ChatRequest,
    db: Session = Depends(get_session),
    current_admin: UserEntity = Depends(get_current_admin)
):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY no configurada")

    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            # Paso 1: Generar SQL
            sql_prompt = f"""
            ### SYSTEM INSTRUCTIONS:
            You are a strict SQL Generator.
            
            ### SCHEMA:
            - Table 'users': (id, full_name, role ['ADMIN', 'ORGANIZER', 'ATTENDEE'])
            - Table 'events': (id, title, status)
            - Table 'attendees': (id, user_id, event_id, status)
            - Table 'sessions': (id, title, speaker_name, event_id)

            ### MANDATORY RULES:
            1. KEYWORDS ONLY: In LIKE clauses, use ONLY the event or person name. IGNORE question words like 'estado', 'quien', 'cuantos', 'dime', 'de', 'la'.
               Example: "Estado de Benito" -> title LIKE '%Benito%'
            2. SPEAKERS: To find a speaker of an event, JOIN 'events' and 'sessions'.
               Example: "Speaker de Tech" -> SELECT speaker_name FROM sessions s JOIN events e ON s.event_id = e.id WHERE e.title LIKE '%Tech%'
            3. NAMES: ALWAYS use '%' between words. Example: '%Elena%Perez%'
            4. ONLY SQL: Respond only with the SELECT statement.

            ### QUESTION:
            "{request.message}"
            """

            res_sql = await client.post(GROQ_URL, headers=headers, json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": sql_prompt}],
                "temperature": 0
            }, timeout=30.0)
            
            if res_sql.status_code != 200:
                logger.error(f"Groq SQL Error: {res_sql.text}")
                return ChatResponse(answer=f"Error de Groq (SQL): {res_sql.json().get('error', {}).get('message', 'Error desconocido')}")

            data_sql = res_sql.json()
            sql_query = data_sql['choices'][0]['message']['content'].strip()
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            logger.info(f"AI Generated SQL: {sql_query}")

            if "NONE" in sql_query.upper():
                return ChatResponse(answer="No tengo información suficiente para responder eso.")

            # Paso 2: Ejecutar en Postgres
            try:
                result = db.execute(text(sql_query))
                rows = [dict(row._mapping) for row in result]
                logger.info(f"SQL Results: {len(rows)} rows found")
            except Exception as sql_err:
                logger.error(f"SQL Execution Error: {str(sql_err)}")
                return ChatResponse(answer="Hubo un problema técnico al consultar la base de datos.")

            # Paso 3: Redactar respuesta humana con Groq
            final_prompt = f"""
            Admin pregunta: "{request.message}"
            Datos obtenidos de la DB: {json.dumps(rows, default=str)}
            
            Redacta una respuesta muy breve y profesional para el administrador basada en estos datos.
            Si no hay datos, dilo. No menciones el SQL.
            """
            
            res_final = await client.post(GROQ_URL, headers=headers, json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": final_prompt}],
                "temperature": 0.5
            }, timeout=30.0)
            
            if res_final.status_code != 200:
                 logger.error(f"Groq Final Error: {res_final.text}")
                 return ChatResponse(answer="Error al redactar la respuesta final.")

            data_final = res_final.json()
            answer = data_final['choices'][0]['message']['content'].strip()

            return ChatResponse(answer=answer, sql=sql_query, data=rows)

    except Exception as e:
        logger.error(f"Admin Chat Error (Groq): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en el asistente: {str(e)}")
