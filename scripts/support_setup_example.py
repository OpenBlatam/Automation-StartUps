#!/usr/bin/env python3
"""
Script de Ejemplo para Configurar Sistema de Soporte

Este script ayuda a poblar la base de datos con datos de ejemplo:
- Agentes de soporte
- Reglas de enrutamiento
- Clientes VIP/Enterprise (opcional)

Uso:
    python support_setup_example.py
"""

import os
import sys
import psycopg2
from typing import List, Dict, Any

# Configuración de base de datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "support_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": os.getenv("DB_PORT", "5432")
}


def create_agents(conn) -> None:
    """Crea agentes de ejemplo."""
    agents = [
        {
            "agent_id": "agent-001",
            "agent_name": "María González",
            "email": "maria.gonzalez@example.com",
            "department": "technical",
            "specialties": ["technical", "billing"],
            "max_concurrent_tickets": 5
        },
        {
            "agent_id": "agent-002",
            "agent_name": "Juan Pérez",
            "email": "juan.perez@example.com",
            "department": "billing",
            "specialties": ["billing", "payment"],
            "max_concurrent_tickets": 6
        },
        {
            "agent_id": "agent-003",
            "agent_name": "Ana Martínez",
            "email": "ana.martinez@example.com",
            "department": "support",
            "specialties": ["general", "account"],
            "max_concurrent_tickets": 8
        },
        {
            "agent_id": "agent-004",
            "agent_name": "Carlos Rodríguez",
            "email": "carlos.rodriguez@example.com",
            "department": "technical",
            "specialties": ["technical", "security"],
            "max_concurrent_tickets": 5
        },
        {
            "agent_id": "agent-005",
            "agent_name": "Laura Sánchez",
            "email": "laura.sanchez@example.com",
            "department": "sales",
            "specialties": ["sales", "pricing"],
            "max_concurrent_tickets": 7
        }
    ]
    
    cur = conn.cursor()
    
    for agent in agents:
        cur.execute("""
            INSERT INTO support_agents (
                agent_id,
                agent_name,
                email,
                department,
                specialties,
                max_concurrent_tickets,
                is_available
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (agent_id) DO UPDATE SET
                agent_name = EXCLUDED.agent_name,
                email = EXCLUDED.email,
                department = EXCLUDED.department,
                specialties = EXCLUDED.specialties,
                max_concurrent_tickets = EXCLUDED.max_concurrent_tickets,
                updated_at = NOW()
        """, (
            agent["agent_id"],
            agent["agent_name"],
            agent["email"],
            agent["department"],
            agent["specialties"],
            agent["max_concurrent_tickets"],
            True
        ))
    
    conn.commit()
    cur.close()
    print(f"✅ Creados {len(agents)} agentes de soporte")


def create_routing_rules(conn) -> None:
    """Crea reglas de enrutamiento de ejemplo."""
    rules = [
        {
            "rule_name": "Billing Issues - Auto Assign",
            "priority_order": 1,
            "conditions": {"category": "billing"},
            "target_department": "billing",
            "target_specialties": ["billing"],
            "auto_assign": False,
            "is_active": True
        },
        {
            "rule_name": "Technical Critical - Auto Assign",
            "priority_order": 2,
            "conditions": {
                "priority": ["critical", "urgent"],
                "category": "technical"
            },
            "target_department": "technical",
            "target_specialties": ["technical"],
            "auto_assign": True,
            "is_active": True
        },
        {
            "rule_name": "Security Issues",
            "priority_order": 3,
            "conditions": {
                "category": "security"
            },
            "target_department": "technical",
            "target_specialties": ["security", "technical"],
            "auto_assign": True,
            "is_active": True
        },
        {
            "rule_name": "Sales Inquiries",
            "priority_order": 4,
            "conditions": {
                "category": "sales"
            },
            "target_department": "sales",
            "target_specialties": ["sales"],
            "auto_assign": False,
            "is_active": True
        },
        {
            "rule_name": "VIP Customers - High Priority",
            "priority_order": 5,
            "conditions": {
                "tags": ["vip"]
            },
            "target_department": "support",
            "target_specialties": [],
            "auto_assign": True,
            "is_active": True
        }
    ]
    
    cur = conn.cursor()
    
    for rule in rules:
        import json
        cur.execute("""
            INSERT INTO support_routing_rules (
                rule_name,
                priority_order,
                conditions,
                target_department,
                target_specialties,
                auto_assign,
                is_active
            ) VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            rule["rule_name"],
            rule["priority_order"],
            json.dumps(rule["conditions"]),
            rule["target_department"],
            rule["target_specialties"],
            rule["auto_assign"],
            rule["is_active"]
        ))
    
    conn.commit()
    cur.close()
    print(f"✅ Creadas {len(rules)} reglas de enrutamiento")


def verify_setup(conn) -> None:
    """Verifica que el setup se haya completado correctamente."""
    cur = conn.cursor()
    
    # Contar agentes
    cur.execute("SELECT COUNT(*) FROM support_agents WHERE is_available = true")
    agent_count = cur.fetchone()[0]
    
    # Contar reglas
    cur.execute("SELECT COUNT(*) FROM support_routing_rules WHERE is_active = true")
    rule_count = cur.fetchone()[0]
    
    # Contar FAQs
    cur.execute("SELECT COUNT(*) FROM support_faq_articles WHERE is_active = true")
    faq_count = cur.fetchone()[0]
    
    cur.close()
    
    print("\n📊 Resumen del Setup:")
    print(f"   - Agentes activos: {agent_count}")
    print(f"   - Reglas de enrutamiento: {rule_count}")
    print(f"   - Artículos FAQ: {faq_count}")
    
    if agent_count > 0 and rule_count > 0 and faq_count > 0:
        print("\n✅ Setup completado exitosamente!")
    else:
        print("\n⚠️  Algunos componentes no se configuraron correctamente")


def main():
    """Función principal."""
    print("🚀 Configurando Sistema de Soporte...")
    print(f"   Conectando a: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexión exitosa\n")
        
        # Crear componentes
        create_agents(conn)
        create_routing_rules(conn)
        
        # Verificar
        verify_setup(conn)
        
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

