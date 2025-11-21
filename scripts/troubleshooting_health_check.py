"""
Health Check Avanzado para Sistema de Troubleshooting
Verifica todos los componentes del sistema
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import psycopg2
import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "integrations"))

from support_troubleshooting_agent import TroubleshootingAgent


class TroubleshootingHealthCheck:
    """Health check completo del sistema"""
    
    def __init__(self, db_url: str = None, api_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        self.api_url = api_url or os.getenv("API_URL", "http://localhost:3000")
        self.checks: List[Dict] = []
    
    def run_all_checks(self) -> Dict:
        """Ejecuta todos los health checks"""
        self.checks = []
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # Check 1: Base de datos
        db_check = self.check_database()
        results["checks"]["database"] = db_check
        self.checks.append(db_check)
        
        # Check 2: Agente Python
        agent_check = self.check_agent()
        results["checks"]["agent"] = agent_check
        self.checks.append(agent_check)
        
        # Check 3: Base de conocimiento
        kb_check = self.check_knowledge_base()
        results["checks"]["knowledge_base"] = kb_check
        self.checks.append(kb_check)
        
        # Check 4: API REST
        api_check = self.check_api()
        results["checks"]["api"] = api_check
        self.checks.append(api_check)
        
        # Check 5: Vistas materializadas
        views_check = self.check_materialized_views()
        results["checks"]["materialized_views"] = views_check
        self.checks.append(views_check)
        
        # Check 6: Configuración
        config_check = self.check_configuration()
        results["checks"]["configuration"] = config_check
        self.checks.append(config_check)
        
        # Determinar estado general
        failed_checks = [c for c in self.checks if c["status"] == "unhealthy"]
        if failed_checks:
            results["overall_status"] = "unhealthy"
        elif any(c["status"] == "degraded" for c in self.checks):
            results["overall_status"] = "degraded"
        
        results["summary"] = {
            "total_checks": len(self.checks),
            "healthy": len([c for c in self.checks if c["status"] == "healthy"]),
            "degraded": len([c for c in self.checks if c["status"] == "degraded"]),
            "unhealthy": len(failed_checks)
        }
        
        return results
    
    def check_database(self) -> Dict:
        """Verifica conexión y estado de BD"""
        check = {
            "name": "database",
            "status": "unhealthy",
            "message": "",
            "details": {}
        }
        
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Verificar tablas principales
            tables = [
                "support_troubleshooting_sessions",
                "support_troubleshooting_attempts",
                "support_troubleshooting_feedback"
            ]
            
            missing_tables = []
            for table in tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                if not cursor.fetchone()[0]:
                    missing_tables.append(table)
            
            if missing_tables:
                check["status"] = "unhealthy"
                check["message"] = f"Tablas faltantes: {', '.join(missing_tables)}"
            else:
                # Verificar sesiones activas
                cursor.execute("""
                    SELECT COUNT(*) FROM support_troubleshooting_sessions
                    WHERE status IN ('started', 'in_progress')
                """)
                active_sessions = cursor.fetchone()[0]
                
                check["status"] = "healthy"
                check["message"] = "Base de datos conectada y funcionando"
                check["details"] = {
                    "active_sessions": active_sessions,
                    "tables_ok": True
                }
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            check["status"] = "unhealthy"
            check["message"] = f"Error conectando a BD: {str(e)}"
        
        return check
    
    def check_agent(self) -> Dict:
        """Verifica que el agente funcione correctamente"""
        check = {
            "name": "agent",
            "status": "unhealthy",
            "message": "",
            "details": {}
        }
        
        try:
            agent = TroubleshootingAgent()
            
            # Verificar que puede detectar problemas
            test_problem = "No puedo instalar el software"
            detected = agent.detect_problem(test_problem)
            
            if detected:
                check["status"] = "healthy"
                check["message"] = "Agente funcionando correctamente"
                check["details"] = {
                    "problems_in_kb": len(agent.knowledge_base),
                    "detection_working": True
                }
            else:
                check["status"] = "degraded"
                check["message"] = "Agente funciona pero no detectó problema de prueba"
            
        except Exception as e:
            check["status"] = "unhealthy"
            check["message"] = f"Error en agente: {str(e)}"
        
        return check
    
    def check_knowledge_base(self) -> Dict:
        """Verifica estado de la base de conocimiento"""
        check = {
            "name": "knowledge_base",
            "status": "unhealthy",
            "message": "",
            "details": {}
        }
        
        try:
            kb_path = Path(__file__).parent.parent / "data" / "integrations" / "support_troubleshooting_kb.json"
            
            if not kb_path.exists():
                check["status"] = "unhealthy"
                check["message"] = "Archivo de KB no encontrado"
                return check
            
            with open(kb_path, 'r') as f:
                kb = json.load(f)
            
            if len(kb) == 0:
                check["status"] = "unhealthy"
                check["message"] = "KB vacía"
            elif len(kb) < 3:
                check["status"] = "degraded"
                check["message"] = f"KB tiene solo {len(kb)} problemas (recomendado: 5+)"
            else:
                check["status"] = "healthy"
                check["message"] = f"KB tiene {len(kb)} problemas"
            
            check["details"] = {
                "problem_count": len(kb),
                "problems": list(kb.keys())
            }
            
        except Exception as e:
            check["status"] = "unhealthy"
            check["message"] = f"Error leyendo KB: {str(e)}"
        
        return check
    
    def check_api(self) -> Dict:
        """Verifica que la API REST responda"""
        check = {
            "name": "api",
            "status": "unhealthy",
            "message": "",
            "details": {}
        }
        
        try:
            response = requests.get(
                f"{self.api_url}/api/support/troubleshooting/realtime",
                timeout=5
            )
            
            if response.status_code == 200:
                check["status"] = "healthy"
                check["message"] = "API respondiendo correctamente"
                check["details"] = {
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            else:
                check["status"] = "degraded"
                check["message"] = f"API responde con código {response.status_code}"
                
        except requests.exceptions.Timeout:
            check["status"] = "unhealthy"
            check["message"] = "API timeout"
        except requests.exceptions.ConnectionError:
            check["status"] = "unhealthy"
            check["message"] = "No se puede conectar a la API"
        except Exception as e:
            check["status"] = "unhealthy"
            check["message"] = f"Error verificando API: {str(e)}"
        
        return check
    
    def check_materialized_views(self) -> Dict:
        """Verifica estado de vistas materializadas"""
        check = {
            "name": "materialized_views",
            "status": "unhealthy",
            "message": "",
            "details": {}
        }
        
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Verificar vistas existentes
            cursor.execute("""
                SELECT matviewname 
                FROM pg_matviews 
                WHERE schemaname = 'public' 
                AND matviewname LIKE 'mv_%troubleshooting%'
            """)
            views = [row[0] for row in cursor.fetchall()]
            
            if not views:
                check["status"] = "degraded"
                check["message"] = "No hay vistas materializadas"
            else:
                # Verificar última actualización
                cursor.execute("""
                    SELECT 
                        matviewname,
                        pg_size_pretty(pg_total_relation_size('public.' || matviewname)) as size
                    FROM pg_matviews 
                    WHERE schemaname = 'public' 
                    AND matviewname LIKE 'mv_%troubleshooting%'
                """)
                view_info = {row[0]: row[1] for row in cursor.fetchall()}
                
                check["status"] = "healthy"
                check["message"] = f"{len(views)} vistas materializadas encontradas"
                check["details"] = {
                    "view_count": len(views),
                    "views": view_info
                }
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            check["status"] = "unhealthy"
            check["message"] = f"Error verificando vistas: {str(e)}"
        
        return check
    
    def check_configuration(self) -> Dict:
        """Verifica configuración del sistema"""
        check = {
            "name": "configuration",
            "status": "healthy",
            "message": "",
            "details": {}
        }
        
        required_env_vars = ["DATABASE_URL"]
        optional_env_vars = ["OPENAI_API_KEY", "KESTRA_WEBHOOK_URL", "SLACK_WEBHOOK_URL"]
        
        missing_required = []
        missing_optional = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        for var in optional_env_vars:
            if not os.getenv(var):
                missing_optional.append(var)
        
        if missing_required:
            check["status"] = "unhealthy"
            check["message"] = f"Variables requeridas faltantes: {', '.join(missing_required)}"
        elif missing_optional:
            check["status"] = "degraded"
            check["message"] = f"Algunas variables opcionales faltantes: {', '.join(missing_optional)}"
        else:
            check["message"] = "Configuración completa"
        
        check["details"] = {
            "required_vars": {var: bool(os.getenv(var)) for var in required_env_vars},
            "optional_vars": {var: bool(os.getenv(var)) for var in optional_env_vars}
        }
        
        return check
    
    def get_health_summary(self) -> str:
        """Obtiene resumen legible del health check"""
        results = self.run_all_checks()
        
        summary = []
        summary.append(f"🏥 Health Check - {results['overall_status'].upper()}")
        summary.append(f"Timestamp: {results['timestamp']}")
        summary.append("")
        summary.append("Componentes:")
        
        for check_name, check_result in results["checks"].items():
            status_icon = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌"
            }.get(check_result["status"], "❓")
            
            summary.append(f"  {status_icon} {check_name}: {check_result['message']}")
        
        summary.append("")
        summary.append(f"Resumen: {results['summary']['healthy']} healthy, "
                      f"{results['summary']['degraded']} degraded, "
                      f"{results['summary']['unhealthy']} unhealthy")
        
        return "\n".join(summary)


if __name__ == "__main__":
    import os
    
    health_check = TroubleshootingHealthCheck()
    results = health_check.run_all_checks()
    
    print(json.dumps(results, indent=2))
    print("\n" + health_check.get_health_summary())



