# Salt - Gestión de Configuración basada en Estados

Salt es una herramienta alternativa a Ansible para gestión de configuración y automatización de infraestructura.

## Estructura

```
infra/salt/
├── master.conf           # Configuración del master
├── minion.conf          # Configuración de minions
├── top.sls              # Mapeo de estados a hosts
├── salt/                # Estados (states)
│   ├── k8s/
│   │   ├── node.sls
│   │   └── docker.sls
│   ├── airflow/
│   │   └── server.sls
│   └── common/
├── pillar/              # Datos sensibles y configuración
│   ├── top.sls
│   ├── k8s.sls
│   ├── airflow.sls
│   └── common.sls
├── salt/                # Estados (states)
│   ├── k8s/
│   │   ├── node.sls
│   │   └── docker.sls
│   ├── airflow/
│   │   └── server.sls
│   └── common/
│       ├── packages.sls
│       └── security.sls
└── README.md
```

## Instalación

### Master

```bash
# Ubuntu/Debian
curl -L https://bootstrap.saltproject.io | sudo sh -s -- -M

# O vía pip
pip install salt
```

### Minion

```bash
# En cada nodo a gestionar
curl -L https://bootstrap.saltproject.io | sudo sh -s -- minion
```

## Uso

### Aceptar minions

```bash
# Listar minions pendientes
salt-key -L

# Aceptar todos
salt-key -A -y

# Aceptar específico
salt-key -a minion-id -y
```

### Aplicar estados

```bash
# Aplicar estados a todos los minions
salt '*' state.apply

# Aplicar estado específico
salt '*' state.apply k8s.node

# Aplicar a grupo específico
salt 'kubernetes*' state.apply
```

### Comandos ad-hoc

```bash
# Ejecutar comando en todos los minions
salt '*' cmd.run 'uname -a'

# Verificar conectividad
salt '*' test.ping

# Obtener información del sistema
salt '*' grains.items
salt '*' disk.usage
```

### Pillar (configuración por entorno)

```bash
# Ver pillar data de un minion
salt '*' pillar.items

# Aplicar estados con pillar específico
salt '*' state.apply pillar='{"k8s_version": "1.29.0-00"}'
```

## Estados Disponibles

### k8s.node
Configura nodos Kubernetes:
- ✅ Instala paquetes requeridos (apt-transport-https, ca-certificates, etc.)
- ✅ Añade repositorio Kubernetes con detección automática de OS codename
- ✅ Instala kubelet, kubeadm, kubectl con versiones desde pillar
- ✅ Configura sysctl (bridge, ip_forward)
- ✅ Carga módulos del kernel (br_netfilter, overlay)
- ✅ Hace módulos persistentes
- ✅ Deshabilita swap
- ✅ Crea directorios necesarios

### k8s.docker
Instala y configura Docker:
- Añade repositorio oficial
- Instala docker-ce
- Inicia servicio

### airflow.server
Configura servidor Airflow:
- Crea usuario y directorios
- Instala dependencias Python
- Configura servicios systemd

### common.packages
Instala paquetes comunes:
- Lista de paquetes desde pillar
- Configurable por entorno

### common.security
Configuraciones de seguridad básicas:
- Actualización del sistema
- Configuración de firewall (ufw)
- Permisos SSH

## Pillar - Gestión de Datos

Los datos de configuración se gestionan mediante pillar:

```bash
# Ver pillar data de un minion
salt '*' pillar.items

# Ver pillar específico
salt 'kubernetes*' pillar.get k8s_version

# Aplicar estados con pillar específico
salt '*' state.apply pillar='{"k8s_version": "1.30.0-00"}'
```

### Estructura de Pillar

- `pillar/top.sls` - Mapea pillar a minions
- `pillar/k8s.sls` - Configuración de Kubernetes
- `pillar/airflow.sls` - Configuración de Airflow
- `pillar/common.sls` - Configuración común

## Integración con Terraform

```bash
# 1. Provisionar infraestructura
make tf-apply

# 2. Exportar outputs de Terraform
terraform output -json > /etc/salt/terraform-output.json

# 3. Usar pillar desde Terraform (vía ext_pillar en master.conf)
salt '*' state.apply
```

## Ventajas sobre Ansible

1. **Escalabilidad**: Mejor para grandes flotas (1000+ servidores)
2. **Performance**: Comunicación más rápida con minions persistentes
3. **Event-driven**: Sistema de eventos y reactor para automatización reactiva
4. **Granularidad**: Más control sobre estados y dependencias

## Ejemplo de Estado Personalizado

```yaml
# salt/myapp/install.sls
{% set app_version = pillar.get('myapp_version', '1.0.0') %}

myapp_package:
  pkg.installed:
    - name: myapp={{ app_version }}
    - refresh: true

myapp_config:
  file.managed:
    - name: /etc/myapp/config.conf
    - source: salt://myapp/config.conf
    - template: jinja
    - mode: 0644
    - user: root
    - group: root
    - require:
      - pkg: myapp_package

myapp_service:
  service.running:
    - name: myapp
    - enable: True
    - require:
      - file: myapp_config
```

## Mejoras Recientes

### ✨ Estados Mejorados

1. **k8s.node.sls**:
   - Detección automática de OS codename para repositorios
   - Mejor manejo de dependencias
   - Carga de módulos del kernel
   - Persistencia de configuración

2. **common.packages.sls**:
   - Instalación de paquetes comunes desde pillar
   - Configurable por entorno

3. **common.security.sls**:
   - Configuraciones básicas de seguridad
   - Firewall y actualizaciones

### 🔧 Pillar Mejorado

- Estructura organizada por componente
- Valores por defecto sensatos
- Fácil personalización por entorno

## Integración CI/CD

Salt puede ejecutarse desde Jenkins o GitHub Actions:

```bash
# En pipeline
salt 'kubernetes*' state.apply k8s.node
salt 'airflow*' state.apply airflow.server
```

