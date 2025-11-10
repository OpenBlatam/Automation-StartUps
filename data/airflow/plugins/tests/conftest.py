"""
Pytest fixtures para tests de approval_cleanup.
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta


@pytest.fixture
def mock_pg_hook():
    """Fixture para mock de PostgresHook"""
    mock_hook = Mock()
    mock_conn = Mock()
    mock_cursor = Mock()
    
    mock_hook.get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.description = None
    mock_cursor.rowcount = 0
    
    return mock_hook


@pytest.fixture
def sample_history_data():
    """Fixture con datos de historial de ejemplo"""
    base_date = datetime(2025, 1, 1)
    return [
        {
            'id': i,
            'cleanup_date': base_date + timedelta(days=i),
            'archived_count': 10 + i * 5,
            'deleted_count': 5 + i * 2,
            'notifications_deleted': 3 + i,
            'database_size_bytes': 1000000 + i * 100000,
            'total_pending': 20 + i * 3,
            'total_completed': 50 + i * 10,
            'execution_duration_ms': 1500.0 + i * 100,
            'dry_run': False
        }
        for i in range(10)
    ]


@pytest.fixture
def sample_cleanup_data():
    """Fixture con datos de cleanup de ejemplo"""
    return {
        'archived_count': 100,
        'deleted_count': 50,
        'notifications_deleted': 25,
        'stale_count': 10,
        'database_size_bytes': 5000000,
        'total_pending': 30,
        'total_completed': 200,
        'indexes_optimized': 5,
        'views_refreshed': 2,
        'execution_duration_ms': 3000.0,
        'dry_run': False,
        'notes': 'Test cleanup run'
    }


@pytest.fixture
def sample_request_ids():
    """Fixture con lista de IDs de requests de ejemplo"""
    return list(range(1, 101))  # 100 IDs


@pytest.fixture
def sample_table_sizes():
    """Fixture con tamaños de tablas de ejemplo"""
    return [
        {
            'schema': 'public',
            'table': 'approval_requests',
            'size_pretty': '500 MB',
            'total_bytes': 524288000,
            'table_bytes': 400000000,
            'indexes_bytes': 124288000
        },
        {
            'schema': 'public',
            'table': 'approval_notifications',
            'size_pretty': '100 MB',
            'total_bytes': 104857600,
            'table_bytes': 80000000,
            'indexes_bytes': 24857600
        },
    ]


@pytest.fixture
def sample_request_counts():
    """Fixture con conteos de requests por status"""
    return {
        'pending': 30,
        'completed': 150,
        'rejected': 20,
        'approved': 100,
    }


@pytest.fixture
def sample_health_scores():
    """Fixture con health scores de ejemplo"""
    return {
        'overall_score': 85.5,
        'status': 'good',
        'status_emoji': '🟡',
        'scores': {
            'sla': 90,
            'performance': 85,
            'security': 95,
            'database': 80,
            'reliability': 90
        },
        'weights': {
            'sla': 0.25,
            'performance': 0.20,
            'security': 0.25,
            'database': 0.20,
            'reliability': 0.10
        }
    }


@pytest.fixture
def sample_sla_metrics():
    """Fixture con métricas de SLA de ejemplo"""
    return {
        'approved_within_sla': 90,
        'approved_outside_sla': 10,
        'rejected_within_sla': 15,
        'rejected_outside_sla': 5,
        'pending_over_sla': 5,
        'total_completed': 120,
        'approval_sla_percentage': 90.0,
        'rejection_sla_percentage': 75.0,
        'overall_sla_percentage': 87.5,
        'sla_met': True
    }


@pytest.fixture
def sample_bottlenecks():
    """Fixture con bottlenecks de ejemplo"""
    return {
        'bottlenecks': [
            {
                'type': 'query_performance',
                'severity': 'high',
                'description': 'Slow queries detected',
                'impact': 'high',
                'recommendations': ['Add indexes', 'Optimize queries']
            },
            {
                'type': 'connection_pool',
                'severity': 'medium',
                'description': 'Connection pool exhausted',
                'impact': 'medium',
                'recommendations': ['Increase pool size']
            }
        ],
        'high_severity': [
            {
                'type': 'query_performance',
                'severity': 'high'
            }
        ],
        'bottleneck_count': 2,
        'high_severity_count': 1
    }


@pytest.fixture
def sample_cost_analysis():
    """Fixture con análisis de costos de ejemplo"""
    return {
        'storage': {
            'size_gb': 50.0,
            'cost_per_gb_month': 0.10,
            'monthly_cost': 5.0,
            'annual_cost': 60.0
        },
        'wasted_storage': {
            'size_gb': 5.0,
            'monthly_cost': 0.5,
            'annual_cost': 6.0,
            'percentage_of_total': 10.0
        },
        'processing': {
            'active_connections': 10,
            'cost_per_connection_month': 0.05,
            'monthly_cost': 0.5,
            'annual_cost': 6.0
        },
        'total': {
            'monthly_cost': 6.0,
            'annual_cost': 72.0
        },
        'savings_recommendations': [
            {
                'type': 'remove_unused_indexes',
                'potential_savings_monthly': 0.5,
                'potential_savings_annual': 6.0
            }
        ],
        'total_potential_savings_monthly': 0.5
    }


@pytest.fixture
def sample_recommendations():
    """Fixture con recomendaciones de ejemplo"""
    return {
        'recommendations': [
            {
                'id': '1',
                'title': 'Improve Query Performance',
                'priority': 'high',
                'category': 'performance',
                'impact': 'high',
                'effort': 'medium',
                'estimated_improvement': '30% faster queries'
            },
            {
                'id': '2',
                'title': 'Optimize Storage Costs',
                'priority': 'medium',
                'category': 'cost',
                'impact': 'medium',
                'effort': 'low',
                'estimated_improvement': '$50 annual savings'
            }
        ],
        'recommendation_count': 2,
        'critical_count': 0,
        'high_priority_count': 1,
        'top_recommendations': [
            {
                'id': '1',
                'title': 'Improve Query Performance'
            }
        ]
    }


@pytest.fixture
def sample_anomaly_data():
    """Fixture con datos de anomalía de ejemplo"""
    return {
        'is_anomaly': True,
        'z_score': 3.5,
        'mean': 100.0,
        'std': 15.0,
        'threshold': 2.5,
        'historical_values_count': 10,
        'reason': 'calculated'
    }


@pytest.fixture
def sample_trend_data():
    """Fixture con datos de tendencia de ejemplo"""
    return {
        'trends_available': True,
        'days_analyzed': 30,
        'data_points': 10,
        'archived_trend': 'increasing',
        'deleted_trend': 'increasing',
        'size_trend': 'increasing',
        'avg_archived_per_run': 35.0,
        'avg_deleted_per_run': 15.0,
        'archived_growth_pct': 50.0,
        'size_growth_pct': 30.0
    }

