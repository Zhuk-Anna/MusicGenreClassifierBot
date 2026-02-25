import os
import aiohttp
from config import API_URL

def get_file_extension(file) -> str:
    # если есть имя файла
    if hasattr(file, "file_name") and file.file_name:
        return os.path.splitext(file.file_name)[1].lstrip(".").lower()
    # для voice Telegram — всегда ogg
    if hasattr(file, "mime_type") and file.mime_type == "audio/ogg":
        return "ogg"
    # fallback
    return "mp3"


async def load_genres():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL.replace("/predict", "/info")) as response:
            data = await response.json()
            return data.get("supported_genres", [])