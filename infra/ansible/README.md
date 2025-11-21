# Ansible - Gestión de Configuración

Ansible se integra con Terraform para gestionar la configuración de servidores después del provisionamiento inicial.

## Estructura

```
infra/ansible/
├── ansible.cfg              # Configuración principal
├── inventory/               # Inventario de hosts
│   └── hosts.ini
├── playbooks/              # Playbooks principales
│   ├── k8s-node-setup.yml
│   ├── airflow-server-setup.yml
│   └── complete-infra-setup.yml
├── group_vars/             # Variables por grupo
│   ├── kubernetes.yml
│   └── airflow.yml
├── vars/                   # Variables por entorno
│   ├── dev.yml
│   ├── stg.yml
│   └── prod.yml
├── roles/                  # Roles reutilizables (opcional)
├── templates/              # Plantillas Jinja2
├── scripts/                # Scripts de integración
│   ├── update-inventory-from-terraform.py
│   └── validate-terraform-outputs.sh
├── requirements.yml        # Dependencias (colecciones y roles)
├── .ansible-lint.yml       # Configuración de linting
└── README.md
```

## Instalación

```bash
# Instalar Ansible
make ansible-install

# O manualmente
pip install ansible ansible-lint

# Instalar colecciones y roles
ansible-galaxy install -r requirements.yml
```

## Uso

### Validar conectividad

```bash
make ansible-ping
# O
ansible all -i inventory/hosts.ini -m ping
```

### Actualizar inventario desde Terraform

```bash
# 1. Generar outputs de Terraform
cd infra/terraform
terraform output -json > terraform-output.json

# 2. Actualizar inventario automáticamente
make ansible-update-inventory
# O
cd infra/ansible && python3 scripts/update-inventory-from-terraform.py
```

### Validar outputs de Terraform

```bash
make ansible-validate-terraform
```

### Ejecutar playbooks

```bash
# Configurar nodos Kubernetes
make ansible-playbook-k8s
# O con variables específicas
ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml \
  -e @vars/dev.yml

# Configurar servidor Airflow
make ansible-playbook-airflow

# Setup completo
ansible-playbook -i inventory/hosts.ini playbooks/complete-infra-setup.yml \
  -e @vars/prod.yml
```

### Usar tags para ejecutar tareas específicas

```bash
# Solo instalar paquetes
ansible-playbook playbooks/k8s-node-setup.yml --tags packages

# Solo configuración de red
ansible-playbook playbooks/k8s-node-setup.yml --tags networking

# Solo Kubernetes
ansible-playbook playbooks/k8s-node-setup.yml --tags kubernetes
```

### Modo check (dry-run)

```bash
ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml --check
```

## Integración con Terraform

Flujo completo de integración:

```bash
# 1. Provisionar infraestructura
cd infra/terraform
terraform init
terraform plan
terraform apply

# 2. Exportar outputs
terraform output -json > terraform-output.json

# 3. Validar outputs
cd ../ansible
make ansible-validate-terraform

# 4. Actualizar inventario dinámicamente
make ansible-update-inventory

# 5. Configurar servidores
make ansible-playbook-k8s
make ansible-playbook-airflow
```

## Playbooks Disponibles

### 1. k8s-node-setup.yml
Configura nodos Kubernetes (masters y workers):
- ✅ Validación de OS y kernel
- ✅ Instala containerd, kubelet, kubeadm, kubectl
- ✅ Configura sysctl y módulos del kernel
- ✅ Prepara el sistema para unirse al cluster
- ✅ Tags: packages, networking, kubernetes, common

### 2. airflow-server-setup.yml
Configura servidor Airflow:
- ✅ Crea usuario y directorios
- ✅ Instala Python y dependencias
- ✅ Configura entorno virtual
- ✅ Configura servicios systemd (webserver y scheduler)

### 3. complete-infra-setup.yml
Playbook maestro que orquesta el setup completo:
- ✅ Setup común (paquetes)
- ✅ Setup de Kubernetes si aplica
- ✅ Setup de Airflow si aplica
- ✅ Ejecución secuencial para evitar conflictos

## Variables

Las variables se organizan por jerarquía:

1. **vars/** - Variables por entorno (dev, stg, prod)
2. **group_vars/** - Variables por grupo de hosts (kubernetes, airflow)
3. **host_vars/** - Variables por host específico (opcional)
4. Línea de comandos con `-e`

### Ejemplo de uso de variables

```bash
# Usar variables de entorno dev
ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml \
  -e @vars/dev.yml

# Sobrescribir variable específica
ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml \
  -e @vars/prod.yml \
  -e kubernetes_version=1.30.0-00
```

## Buenas Prácticas

1. ✅ **Usar roles** para funcionalidad reutilizable
2. ✅ **Separar variables** por entorno
3. ✅ **Usar tags** para ejecutar tareas específicas
4. ✅ **Validar playbooks** con `--check` antes de ejecutar
5. ✅ **Usar Vault** para secretos sensibles (ansible-vault)
6. ✅ **Idempotencia** - Los playbooks deben poder ejecutarse múltiples veces
7. ✅ **Validaciones** - Verificar precondiciones antes de ejecutar

## Linting

```bash
# Lint playbooks
make ansible-lint
# O
ansible-lint playbooks/*.yml
```

## Troubleshooting

### Error: "Host key checking failed"

Solución: Ya está deshabilitado en `ansible.cfg` (`host_key_checking = False`)

### Error: "No route to host"

```bash
# Verificar conectividad
ansible all -i inventory/hosts.ini -m ping -v

# Verificar que las IPs son correctas
ansible-inventory -i inventory/hosts.ini --list
```

### Error: "Permission denied"

```bash
# Usar --ask-become-pass si necesitas sudo
ansible-playbook -i inventory/hosts.ini playbook.yml --ask-become-pass

# O configurar SSH keys correctamente
ssh-copy-id user@host
```

## Integración CI/CD

Ansible puede ejecutarse desde Jenkins o GitHub Actions:

```yaml
# .github/workflows/ansible.yml
- name: Run Ansible
  run: |
    cd infra/ansible
    ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml
```

## Referencias

- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Ansible Galaxy](https://galaxy.ansible.com/)
