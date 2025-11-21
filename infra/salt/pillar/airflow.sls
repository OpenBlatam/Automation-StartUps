# Pillar data para Airflow servers

airflow:
  version: "2.8.0"
  user: "airflow"
  home: "/opt/airflow"
  executor: "LocalExecutor"
  
  database:
    type: "sqlite"
    connection: "sqlite:///opt/airflow/airflow.db"

python:
  version: "3"
  venv_path: "/opt/airflow/venv"


