from supabase import create_client, Client
import uuid
import os

SUPABASE_URL = "https://yotmkfccxktsupzdtbvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdG1rZmNjeGt0c3VwemR0YnZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODU0NzkwNCwiZXhwIjoyMDY0MTIzOTA0fQ.ymMmRbO9plx0DLXjNJDvrKt2_aWdi4_h1bczP18qntU"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def subir_imagen(bucket: str, imagen_bytes: bytes, imagen_filename: str) -> str | None:
    try:
        # Asegura un nombre único
        extension = os.path.splitext(imagen_filename)[1]
        nuevo_nombre = f"{uuid.uuid4()}{extension}"

        # Sube la imagen al bucket especificado
        response = supabase.storage.from_(bucket).upload(
            nuevo_nombre,
            imagen_bytes,
            {"content-type": "image/jpeg"}
        )

        # Verifica si hubo error
        if isinstance(response, dict) and response.get("error"):
            print("Error al subir imagen:", response["error"]["message"])
            return None

        # Obtiene la URL pública
        url = supabase.storage.from_(bucket).get_public_url(nuevo_nombre)
        return url

    except Exception as e:
        print("Excepción al subir imagen:", e)
        return None
