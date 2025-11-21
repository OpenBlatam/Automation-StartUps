#!/bin/bash
# Script de inicio rápido para Ansible

set -euo pipefail

echo "🚀 Iniciando setup rápido con Ansible..."

# Verificar que Terraform ha generado outputs
if [[ ! -f "../terraform/terraform-output.json" ]]; then
    echo "❌ Error: No se encontró terraform-output.json"
    echo "💡 Ejecuta primero: cd ../terraform && terraform output -json > terraform-output.json"
    exit 1
fi

# Actualizar inventario
echo "📋 Actualizando inventario desde Terraform..."
python3 scripts/update-inventory-from-terraform.py

# Verificar conectividad
echo "🔍 Verificando conectividad..."
ansible all -i inventory/hosts.ini -m ping

# Preguntar qué configurar
echo ""
echo "¿Qué deseas configurar?"
echo "1) Nodos Kubernetes"
echo "2) Servidor Airflow"
echo "3) Ambos"
read -p "Opción [1-3]: " option

case $option in
    1)
        echo "⚙️  Configurando nodos Kubernetes..."
        ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml
        ;;
    2)
        echo "⚙️  Configurando servidor Airflow..."
        ansible-playbook -i inventory/hosts.ini playbooks/airflow-server-setup.yml
        ;;
    3)
        echo "⚙️  Configurando todo..."
        ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml
        ansible-playbook -i inventory/hosts.ini playbooks/airflow-server-setup.yml
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo "✅ Setup completado!"

