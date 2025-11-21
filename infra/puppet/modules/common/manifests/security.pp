# Common security configurations

class common::security {
  # Actualizar sistema periódicamente
  exec { 'apt-update':
    command => '/usr/bin/apt-get update',
    path    => '/usr/bin:/bin',
  }

  # Instalar actualizaciones de seguridad
  package { ['unattended-upgrades']:
    ensure => present,
  }

  # Configurar firewall básico
  if !defined(Package['ufw']) {
    package { 'ufw':
      ensure => present,
    }
  }

  exec { 'ufw-enable':
    command => '/usr/sbin/ufw --force enable',
    unless  => '/usr/sbin/ufw status | /bin/grep -q "Status: active"',
    require => Package['ufw'],
  }

  exec { 'ufw-allow-ssh':
    command => '/usr/sbin/ufw allow ssh',
    unless  => '/usr/sbin/ufw status | /bin/grep -q "22/tcp"',
    require => Exec['ufw-enable'],
  }
}


