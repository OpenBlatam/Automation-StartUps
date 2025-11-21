# Kubernetes node setup
#
# This class configures a node to be ready for Kubernetes installation.
# It installs kubelet, kubeadm, kubectl and configures system prerequisites.

class k8s::node {
  $k8s_version = hiera('k8s_version', '1.29.0-00')
  
  # Validar OS
  if $facts['os']['family'] != 'Debian' {
    fail("Unsupported OS family: ${facts['os']['family']}")
  }

  # Paquetes requeridos
  $required_packages = [
    'apt-transport-https',
    'ca-certificates',
    'curl',
    'gnupg',
    'lsb-release',
  ]

  package { $required_packages:
    ensure => present,
    before => Apt::Source['kubernetes'],
  }

  # Añadir repositorio Kubernetes
  apt::source { 'kubernetes':
    location => 'https://apt.kubernetes.io/',
    repos    => 'main',
    key      => {
      id     => 'A7317B0F',
      source => 'https://packages.cloud.google.com/apt/doc/apt-key.gpg',
    },
    notify   => Exec['apt_update'],
  }

  exec { 'apt_update':
    command     => '/usr/bin/apt-get update',
    refreshonly => true,
    before      => Package['kubelet'],
  }

  # Instalar paquetes Kubernetes
  package { ['kubelet', 'kubeadm', 'kubectl']:
    ensure  => $k8s_version,
    require => Apt::Source['kubernetes'],
  }

  # Servicio kubelet
  service { 'kubelet':
    ensure  => 'running',
    enable  => true,
    require => Package['kubelet'],
  }

  # Configurar sysctl
  sysctl { 'net.bridge.bridge-nf-call-iptables':
    ensure => present,
    value  => '1',
  }

  sysctl { 'net.bridge.bridge-nf-call-ip6tables':
    ensure => present,
    value  => '1',
  }

  sysctl { 'net.ipv4.ip_forward':
    ensure => present,
    value  => '1',
  }

  # Cargar módulos del kernel
  kmod::load { ['br_netfilter', 'overlay']:
    ensure => present,
  }

  # Hacer módulos persistentes
  file { '/etc/modules-load.d/k8s.conf':
    ensure  => file,
    content => "br_netfilter\noverlay\n",
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
  }

  # Deshabilitar swap
  exec { 'disable-swap':
    command => '/sbin/swapoff -a',
    unless  => '/usr/bin/swapon --summary | /bin/grep -q "^/dev"',
    before  => File_line['disable-swap-fstab'],
  }

  file_line { 'disable-swap-fstab':
    path    => '/etc/fstab',
    line    => '# Swap disabled by Puppet',
    match   => '^([^#].*?\sswap\s)',
    replace => false,
  }

  # Directorio de configuración kubelet
  file { '/var/lib/kubelet':
    ensure => directory,
    owner  => 'root',
    group  => 'root',
    mode   => '0755',
  }
}

