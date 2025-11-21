include:
  - python.python3

airflow_user:
  user.present:
    - name: airflow
    - home: /opt/airflow
    - shell: /bin/bash
    - createhome: True

airflow_dirs:
  file.directory:
    - names:
      - /opt/airflow/dags
      - /opt/airflow/logs
      - /opt/airflow/plugins
      - /opt/airflow/config
    - user: airflow
    - group: airflow
    - mode: 755
    - makedirs: True

airflow_venv:
  virtualenv.managed:
    - name: /opt/airflow/venv
    - python: python3
    - user: airflow
    - requirements: /srv/salt/airflow/requirements.txt
    - require:
      - user: airflow_user
      - pkg: python3_pip

airflow_config:
  file.managed:
    - name: /opt/airflow/config/airflow.cfg
    - source: salt://airflow/airflow.cfg
    - template: jinja
    - user: airflow
    - group: airflow
    - mode: 644
    - require:
      - file: airflow_dirs

airflow_webserver:
  service.running:
    - name: airflow-webserver
    - enable: True
    - require:
      - virtualenv: airflow_venv

airflow_scheduler:
  service.running:
    - name: airflow-scheduler
    - enable: True
    - require:
      - virtualenv: airflow_venv


