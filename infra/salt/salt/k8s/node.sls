include:
  - k8s.docker
  - common.packages

# Variables desde pillar
{% set k8s_version = pillar.get('k8s_version', '1.29.0-00') %}

# Instalar paquetes requeridos primero
k8s_required_packages:
  pkg.installed:
    - pkgs:
      - apt-transport-https
      - ca-certificates
      - curl
      - gnupg
      - lsb-release

# Añadir repositorio Kubernetes
k8s_apt_repo:
  pkgrepo.managed:
    - name: deb https://apt.kubernetes.io/ kubernetes-{{ grains['oscodename'] }} main
    - file: /etc/apt/sources.list.d/kubernetes.list
    - key_url: https://packages.cloud.google.com/apt/doc/apt-key.gpg
    - require_in:
      - pkg: kubelet

# Instalar paquetes Kubernetes
kubelet:
  pkg.installed:
    - name: kubelet={{ k8s_version }}
    - refresh: true

kubeadm:
  pkg.installed:
    - name: kubeadm={{ k8s_version }}
    - refresh: true

kubectl:
  pkg.installed:
    - name: kubectl={{ k8s_version }}
    - refresh: true

# Configurar servicio kubelet
kubelet_service:
  service.running:
    - name: kubelet
    - enable: True
    - require:
      - pkg: kubelet

# Configurar sysctl para Kubernetes
sysctl_bridge_iptables:
  sysctl.present:
    - name: net.bridge.bridge-nf-call-iptables
    - value: 1

sysctl_bridge_ip6tables:
  sysctl.present:
    - name: net.bridge.bridge-nf-call-ip6tables
    - value: 1

sysctl_ipv4_forward:
  sysctl.present:
    - name: net.ipv4.ip_forward
    - value: 1

# Cargar módulos del kernel
load_br_netfilter:
  kmod.present:
    - name: br_netfilter

load_overlay:
  kmod.present:
    - name: overlay

# Hacer módulos persistentes
k8s_modules_config:
  file.managed:
    - name: /etc/modules-load.d/k8s.conf
    - contents: |
        br_netfilter
        overlay
    - mode: 0644

# Deshabilitar swap
disable_swap:
  cmd.run:
    - name: swapoff -a
    - unless: "swapon --summary | grep -q '^/dev'"
    - require_in:
      - file: fstab_no_swap

# Comentar swap en fstab
fstab_no_swap:
  file.replace:
    - name: /etc/fstab
    - pattern: '^([^#].*?\sswap\s)'
    - repl: '#\1'
    - backup: '.bak'

# Crear directorio de configuración kubelet
kubelet_config_dir:
  file.directory:
    - name: /var/lib/kubelet
    - mode: 0755
    - makedirs: true

