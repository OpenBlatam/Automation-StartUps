#!/usr/bin/env python3
"""
Script para limpiar runs antiguos de MLflow automáticamente.
Ejecutar periódicamente via CronJob o Airflow DAG.

Uso:
    python cleanup_old_runs.py --retention-days 90 --delete-failed
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

try:
    import mlflow
    from mlflow.tracking import MlflowClient
except ImportError:
    print("ERROR: MLflow no está instalado. Instalar con: pip install mlflow")
    sys.exit(1)


def get_mlflow_client(tracking_uri: str) -> MlflowClient:
    """Inicializa cliente de MLflow."""
    mlflow.set_tracking_uri(tracking_uri)
    return MlflowClient(tracking_uri=tracking_uri)


def list_runs_older_than(
    client: MlflowClient,
    experiment_id: str,
    cutoff_date: datetime,
    max_results: int = 1000
) -> List:
    """Lista runs más antiguos que la fecha de corte."""
    try:
        runs = client.search_runs(
            experiment_ids=[experiment_id],
            filter_string=f"start_time < '{cutoff_date.isoformat()}'",
            max_results=max_results,
            order_by=["start_time ASC"]
        )
        return runs
    except Exception as e:
        print(f"ERROR: No se pudieron obtener runs del experimento {experiment_id}: {e}")
        return []


def delete_run_safely(
    client: MlflowClient,
    run_id: str,
    delete_artifacts: bool = False
) -> bool:
    """Elimina un run de forma segura."""
    try:
        # Verificar si el run existe
        run = client.get_run(run_id)
        
        if run.info.status == "FINISHED" or run.info.status == "FAILED":
            # Listar artefactos antes de eliminar
            try:
                artifacts = client.list_artifacts(run_id)
                has_artifacts = len(list(artifacts)) > 0
            except:
                has_artifacts = False
            
            # Eliminar run
            client.delete_run(run_id)
            
            # Opcional: eliminar artefactos de S3
            if delete_artifacts and has_artifacts:
                print(f"  WARNING: Artefactos no eliminados automáticamente de S3 para run {run_id}")
                print(f"  Ejecutar manualmente si es necesario: aws s3 rm s3://bucket/mlflow/artifacts/{run_id}/ --recursive")
            
            return True
        else:
            print(f"  SKIP: Run {run_id} tiene estado {run.info.status}, no se elimina")
            return False
    except Exception as e:
        print(f"  ERROR: No se pudo eliminar run {run_id}: {e}")
        return False


def cleanup_experiment(
    client: MlflowClient,
    experiment_name: Optional[str] = None,
    experiment_id: Optional[str] = None,
    retention_days: int = 90,
    delete_failed: bool = True,
    min_runs_to_keep: int = 10,
    delete_artifacts: bool = False,
    dry_run: bool = False
) -> dict:
    """Limpia runs antiguos de un experimento."""
    stats = {
        "experiment_name": experiment_name or experiment_id,
        "runs_found": 0,
        "runs_deleted": 0,
        "runs_skipped": 0,
        "errors": 0
    }
    
    try:
        if experiment_id:
            exp = client.get_experiment(experiment_id)
        elif experiment_name:
            exp = client.get_experiment_by_name(experiment_name)
            if not exp:
                print(f"ERROR: Experimento '{experiment_name}' no encontrado")
                return stats
        else:
            print("ERROR: Debe especificar experiment_name o experiment_id")
            return stats
        
        experiment_id = exp.experiment_id
        stats["experiment_name"] = exp.name
        
        print(f"\n📊 Procesando experimento: {exp.name} (ID: {experiment_id})")
        
        # Calcular fecha de corte
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        print(f"🗓️  Fecha de corte: {cutoff_date.isoformat()} ({retention_days} días atrás)")
        
        # Obtener runs antiguos
        old_runs = list_runs_older_than(client, experiment_id, cutoff_date)
        stats["runs_found"] = len(old_runs)
        
        print(f"🔍 Encontrados {len(old_runs)} runs antiguos")
        
        if dry_run:
            print("🔍 DRY RUN: No se eliminarán runs, solo mostrar información")
        
        # Mantener al menos min_runs_to_keep
        if len(old_runs) > min_runs_to_keep:
            runs_to_delete = old_runs[:-min_runs_to_keep]  # Mantener los últimos N
            print(f"📌 Manteniendo los últimos {min_runs_to_keep} runs")
        else:
            runs_to_delete = []
            print(f"📌 Todos los runs se mantienen (hay menos de {min_runs_to_keep} runs antiguos)")
        
        # Eliminar runs
        for run in runs_to_delete:
            run_id = run.info.run_id
            status = run.info.status
            
            # Saltar runs activos
            if status == "RUNNING":
                print(f"  SKIP: Run {run_id} está corriendo")
                stats["runs_skipped"] += 1
                continue
            
            # Saltar runs fallidos si no se debe eliminar
            if status == "FAILED" and not delete_failed:
                print(f"  SKIP: Run {run_id} falló pero delete_failed=False")
                stats["runs_skipped"] += 1
                continue
            
            print(f"  {'[DRY RUN] ' if dry_run else ''}Eliminando run {run_id} (status: {status}, start: {run.info.start_time})")
            
            if not dry_run:
                if delete_run_safely(client, run_id, delete_artifacts):
                    stats["runs_deleted"] += 1
                else:
                    stats["errors"] += 1
            else:
                stats["runs_deleted"] += 1  # Contar en dry run también
        
        print(f"\n✅ Resumen:")
        print(f"   - Runs encontrados: {stats['runs_found']}")
        print(f"   - Runs eliminados: {stats['runs_deleted']}")
        print(f"   - Runs saltados: {stats['runs_skipped']}")
        print(f"   - Errores: {stats['errors']}")
        
    except Exception as e:
        print(f"ERROR: Error procesando experimento: {e}")
        stats["errors"] += 1
    
    return stats


def cleanup_all_experiments(
    client: MlflowClient,
    retention_days: int = 90,
    delete_failed: bool = True,
    min_runs_to_keep: int = 10,
    delete_artifacts: bool = False,
    dry_run: bool = False
) -> List[dict]:
    """Limpia todos los experimentos."""
    all_stats = []
    
    try:
        experiments = client.search_experiments()
        print(f"🔍 Encontrados {len(experiments)} experimentos\n")
        
        for exp in experiments:
            stats = cleanup_experiment(
                client=client,
                experiment_id=exp.experiment_id,
                retention_days=retention_days,
                delete_failed=delete_failed,
                min_runs_to_keep=min_runs_to_keep,
                delete_artifacts=delete_artifacts,
                dry_run=dry_run
            )
            all_stats.append(stats)
    
    except Exception as e:
        print(f"ERROR: Error obteniendo experimentos: {e}")
    
    # Resumen global
    total_runs_deleted = sum(s["runs_deleted"] for s in all_stats)
    total_runs_found = sum(s["runs_found"] for s in all_stats)
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN GLOBAL")
    print(f"{'='*60}")
    print(f"Experimentos procesados: {len(all_stats)}")
    print(f"Total runs encontrados: {total_runs_found}")
    print(f"Total runs eliminados: {total_runs_deleted}")
    
    return all_stats


def main():
    parser = argparse.ArgumentParser(
        description="Limpia runs antiguos de MLflow automáticamente"
    )
    parser.add_argument(
        "--tracking-uri",
        default=os.getenv("MLFLOW_TRACKING_URI", "http://mlflow.example.com"),
        help="URI del servidor MLflow (default: env MLFLOW_TRACKING_URI)"
    )
    parser.add_argument(
        "--experiment",
        help="Nombre o ID del experimento específico (opcional, limpia todos si no se especifica)"
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=90,
        help="Días de retención (default: 90)"
    )
    parser.add_argument(
        "--delete-failed",
        action="store_true",
        help="Eliminar runs fallidos también"
    )
    parser.add_argument(
        "--min-runs-to-keep",
        type=int,
        default=10,
        help="Mínimo de runs a mantener por experimento (default: 10)"
    )
    parser.add_argument(
        "--delete-artifacts",
        action="store_true",
        help="También eliminar artefactos de S3 (requiere permisos)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Modo dry-run: solo muestra qué se eliminaría sin hacer cambios"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🧹 MLflow Cleanup Script")
    print("="*60)
    print(f"Tracking URI: {args.tracking_uri}")
    print(f"Retention days: {args.retention_days}")
    print(f"Delete failed: {args.delete_failed}")
    print(f"Min runs to keep: {args.min_runs_to_keep}")
    print(f"Dry run: {args.dry_run}")
    print("="*60)
    
    client = get_mlflow_client(args.tracking_uri)
    
    if args.experiment:
        cleanup_experiment(
            client=client,
            experiment_name=args.experiment,
            retention_days=args.retention_days,
            delete_failed=args.delete_failed,
            min_runs_to_keep=args.min_runs_to_keep,
            delete_artifacts=args.delete_artifacts,
            dry_run=args.dry_run
        )
    else:
        cleanup_all_experiments(
            client=client,
            retention_days=args.retention_days,
            delete_failed=args.delete_failed,
            min_runs_to_keep=args.min_runs_to_keep,
            delete_artifacts=args.delete_artifacts,
            dry_run=args.dry_run
        )


if __name__ == "__main__":
    main()

