def get_supabase_path_from_url(url: str, bucket_name: str) -> str:
    """Extrae la ruta dentro del bucket de una URL pública de Supabase."""
    parts = url.split(f"/public/{bucket_name}/")
    if len(parts) > 1:
        return parts[-1]
    return ""
