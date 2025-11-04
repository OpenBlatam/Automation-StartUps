#!/usr/bin/env python3
"""
Script para actualizar el inventario de Ansible desde outputs de Terraform.
Lee terraform-output.json y genera un inventory actualizado.
"""

import json
import sys
from pathlib import Path

def load_terraform_output(tf_output_file: str) -> dict:
    """Carga outputs de Terraform desde archivo JSON."""
    try:
        with open(tf_output_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró {tf_output_file}")
        print("Ejecuta primero: terraform output -json > terraform-output.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        sys.exit(1)

def generate_inventory(tf_output: dict, inventory_path: str) -> None:
    """Genera inventory de Ansible desde outputs de Terraform."""
    
    inventory_content = []
    inventory_content.append("[kubernetes_masters]")
    
    # Extraer IPs de masters (asumiendo estructura común)
    if 'k8s_master_ips' in tf_output.get('value', {}):
        master_ips = tf_output['value']['k8s_master_ips']
        if isinstance(master_ips, list):
            for idx, ip in enumerate(master_ips, 1):
                inventory_content.append(f"k8s-master-{idx} ansible_host={ip} ansible_user=ubuntu")
    
    inventory_content.append("\n[kubernetes_workers]")
    
    # Extraer IPs de workers
    if 'k8s_worker_ips' in tf_output.get('value', {}):
        worker_ips = tf_output['value']['k8s_worker_ips']
        if isinstance(worker_ips, list):
            for idx, ip in enumerate(worker_ips, 1):
                inventory_content.append(f"k8s-worker-{idx} ansible_host={ip} ansible_user=ubuntu")
    
    inventory_content.append("\n[kubernetes:children]")
    inventory_content.append("kubernetes_masters")
    inventory_content.append("kubernetes_workers")
    
    inventory_content.append("\n[airflow]")
    if 'airflow_ip' in tf_output.get('value', {}):
        airflow_ip = tf_output['value']['airflow_ip']
        inventory_content.append(f"airflow-1 ansible_host={airflow_ip} ansible_user=ubuntu")
    
    inventory_content.append("\n[all:vars]")
    inventory_content.append("ansible_python_interpreter=/usr/bin/python3")
    inventory_content.append("cluster_name=biz-automation-dev")
    inventory_content.append("environment=dev")
    
    # Escribir inventory
    with open(inventory_path, 'w') as f:
        f.write('\n'.join(inventory_content))
    
    print(f"✅ Inventory actualizado en {inventory_path}")

def main():
    script_dir = Path(__file__).parent.parent
    tf_output_file = script_dir.parent / "terraform" / "terraform-output.json"
    inventory_file = script_dir / "inventory" / "hosts.ini"
    
    if not tf_output_file.exists():
        print(f"⚠️  No se encontró {tf_output_file}")
        print("💡 Ejecuta: cd infra/terraform && terraform output -json > terraform-output.json")
        sys.exit(1)
    
    tf_output = load_terraform_output(str(tf_output_file))
    generate_inventory(tf_output, str(inventory_file))
    print("✨ Listo para usar con Ansible")

if __name__ == "__main__":
    main()


