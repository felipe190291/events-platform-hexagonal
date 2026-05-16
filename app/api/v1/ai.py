import os
import httpx
import logging
import base64
from fastapi import APIRouter, Depends
from app.api.schemas.ai import ImageGenerateRequest, ImageGenerateResponse
from app.api.dependencies import get_current_user
from app.domain.entities.user import UserEntity
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/ai", tags=["AI Integration"])

@router.post("/generate-image", response_model=ImageGenerateResponse)
async def generate_image(
    request: ImageGenerateRequest,
    current_user: UserEntity = Depends(get_current_user)
):
    """Generates an image using Hugging Face Inference API (Stable Diffusion)"""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    FALLBACK_IMAGE = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&q=80&w=1000"

    if not api_key:
        logger.error("AI: No se encontró HUGGINGFACE_API_KEY")
        # Si no hay llave, volvemos a Pollinations como respaldo rápido
        import urllib.parse
        encoded = urllib.parse.quote(request.prompt)
        return ImageGenerateResponse(url=f"https://pollinations.ai/p/{encoded}", is_generated=True)

    try:
        logger.info(f"AI: Generando imagen gratuita para: {request.prompt}")
        
        import urllib.parse
        encoded_prompt = urllib.parse.quote(request.prompt)
        import time
        seed = int(time.time())
        
        # Usamos Pollinations como motor principal por su fiabilidad y gratuidad
        # La URL de Pollinations es muy robusta
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"

        async with httpx.AsyncClient() as client:
            response = await client.get(pollinations_url, timeout=60.0)
            
            if response.status_code == 200:
                image_bytes = response.content
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                logger.info("AI: Imagen generada con éxito (Motor: Pollinations/Flux).")
                return ImageGenerateResponse(url=f"data:image/jpeg;base64,{image_b64}", is_generated=True)
            
            logger.error(f"AI: Error en motor principal ({response.status_code})")

    except Exception as e:
        logger.error(f"AI Exception: {str(e)}")

    return ImageGenerateResponse(url=FALLBACK_IMAGE, is_generated=False)
