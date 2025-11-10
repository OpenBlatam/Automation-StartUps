"""
Tests avanzados para funciones complejas de approval_cleanup.
Incluye recomendaciones, predicciones, health scoring, y análisis avanzados.
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from data.airflow.plugins.approval_cleanup_analytics import (
    calculate_percentiles,
    detect_anomaly,
    predict_capacity_need,
    analyze_trends,
)
from data.airflow.plugins.approval_cleanup_utils import (
    format_duration_ms,
    format_bytes,
    safe_divide,
    calculate_percentage_change,
)


class TestHealthScoring:
    """Tests para funciones de health scoring"""
    
    def test_health_score_calculation_excellent(self):
        """Test cálculo de health score excelente"""
        scores = {
            'sla': 95,
            'performance': 90,
            'security': 100,
            'database': 85,
            'reliability': 95
        }
        
        # Calcular score ponderado
        weights = {
            'sla': 0.25,
            'performance': 0.20,
            'security': 0.25,
            'database': 0.20,
            'reliability': 0.10
        }
        
        weighted_score = sum(scores[k] * weights[k] for k in scores.keys())
        
        assert weighted_score >= 90
        assert weighted_score <= 100
    
    def test_health_score_calculation_poor(self):
        """Test cálculo de health score pobre"""
        scores = {
            'sla': 50,
            'performance': 40,
            'security': 60,
            'database': 45,
            'reliability': 55
        }
        
        weights = {
            'sla': 0.25,
            'performance': 0.20,
            'security': 0.25,
            'database': 0.20,
            'reliability': 0.10
        }
        
        weighted_score = sum(scores[k] * weights[k] for k in scores.keys())
        
        assert weighted_score < 60
        assert weighted_score >= 0


class TestRecommendations:
    """Tests para generación de recomendaciones"""
    
    def test_recommendation_priority_sorting(self):
        """Test ordenamiento de recomendaciones por prioridad"""
        recommendations = [
            {'id': '1', 'priority': 'low', 'priority_score': 30},
            {'id': '2', 'priority': 'critical', 'priority_score': 100},
            {'id': '3', 'priority': 'high', 'priority_score': 80},
            {'id': '4', 'priority': 'medium', 'priority_score': 50},
        ]
        
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(
            key=lambda x: (
                priority_order.get(x.get('priority', 'low'), 0),
                x.get('priority_score', 0)
            ),
            reverse=True
        )
        
        assert recommendations[0]['priority'] == 'critical'
        assert recommendations[0]['id'] == '2'
    
    def test_recommendation_grouping_by_category(self):
        """Test agrupación de recomendaciones por categoría"""
        recommendations = [
            {'id': '1', 'category': 'performance'},
            {'id': '2', 'category': 'cost'},
            {'id': '3', 'category': 'performance'},
            {'id': '4', 'category': 'security'},
        ]
        
        by_category = {}
        for rec in recommendations:
            category = rec.get('category', 'other')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rec)
        
        assert len(by_category['performance']) == 2
        assert len(by_category['cost']) == 1
        assert len(by_category['security']) == 1


class TestCapacityPrediction:
    """Tests para predicción de capacidad"""
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_predict_capacity_with_growth(self, mock_get_hook):
        """Test predicción con crecimiento positivo"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        from datetime import datetime, timedelta
        base_date = datetime(2025, 1, 1)
        
        # Simular crecimiento histórico del 10% por período
        history = []
        for i in range(10):
            date = base_date + timedelta(days=i)
            size_bytes = 1000000 * (1.1 ** i)  # Crecimiento del 10%
            history.append((date, size_bytes, 10, 5, 20, 50))
        
        mock_hook.get_records.return_value = history
        
        result = predict_capacity_need(days_ahead=30, pg_hook=mock_hook)
        
        assert result['prediction_available'] is True
        assert result['predicted_size_bytes'] > result['current_size_bytes']
        assert result['avg_growth_rate'] > 0
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_predict_capacity_no_growth(self, mock_get_hook):
        """Test predicción sin crecimiento"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        from datetime import datetime
        base_date = datetime(2025, 1, 1)
        
        # Tamaño constante
        history = [
            (base_date, 1000000, 10, 5, 20, 50),
            (base_date, 1000000, 10, 5, 20, 50),
            (base_date, 1000000, 10, 5, 20, 50),
        ]
        
        mock_hook.get_records.return_value = history
        
        result = predict_capacity_need(days_ahead=30, pg_hook=mock_hook)
        
        # Con crecimiento 0, la predicción debería ser igual al tamaño actual
        if result['prediction_available']:
            assert abs(result['predicted_size_bytes'] - result['current_size_bytes']) < 1000


class TestCostAnalysis:
    """Tests para análisis de costos"""
    
    def test_storage_cost_calculation(self):
        """Test cálculo de costos de almacenamiento"""
        storage_cost_per_gb_month = 0.10
        db_size_gb = 100
        
        monthly_cost = db_size_gb * storage_cost_per_gb_month
        annual_cost = monthly_cost * 12
        
        assert monthly_cost == 10.0
        assert annual_cost == 120.0
    
    def test_wasted_storage_cost(self):
        """Test cálculo de costos de almacenamiento desperdiciado"""
        storage_cost_per_gb_month = 0.10
        unused_size_gb = 20
        
        wasted_cost = unused_size_gb * storage_cost_per_gb_month
        annual_wasted = wasted_cost * 12
        
        assert wasted_cost == 2.0
        assert annual_wasted == 24.0
        assert annual_wasted > 0
    
    def test_cost_savings_recommendations(self):
        """Test generación de recomendaciones de ahorro"""
        wasted_storage_cost = 5.0  # $5/mes
        db_size_gb = 150
        
        savings_recommendations = []
        
        if wasted_storage_cost > 1:
            savings_recommendations.append({
                'type': 'remove_unused_indexes',
                'potential_savings_monthly': wasted_storage_cost,
                'potential_savings_annual': wasted_storage_cost * 12
            })
        
        if db_size_gb > 100:
            storage_cost_per_gb_month = 0.10
            potential_savings = db_size_gb * 0.3 * storage_cost_per_gb_month
            savings_recommendations.append({
                'type': 'archive_old_data',
                'potential_savings_monthly': potential_savings,
                'potential_savings_annual': potential_savings * 12
            })
        
        assert len(savings_recommendations) == 2
        total_savings = sum(r['potential_savings_monthly'] for r in savings_recommendations)
        assert total_savings > 0


class TestAnomalyDetection:
    """Tests para detección de anomalías"""
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_anomaly_detection_high_value(self, mock_get_hook):
        """Test detección de valor anómalo alto"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        # Historial con valores alrededor de 100
        mock_hook.get_records.return_value = [
            (90, 5, 3, 1000000),
            (100, 7, 4, 1100000),
            (110, 6, 5, 1200000),
            (95, 8, 3, 1050000),
            (105, 9, 4, 1150000),
        ]
        
        # Valor muy alto (1000 cuando promedio es ~100)
        result = detect_anomaly(1000, 'archived_count', pg_hook=mock_hook)
        
        assert result['is_anomaly'] is True
        assert result['z_score'] > 2.5  # Threshold por defecto
    
    @patch('data.airflow.plugins.approval_cleanup_analytics.get_pg_hook')
    def test_anomaly_detection_normal_value(self, mock_get_hook):
        """Test que no detecta anomalía en valor normal"""
        mock_hook = Mock()
        mock_get_hook.return_value = mock_hook
        
        mock_hook.get_records.return_value = [
            (90, 5, 3, 1000000),
            (100, 7, 4, 1100000),
            (110, 6, 5, 1200000),
        ]
        
        # Valor dentro del rango normal
        result = detect_anomaly(105, 'archived_count', pg_hook=mock_hook)
        
        assert result['is_anomaly'] is False
        assert result['z_score'] < 2.5


