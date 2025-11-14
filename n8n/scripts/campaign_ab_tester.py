#!/usr/bin/env python3
"""
Campaign A/B Tester
Sistema automatizado de A/B testing para campañas
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics


class CampaignABTester:
    """
    Sistema de A/B testing para campañas
    Gestiona variaciones, asignación de usuarios y análisis de resultados
    """
    
    def __init__(self, n8n_base_url: str, api_key: str):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def create_ab_test(
        self,
        test_name: str,
        variations: List[Dict[str, Any]],
        traffic_split: Optional[Dict[str, float]] = None,
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo test A/B
        
        Args:
            test_name: Nombre del test
            variations: Lista de variaciones a testear
            traffic_split: Distribución de tráfico (default: 50/50)
            metrics: Métricas a trackear (default: ['engagement', 'conversion'])
        
        Returns:
            Dict con información del test creado
        """
        if traffic_split is None:
            # Distribución equitativa
            split = 1.0 / len(variations)
            traffic_split = {f"variant_{i+1}": split for i in range(len(variations))}
        
        if metrics is None:
            metrics = ['engagement', 'conversion']
        
        test_config = {
            "testId": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "testName": test_name,
            "variations": variations,
            "trafficSplit": traffic_split,
            "metrics": metrics,
            "status": "active",
            "createdAt": datetime.now().isoformat(),
            "results": {}
        }
        
        return test_config
    
    def assign_variant(
        self,
        test_id: str,
        user_id: str,
        test_config: Dict[str, Any]
    ) -> str:
        """
        Asigna una variante a un usuario
        
        Args:
            test_id: ID del test
            user_id: ID del usuario
            test_config: Configuración del test
        
        Returns:
            ID de la variante asignada
        """
        # Hash determinístico basado en user_id y test_id
        import hashlib
        hash_value = int(hashlib.md5(f"{test_id}_{user_id}".encode()).hexdigest(), 16)
        
        # Asignar basado en hash
        cumulative = 0
        for variant_id, split in test_config["trafficSplit"].items():
            cumulative += split
            if (hash_value % 10000) / 10000 < cumulative:
                return variant_id
        
        # Fallback a primera variante
        return list(test_config["trafficSplit"].keys())[0]
    
    def track_event(
        self,
        test_id: str,
        variant_id: str,
        user_id: str,
        event_type: str,
        event_data: Optional[Dict] = None
    ) -> None:
        """
        Trackea un evento para el test A/B
        
        Args:
            test_id: ID del test
            variant_id: ID de la variante
            user_id: ID del usuario
            event_type: Tipo de evento (engagement, conversion, etc.)
            event_data: Datos adicionales del evento
        """
        event = {
            "testId": test_id,
            "variantId": variant_id,
            "userId": user_id,
            "eventType": event_type,
            "eventData": event_data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # En producción, esto guardaría en base de datos
        # Por ahora, solo retornamos
        return event
    
    def analyze_results(
        self,
        test_id: str,
        events: List[Dict[str, Any]],
        test_config: Dict[str, Any],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Analiza resultados del test A/B
        
        Args:
            test_id: ID del test
            events: Lista de eventos trackeados
            test_config: Configuración del test
            confidence_level: Nivel de confianza (default: 95%)
        
        Returns:
            Dict con análisis completo
        """
        # Agrupar eventos por variante
        variant_stats = defaultdict(lambda: {
            "users": set(),
            "events": defaultdict(int),
            "conversions": 0
        })
        
        for event in events:
            variant_id = event["variantId"]
            user_id = event["userId"]
            event_type = event["eventType"]
            
            variant_stats[variant_id]["users"].add(user_id)
            variant_stats[variant_id]["events"][event_type] += 1
            
            if event_type == "conversion":
                variant_stats[variant_id]["conversions"] += 1
        
        # Calcular métricas por variante
        results = {}
        for variant_id, stats in variant_stats.items():
            unique_users = len(stats["users"])
            conversions = stats["conversions"]
            
            conversion_rate = conversions / unique_users if unique_users > 0 else 0
            engagement_count = stats["events"].get("engagement", 0)
            engagement_rate = engagement_count / unique_users if unique_users > 0 else 0
            
            results[variant_id] = {
                "uniqueUsers": unique_users,
                "conversions": conversions,
                "conversionRate": conversion_rate,
                "engagementCount": engagement_count,
                "engagementRate": engagement_rate,
                "events": dict(stats["events"])
            }
        
        # Determinar ganador
        winner = self._determine_winner(results, confidence_level)
        
        # Calcular significancia estadística
        significance = self._calculate_significance(results, confidence_level)
        
        return {
            "testId": test_id,
            "results": results,
            "winner": winner,
            "significance": significance,
            "confidenceLevel": confidence_level,
            "analyzedAt": datetime.now().isoformat()
        }
    
    def _determine_winner(
        self,
        results: Dict[str, Dict[str, Any]],
        confidence_level: float
    ) -> Optional[Dict[str, Any]]:
        """Determina el ganador del test"""
        if len(results) < 2:
            return None
        
        # Comparar tasas de conversión
        variants = list(results.items())
        variants.sort(key=lambda x: x[1]["conversionRate"], reverse=True)
        
        best = variants[0]
        second = variants[1] if len(variants) > 1 else None
        
        if second is None:
            return {
                "variantId": best[0],
                "conversionRate": best[1]["conversionRate"],
                "improvement": 0.0,
                "confidence": 1.0
            }
        
        improvement = ((best[1]["conversionRate"] - second[1]["conversionRate"]) 
                      / second[1]["conversionRate"] * 100) if second[1]["conversionRate"] > 0 else 0
        
        # Calcular confianza (simplificado)
        confidence = self._calculate_confidence(best[1], second[1], confidence_level)
        
        return {
            "variantId": best[0],
            "conversionRate": best[1]["conversionRate"],
            "improvement": improvement,
            "confidence": confidence,
            "isSignificant": confidence >= confidence_level
        }
    
    def _calculate_confidence(
        self,
        variant1: Dict[str, Any],
        variant2: Dict[str, Any],
        confidence_level: float
    ) -> float:
        """Calcula confianza estadística (simplificado)"""
        # En producción, usaría test estadístico real (t-test, chi-square, etc.)
        n1 = variant1["uniqueUsers"]
        n2 = variant2["uniqueUsers"]
        
        if n1 < 30 or n2 < 30:
            return 0.5  # Baja confianza con muestras pequeñas
        
        # Simulación de cálculo de confianza
        diff = abs(variant1["conversionRate"] - variant2["conversionRate"])
        
        if diff > 0.05:  # Diferencia del 5%
            return 0.9
        elif diff > 0.02:  # Diferencia del 2%
            return 0.7
        else:
            return 0.5
    
    def _calculate_significance(
        self,
        results: Dict[str, Dict[str, Any]],
        confidence_level: float
    ) -> Dict[str, Any]:
        """Calcula significancia estadística"""
        # Simplificado - en producción usaría test estadístico real
        variants = list(results.values())
        
        if len(variants) < 2:
            return {"isSignificant": False, "pValue": 1.0}
        
        # Comparar todas las variantes
        max_rate = max(v["conversionRate"] for v in variants)
        min_rate = min(v["conversionRate"] for v in variants)
        
        diff = max_rate - min_rate
        
        # Estimación simplificada de p-value
        if diff > 0.10:  # Diferencia del 10%
            p_value = 0.01
        elif diff > 0.05:  # Diferencia del 5%
            p_value = 0.05
        else:
            p_value = 0.20
        
        is_significant = p_value < (1 - confidence_level)
        
        return {
            "isSignificant": is_significant,
            "pValue": p_value,
            "difference": diff
        }
    
    def generate_report(
        self,
        analysis: Dict[str, Any],
        output_format: str = "json"
    ) -> str:
        """
        Genera reporte del test A/B
        
        Args:
            analysis: Resultados del análisis
            output_format: Formato (json, markdown, html)
        
        Returns:
            Reporte en el formato especificado
        """
        if output_format == "json":
            return json.dumps(analysis, indent=2, ensure_ascii=False)
        
        elif output_format == "markdown":
            md = f"""# Reporte de A/B Test

## Test ID: {analysis['testId']}

### Resultados por Variante

"""
            for variant_id, results in analysis["results"].items():
                md += f"""### Variante: {variant_id}

- **Usuarios únicos**: {results['uniqueUsers']:,}
- **Conversiones**: {results['conversions']:,}
- **Tasa de conversión**: {results['conversionRate']:.2%}
- **Engagement rate**: {results['engagementRate']:.2%}

"""
            
            if analysis.get("winner"):
                winner = analysis["winner"]
                md += f"""### 🏆 Ganador: {winner['variantId']}

- **Tasa de conversión**: {winner['conversionRate']:.2%}
- **Mejora**: +{winner['improvement']:.1f}%
- **Confianza**: {winner['confidence']:.1%}
- **Significativo**: {'Sí' if winner.get('isSignificant') else 'No'}

"""
            
            md += f"""### Significancia Estadística

- **Significativo**: {'Sí' if analysis['significance']['isSignificant'] else 'No'}
- **p-value**: {analysis['significance']['pValue']:.4f}
- **Diferencia**: {analysis['significance']['difference']:.2%}

---
*Generado el {analysis['analyzedAt']}*
"""
            return md
        
        else:  # html
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Reporte A/B Test - {analysis['testId']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .variant {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
        .winner {{ background: #d4edda; border-color: #28a745; }}
    </style>
</head>
<body>
    <h1>Reporte de A/B Test</h1>
    <h2>Test ID: {analysis['testId']}</h2>
    
    <h3>Resultados por Variante</h3>
"""
            for variant_id, results in analysis["results"].items():
                is_winner = analysis.get("winner", {}).get("variantId") == variant_id
                class_name = "variant winner" if is_winner else "variant"
                html += f"""
    <div class="{class_name}">
        <h4>{'🏆 ' if is_winner else ''}Variante: {variant_id}</h4>
        <ul>
            <li>Usuarios únicos: {results['uniqueUsers']:,}</li>
            <li>Conversiones: {results['conversions']:,}</li>
            <li>Tasa de conversión: {results['conversionRate']:.2%}</li>
            <li>Engagement rate: {results['engagementRate']:.2%}</li>
        </ul>
    </div>
"""
            
            html += f"""
    <h3>Significancia Estadística</h3>
    <p>Significativo: {'Sí' if analysis['significance']['isSignificant'] else 'No'}</p>
    <p>p-value: {analysis['significance']['pValue']:.4f}</p>
    
    <hr>
    <p><small>Generado el {analysis['analyzedAt']}</small></p>
</body>
</html>"""
            return html


def main():
    """Ejemplo de uso"""
    tester = CampaignABTester(
        n8n_base_url="https://your-n8n.com",
        api_key="your_api_key"
    )
    
    # Crear test A/B
    variations = [
        {"id": "variant_1", "name": "Control", "caption": "Caption original"},
        {"id": "variant_2", "name": "Variante A", "caption": "Caption con emojis 🚀"},
        {"id": "variant_3", "name": "Variante B", "caption": "Caption con urgencia ⚡"}
    ]
    
    test_config = tester.create_ab_test(
        test_name="Test de Captions",
        variations=variations,
        traffic_split={"variant_1": 0.33, "variant_2": 0.33, "variant_3": 0.34}
    )
    
    print(f"Test creado: {test_config['testId']}")
    
    # Simular eventos
    events = []
    for i in range(100):
        user_id = f"user_{i}"
        variant_id = tester.assign_variant(test_config["testId"], user_id, test_config)
        
        # Track engagement
        events.append(tester.track_event(
            test_config["testId"],
            variant_id,
            user_id,
            "engagement"
        ))
        
        # Track conversion (10% de usuarios)
        if i % 10 == 0:
            events.append(tester.track_event(
                test_config["testId"],
                variant_id,
                user_id,
                "conversion"
            ))
    
    # Analizar resultados
    analysis = tester.analyze_results(
        test_config["testId"],
        events,
        test_config
    )
    
    # Generar reporte
    report = tester.generate_report(analysis, output_format="markdown")
    print("\n" + report)


if __name__ == "__main__":
    main()



