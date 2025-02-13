from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List, Optional
from pathlib import Path
import os
from jinja2 import Environment, select_autoescape, FileSystemLoader

# Configuración de email
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", "sistema@cortinas.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates'
)

# Configuración de plantillas
templates = Environment(
    loader=FileSystemLoader('app/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

class EmailNotifier:
    def __init__(self):
        self.fast_mail = FastMail(conf)
        self.manufacturing_email = os.getenv("MANUFACTURING_EMAIL", "manufactura@cortinas.com")
        self.warehouse_email = os.getenv("WAREHOUSE_EMAIL", "almacen@cortinas.com")

    async def send_production_started_notification(self, cortina, diseno, materiales):
        """
        Envía notificación cuando la cortina entra en producción
        """
        # Email para el cliente
        if cortina.email:
            await self._send_client_production_notification(cortina)

        # Email para manufactura
        await self._send_manufacturing_order(cortina, diseno, materiales)

    async def send_production_completed_notification(self, cortina, diseno):
        """
        Envía notificación cuando la cortina está completada
        """
        # Email para el cliente
        if cortina.email:
            await self._send_client_completion_notification(cortina)

        # Email para almacén
        await self._send_warehouse_notification(cortina, diseno)

    async def _send_client_production_notification(self, cortina):
        """Envía email al cliente cuando su cortina entra en producción"""
        template = templates.get_template('production_started_client.html')
        html = template.render(
            order_id=cortina.id,
            client_name=cortina.cliente,
            dimensions=f"{cortina.ancho}cm x {cortina.alto}cm"
        )

        message = MessageSchema(
            subject=f"Tu cortina #{cortina.id} ha entrado en producción",
            recipients=[cortina.email],
            body=html,
            subtype="html"
        )

        await self.fast_mail.send_message(message)

    async def _send_manufacturing_order(self, cortina, diseno, materiales):
        """Envía orden de manufactura detallada"""
        template = templates.get_template('manufacturing_order.html')
        html = template.render(
            order_id=cortina.id,
            design_name=diseno.nombre,
            dimensions=f"{cortina.ancho}cm x {cortina.alto}cm",
            materials=materiales,
            notes=cortina.notas
        )

        message = MessageSchema(
            subject=f"Orden de Manufactura - Cortina #{cortina.id}",
            recipients=[self.manufacturing_email],
            body=html,
            subtype="html"
        )

        await self.fast_mail.send_message(message)

    async def _send_client_completion_notification(self, cortina):
        """Envía notificación al cliente cuando su cortina está lista"""
        template = templates.get_template('production_completed_client.html')
        html = template.render(
            order_id=cortina.id,
            client_name=cortina.cliente,
            dimensions=f"{cortina.ancho}cm x {cortina.alto}cm"
        )

        message = MessageSchema(
            subject=f"Tu cortina #{cortina.id} está lista",
            recipients=[cortina.email],
            body=html,
            subtype="html"
        )

        await self.fast_mail.send_message(message)

    async def _send_warehouse_notification(self, cortina, diseno):
        """Envía notificación a almacén para preparar la entrega"""
        template = templates.get_template('warehouse_notification.html')
        html = template.render(
            order_id=cortina.id,
            client_name=cortina.cliente,
            client_phone=cortina.telefono,
            client_email=cortina.email,
            design_name=diseno.nombre,
            dimensions=f"{cortina.ancho}cm x {cortina.alto}cm"
        )

        message = MessageSchema(
            subject=f"Cortina Lista para Entrega - #{cortina.id}",
            recipients=[self.warehouse_email],
            body=html,
            subtype="html"
        )

        await self.fast_mail.send_message(message)