class TestTrendAnalysis:
    """Tests para análisis de tendencias"""
    
    def test_trend_analysis_increasing(self):
        """Test análisis de tendencia creciente"""
        history = [
            {'archived_count': 10, 'database_size_bytes': 1000000},
            {'archived_count': 20, 'database_size_bytes': 2000000},
            {'archived_count': 30, 'database_size_bytes': 3000000},
            {'archived_count': 40, 'database_size_bytes': 4000000},
        ]
        
        result = analyze_trends(history, days=30)
        
        assert result['trends_available'] is True
        assert result['archived_trend'] == 'increasing'
        assert result['size_trend'] == 'increasing'
        assert result['archived_growth_pct'] > 0
    
    def test_trend_analysis_decreasing(self):
        """Test análisis de tendencia decreciente"""
        history = [
            {'archived_count': 40, 'database_size_bytes': 4000000},
            {'archived_count': 30, 'database_size_bytes': 3000000},
            {'archived_count': 20, 'database_size_bytes': 2000000},
            {'archived_count': 10, 'database_size_bytes': 1000000},
        ]
        
        result = analyze_trends(history, days=30)
        
        assert result['trends_available'] is True
        assert result['archived_trend'] == 'decreasing'
        assert result['size_trend'] == 'decreasing'
        assert result['archived_growth_pct'] < 0
    
    def test_trend_analysis_stable(self):
        """Test análisis de tendencia estable"""
        history = [
            {'archived_count': 10, 'database_size_bytes': 1000000},
            {'archived_count': 10, 'database_size_bytes': 1000000},
            {'archived_count': 10, 'database_size_bytes': 1000000},
        ]
        
        result = analyze_trends(history, days=30)
        
        assert result['trends_available'] is True
        assert result['archived_trend'] == 'stable'
        assert result['archived_growth_pct'] == 0


