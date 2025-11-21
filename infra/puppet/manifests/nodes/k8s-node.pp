# Kubernetes node configuration

node /^k8s-(master|worker)-\d+$/ {
  include common::packages
  include common::security
  include common::sysctl
  include k8s::node
  include k8s::docker
}

