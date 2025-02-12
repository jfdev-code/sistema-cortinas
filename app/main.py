# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import database functions with their correct names
from .database import init_db, close_db_connections
from .routes import (
    tipo_insumo_routes,
    referencia_routes,
    color_routes,
    inventario_routes,
    diseno_routes,
    cortina_routes,
    rentabilidad_routes
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sistema de Gestión de Cortinas",
    description="API para la gestión integral de un sistema de fabricación de cortinas",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://cortinas-frontend.onrender.com"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(tipo_insumo_routes, prefix="/api/v1")
app.include_router(referencia_routes, prefix="/api/v1")
app.include_router(color_routes, prefix="/api/v1")
app.include_router(inventario_routes, prefix="/api/v1")
app.include_router(diseno_routes, prefix="/api/v1")
app.include_router(cortina_routes, prefix="/api/v1")
app.include_router(rentabilidad_routes, prefix="/api/v1")
app.include_router(cortina_routes, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler that initializes application resources,
    particularly the database connection and tables.
    """
    logger.info("Starting up the application...")
    await init_db()
    logger.info("Application startup completed!")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler that ensures proper cleanup of resources,
    particularly database connections.
    """
    logger.info("Shutting down the application...")
    await close_db_connections()
    logger.info("Application shutdown completed!")

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "app": "Sistema de Gestión de Cortinas",
        "version": "1.0.0",
        "documentation": "/docs"
    }