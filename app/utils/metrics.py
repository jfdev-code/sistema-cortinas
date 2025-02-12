# app/utils/metrics.py
from contextlib import contextmanager
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from functools import wraps
import time
from typing import Callable
from contextvars import ContextVar
import logging

logger = logging.getLogger(__name__)

# Definimos métricas básicas con nombres más descriptivos y etiquetas apropiadas
REQUEST_COUNT = Counter(
    'cortinas_http_requests_total',
    'Total de peticiones HTTP al sistema de cortinas',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'cortinas_http_request_duration_seconds',
    'Latencia de peticiones HTTP al sistema de cortinas',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]  # Buckets en segundos
)

ACTIVE_REQUESTS = Gauge(
    'cortinas_active_requests',
    'Número actual de peticiones activas'
)

DB_CONNECTIONS = Gauge(
    'cortinas_db_connections_active',
    'Número actual de conexiones activas a la base de datos'
)

INVENTORY_LEVEL = Gauge(
    'cortinas_inventory_level',
    'Nivel actual de inventario por producto',
    ['referencia_id', 'color_id', 'ubicacion']
)

ORDER_VALUE = Histogram(
    'cortinas_order_value_pesos',
    'Distribución del valor de las órdenes en pesos',
    buckets=[1000, 5000, 10000, 20000, 50000, 100000]
)

# Métricas adicionales específicas del negocio
PRODUCTION_TIME = Histogram(
    'cortinas_production_time_minutes',
    'Tiempo de producción por cortina',
    ['tipo_cortina'],
    buckets=[30, 60, 90, 120, 180, 240]  # Buckets en minutos
)

MATERIAL_USAGE = Counter(
    'cortinas_material_usage_meters',
    'Uso de material en metros',
    ['tipo_material', 'referencia']
)

class MetricsMiddleware:
    """
    Middleware para recolectar métricas de las peticiones HTTP de manera automática.
    Registra conteos, latencias y mantiene tracking de peticiones activas.
    """
    
    async def __call__(self, request: Request, call_next):
        # Incrementamos el contador de peticiones activas
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Registramos la petición exitosa
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status_code
            ).inc()
            
            # Registramos la latencia
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # Registramos la petición fallida
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            raise
            
        finally:
            # Siempre decrementamos el contador de peticiones activas
            ACTIVE_REQUESTS.dec()

class DatabaseMetrics:
    """
    Clase para rastrear métricas relacionadas con la base de datos.
    Mantiene conteo de conexiones y registra tiempos de consulta.
    """
    
    def __init__(self):
        self._active_connections = 0
        self.query_latency = Histogram(
            'cortinas_db_query_duration_seconds',
            'Duración de consultas a la base de datos',
            ['query_type']
        )
    
    def connection_created(self):
        """Registra una nueva conexión a la base de datos"""
        self._active_connections += 1
        DB_CONNECTIONS.set(self._active_connections)
    
    def connection_closed(self):
        """Registra el cierre de una conexión a la base de datos"""
        self._active_connections -= 1
        DB_CONNECTIONS.set(self._active_connections)
    
    @contextmanager
    def track_query_latency(self, query_type: str):
        """Contexto para medir la latencia de consultas"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.query_latency.labels(query_type=query_type).observe(duration)

def track_inventory_change(referencia_id: str, color_id: str, cantidad: float, ubicacion: str):
    """
    Actualiza las métricas de inventario cuando hay cambios.
    """
    INVENTORY_LEVEL.labels(
        referencia_id=referencia_id,
        color_id=color_id,
        ubicacion=ubicacion
    ).set(cantidad)

def track_material_usage(tipo_material: str, referencia: str, cantidad: float):
    """
    Registra el uso de material en la producción.
    """
    MATERIAL_USAGE.labels(
        tipo_material=tipo_material,
        referencia=referencia
    ).inc(cantidad)

# Endpoint para exponer métricas a Prometheus
async def metrics_endpoint():
    """
    Endpoint que expone las métricas en formato que Prometheus puede consumir.
    """
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Registramos el endpoint en FastAPI
def init_metrics(app):
    """
    Inicializa el sistema de métricas y registra el endpoint en la aplicación.
    """
    app.add_route("/metrics", metrics_endpoint)
    logger.info("Sistema de métricas inicializado correctamente")