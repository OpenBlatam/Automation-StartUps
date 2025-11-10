"""
Integración con Calendarios para Contratos
Sincronización de fechas importantes con calendarios
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger("airflow.task")


def create_calendar_event(
    contract_id: str,
    event_title: str,
    event_date: datetime,
    event_type: str = "reminder",  # 'reminder', 'deadline', 'renewal', 'signature_due'
    description: str = None,
    calendar_provider: str = None
) -> Dict[str, Any]:
    """
    Crea un evento de calendario para un contrato.
    
    Args:
        contract_id: ID del contrato
        event_title: Título del evento
        event_date: Fecha del evento
        event_type: Tipo de evento
        description: Descripción del evento
        calendar_provider: Proveedor de calendario ('google', 'outlook', 'ical')
        
    Returns:
        Dict con información del evento creado
    """
    calendar_provider = calendar_provider or os.getenv("CALENDAR_PROVIDER", "ical")
    
    event_data = {
        "contract_id": contract_id,
        "event_title": event_title,
        "event_date": event_date.isoformat(),
        "event_type": event_type,
        "description": description or f"Evento relacionado con contrato {contract_id}",
        "calendar_provider": calendar_provider,
        "created_at": datetime.now().isoformat()
    }
    
    if calendar_provider == "google":
        # TODO: Implementar integración con Google Calendar API
        logger.info("Google Calendar integration not yet implemented")
    elif calendar_provider == "outlook":
        # TODO: Implementar integración con Outlook Calendar API
        logger.info("Outlook Calendar integration not yet implemented")
    else:
        # Generar iCal format
        event_data["ical_content"] = generate_ical_event(event_data)
    
    return event_data


def generate_ical_event(event_data: Dict[str, Any]) -> str:
    """
    Genera contenido iCal para un evento.
    
    Args:
        event_data: Datos del evento
        
    Returns:
        String con formato iCal
    """
    from datetime import datetime
    
    event_date = datetime.fromisoformat(event_data["event_date"])
    end_date = event_date + timedelta(hours=1)
    
    # Formato iCal
    ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Contract Management System//EN
BEGIN:VEVENT
UID:{event_data['contract_id']}-{event_data['event_type']}@contracts
DTSTART:{event_date.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_date.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{event_data['event_title']}
DESCRIPTION:{event_data['description']}
LOCATION:Contract Management System
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""
    
    return ical


def get_contract_calendar_events(
    contract_id: str,
    start_date: datetime = None,
    end_date: datetime = None
) -> List[Dict[str, Any]]:
    """
    Obtiene todos los eventos de calendario para un contrato.
    
    Args:
        contract_id: ID del contrato
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
        
    Returns:
        Lista de eventos
    """
    events = []
    
    # Obtener fechas importantes del contrato
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        query = """
            SELECT 
                contract_id, title, start_date, expiration_date,
                signed_date, expiration_date - INTERVAL '30 days' as renewal_reminder
            FROM contracts
            WHERE contract_id = %s
        """
        contract = hook.get_first(query, parameters=(contract_id,))
        
        if contract:
            # Evento de inicio
            if contract[2]:  # start_date
                events.append({
                    "contract_id": contract_id,
                    "event_type": "start_date",
                    "event_title": f"Inicio: {contract[1]}",
                    "event_date": contract[2].isoformat() if hasattr(contract[2], 'isoformat') else str(contract[2]),
                    "description": f"Fecha de inicio del contrato {contract_id}"
                })
            
            # Evento de expiración
            if contract[3]:  # expiration_date
                events.append({
                    "contract_id": contract_id,
                    "event_type": "expiration",
                    "event_title": f"Expiración: {contract[1]}",
                    "event_date": contract[3].isoformat() if hasattr(contract[3], 'isoformat') else str(contract[3]),
                    "description": f"Fecha de expiración del contrato {contract_id}"
                })
            
            # Recordatorio de renovación
            if contract[4] and contract[3]:  # signed_date y expiration_date
                reminder_date = contract[3] - timedelta(days=30)
                if isinstance(reminder_date, datetime):
                    events.append({
                        "contract_id": contract_id,
                        "event_type": "renewal_reminder",
                        "event_title": f"Recordatorio Renovación: {contract[1]}",
                        "event_date": reminder_date.isoformat(),
                        "description": f"Recordatorio de renovación para contrato {contract_id}"
                    })
    except Exception as e:
        logger.warning(f"Error obteniendo eventos de calendario: {e}")
    
    # Filtrar por rango de fechas si se especifica
    if start_date or end_date:
        filtered_events = []
        for event in events:
            event_dt = datetime.fromisoformat(event["event_date"])
            if start_date and event_dt < start_date:
                continue
            if end_date and event_dt > end_date:
                continue
            filtered_events.append(event)
        events = filtered_events
    
    return events

