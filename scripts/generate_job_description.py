#!/usr/bin/env python3
"""
Script de ejemplo para generar descripciones de puesto usando el DAG de Airflow.

Uso:
    python scripts/generate_job_description.py --role "Gerente de Operaciones" --level Senior
"""

import argparse
import json
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from airflow.api.client.local_client import Client
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    print("⚠️  Airflow no está disponible. Este script requiere Airflow instalado.")


def generate_job_config(args):
    """Genera la configuración para el DAG basada en argumentos."""
    config = {
        "role": args.role,
    }
    
    if args.level:
        config["level"] = args.level
    
    if args.department:
        config["department"] = args.department
    
    if args.ai_experience_years:
        config["ai_experience_years"] = int(args.ai_experience_years)
    
    if args.skills:
        config["skills"] = [s.strip() for s in args.skills.split(",")]
    
    if args.preferred_skills:
        config["preferred_skills"] = [s.strip() for s in args.preferred_skills.split(",")]
    
    if args.location:
        config["location"] = args.location
    
    if args.salary_range:
        config["salary_range"] = args.salary_range
    
    return config


def trigger_dag_via_airflow(config):
    """Activa el DAG de Airflow con la configuración proporcionada."""
    if not AIRFLOW_AVAILABLE:
        print("❌ No se puede activar el DAG: Airflow no está disponible")
        return False
    
    try:
        client = Client(None, None)
        
        print(f"🚀 Activando DAG 'job_description_ai_generator'...")
        print(f"📋 Configuración: {json.dumps(config, indent=2, ensure_ascii=False)}")
        
        dag_run = client.trigger_dag(
            dag_id='job_description_ai_generator',
            conf=config,
            run_id=f"manual_{config['role'].lower().replace(' ', '_')}_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        print(f"✅ DAG activado exitosamente!")
        print(f"📊 Run ID: {dag_run.run_id}")
        print(f"🔗 Revisa el estado en la UI de Airflow")
        
        return True
        
    except Exception as e:
        print(f"❌ Error activando el DAG: {str(e)}")
        return False


def save_config_to_file(config, output_file):
    """Guarda la configuración en un archivo JSON."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Configuración guardada en: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Genera descripciones de puesto optimizadas para talento con experiencia en IA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Básico
  python scripts/generate_job_description.py --role "Gerente de Operaciones"
  
  # Completo
  python scripts/generate_job_description.py \\
    --role "Data Scientist" \\
    --level Senior \\
    --department "Data Science" \\
    --ai-experience-years 3 \\
    --skills "Python, Machine Learning, SQL" \\
    --preferred-skills "TensorFlow, PyTorch" \\
    --location "Remoto"
  
  # Solo guardar configuración (sin activar DAG)
  python scripts/generate_job_description.py \\
    --role "MLOps Engineer" \\
    --output config.json \\
    --no-trigger
        """
    )
    
    parser.add_argument(
        '--role',
        required=True,
        help='Nombre del puesto (ej: "Gerente de Operaciones")'
    )
    
    parser.add_argument(
        '--level',
        choices=['Junior', 'Mid', 'Senior', 'Lead'],
        help='Nivel del puesto'
    )
    
    parser.add_argument(
        '--department',
        help='Departamento (ej: "Operaciones", "Data Science")'
    )
    
    parser.add_argument(
        '--ai-experience-years',
        type=int,
        help='Años de experiencia requeridos en IA/ML'
    )
    
    parser.add_argument(
        '--skills',
        help='Habilidades requeridas separadas por comas (ej: "Python, ML, Airflow")'
    )
    
    parser.add_argument(
        '--preferred-skills',
        help='Habilidades preferidas separadas por comas'
    )
    
    parser.add_argument(
        '--location',
        help='Ubicación del trabajo (ej: "Remoto", "Híbrido", "Ciudad, País")'
    )
    
    parser.add_argument(
        '--salary-range',
        help='Rango salarial (ej: "Competitivo", "$80k-$120k")'
    )
    
    parser.add_argument(
        '--output',
        help='Archivo donde guardar la configuración JSON (opcional)'
    )
    
    parser.add_argument(
        '--no-trigger',
        action='store_true',
        help='No activar el DAG, solo generar la configuración'
    )
    
    args = parser.parse_args()
    
    # Generar configuración
    config = generate_job_config(args)
    
    # Guardar en archivo si se especifica
    if args.output:
        save_config_to_file(config, args.output)
    
    # Activar DAG si no se especifica --no-trigger
    if not args.no_trigger:
        if not AIRFLOW_AVAILABLE:
            print("\n💡 Tip: Guarda la configuración y actívala manualmente desde la UI de Airflow")
            if not args.output:
                save_config_to_file(config, f"job_config_{config['role'].lower().replace(' ', '_')}.json")
        else:
            success = trigger_dag_via_airflow(config)
            if not success:
                sys.exit(1)
    else:
        print("📋 Configuración generada (DAG no activado):")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        if not args.output:
            save_config_to_file(config, f"job_config_{config['role'].lower().replace(' ', '_')}.json")


if __name__ == '__main__':
    main()