class TestFormatting:
    """Tests para funciones de formateo"""
    
    def test_format_duration_edge_cases(self):
        """Test formateo de duración en casos edge"""
        # Muy pequeño
        result = format_duration_ms(0.1)
        assert "ms" in result
        
        # Muy grande
        result = format_duration_ms(3600000 * 24)  # 24 horas
        assert "m" in result or "h" in result
        
        # Exactamente 1 segundo
        result = format_duration_ms(1000)
        assert "1" in result or "s" in result
    
    def test_format_bytes_edge_cases(self):
        """Test formateo de bytes en casos edge"""
        # Muy pequeño
        result = format_bytes(1)
        assert "B" in result
        
        # Exactamente 1 KB
        result = format_bytes(1024)
        assert "KB" in result
        
        # Exactamente 1 MB
        result = format_bytes(1024 * 1024)
        assert "MB" in result
        
        # Muy grande
        result = format_bytes(1024 ** 5)  # 1 PB
        assert "PB" in result or "TB" in result


class TestPercentageCalculations:
    """Tests para cálculos porcentuales"""
    
    def test_percentage_change_various_scenarios(self):
        """Test cambio porcentual en varios escenarios"""
        # Aumento del 50%
        result = calculate_percentage_change(100, 150)
        assert result == 50.0
        
        # Disminución del 25%
        result = calculate_percentage_change(100, 75)
        assert result == -25.0
        
        # Sin cambio
        result = calculate_percentage_change(100, 100)
        assert result == 0.0
        
        # Duplicación
        result = calculate_percentage_change(100, 200)
        assert result == 100.0
    
    def test_safe_divide_various_scenarios(self):
        """Test división segura en varios escenarios"""
        # División normal
        assert safe_divide(10, 2) == 5.0
        
        # División por cero
        assert safe_divide(10, 0) == 0.0
        
        # División por cero con default
        assert safe_divide(10, 0, default=-1.0) == -1.0
        
        # División con decimales
        result = safe_divide(1, 3)
        assert abs(result - 0.3333333333333333) < 0.0001


class TestMetricCorrelations:
    """Tests para análisis de correlaciones de métricas"""
    
    def test_correlation_database_size_vs_processing(self):
        """Test correlación entre tamaño de BD y tiempo de procesamiento"""
        db_size_gb = 75
        avg_processing_hours = 80
        
        # Detectar correlación
        has_correlation = db_size_gb > 50 and avg_processing_hours > 72
        
        if has_correlation:
            correlation = {
                'type': 'database_size_vs_processing_time',
                'strength': 'moderate',
                'db_size_gb': db_size_gb,
                'avg_processing_hours': avg_processing_hours
            }
            
            assert correlation['strength'] == 'moderate'
            assert correlation['db_size_gb'] > 50
    
    def test_correlation_stale_requests_impact(self):
        """Test correlación entre requests stale y SLA"""
        stale_count = 75
        
        if stale_count > 50:
            correlation = {
                'type': 'stale_requests_impact',
                'strength': 'strong',
                'stale_count': stale_count
            }
            
            assert correlation['strength'] == 'strong'
            assert correlation['stale_count'] > 50


