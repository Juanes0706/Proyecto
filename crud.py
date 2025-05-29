from supabase_client import supabase
from typing import Optional
import unicodedata

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
    return None

def actualizar_estado_bus(bus_id: int, nuevo_estado: bool):
    response = supabase.table("buses").update({"activo": nuevo_estado}).eq("id", bus_id).execute()
    if response.status_code == 204:
        return {"mensaje": f"Estado de bus actualizado a {'activo' if nuevo_estado else 'inactivo'}"}
    return None

def crear_bus(bus: dict, imagen_url: Optional[str] = None):
    bus_data = {
        "nombre_bus": bus.get("nombre_bus"),
        "tipo": bus.get("tipo").lower().strip() if bus.get("tipo") else None,
        "activo": bus.get("activo"),
        "imagen": imagen_url
    }
    response = supabase.table("buses").insert(bus_data).execute()
    return response.data[0] if response.data else None

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
    return None

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

def crear_estacion(estacion: dict, imagen_url: Optional[str] = None):
    estacion_data = {
        "nombre_estacion": estacion.get("nombre_estacion"),
        "localidad": estacion.get("localidad"),
        "rutas_asociadas": estacion.get("rutas_asociadas"),
        "activo": estacion.get("activo"),
        "imagen": imagen_url
    }
    response = supabase.table("estaciones").insert(estacion_data).execute()
    return response.data[0] if response.data else None
