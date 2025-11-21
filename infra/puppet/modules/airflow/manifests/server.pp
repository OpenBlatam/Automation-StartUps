# Airflow server setup

class airflow::server {
  $airflow_user = 'airflow'
  $airflow_home = '/opt/airflow'
  $airflow_version = hiera('airflow_version', '2.8.0')

  # Usuario Airflow
  user { $airflow_user:
    ensure     => present,
    home       => $airflow_home,
    shell      => '/bin/bash',
    managehome => true,
    system     => false,
  }

  # Directorios
  file { [
    "${airflow_home}/dags",
    "${airflow_home}/logs",
    "${airflow_home}/plugins",
    "${airflow_home}/config",
  ]:
    ensure => directory,
    owner  => $airflow_user,
    group  => $airflow_user,
    mode   => '0755',
    require => User[$airflow_user],
  }

  # Virtual environment
  python::pyvenv { "${airflow_home}/venv":
    version => '3',
    owner   => $airflow_user,
    require => [
      User[$airflow_user],
      Package['python3-venv'],
    ],
  }

  # Instalar Airflow
  python::pip { 'airflow':
    pkgname      => "apache-airflow==${airflow_version}",
    virtualenv   => "${airflow_home}/venv",
    owner        => $airflow_user,
    require      => Python::Pyvenv["${airflow_home}/venv"],
  }

  # Configuración
  file { "${airflow_home}/config/airflow.cfg":
    ensure  => present,
    content => template('airflow/airflow.cfg.erb'),
    owner   => $airflow_user,
    group   => $airflow_user,
    mode    => '0644',
    require => File["${airflow_home}/config"],
  }

  # Servicio systemd (simplificado)
  systemd::unit_file { 'airflow-webserver.service':
    content => template('airflow/airflow-webserver.service.erb'),
    require => Python::Pip['airflow'],
  }

  service { 'airflow-webserver':
    ensure => running,
    enable => true,
    require => Systemd::Unit_file['airflow-webserver.service'],
  }
}


