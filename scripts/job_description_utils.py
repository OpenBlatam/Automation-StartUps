#!/usr/bin/env python3
"""
Utilidades para el sistema de descripciones de puesto.

Funcionalidades:
- Generar descripción con template de industria
- Optimizar descripción existente
- Analizar performance de variantes
- Listar templates disponibles
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from airflow.api.client.local_client import Client
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    print("⚠️  Airflow no está disponible. Este script requiere Airflow instalado.")


def generate_with_industry_template(industry: str, role: str, level: str = "Senior"):
    """Genera una descripción usando un template de industria."""
    if not AIRFLOW_AVAILABLE:
        print("❌ Airflow no está disponible")
        return False
    
    try:
        client = Client(None, None)
        
        # Paso 1: Cargar template
        print(f"📋 Cargando template para industria: {industry}")
        template_config = {
            "industry": industry,
            "role": role,
            "level": level
        }
        
        template_run = client.trigger_dag(
            dag_id='job_description_templates',
            conf=template_config
        )
        print(f"✅ Template cargado: {template_run.run_id}")
        
        # Paso 2: Generar descripción usando el template
        print(f"🚀 Generando descripción...")
        description_config = {
            "role": role,
            "level": level,
            "industry": industry,
            "use_industry_template": True
        }
        
        desc_run = client.trigger_dag(
            dag_id='job_description_ai_generator',
            conf=description_config
        )
        print(f"✅ Descripción generada: {desc_run.run_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def optimize_existing(job_description_id: int):
    """Optimiza una descripción existente."""
    if not AIRFLOW_AVAILABLE:
        print("❌ Airflow no está disponible")
        return False
    
    try:
        client = Client(None, None)
        
        print(f"🔍 Analizando descripción {job_description_id}...")
        config = {
            "job_description_id": job_description_id
        }
        
        run = client.trigger_dag(
            dag_id='job_description_optimizer',
            conf=config
        )
        
        print(f"✅ Análisis iniciado: {run.run_id}")
        print("📊 El DAG ejecutará:")
        print("  - Análisis de sentimiento")
        print("  - Análisis de keywords")
        print("  - Generación de recomendaciones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def ab_test(job_description_id: int, num_variants: int = 3):
    """Inicia A/B testing de una descripción."""
    if not AIRFLOW_AVAILABLE:
        print("❌ Airflow no está disponible")
        return False
    
    try:
        client = Client(None, None)
        
        print(f"🧪 Iniciando A/B testing para descripción {job_description_id}...")
        config = {
            "job_description_id": job_description_id,
            "num_variants": num_variants
        }
        
        run = client.trigger_dag(
            dag_id='job_description_optimizer',
            conf=config
        )
        
        print(f"✅ A/B testing iniciado: {run.run_id}")
        print(f"📊 Se generarán {num_variants} variantes con diferentes enfoques")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def list_industries():
    """Lista las industrias disponibles."""
    industries = [
        "fintech",
        "healthcare",
        "ecommerce",
        "saas",
        "consulting",
        "startup"
    ]
    
    print("🏭 Industrias disponibles:")
    for industry in industries:
        print(f"  - {industry}")
    
    return industries


def main():
    parser = argparse.ArgumentParser(
        description='Utilidades para el sistema de descripciones de puesto',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Generar con template de industria
  python scripts/job_description_utils.py generate --industry fintech --role "ML Engineer"
  
  # Optimizar descripción existente
  python scripts/job_description_utils.py optimize --id 123
  
  # A/B testing
  python scripts/job_description_utils.py ab-test --id 123 --variants 3
  
  # Listar industrias
  python scripts/job_description_utils.py list-industries
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando: generate
    gen_parser = subparsers.add_parser('generate', help='Generar descripción con template de industria')
    gen_parser.add_argument('--industry', required=True, help='Industria (fintech, healthcare, etc.)')
    gen_parser.add_argument('--role', required=True, help='Rol del puesto')
    gen_parser.add_argument('--level', default='Senior', help='Nivel (Junior, Mid, Senior)')
    
    # Comando: optimize
    opt_parser = subparsers.add_parser('optimize', help='Optimizar descripción existente')
    opt_parser.add_argument('--id', type=int, required=True, help='ID de la descripción')
    
    # Comando: ab-test
    ab_parser = subparsers.add_parser('ab-test', help='Iniciar A/B testing')
    ab_parser.add_argument('--id', type=int, required=True, help='ID de la descripción')
    ab_parser.add_argument('--variants', type=int, default=3, help='Número de variantes (default: 3)')
    
    # Comando: list-industries
    subparsers.add_parser('list-industries', help='Listar industrias disponibles')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'generate':
        success = generate_with_industry_template(
            args.industry,
            args.role,
            args.level
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'optimize':
        success = optimize_existing(args.id)
        sys.exit(0 if success else 1)
    
    elif args.command == 'ab-test':
        success = ab_test(args.id, args.variants)
        sys.exit(0 if success else 1)
    
    elif args.command == 'list-industries':
        list_industries()
        sys.exit(0)


if __name__ == '__main__':
    main()






