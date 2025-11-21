# Guía de Integración - Herramientas de Infraestructura

Esta guía explica cómo integrar y usar todas las herramientas de gestión de configuración y CI/CD.

## 🎯 Visión General

El proyecto integra múltiples herramientas para gestionar infraestructura de forma completa:

1. **Terraform** - Provisionamiento de infraestructura (IaC)
2. **Ansible** - Configuración de servidores (sin agentes)
3. **Salt** - Gestión de estados (escalable)
4. **Puppet** - Configuración declarativa
5. **Chef** - Gestión con recipes (Ruby DSL)
6. **Jenkins** - Automatización CI/CD

## 📋 Flujo Recomendado

### Opción 1: Terraform + Ansible (Recomendado para empezar)

```bash
# 1. Provisionar infraestructura
make tf-init
make tf-plan
make tf-apply

# 2. Exportar outputs
make tf-output

# 3. Actualizar inventario de Ansible
make ansible-update-inventory

# 4. Verificar conectividad
make ansible-ping

# 5. Configurar servidores
make ansible-playbook-k8s
make ansible-playbook-airflow
```

### Opción 2: Terraform + Salt (Para grandes flotas)

```bash
# 1. Provisionar infraestructura
make tf-apply

# 2. Exportar outputs
make tf-output

# 3. Aceptar minions en Salt master
salt-key -A -y

# 4. Verificar conectividad
make salt-test

# 5. Aplicar estados
make salt-apply
# O estado específico
make salt-state STATE=k8s.node
```

### Opción 3: Terraform + Puppet

```bash
# 1. Provisionar infraestructura
make tf-apply

# 2. Firmar certificados en Puppet master
sudo puppet cert list
sudo puppet cert sign <node-name>

# 3. Aplicar configuración
make puppet-apply
```

## 🔄 Integración Completa

### Flujo End-to-End con Make

```bash
# Todo en un comando
make infra-complete
```

Este comando ejecuta:
1. Terraform init/plan/apply
2. Exporta outputs
3. Actualiza inventario de Ansible
4. Verifica conectividad
5. Pregunta confirmación antes de configurar

### Integración con CI/CD

#### GitHub Actions

```yaml
name: Infrastructure Deployment

on:
  push:
    branches: [main]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Terraform Apply
        run: make tf-apply
      
  ansible:
    needs: terraform
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Ansible
        run: make ansible-install
      - name: Configure Servers
        run: make ansible-playbook-k8s
```

#### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Terraform') {
            steps {
                sh 'make tf-apply'
            }
        }
        stage('Ansible') {
            steps {
                sh 'make ansible-update-inventory'
                sh 'make ansible-playbook-k8s'
            }
        }
    }
}
```

## 🔧 Configuración por Entorno

### Desarrollo

```bash
# Ansible
ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml \
  -e @vars/dev.yml

# Salt
salt 'dev-*' state.apply pillar='{"environment": "dev"}'

# Puppet
puppet agent -t --environment dev
```

### Producción

```bash
# Ansible
ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml \
  -e @vars/prod.yml \
  --check  # Siempre revisar primero

# Salt
salt 'prod-*' state.apply pillar='{"environment": "prod"}'

# Puppet
puppet agent -t --environment prod
```

## 🎨 Elegir la Herramienta Correcta

### Usa Ansible si:
- ✅ Equipo pequeño-mediano (< 500 servidores)
- ✅ Prefieres no instalar agentes
- ✅ Quieres fácil de aprender
- ✅ Necesitas ad-hoc commands frecuentes

### Usa Salt si:
- ✅ Flota grande (> 1000 servidores)
- ✅ Necesitas alta performance
- ✅ Quieres sistema event-driven
- ✅ Prefieres comunicación push/pull

### Usa Puppet si:
- ✅ Modelo declarativo te gusta
- ✅ Necesitas reporting avanzado
- ✅ Ya tienes experiencia con Puppet
- ✅ Quieres módulos maduros

### Usa Chef si:
- ✅ Prefieres Ruby DSL
- ✅ Necesitas testing con Test Kitchen
- ✅ Quieres granularidad fina
- ✅ Tienes experiencia con Ruby

## 🔐 Gestión de Secretos

### Ansible Vault

```bash
# Crear archivo encriptado
ansible-vault create vars/secrets.yml

# Editar
ansible-vault edit vars/secrets.yml

# Usar en playbook
ansible-playbook playbook.yml --ask-vault-pass
```

### Salt Pillar con GPG

```yaml
# pillar/top.sls
base:
  '*':
    - secrets

# pillar/secrets.sls
secret_key: |
  -----BEGIN PGP MESSAGE-----
  ...
  -----END PGP MESSAGE-----
```

### Puppet Hiera con EYAML

```yaml
# hiera.yaml
:eyaml:
  :datadir: data
  :extension: 'yaml'
```

## 📊 Monitoreo y Reporting

### Ansible

```bash
# Verificar cambios antes de aplicar
ansible-playbook playbook.yml --check --diff

# Ejecutar con verbose
ansible-playbook playbook.yml -vvv
```

### Salt

```bash
# Ver detalles de ejecución
salt '*' state.apply --state-verbose=True

# Ver cambios propuestos
salt '*' state.show_sls k8s.node
```

### Puppet

```bash
# Ver reporte
puppet agent -t --report

# Ver catalogo
puppet agent -t --noop --graph
```

## 🚨 Troubleshooting

### Problemas Comunes

1. **Ansible: Host unreachable**
   ```bash
   # Verificar SSH
   ssh -i key.pem user@host
   
   # Verificar inventario
   ansible-inventory -i inventory/hosts.ini --list
   ```

2. **Salt: Minion no responde**
   ```bash
   # Verificar minion
   salt 'minion-id' test.ping
   
   # Ver logs
   tail -f /var/log/salt/minion
   ```

3. **Puppet: Certificate issues**
   ```bash
   # Limpiar certificado
   sudo puppet cert clean <node-name>
   
   # Regenerar
   sudo puppet cert regenerate <node-name>
   ```

## 📚 Recursos Adicionales

- [Documentación Ansible](https://docs.ansible.com/)
- [Documentación Salt](https://docs.saltproject.io/)
- [Documentación Puppet](https://puppet.com/docs/)
- [Documentación Chef](https://docs.chef.io/)
- [Documentación Jenkins](https://www.jenkins.io/doc/)

## 🎓 Ejemplos Prácticos

Ver los READMEs individuales en cada directorio:
- `infra/ansible/README.md`
- `infra/salt/README.md`
- `infra/puppet/README.md`

