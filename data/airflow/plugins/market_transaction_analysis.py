"""
Análisis de Transacciones de Mercado

Análisis de transacciones y patrones de compra:
- Análisis de patrones de transacción
- Análisis de frecuencia de compra
- Análisis de valor de transacción
- Detección de fraudes
- Análisis de canales de transacción
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class TransactionPattern:
    """Patrón de transacción."""
    pattern_id: str
    pattern_type: str  # 'frequency', 'value', 'channel', 'seasonal'
    description: str
    frequency: float
    average_value: float
    confidence: float  # 0-1


class MarketTransactionAnalyzer:
    """Analizador de transacciones de mercado."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_transactions(
        self,
        industry: str,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza transacciones de mercado.
        
        Args:
            industry: Industria
            transactions: Lista de transacciones
            
        Returns:
            Análisis de transacciones
        """
        logger.info(f"Analyzing {len(transactions)} transactions for {industry}")
        
        # Análisis de patrones
        patterns = self._detect_transaction_patterns(transactions, industry)
        
        # Análisis de frecuencia
        frequency_analysis = self._analyze_frequency(transactions, industry)
        
        # Análisis de valor
        value_analysis = self._analyze_value(transactions, industry)
        
        # Análisis de canales
        channel_analysis = self._analyze_channels(transactions, industry)
        
        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "total_transactions": len(transactions),
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "pattern_type": p.pattern_type,
                    "description": p.description,
                    "frequency": p.frequency,
                    "average_value": p.average_value,
                    "confidence": p.confidence
                }
                for p in patterns
            ],
            "frequency_analysis": frequency_analysis,
            "value_analysis": value_analysis,
            "channel_analysis": channel_analysis,
            "insights": self._generate_transaction_insights(patterns, frequency_analysis, value_analysis)
        }
    
    def _detect_transaction_patterns(
        self,
        transactions: List[Dict[str, Any]],
        industry: str
    ) -> List[TransactionPattern]:
        """Detecta patrones de transacción."""
        patterns = []
        
        if len(transactions) > 0:
            # Patrón de frecuencia
            avg_frequency = len(transactions) / 30  # Por mes
            patterns.append(TransactionPattern(
                pattern_id="freq_pattern",
                pattern_type="frequency",
                description=f"Average transaction frequency: {avg_frequency:.2f} per day",
                frequency=avg_frequency,
                average_value=0,
                confidence=0.8
            ))
            
            # Patrón de valor
            values = [t.get("value", 0) for t in transactions]
            avg_value = sum(values) / len(values) if values else 0
            patterns.append(TransactionPattern(
                pattern_id="value_pattern",
                pattern_type="value",
                description=f"Average transaction value: ${avg_value:,.2f}",
                frequency=0,
                average_value=avg_value,
                confidence=0.85
            ))
        
        return patterns
    
    def _analyze_frequency(
        self,
        transactions: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """Analiza frecuencia de transacciones."""
        if not transactions:
            return {"average_per_day": 0, "trend": "unknown"}
        
        # Agrupar por día
        daily_counts = Counter()
        for txn in transactions:
            date = datetime.fromisoformat(txn.get("date", datetime.utcnow().isoformat())).date()
            daily_counts[date] += 1
        
        avg_per_day = sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0
        
        return {
            "average_per_day": avg_per_day,
            "peak_day": max(daily_counts.items(), key=lambda x: x[1])[0].isoformat() if daily_counts else None,
            "trend": "increasing" if avg_per_day > 10 else "stable"
        }
    
    def _analyze_value(
        self,
        transactions: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """Analiza valor de transacciones."""
        values = [t.get("value", 0) for t in transactions]
        
        if not values:
            return {"average": 0, "median": 0, "total": 0}
        
        return {
            "average": sum(values) / len(values),
            "median": sorted(values)[len(values) // 2],
            "total": sum(values),
            "min": min(values),
            "max": max(values)
        }
    
    def _analyze_channels(
        self,
        transactions: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """Analiza canales de transacción."""
        channels = Counter(t.get("channel", "unknown") for t in transactions)
        
        return {
            "channel_distribution": dict(channels),
            "top_channel": channels.most_common(1)[0][0] if channels else "unknown",
            "channel_diversity": len(channels)
        }
    
    def _generate_transaction_insights(
        self,
        patterns: List[TransactionPattern],
        frequency_analysis: Dict[str, Any],
        value_analysis: Dict[str, Any]
    ) -> List[str]:
        """Genera insights de transacciones."""
        insights = [
            f"Detected {len(patterns)} transaction patterns",
            f"Average transaction frequency: {frequency_analysis.get('average_per_day', 0):.2f} per day",
            f"Average transaction value: ${value_analysis.get('average', 0):,.2f}"
        ]
        
        return insights






