#!/usr/bin/env python3
"""
Health Check del Sistema de Automatización de Soporte

Verifica que todos los componentes estén funcionando correctamente:
- Conexión a base de datos
- Tablas necesarias
- FAQs disponibles
- Agentes configurados
- Reglas de enrutamiento
- Integraciones externas (opcional)
"""
import os
import sys
import psycopg2
from typing import Dict, Any, List
from datetime import datetime

# Configuración
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "support_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": os.getenv("DB_PORT", "5432")
}

CHECKS = {
    "database_connection": False,
    "tables_exist": False,
    "faqs_available": False,
    "agents_configured": False,
    "routing_rules": False,
    "openai_available": False,
    "slack_available": False,
}

ERRORS = []


def check_database_connection() -> bool:
    """Verifica conexión a base de datos."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        CHECKS["database_connection"] = True
        print("✅ Conexión a base de datos: OK")
        return True
    except Exception as e:
        ERRORS.append(f"Conexión a BD: {e}")
        print(f"❌ Conexión a base de datos: FALLO - {e}")
        return False


def check_tables_exist() -> bool:
    """Verifica que las tablas necesarias existan."""
    required_tables = [
        "support_tickets",
        "support_chatbot_interactions",
        "support_faq_articles",
        "support_ticket_history",
        "support_agents",
        "support_routing_rules"
    ]
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        missing_tables = []
        for table in required_tables:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table,))
            
            if not cur.fetchone()[0]:
                missing_tables.append(table)
        
        cur.close()
        conn.close()
        
        if missing_tables:
            ERRORS.append(f"Tablas faltantes: {', '.join(missing_tables)}")
            print(f"❌ Tablas necesarias: FALLO - Faltan: {', '.join(missing_tables)}")
            return False
        else:
            CHECKS["tables_exist"] = True
            print("✅ Tablas necesarias: OK")
            return True
            
    except Exception as e:
        ERRORS.append(f"Verificación de tablas: {e}")
        print(f"❌ Tablas necesarias: FALLO - {e}")
        return False


def check_faqs_available() -> bool:
    """Verifica que haya FAQs disponibles."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) 
            FROM support_faq_articles 
            WHERE is_active = true
        """)
        
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        if count == 0:
            ERRORS.append("No hay FAQs activos en la base de datos")
            print("⚠️  FAQs disponibles: ADVERTENCIA - No hay FAQs activos")
            return False
        else:
            CHECKS["faqs_available"] = True
            print(f"✅ FAQs disponibles: OK ({count} artículos)")
            return True
            
    except Exception as e:
        ERRORS.append(f"Verificación de FAQs: {e}")
        print(f"❌ FAQs disponibles: FALLO - {e}")
        return False


def check_agents_configured() -> bool:
    """Verifica que haya agentes configurados."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) 
            FROM support_agents 
            WHERE is_available = true
        """)
        
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        if count == 0:
            ERRORS.append("No hay agentes disponibles configurados")
            print("⚠️  Agentes configurados: ADVERTENCIA - No hay agentes disponibles")
            return False
        else:
            CHECKS["agents_configured"] = True
            print(f"✅ Agentes configurados: OK ({count} agentes)")
            return True
            
    except Exception as e:
        ERRORS.append(f"Verificación de agentes: {e}")
        print(f"❌ Agentes configurados: FALLO - {e}")
        return False


def check_routing_rules() -> bool:
    """Verifica que haya reglas de enrutamiento."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) 
            FROM support_routing_rules 
            WHERE is_active = true
        """)
        
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        if count == 0:
            ERRORS.append("No hay reglas de enrutamiento activas")
            print("⚠️  Reglas de enrutamiento: ADVERTENCIA - No hay reglas activas")
            return False
        else:
            CHECKS["routing_rules"] = True
            print(f"✅ Reglas de enrutamiento: OK ({count} reglas)")
            return True
            
    except Exception as e:
        ERRORS.append(f"Verificación de reglas: {e}")
        print(f"❌ Reglas de enrutamiento: FALLO - {e}")
        return False


def check_openai_available() -> bool:
    """Verifica disponibilidad de OpenAI (opcional)."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("ℹ️  OpenAI: No configurado (opcional)")
        return True  # No es crítico
    
    try:
        import requests
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )
        
        if response.status_code == 200:
            CHECKS["openai_available"] = True
            print("✅ OpenAI: OK")
            return True
        else:
            ERRORS.append(f"OpenAI API: Status {response.status_code}")
            print(f"❌ OpenAI: FALLO - Status {response.status_code}")
            return False
            
    except Exception as e:
        ERRORS.append(f"OpenAI: {e}")
        print(f"❌ OpenAI: FALLO - {e}")
        return False


def check_slack_available() -> bool:
    """Verifica disponibilidad de Slack webhook (opcional)."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("ℹ️  Slack: No configurado (opcional)")
        return True  # No es crítico
    
    CHECKS["slack_available"] = True
    print("✅ Slack: Configurado")
    return True


def generate_report() -> Dict[str, Any]:
    """Genera reporte de health check."""
    total_checks = len(CHECKS)
    passed_checks = sum(1 for v in CHECKS.values() if v)
    critical_checks = ["database_connection", "tables_exist"]
    critical_passed = all(CHECKS[k] for k in critical_checks)
    
    status = "HEALTHY" if critical_passed and passed_checks >= total_checks * 0.8 else "UNHEALTHY"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "checks": CHECKS.copy(),
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "errors": ERRORS.copy(),
        "critical_passed": critical_passed
    }
    
    return report


def main():
    """Ejecuta todos los health checks."""
    print("🏥 Health Check del Sistema de Automatización de Soporte\n")
    print("=" * 60)
    
    # Checks críticos
    check_database_connection()
    if CHECKS["database_connection"]:
        check_tables_exist()
        if CHECKS["tables_exist"]:
            check_faqs_available()
            check_agents_configured()
            check_routing_rules()
    
    # Checks opcionales
    check_openai_available()
    check_slack_available()
    
    # Reporte
    print("\n" + "=" * 60)
    report = generate_report()
    
    print(f"\n📊 Resumen:")
    print(f"   Estado: {report['status']}")
    print(f"   Checks pasados: {report['passed_checks']}/{report['total_checks']}")
    
    if ERRORS:
        print(f"\n❌ Errores encontrados:")
        for error in ERRORS:
            print(f"   - {error}")
    
    if report["status"] == "HEALTHY":
        print("\n✅ Sistema saludable")
        sys.exit(0)
    else:
        print("\n⚠️  Sistema con problemas - revisa los errores")
        sys.exit(1)


if __name__ == "__main__":
    main()

