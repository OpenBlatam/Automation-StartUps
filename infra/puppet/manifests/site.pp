# Site-wide Puppet configuration

# Importaciones por entorno
import 'nodes/*.pp'

# Configuración global
File {
  owner => 'root',
  group => 'root',
  mode  => '0644',
}

Package {
  ensure => 'present',
}

Service {
  ensure => 'running',
  enable => true,
}

# Definiciones de clases base
node default {
  include common::packages
  include common::security
  include common::sysctl
}

