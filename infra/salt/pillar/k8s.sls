# Pillar data para Kubernetes nodes

k8s_version: "1.29.0-00"
cluster_name: "biz-automation-dev"
pod_cidr: "10.244.0.0/16"
service_cidr: "10.96.0.0/12"

containerd:
  version: "1.7.0"
  config_path: "/etc/containerd/config.toml"

network:
  sysctl:
    net.bridge.bridge-nf-call-iptables: 1
    net.bridge.bridge-nf-call-ip6tables: 1
    net.ipv4.ip_forward: 1


