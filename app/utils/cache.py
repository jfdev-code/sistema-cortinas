# app/utils/cache.py
from functools import wraps
from typing import Any, Optional, Callable
import pickle
from datetime import datetime, timedelta
import hashlib
import json
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.diseno import Diseno

class CacheManager:
    def __init__(self, redis_client=None):
        self.cache = {}  # Fallback a memoria si no hay Redis
        self.redis = redis_client
    
    def _get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera una key única para los argumentos dados"""
        key_parts = [prefix]
        
        # Agregamos args y kwargs a la key
        if args:
            key_parts.append(pickle.dumps(args))
        if kwargs:
            key_parts.append(pickle.dumps(sorted(kwargs.items())))
            
        key_str = ''.join(str(p) for p in key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché"""
        if self.redis:
            value = await self.redis.get(key)
            if value:
                return pickle.loads(value)
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """Guarda un valor en el caché"""
        if self.redis:
            await self.redis.set(key, pickle.dumps(value), expire=expire)
        else:
            self.cache[key] = value
            
    async def delete(self, key: str) -> None:
        """Elimina una key del caché"""
        if self.redis:
            await self.redis.delete(key)
        else:
            self.cache.pop(key, None)

    async def clear_pattern(self, pattern: str) -> None:
        """Limpia todas las keys que coincidan con el patrón"""
        if self.redis:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        else:
            # Para caché en memoria, usamos un enfoque simple
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for k in keys_to_delete:
                del self.cache[k]

def cached(
    prefix: str,
    expire: int = 3600,
    vary_on_auth: bool = True
):
    """
    Decorador para cachear resultados de funciones y métodos.
    
    Args:
        prefix: Prefijo para la key de caché
        expire: Tiempo de expiración en segundos
        vary_on_auth: Si es True, la caché varía según el usuario autenticado
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtenemos el CacheManager del primer argumento si es self
            cache_manager = getattr(args[0], 'cache_manager', None) if args else None
            
            if not cache_manager:
                # Si no hay cache_manager, ejecutamos la función original
                return await func(*args, **kwargs)
            
            # Construimos la key de caché
            cache_key = cache_manager._get_cache_key(prefix, *args, **kwargs)
            
            # Si vary_on_auth es True, incluimos el user_id en la key
            if vary_on_auth:
                request = kwargs.get('request')
                if request and hasattr(request, 'user'):
                    cache_key += f"_user_{request.user.id}"
            
            # Intentamos obtener del caché
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Si no está en caché, ejecutamos la función
            result = await func(*args, **kwargs)
            
            # Guardamos en caché
            await cache_manager.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

# Ejemplo de uso en servicios:
class DisenoService:
    def __init__(self, db: Session, cache_manager: CacheManager):
        self.db = db
        self.cache_manager = cache_manager
    
    @cached("diseno_detail", expire=3600)
    async def get_diseno_detail(self, diseno_id: int) -> dict:
        """Obtiene los detalles de un diseño con caché"""
        # Lógica para obtener detalles del diseño
        diseno = self.db.query(Diseno).get(diseno_id)
        if not diseno:
            return None
            
        return {
            "id": diseno.id,
            "nombre": diseno.nombre,
            "descripcion": diseno.descripcion,
            "costo_base": diseno.costo_mano_obra,
            # ... más detalles
        }
    
    @cached("disenos_list", expire=1800)
    async def list_disenos(self, skip: int = 0, limit: int = 100) -> list:
        """Lista diseños con caché"""
        disenos = self.db.query(Diseno).offset(skip).limit(limit).all()
        return [
            {
                "id": d.id,
                "nombre": d.nombre,
                "costo_base": d.costo_mano_obra
            }
            for d in disenos
        ]