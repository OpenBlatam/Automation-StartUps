"""
Tests helpers para ads reporting.

Funciones auxiliares para testing.
"""

from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime, timedelta


def create_mock_campaign_data(
    count: int = 10,
    platform: str = "facebook",
    date_start: str = None,
    date_stop: str = None
) -> List[Dict[str, Any]]:
    """
    Crea datos mock de campañas para testing.
    
    Args:
        count: Número de registros a crear
        platform: Plataforma (facebook, tiktok, google)
        date_start: Fecha inicio (opcional)
        date_stop: Fecha fin (opcional)
        
    Returns:
        Lista de datos mock
    """
    if date_start is None:
        date_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    if date_stop is None:
        date_stop = datetime.now().strftime("%Y-%m-%d")
    
    data = []
    for i in range(count):
        impressions = 1000 + (i * 100)
        clicks = 50 + (i * 5)
        spend = 10.0 + (i * 1.0)
        
        record = {
            "date_start": date_start,
            "date_stop": date_stop,
            "platform": platform,
            "campaign_id": f"camp_{i}",
            "campaign_name": f"Campaign {i}",
            "ad_group_id": f"adgroup_{i}",
            "ad_group_name": f"Ad Group {i}",
            "ad_id": f"ad_{i}",
            "ad_name": f"Ad {i}",
            "impressions": impressions,
            "clicks": clicks,
            "spend": spend,
            "conversions": 5.0 + (i * 0.5),
            "ctr": (clicks / impressions * 100) if impressions > 0 else 0.0,
            "cpc": (spend / clicks) if clicks > 0 else 0.0,
            "cpa": (spend / (5.0 + i * 0.5)) if (5.0 + i * 0.5) > 0 else 0.0,
            "roas": 3.0 + (i * 0.1),
            "conversion_rate": ((5.0 + i * 0.5) / clicks * 100) if clicks > 0 else 0.0,
        }
        
        if platform == "tiktok":
            record["reach"] = impressions
            record["cpi"] = 2.0
            record["ad_format"] = "video"
        
        data.append(record)
    
    return data


def create_mock_audience_data(
    audience_types: List[str] = None,
    date_start: str = None,
    date_stop: str = None
) -> List[Dict[str, Any]]:
    """
    Crea datos mock de audiencias para testing.
    
    Args:
        audience_types: Tipos de audiencia
        date_start: Fecha inicio
        date_stop: Fecha fin
        
    Returns:
        Lista de datos de audiencias
    """
    if audience_types is None:
        audience_types = ["custom", "lookalike", "interest"]
    
    if date_start is None:
        date_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if date_stop is None:
        date_stop = datetime.now().strftime("%Y-%m-%d")
    
    data = []
    for i, audience_type in enumerate(audience_types):
        spend = 100.0 * (i + 1)
        conversions = 10.0 * (i + 1)
        
        data.append({
            "date_start": date_start,
            "date_stop": date_stop,
            "audience_type": audience_type,
            "spend": spend,
            "conversions": conversions,
            "revenue": spend * (2.0 + i * 0.5),
            "cpa": spend / conversions if conversions > 0 else 0.0,
            "conversion_value": (spend * (2.0 + i * 0.5)) / conversions if conversions > 0 else 0.0
        })
    
    return data


class MockClient:
    """Cliente mock para testing."""
    
    def __init__(self, platform: str = "facebook"):
        """Inicializa cliente mock."""
        self.platform = platform
        self._calls = []
    
    def get_base_url(self) -> str:
        """Retorna URL mock."""
        return f"https://api.mock-{self.platform}.com"
    
    def get_default_headers(self) -> Dict[str, str]:
        """Retorna headers mock."""
        return {"Authorization": "Bearer mock_token"}
    
    def _execute_request_with_retry(self, method: str, url: str, **kwargs) -> Any:
        """Registra llamadas mock."""
        self._calls.append({
            "method": method,
            "url": url,
            "kwargs": kwargs
        })
        
        # Retornar respuesta mock
        class MockResponse:
            def json(self):
                return {"data": [], "paging": {}}
        
        return MockResponse()
    
    def get_call_count(self) -> int:
        """Retorna número de llamadas."""
        return len(self._calls)


class MockStorage:
    """Storage mock para testing."""
    
    def __init__(self):
        """Inicializa storage mock."""
        self.saved_data: Dict[str, List[Dict[str, Any]]] = {}
        self.table_schemas: Dict[str, Dict[str, str]] = {}
    
    def ensure_table_exists(self, table_name: str, schema: Dict[str, str]) -> None:
        """Registra schema de tabla."""
        self.table_schemas[table_name] = schema
    
    def save_campaign_performance(
        self,
        data: List[Dict[str, Any]],
        table_name: str
    ) -> Dict[str, Any]:
        """Guarda datos en mock."""
        if table_name not in self.saved_data:
            self.saved_data[table_name] = []
        self.saved_data[table_name].extend(data)
        return {"saved": len(data), "errors": 0}
    
    def get_saved_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Obtiene datos guardados."""
        return self.saved_data.get(table_name, [])

