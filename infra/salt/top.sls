base:
  'kubernetes*':
    - k8s.node
    - k8s.docker
  'airflow*':
    - airflow.server
    - python.python3
  'prometheus*':
    - monitoring.prometheus
  'grafana*':
    - monitoring.grafana
  '*':
    - common.packages
    - common.security


