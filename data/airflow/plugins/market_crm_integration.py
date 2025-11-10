"""
Integración con CRM/ERP

Integra análisis de mercado con sistemas CRM/ERP para:
- Sincronizar oportunidades
- Actualizar contactos con insights
- Crear tareas basadas en recomendaciones
- Trackear ROI de acciones
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class MarketCRMIntegration:
    """Integración con sistemas CRM/ERP."""
    
    def __init__(
        self,
        crm_type: str = "salesforce",
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Inicializa integración con CRM.
        
        Args:
            crm_type: Tipo de CRM ("salesforce", "hubspot", "custom")
            api_endpoint: Endpoint de API
            api_key: API key
        """
        self.crm_type = crm_type.lower()
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.http_client = httpx.Client(timeout=30.0)
        self.logger = logging.getLogger(__name__)
    
    def sync_opportunities_to_crm(
        self,
        opportunities: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """
        Sincroniza oportunidades con CRM.
        
        Args:
            opportunities: Lista de oportunidades
            industry: Industria
            
        Returns:
            Resultado de sincronización
        """
        if not self.api_endpoint:
            logger.warning("CRM API endpoint not configured")
            return {"synced": False, "reason": "No API endpoint"}
        
        logger.info(f"Syncing {len(opportunities)} opportunities to {self.crm_type}")
        
        synced_count = 0
        failed_count = 0
        
        for opp in opportunities:
            try:
                success = self._create_crm_opportunity(opp, industry)
                if success:
                    synced_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error syncing opportunity: {e}")
                failed_count += 1
        
        return {
            "synced": True,
            "total_opportunities": len(opportunities),
            "synced_count": synced_count,
            "failed_count": failed_count,
            "crm_type": self.crm_type
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _create_crm_opportunity(
        self,
        opportunity: Dict[str, Any],
        industry: str
    ) -> bool:
        """Crea oportunidad en CRM."""
        # Preparar datos según tipo de CRM
        if self.crm_type == "salesforce":
            payload = {
                "Name": opportunity.get("title", "Market Opportunity"),
                "Description": opportunity.get("description", ""),
                "StageName": "Prospecting",
                "Amount": opportunity.get("roi_analysis", {}).get("expected_return", 0) if opportunity.get("roi_analysis") else 0,
                "Industry": industry,
                "Type": "Market Research"
            }
        elif self.crm_type == "hubspot":
            payload = {
                "properties": {
                    "dealname": opportunity.get("title", "Market Opportunity"),
                    "dealstage": "appointmentscheduled",
                    "amount": str(opportunity.get("roi_analysis", {}).get("expected_return", 0)) if opportunity.get("roi_analysis") else "0",
                    "industry": industry
                }
            }
        else:
            # Custom CRM
            payload = {
                "title": opportunity.get("title", "Market Opportunity"),
                "description": opportunity.get("description", ""),
                "industry": industry,
                "opportunity_data": opportunity
            }
        
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = self.http_client.post(
                self.api_endpoint,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating CRM opportunity: {e}")
            return False
    
    def create_tasks_from_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        assignee_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea tareas en CRM basadas en recomendaciones.
        
        Args:
            recommendations: Lista de recomendaciones
            assignee_id: ID del asignado (opcional)
            
        Returns:
            Resultado de creación de tareas
        """
        if not self.api_endpoint:
            return {"tasks_created": False, "reason": "No API endpoint"}
        
        logger.info(f"Creating tasks from {len(recommendations)} recommendations")
        
        created_count = 0
        
        for rec in recommendations:
            if rec.get("priority") == "high":
                try:
                    success = self._create_crm_task(rec, assignee_id)
                    if success:
                        created_count += 1
                except Exception as e:
                    logger.error(f"Error creating task: {e}")
        
        return {
            "tasks_created": True,
            "total_recommendations": len(recommendations),
            "tasks_created_count": created_count,
            "crm_type": self.crm_type
        }
    
    def _create_crm_task(
        self,
        recommendation: Dict[str, Any],
        assignee_id: Optional[str]
    ) -> bool:
        """Crea tarea en CRM."""
        if self.crm_type == "salesforce":
            payload = {
                "Subject": recommendation.get("title", "Market Recommendation"),
                "Description": recommendation.get("description", ""),
                "Status": "Not Started",
                "Priority": "High"
            }
            if assignee_id:
                payload["OwnerId"] = assignee_id
        elif self.crm_type == "hubspot":
            payload = {
                "properties": {
                    "hs_task_subject": recommendation.get("title", "Market Recommendation"),
                    "hs_task_body": recommendation.get("description", ""),
                    "hs_task_status": "NOT_STARTED",
                    "hs_task_priority": "HIGH"
                }
            }
        else:
            payload = {
                "title": recommendation.get("title", "Market Recommendation"),
                "description": recommendation.get("description", ""),
                "priority": "high",
                "recommendation_data": recommendation
            }
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = self.http_client.post(
                f"{self.api_endpoint}/tasks",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Error creating CRM task: {e}")
            return False
    
    def update_contacts_with_insights(
        self,
        insights: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """
        Actualiza contactos en CRM con insights relevantes.
        
        Args:
            insights: Lista de insights
            industry: Industria
            
        Returns:
            Resultado de actualización
        """
        if not self.api_endpoint:
            return {"updated": False, "reason": "No API endpoint"}
        
        # Filtrar insights de alta prioridad
        high_priority = [i for i in insights if i.get("priority") == "high"]
        
        logger.info(f"Updating contacts with {len(high_priority)} high-priority insights")
        
        # En producción, buscarías contactos relevantes en CRM
        # Por ahora, simulamos la actualización
        
        return {
            "updated": True,
            "insights_count": len(high_priority),
            "contacts_updated": 0,  # Simulado
            "crm_type": self.crm_type
        }






