# app/events/event_manager.py
from typing import Any, Callable, Dict, List, Set
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventario_insumo import InventarioInsumo

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Base class for system events"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()

class AsyncEventManager:
    """
    Async event manager that allows publishing and subscribing to system events
    """
    def __init__(self):
        self._subscribers: Dict[str, Set[Callable]] = {}
        self._logger = logging.getLogger(__name__)
    
    async def publish(self, event: Event) -> None:
        """
        Publishes an event to all subscribers asynchronously
        """
        if event.type not in self._subscribers:
            return
            
        tasks = []
        for subscriber in self._subscribers[event.type]:
            try:
                # Execute each subscriber asynchronously
                task = asyncio.create_task(subscriber(event))
                tasks.append(task)
            except Exception as e:
                self._logger.error(
                    f"Error notifying subscriber for event {event.type}: {str(e)}"
                )
        
        # Wait for all subscribers to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribes a callback function to an event type
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Unsubscribes a callback function from an event type
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(callback)

# Specific system events
@dataclass
class StockLowEvent(Event):
    """Event for when stock is below minimum"""
    type: str = "stock_low"

@dataclass
class OrderCreatedEvent(Event):
    """Event for when a new order is created"""
    type: str = "order_created"

@dataclass
class StockUpdatedEvent(Event):
    """Event for when stock is updated"""
    type: str = "stock_updated"

# Base notifiers
class BaseNotifier:
    """Base class for implementing different types of notifiers"""
    async def notify(self, event: Event) -> None:
        raise NotImplementedError()

class AsyncEmailNotifier(BaseNotifier):
    """Implementation of email notifications"""
    async def notify(self, event: Event) -> None:
        if isinstance(event, StockLowEvent):
            await self._notify_low_stock(event)
        elif isinstance(event, OrderCreatedEvent):
            await self._notify_order_created(event)
    
    async def _notify_low_stock(self, event: StockLowEvent) -> None:
        # Email sending logic would go here
        inventario = event.data.get('inventario')
        mensaje = (
            f"Stock bajo para el producto {inventario['referencia']}\n"
            f"Stock actual: {inventario['cantidad']}\n"
            f"Stock mínimo: {inventario['cantidad_minima']}"
        )
        logger.info(f"Enviando email: {mensaje}")

    async def _notify_order_created(self, event: OrderCreatedEvent) -> None:
        orden = event.data.get('orden')
        mensaje = (
            f"Nueva orden creada: {orden['id']}\n"
            f"Cliente: {orden['cliente']}\n"
            f"Total: ${orden['total']}"
        )
        logger.info(f"Enviando email: {mensaje}")

class AsyncSlackNotifier(BaseNotifier):
    """Implementation of Slack notifications"""
    async def notify(self, event: Event) -> None:
        if isinstance(event, StockLowEvent):
            await self._notify_low_stock(event)
        elif isinstance(event, OrderCreatedEvent):
            await self._notify_order_created(event)
    
    async def _notify_low_stock(self, event: StockLowEvent) -> None:
        inventario = event.data.get('inventario')
        mensaje = {
            "text": "🚨 *ALERTA DE STOCK BAJO*",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*Producto:* {inventario['referencia']}\n"
                            f"*Stock actual:* {inventario['cantidad']}\n"
                            f"*Stock mínimo:* {inventario['cantidad_minima']}"
                        )
                    }
                }
            ]
        }
        logger.info(f"Enviando a Slack: {mensaje}")

    async def _notify_order_created(self, event: OrderCreatedEvent) -> None:
        orden = event.data.get('orden')
        mensaje = {
            "text": "📦 *NUEVA ORDEN*",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*ID:* {orden['id']}\n"
                            f"*Cliente:* {orden['cliente']}\n"
                            f"*Total:* ${orden['total']}"
                        )
                    }
                }
            ]
        }
        logger.info(f"Enviando a Slack: {mensaje}")

# Initialize event system
event_manager = AsyncEventManager()
email_notifier = AsyncEmailNotifier()
slack_notifier = AsyncSlackNotifier()

# Register notifiers for different events
event_manager.subscribe("stock_low", email_notifier.notify)
event_manager.subscribe("stock_low", slack_notifier.notify)
event_manager.subscribe("order_created", email_notifier.notify)
event_manager.subscribe("order_created", slack_notifier.notify)

class AsyncInventoryService:
    """Example service using async event manager"""
    def __init__(self, db: AsyncSession, event_manager: AsyncEventManager):
        self.db = db
        self.event_manager = event_manager
    
    async def actualizar_stock(
        self,
        inventario_id: int,
        cantidad: float,
        motivo: str
    ) -> None:
        """Example of using events in a service method"""
        async with self.db.begin():
            # Get inventory record
            stmt = select(InventarioInsumo).where(InventarioInsumo.id == inventario_id)
            result = await self.db.execute(stmt)
            inventario = result.scalar_one_or_none()
            
            if not inventario:
                raise ValueError(f"Inventario {inventario_id} no encontrado")
            
            cantidad_anterior = inventario.cantidad
            inventario.cantidad += cantidad
            
            # Publish stock update event
            await self.event_manager.publish(
                StockUpdatedEvent(
                    data={
                        "inventario_id": inventario_id,
                        "cantidad_anterior": cantidad_anterior,
                        "cantidad_nueva": inventario.cantidad,
                        "cambio": cantidad,
                        "motivo": motivo
                    }
                )
            )
            
            # Check if we reached minimum level
            if inventario.cantidad <= inventario.cantidad_minima:
                await self.event_manager.publish(
                    StockLowEvent(
                        data={
                            "inventario": {
                                "id": inventario.id,
                                "referencia": inventario.referencia.nombre,
                                "cantidad": inventario.cantidad,
                                "cantidad_minima": inventario.cantidad_minima
                            }
                        }
                    )
                )