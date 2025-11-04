# Puppet - Gestión de Configuración Declarativa

Puppet utiliza un modelo declarativo para gestionar la configuración de sistemas.

## Estructura

```
infra/puppet/
├── manifests/
│   ├── site.pp              # Configuración principal
│   └── nodes/               # Definiciones de nodos
│       ├── k8s-node.pp
│       └── airflow-server.pp
├── modules/                 # Módulos Puppet
│   ├── k8s/
│   │   └── manifests/
│   │       ├── node.pp
│   │       └── docker.pp
│   ├── airflow/
│   │   └── manifests/
│   │       └── server.pp
│   └── common/
│       └── manifests/
│           └── packages.pp
├── hiera.yaml              # Configuración Hiera
├── hiera/
│   └── data/               # Datos de configuración
│       ├── common.yaml
│       ├── environments/
│       └── nodes/
├── environment.conf        # Configuración de entorno
└── README.md
```

## Instalación

### Puppet Server (Master)

```bash
# Ubuntu/Debian
wget https://apt.puppet.com/puppet7-release-focal.deb
sudo dpkg -i puppet7-release-focal.deb
sudo apt-get update
sudo apt-get install puppetserver

# Iniciar servicio
sudo systemctl start puppetserver
sudo systemctl enable puppetserver
```

### Puppet Agent (en nodos)

```bash
sudo apt-get install puppet-agent
sudo systemctl start puppet
sudo systemctl enable puppet
```

## Uso

### Configurar Puppet Agent

```bash
# En cada nodo
sudo puppet agent --server puppet-master.example.com --waitforcert 60
```

### Firmar certificados (en master)

```bash
# Listar certificados pendientes
sudo puppet cert list

# Firmar certificado específico
sudo puppet cert sign k8s-master-1

# Firmar todos
sudo puppet cert sign --all
```

### Aplicar configuración

```bash
# En cada nodo (agente)
sudo puppet agent -t

# O desde el master (push)
sudo puppet kick -p 10 --host k8s-master-1
```

### Ejecutar comando ad-hoc

```bash
# Desde master
sudo puppet apply -e "package { 'htop': ensure => installed }"
```

## Módulos Disponibles

### k8s::node
Configura nodos Kubernetes:
- Instala kubelet, kubeadm, kubectl
- Configura servicios
- Deshabilita swap

### k8s::docker
Instala Docker para contenedores.

### airflow::server
Configura servidor Airflow:
- Crea usuario y directorios
- Instala dependencias
- Configura servicios systemd

## Hiera - Gestión de Datos

Hiera permite separar datos de código:

```yaml
# hiera/data/environments/prod.yaml
k8s_version: "1.29.0-00"
airflow_version: "2.8.0"
```

```puppet
# En manifest
$k8s_version = hiera('k8s_version')
```

## Facter - Hechos del Sistema

```bash
# Ver todos los hechos
facter

# Ver hecho específico
facter os.family
facter ipaddress
```

## Ventajas

1. **Declarativo**: Describe el estado deseado, no los pasos
2. **Idempotente**: Puede ejecutarse múltiples veces sin efectos secundarios
3. **Módulos**: Ecosistema rico de módulos reutilizables
4. **Reporting**: Sistema de reporting integrado

## Ejemplo de Manifest

```puppet
class myapp::install {
  package { 'myapp':
    ensure => '1.0.0',
  }

  file { '/etc/myapp/config.conf':
    ensure  => present,
    content => template('myapp/config.conf.erb'),
    require => Package['myapp'],
  }

  service { 'myapp':
    ensure  => running,
    enable  => true,
    require => File['/etc/myapp/config.conf'],
  }
}
```

## Integración con Terraform

```bash
# 1. Provisionar infraestructura
make tf-apply

# 2. Exportar datos para Hiera
terraform output -json > puppet/hiera/data/terraform.json

# 3. Aplicar configuración Puppet
puppet agent -t
```

## Integración CI/CD

Puppet puede integrarse en pipelines de Jenkins:

```groovy
stage('Puppet Apply') {
  steps {
    sh 'puppet agent -t'
  }
}
```


