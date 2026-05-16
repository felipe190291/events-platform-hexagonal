from pydantic import BaseModel

class ImageGenerateRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"

class ImageGenerateResponse(BaseModel):
    url: str
    is_generated: bool
