# Common sysctl configurations

class common::sysctl {
  # Configuraciones de red para Kubernetes
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
}


