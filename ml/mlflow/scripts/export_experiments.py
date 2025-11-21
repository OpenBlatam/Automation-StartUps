#!/usr/bin/env python3
"""
Script para exportar experimentos de MLflow a JSON/CSV para backup o migración.

Uso:
    python export_experiments.py --output-dir ./exports
    python export_experiments.py --experiment "mi-experimento" --format csv
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    import pandas as pd
except ImportError:
    print("ERROR: MLflow y pandas no están instalados. Instalar con: pip install mlflow pandas")
    sys.exit(1)


def export_experiment_to_json(
    client: MlflowClient,
    experiment_id: str,
    output_dir: Path
) -> str:
    """Exporta un experimento completo a JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        exp = client.get_experiment(experiment_id)
        runs = client.search_runs(
            experiment_ids=[experiment_id],
            max_results=10000  # Ajustar según necesidad
        )
        
        experiment_data = {
            "experiment": {
                "experiment_id": exp.experiment_id,
                "name": exp.name,
                "artifact_location": exp.artifact_location,
                "lifecycle_stage": exp.lifecycle_stage,
                "tags": exp.tags,
                "exported_at": datetime.now().isoformat()
            },
            "runs": []
        }
        
        for run in runs:
            run_data = {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "status": run.info.status,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "user_id": run.info.user_id,
                "lifecycle_stage": run.info.lifecycle_stage,
                "params": dict(run.data.params),
                "metrics": dict(run.data.metrics),
                "tags": dict(run.data.tags),
                "artifacts": []
            }
            
            # Listar artefactos (sin descargar)
            try:
                artifacts = client.list_artifacts(run.info.run_id)
                run_data["artifacts"] = [
                    {
                        "path": artifact.path,
                        "is_dir": artifact.is_dir,
                        "file_size": artifact.file_size if hasattr(artifact, 'file_size') else None
                    }
                    for artifact in artifacts
                ]
            except:
                pass
            
            experiment_data["runs"].append(run_data)
        
        # Guardar JSON
        filename = f"{exp.name.replace(' ', '_')}_{exp.experiment_id}.json"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Exportado experimento '{exp.name}' a {output_path}")
        print(f"   - {len(experiment_data['runs'])} runs exportados")
        
        return str(output_path)
    
    except Exception as e:
        print(f"ERROR: Error exportando experimento {experiment_id}: {e}")
        return ""


def export_experiment_to_csv(
    client: MlflowClient,
    experiment_id: str,
    output_dir: Path
) -> str:
    """Exporta un experimento a CSV (solo runs y métricas)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        exp = client.get_experiment(experiment_id)
        runs = client.search_runs(
            experiment_ids=[experiment_id],
            max_results=10000
        )
        
        # Preparar datos para DataFrame
        rows = []
        for run in runs:
            row = {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "status": run.info.status,
                "start_time": datetime.fromtimestamp(run.info.start_time / 1000).isoformat() if run.info.start_time else None,
                "end_time": datetime.fromtimestamp(run.info.end_time / 1000).isoformat() if run.info.end_time else None,
                "user_id": run.info.user_id,
            }
            
            # Agregar parámetros como columnas
            for key, value in run.data.params.items():
                row[f"param_{key}"] = value
            
            # Agregar métricas como columnas
            for key, value in run.data.metrics.items():
                row[f"metric_{key}"] = value
            
            # Agregar tags como columnas
            for key, value in run.data.tags.items():
                row[f"tag_{key}"] = value
            
            rows.append(row)
        
        # Crear DataFrame y guardar
        df = pd.DataFrame(rows)
        
        filename = f"{exp.name.replace(' ', '_')}_{exp.experiment_id}.csv"
        output_path = output_dir / filename
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"✅ Exportado experimento '{exp.name}' a {output_path}")
        print(f"   - {len(rows)} runs exportados")
        print(f"   - {len(df.columns)} columnas")
        
        return str(output_path)
    
    except Exception as e:
        print(f"ERROR: Error exportando experimento {experiment_id}: {e}")
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="Exporta experimentos de MLflow a JSON o CSV"
    )
    parser.add_argument(
        "--tracking-uri",
        default=os.getenv("MLFLOW_TRACKING_URI", "http://mlflow.example.com"),
        help="URI del servidor MLflow"
    )
    parser.add_argument(
        "--experiment",
        help="Nombre o ID del experimento específico (opcional, exporta todos si no se especifica)"
    )
    parser.add_argument(
        "--output-dir",
        default="./mlflow_exports",
        help="Directorio de salida (default: ./mlflow_exports)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "both"],
        default="json",
        help="Formato de exportación (default: json)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("📤 MLflow Export Script")
    print("="*60)
    print(f"Tracking URI: {args.tracking_uri}")
    print(f"Output directory: {args.output_dir}")
    print(f"Format: {args.format}")
    print("="*60)
    
    mlflow.set_tracking_uri(args.tracking_uri)
    client = MlflowClient(tracking_uri=args.tracking_uri)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if args.experiment:
            # Exportar experimento específico
            exp = client.get_experiment_by_name(args.experiment)
            if not exp:
                # Intentar como ID
                exp = client.get_experiment(args.experiment)
            
            if args.format in ["json", "both"]:
                export_experiment_to_json(client, exp.experiment_id, output_dir)
            
            if args.format in ["csv", "both"]:
                export_experiment_to_csv(client, exp.experiment_id, output_dir)
        else:
            # Exportar todos los experimentos
            experiments = client.search_experiments()
            print(f"\n🔍 Encontrados {len(experiments)} experimentos\n")
            
            for exp in experiments:
                if args.format in ["json", "both"]:
                    export_experiment_to_json(client, exp.experiment_id, output_dir)
                
                if args.format in ["csv", "both"]:
                    export_experiment_to_csv(client, exp.experiment_id, output_dir)
        
        print(f"\n✅ Exportación completada. Archivos en: {output_dir.absolute()}")
    
    except Exception as e:
        print(f"ERROR: Error durante exportación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

