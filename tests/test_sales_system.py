#!/usr/bin/env python3
"""
Tests automatizados para el sistema de automatización de ventas.
Valida funcionalidad de componentes principales.
"""

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Dict, Any


# Configuración de test
TEST_DB_CONN = os.getenv("TEST_SALES_DB_CONN", "postgresql://test:test@localhost/test_db")


@pytest.fixture
def db_connection():
    """Fixture para conexión a base de datos de test."""
    conn = psycopg2.connect(TEST_DB_CONN)
    yield conn
    conn.close()


class TestSchema:
    """Tests del schema de base de datos."""
    
    def test_tables_exist(self, db_connection):
        """Verifica que todas las tablas existan."""
        required_tables = [
            'lead_score_history',
            'sales_pipeline',
            'sales_followup_tasks',
            'sales_campaigns',
            'sales_campaign_executions',
            'sales_campaign_events'
        ]
        
        with db_connection.cursor() as cur:
            for table in required_tables:
                cur.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = %s
                """, (table,))
                assert cur.fetchone()[0] > 0, f"Tabla {table} no existe"
    
    def test_views_exist(self, db_connection):
        """Verifica que las vistas existan."""
        required_views = [
            'v_sales_dashboard',
            'v_leads_requires_attention',
            'v_sales_rep_performance'
        ]
        
        with db_connection.cursor() as cur:
            for view in required_views:
                cur.execute("""
                    SELECT COUNT(*) FROM information_schema.views 
                    WHERE table_name = %s
                """, (view,))
                assert cur.fetchone()[0] > 0, f"Vista {view} no existe"
    
    def test_functions_exist(self, db_connection):
        """Verifica que las funciones existan."""
        required_functions = [
            'calculate_lead_score',
            'auto_assign_sales_rep',
            'get_top_opportunities'
        ]
        
        with db_connection.cursor() as cur:
            for func in required_functions:
                cur.execute("""
                    SELECT COUNT(*) FROM pg_proc 
                    WHERE proname = %s
                """, (func,))
                assert cur.fetchone()[0] > 0, f"Función {func} no existe"


class TestScoringFunction:
    """Tests de la función de scoring."""
    
    def test_calculate_lead_score_basic(self, db_connection):
        """Test de scoring básico."""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT calculate_lead_score(
                    'test_lead_1',
                    0, 0, 0,  -- engagement
                    true, true, true,  -- contact info
                    5, 2,  -- source, utm
                    5  -- days
                )
            """)
            score = cur.fetchone()[0]
            assert 20 <= score <= 100, f"Score fuera de rango: {score}"
    
    def test_calculate_lead_score_with_engagement(self, db_connection):
        """Test de scoring con engagement."""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT calculate_lead_score(
                    'test_lead_2',
                    2, 3, 5,  -- replies, clicks, opens
                    true, true, true,
                    5, 2,
                    5
                )
            """)
            score = cur.fetchone()[0]
            assert score >= 50, f"Score con engagement debería ser >= 50: {score}"
    
    def test_calculate_lead_score_with_advanced(self, db_connection):
        """Test de scoring con factores avanzados."""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT calculate_lead_score(
                    'test_lead_3',
                    1, 2, 3,
                    true, true, true,
                    5, 2,
                    5,
                    'example.edu',  -- company domain
                    true,  -- website visited
                    true,  -- demo requested
                    true   -- pricing page viewed
                )
            """)
            score = cur.fetchone()[0]
            assert score >= 70, f"Score con factores avanzados debería ser >= 70: {score}"


class TestAutoAssignFunction:
    """Tests de la función de auto-asignación."""
    
    def test_auto_assign_returns_email(self, db_connection):
        """Verifica que la función retorna un email."""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT auto_assign_sales_rep('test_lead_assign')
            """)
            result = cur.fetchone()[0]
            assert result is not None, "Función debería retornar un email"
            assert '@' in result, "Resultado debería ser un email válido"


class TestViews:
    """Tests de vistas."""
    
    def test_dashboard_view(self, db_connection):
        """Test de vista de dashboard."""
        with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) FROM v_sales_dashboard")
            count = cur.fetchone()[0]
            assert count >= 0, "Vista debería retornar resultados"
    
    def test_leads_attention_view(self, db_connection):
        """Test de vista de leads que requieren atención."""
        with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) FROM v_leads_requires_attention")
            count = cur.fetchone()[0]
            assert count >= 0, "Vista debería retornar resultados"
    
    def test_rep_performance_view(self, db_connection):
        """Test de vista de performance de vendedores."""
        with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) FROM v_sales_rep_performance")
            count = cur.fetchone()[0]
            assert count >= 0, "Vista debería retornar resultados"


class TestDataIntegrity:
    """Tests de integridad de datos."""
    
    def test_no_orphan_tasks(self, db_connection):
        """Verifica que no haya tareas huérfanas."""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM sales_followup_tasks t
                LEFT JOIN sales_pipeline p ON t.pipeline_id = p.id
                WHERE p.id IS NULL
            """)
            orphan_count = cur.fetchone()[0]
            assert orphan_count == 0, f"Encontradas {orphan_count} tareas huérfanas"
    
    def test_pipeline_has_valid_emails(self, db_connection):
        """Verifica que leads en pipeline tengan emails válidos."""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM sales_pipeline
                WHERE email IS NULL OR email = '' OR email NOT LIKE '%@%'
            """)
            invalid_count = cur.fetchone()[0]
            assert invalid_count == 0, f"Encontrados {invalid_count} leads con emails inválidos"
    
    def test_campaigns_have_steps(self, db_connection):
        """Verifica que campañas activas tengan pasos."""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM sales_campaigns
                WHERE enabled = true
                AND (steps_config IS NULL OR jsonb_array_length(steps_config) = 0)
            """)
            invalid_count = cur.fetchone()[0]
            assert invalid_count == 0, f"Encontradas {invalid_count} campañas sin pasos"


class TestPerformance:
    """Tests de performance."""
    
    def test_dashboard_query_performance(self, db_connection):
        """Verifica que la vista de dashboard sea rápida."""
        import time
        
        with db_connection.cursor() as cur:
            start = time.time()
            cur.execute("SELECT COUNT(*) FROM v_sales_dashboard")
            cur.fetchone()
            elapsed = time.time() - start
            
            assert elapsed < 1.0, f"Query de dashboard toma {elapsed:.2f}s (debería ser < 1s)"
    
    def test_indexes_exist(self, db_connection):
        """Verifica que índices importantes existan."""
        important_indexes = [
            'idx_pipeline_stage_priority_score',
            'idx_pipeline_next_followup',
            'idx_tasks_overdue'
        ]
        
        with db_connection.cursor() as cur:
            for idx in important_indexes:
                cur.execute("""
                    SELECT COUNT(*) FROM pg_indexes 
                    WHERE indexname = %s
                """, (idx,))
                assert cur.fetchone()[0] > 0, f"Índice {idx} no existe"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


