from supabase_client import supabase
from typing import Optional
import unicodedata
import re
import uuid

def limpiar_nombre_archivo(nombre: str) -> str:
    nombre = unicodedata.normalize('NFD', nombre)
    nombre = nombre.encode('ascii', 'ignore').decode('utf-8')
    nombre = re.sub(r'\s+', '_', nombre)
    return nombre.lower()

def subir_imagen(bucket_name: str, file_name: str, file_bytes: bytes, content_type: str = "image/jpeg") -> Optional[str]:
    try:
        file_name = limpiar_nombre_archivo(file_name)
        # Opcional: evitar colisiones con UUID
        # file_name = f"{uuid.uuid4().hex}_{file_name}"

        response = supabase.storage.from_(bucket_name).upload(
            file_name,
            file_bytes,
            {"content-type": content_type},
            upsert=True
        )
        if response.get("error"):
            print("Error subiendo imagen:", response["error"])
            return None
        url = f"https://{supabase.supabase_url.replace('https://', '')}/storage/v1/object/public/{bucket_name}/{file_name}"
        return url
    except Exception as e:
        print("Excepción al subir imagen:", e)
        return None

# ---------------------- BUSES ----------------------

def obtener_buses(tipo: Optional[str] = None, activo: Optional[bool] = None):
    query = supabase.table("buses")
    if tipo:
        query = query.ilike("tipo", f"%{tipo}%")
    if activo is not None:
        query = query.eq("activo", activo)
    response = query.select("*").execute()
    buses = response.data
    for bus in buses:
        if bus.get("tipo"):
            bus["tipo"] = bus["tipo"].strip().lower()
    return buses

def obtener_bus_por_id(bus_id: int):
    response = supabase.table("buses").select("*").eq("id", bus_id).single().execute()
    return response.data

def eliminar_bus(bus_id: int):
    bus = obtener_bus_por_id(bus_id)
    if not bus:
        return None
    imagen_url = bus.get("imagen")
    if imagen_url:
        try:
            bucket = "buses"
            filename = imagen_url.split(f"/{bucket}/")[-1]
            supabase.storage.from_(bucket).remove([filename])
        except Exception as e:
            print(f"Error deleting bus image: {e}")
    response = supabase.table("buses").delete().eq("id", bus_id).execute()
    if response.status_code == 204:
        return {"mensaje": "Bus eliminado"}
    return {"error": "Error eliminando bus"}

def actualizar_estado_bus(bus_id: int, nuevo_estado: bool):
    response = supabase.table("buses").update({"activo": nuevo_estado}).eq("id", bus_id).execute()
    if response.status_code == 204:
        return {"mensaje": f"Estado de bus actualizado a {'activo' if nuevo_estado else 'inactivo'}"}
    return None

def crear_bus(bus: dict, imagen_bytes: Optional[bytes] = None, imagen_filename: Optional[str] = None):
    imagen_url = None
    if imagen_bytes and imagen_filename:
        imagen_url = subir_imagen("buses", imagen_filename, imagen_bytes)

    bus_data = {
        "nombre_bus": bus.get("nombre_bus"),
        "tipo": bus.get("tipo").lower().strip() if bus.get("tipo") else None,
        "activo": bus.get("activo"),
        "imagen": imagen_url
    }
    response = supabase.table("buses").insert(bus_data).execute()
    return response.data[0] if response.data else None

def actualizar_imagen_bus(bus_id: int, imagen_url: str):
    response = supabase.table("buses").update({"imagen": imagen_url}).eq("id", bus_id).execute()
    if hasattr(response, "error") and response.error:
        return None
    return response.data[0] if response.data else None

# ---------------------- ESTACIONES ----------------------

def normalize_string(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()

def obtener_estaciones(sector: Optional[str] = None, activo: Optional[bool] = None):
    query = supabase.table("estaciones")
    if sector:
        sector_norm = normalize_string(sector)
        query = query.ilike("localidad", f"%{sector_norm}%")
    if activo is not None:
        query = query.eq("activo", activo)
    response = query.select("*").execute()
    return response.data

def obtener_estacion_por_id(estacion_id: int):
    response = supabase.table("estaciones").select("*").eq("id", estacion_id).single().execute()
    return response.data

def eliminar_estacion(estacion_id: int):
    estacion = obtener_estacion_por_id(estacion_id)
    if not estacion:
        return None
    imagen_url = estacion.get("imagen")
    if imagen_url:
        try:
            bucket = "estaciones"
            filename = imagen_url.split(f"/{bucket}/")[-1]
            supabase.storage.from_(bucket).remove([filename])
        except Exception as e:
            print(f"Error deleting estacion image: {e}")
    response = supabase.table("estaciones").delete().eq("id", estacion_id).execute()
    if response.status_code == 204:
        return {"mensaje": "Estación eliminada"}
    return {"error": "Error eliminando estación"}

def actualizar_estado_estacion(estacion_id: int, nuevo_estado: bool):
    response = supabase.table("estaciones").update({"activo": nuevo_estado}).eq("id", estacion_id).execute()
    if response.status_code == 204:
        return {"mensaje": f"Estado de estación actualizado a {'activo' if nuevo_estado else 'inactivo'}"}
    return None

def actualizar_id_estacion(estacion_id: int, nuevo_id: int):
    response = supabase.table("estaciones").update({"id": nuevo_id}).eq("id", estacion_id).execute()
    if response.status_code == 204:
        return {"mensaje": f"ID de estación actualizado a {nuevo_id}"}
    return None

def crear_estacion(estacion: dict, imagen_bytes: Optional[bytes] = None, imagen_filename: Optional[str] = None):
    imagen_url = None
    if imagen_bytes and imagen_filename:
        imagen_url = subir_imagen("estaciones", imagen_filename, imagen_bytes)

    estacion_data = {
        "nombre_estacion": estacion.get("nombre_estacion"),
        "localidad": estacion.get("localidad"),
        "rutas_asociadas": estacion.get("rutas_asociadas"),
        "activo": estacion.get("activo"),
        "imagen": imagen_url
    }
    response = supabase.table("estaciones").insert(estacion_data).execute()
    return response.data[0] if response.data else None

def actualizar_imagen_estacion(estacion_id: int, imagen_url: str):
    response = supabase.table("estaciones").update({"imagen": imagen_url}).eq("id", estacion_id).execute()
    if hasattr(response, "error") and response.error:
        return None
    return response.data[0] if response.data else None

def actualizar_bus(bus_id: int, update_data: dict):
    response = supabase.table("buses").update(update_data).eq("id", bus_id).execute()
    if response.error:
        return None
    return response.data[0] if response.data else None

def actualizar_estacion(estacion_id: int, update_data: dict):
    response = supabase.table("estaciones").update(update_data).eq("id", estacion_id).execute()
    if response.error:
        return None
    return response.data[0] if response.data else None