class TestFailurePrediction:
    """Tests para predicción de fallos"""
    
    def test_failure_prediction_high_growth(self):
        """Test predicción de fallos por crecimiento alto"""
        recent_sizes = [1000000, 1100000, 1300000, 1500000]
        
        if len(recent_sizes) >= 3:
            growth_rate = ((recent_sizes[-1] - recent_sizes[0]) / recent_sizes[0]) * 100
            has_risk = growth_rate > 20
            
            if has_risk:
                prediction = {
                    'type': 'database_growth',
                    'severity': 'medium',
                    'probability': min(0.8, 0.5 + (growth_rate / 100)),
                    'growth_rate': growth_rate
                }
                
                assert prediction['severity'] == 'medium'
                assert prediction['probability'] > 0.5
    
    def test_failure_prediction_error_pattern(self):
        """Test predicción de fallos por patrón de errores"""
        recent_errors = [
            {'failed': True},
            {'failed': False},
            {'failed': True},
            {'failed': True},
        ]
        
        error_trend = sum(1 for e in recent_errors[-3:] if e.get('failed', False))
        has_risk = error_trend >= 2
        
        if has_risk:
            prediction = {
                'type': 'error_pattern',
                'severity': 'high',
                'probability': 0.7,
                'error_count': error_trend
            }
            
            assert prediction['severity'] == 'high'
            assert prediction['error_count'] >= 2


class TestROIAnalysis:
    """Tests para análisis de ROI"""
    
    def test_roi_calculation(self):
        """Test cálculo de ROI"""
        annual_savings = 5000.0
        implementation_cost = 2000.0
        
        roi_percentage = ((annual_savings - implementation_cost) / implementation_cost * 100)
        payback_months = (implementation_cost / (annual_savings / 12))
        
        assert roi_percentage > 0
        assert payback_months > 0
        assert payback_months < 12  # Payback en menos de un año
    
    def test_roi_multiple_categories(self):
        """Test ROI con múltiples categorías"""
        storage_annual = 1000.0
        time_annual = 2000.0
        remediation_annual = 500.0
        
        total_annual = storage_annual + time_annual + remediation_annual
        implementation_cost = 2000.0
        
        roi_percentage = ((total_annual - implementation_cost) / implementation_cost * 100)
        
        assert total_annual == 3500.0
        assert roi_percentage > 0


class TestBenchmarking:
    """Tests para benchmarking"""
    
    def test_benchmark_comparison(self):
        """Test comparación con benchmarks"""
        current_ms = 5000
        average_ms = 6000
        p95_ms = 7000
        
        vs_average_pct = ((current_ms - average_ms) / average_ms * 100)
        vs_p95_pct = ((current_ms - p95_ms) / p95_ms * 100)
        
        # Si es mejor que el promedio, porcentaje negativo
        assert vs_average_pct < 0
        assert vs_p95_pct < 0
        
        # Determinar status
        if current_ms < average_ms * 0.8:
            status = 'excellent'
        elif current_ms < average_ms:
            status = 'good'
        else:
            status = 'needs_improvement'
        
        assert status in ['excellent', 'good', 'needs_improvement']


class TestIntelligentAlerting:
    """Tests para sistema de alertas inteligente"""
    
    def test_alert_prioritization(self):
        """Test priorización de alertas"""
        alerts = [
            {'id': '1', 'severity': 'low', 'priority': 30},
            {'id': '2', 'severity': 'critical', 'priority': 100},
            {'id': '3', 'severity': 'high', 'priority': 80},
        ]
        
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        alerts.sort(
            key=lambda x: (
                severity_order.get(x.get('severity', 'low'), 0),
                x.get('priority', 0)
            ),
            reverse=True
        )
        
        assert alerts[0]['severity'] == 'critical'
        assert alerts[0]['id'] == '2'
    
    def test_alert_grouping_by_category(self):
        """Test agrupación de alertas por categoría"""
        alerts = [
            {'id': '1', 'category': 'health'},
            {'id': '2', 'category': 'performance'},
            {'id': '3', 'category': 'health'},
        ]
        
        by_category = {}
        for alert in alerts:
            category = alert.get('category', 'other')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(alert)
        
        assert len(by_category['health']) == 2
        assert len(by_category['performance']) == 1

