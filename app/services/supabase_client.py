import os
import uuid
from fastapi import UploadFile
from dotenv import load_dotenv
import aiofiles
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("La variable de entorno SUPABASE_URL no está definida")
if not SUPABASE_KEY:
    raise ValueError("La variable de entorno SUPABASE_KEY no está definida")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_file(file: UploadFile, filename: str, bucket_name: str):
    """Sube un archivo a un bucket específico en Supabase Storage."""
    content = await file.read()
    file_path = f"image/{filename}"

    try:
        res = supabase.storage.from_(bucket_name).upload(
            file_path,
            content,
            {"content-type": file.content_type}
        )
        public_url_response = supabase.storage.from_(bucket_name).get_public_url(file_path)
        return {"url": public_url_response}
    except Exception as e:
        print(f"Error al subir imagen a Supabase Storage en el bucket {bucket_name}: {e}")
        return {"error": str(e)}

async def save_file(file: UploadFile, to_supabase: bool, bucket_name: str):
    """
    Guarda un archivo, ya sea localmente o en Supabase, y devuelve la URL o ruta.
    Ahora acepta bucket_name para especificar dónde subir en Supabase.
    """
    if not file.content_type.startswith("image/"):
        return {"error": "Solo se permiten imágenes"}

    new_filename = f"{uuid.uuid4().hex}_{file.filename}"

    if to_supabase:
        return await upload_file(file, new_filename, bucket_name)
    else:

        return {"error": "Guardado local no implementado para este contexto"}

async def delete_file(file_url: str, bucket_name: str) -> bool:
   
    try:

        path_in_bucket = get_supabase_path_from_url(file_url, bucket_name)
        if not path_in_bucket:
            print(f"No se pudo extraer la ruta del archivo de la URL: {file_url}")
            return False

        res = supabase.storage.from_(bucket_name).remove([path_in_bucket])
        if res and not res[0].get('error'): 
            print(f"Archivo {path_in_bucket} eliminado exitosamente del bucket {bucket_name}.")
            return True
        else:
            print(f"Error al eliminar el archivo {path_in_bucket} del bucket {bucket_name}: {res}")
            return False
    except Exception as e:
        print(f"Excepción al intentar eliminar archivo de Supabase Storage: {e}")
        return False

def get_supabase_path_from_url(url: str, bucket_name: str) -> str:
    """Extrae la ruta del archivo dentro del bucket de una URL pública de Supabase."""
    parts = url.split(f"/public/{bucket_name}/")
    if len(parts) > 1:
        import urllib.parse
        return urllib.parse.unquote(parts[-1])
    return ""