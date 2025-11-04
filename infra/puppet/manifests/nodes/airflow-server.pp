# Airflow server configuration

node /^airflow-\d+$/ {
  include airflow::server
  include python::python3
  include common::packages
}


