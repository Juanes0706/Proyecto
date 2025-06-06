import os
import uuid
import logging 
from fastapi import UploadFile
from dotenv import load_dotenv
import aiofiles
from supabase import create_client

SUPABASE_URL = "https://yotmkfccxktsupzdtbvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdG1rZmNjeGt0c3VwemR0YnZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODU0NzkwNCwiZXhwIjoyMDY0MTIzOTA0fQ.ymMmRbO9plx0DLXjNJDvrKt2_aWdi4_h1bczP18qntU"

SUPABASE_BUCKET = "buses"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_file(file: UploadFile, filename: str):
    content = await file.read()
    file_path = f"image/{filename}"

    try:
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(
            file_path,
            content,
            {"content-type": file.content_type}
        )

        print("Respuesta upload:", res)

        public_url_response = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
        print("Respuesta get_public_url:", public_url_response)

        return {"url": public_url_response}

    except Exception as e:
        print("Error al subir imagen:", e)
        return {"error": str(e)}

async def save_file(file: UploadFile, to_supabase: bool):
    if not file.content_type.startswith("image/"):
        return {"error": "Solo se permiten imágenes"}

    new_filename = f"{uuid.uuid4().hex}_{file.filename}"

    if to_supabase:
        return await upload_file(file, new_filename)
    else:
        return await save_to_local(file, new_filename)


async def save_to_local(file: UploadFile, filename: str):

    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    return {"filename": filename, "local_path": file_path}
