import os
import uuid
import logging 
from fastapi import UploadFile
from dotenv import load_dotenv
import aiofiles
from supabase import create_client
from typing import Optional

load_dotenv() 

SUPABASE_URL = os.getenv("SUPABASE_URL") 
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 

if not SUPABASE_URL or not SUPABASE_KEY: 
    raise ValueError("Las variables de entorno SUPABASE_URL o SUPABASE_KEY no están definidas.") #

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) 

async def upload_file(file: UploadFile, filename: str, bucket_name: str): 
    content = await file.read() 
    file_path = f"image/{filename}" 

    try:
        res = supabase.storage.from_(bucket_name).upload( 
            file_path, 
            content, 
            {"content-type": file.content_type} 
        )

        logging.info(f"Respuesta upload: {res}") 

        public_url_response = supabase.storage.from_(bucket_name).get_public_url(file_path) 
        logging.info(f"Respuesta get_public_url: {public_url_response}") 

        return {"url": public_url_response} 

    except Exception as e:
        logging.error(f"Error al subir imagen: {e}") 
        return {"error": str(e)} 

async def save_file(file: UploadFile, to_supabase: bool, bucket_name: Optional[str] = None): 
    if not file.content_type.startswith("image/"): 
        return {"error": "Solo se permiten imágenes"} 

    new_filename = f"{uuid.uuid4().hex}_{file.filename}" 

    if to_supabase: #
        if not bucket_name: #
            logging.warning("No se especificó el bucket para save_file, usando 'buses' por defecto.") #
            bucket_name = "buses" 
        return await upload_file(file, new_filename, bucket_name) 
    else:
        return await save_to_local(file, new_filename) 


async def save_to_local(file: UploadFile, filename: str): 
    os.makedirs("uploads", exist_ok=True) 
    file_path = os.path.join("uploads", filename) 

    try:
        async with aiofiles.open(file_path, "wb") as out_file: 
            content = await file.read() 
            await out_file.write(content) 

        return {"filename": filename, "local_path": file_path} 
    except Exception as e:
        logging.error(f"Error al guardar archivo localmente: {e}")
        return {"error": str(e)} 

async def get_public_url(filename: str, bucket_name: str) -> str: 
    return supabase.storage.from_(bucket_name).get_public_url(filename) 

