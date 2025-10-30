SHELL := /bin/bash

TF_DIR ?= infra/terraform
K8S_DIR ?= kubernetes

.PHONY: tf-init tf-plan tf-apply tf-destroy tf-fmt tf-validate

tf-init:
	cd $(TF_DIR) && terraform init

tf-plan:
	cd $(TF_DIR) && terraform plan

tf-apply:
	cd $(TF_DIR) && terraform apply -auto-approve

tf-destroy:
	cd $(TF_DIR) && terraform destroy -auto-approve

tf-fmt:
	terraform -chdir=$(TF_DIR) fmt -check

tf-validate:
	terraform -chdir=$(TF_DIR) validate

.PHONY: k8s-namespaces k8s-ingress k8s-integration

k8s-namespaces:
	kubectl apply -f $(K8S_DIR)/namespaces.yaml

k8s-ingress:
	kubectl apply -f $(K8S_DIR)/ingress/nginx-ingress.yaml

k8s-integration:
	kubectl apply -f $(K8S_DIR)/integration/healthz.yaml

.PHONY: k8s-kafka k8s-kafka-topics k8s-connect

k8s-kafka:
	kubectl apply -f $(K8S_DIR)/kafka/strimzi-kafka.yaml

k8s-kafka-topics:
	kubectl apply -f $(K8S_DIR)/kafka/topics/orders.yaml

k8s-connect:
	kubectl apply -f $(K8S_DIR)/kafka/connect/deployment.yaml

.PHONY: kustomize-dev kustomize-stg kustomize-prod

kustomize-dev:
	kubectl apply -k $(K8S_DIR)/overlays/dev

kustomize-stg:
	kubectl apply -k $(K8S_DIR)/overlays/stg

kustomize-prod:
	kubectl apply -k $(K8S_DIR)/overlays/prod

.PHONY: kustomize-validate-dev kustomize-validate-stg kustomize-validate-prod

kustomize-validate-dev:
	kubectl kustomize $(K8S_DIR)/overlays/dev | kubectl apply --dry-run=client -f -

kustomize-validate-stg:
	kubectl kustomize $(K8S_DIR)/overlays/stg | kubectl apply --dry-run=client -f -

kustomize-validate-prod:
	kubectl kustomize $(K8S_DIR)/overlays/prod | kubectl apply --dry-run=client -f -

.PHONY: helmfile-apply helmfile-diff

helmfile-apply:
	helmfile apply

helmfile-diff:
	helmfile diff

.PHONY: js-lint js-format js-typecheck js-audit py-lint py-format all-checks

# JavaScript/TypeScript tasks
js-lint:
	cd web/kpis && npm run lint || true
	cd web/kpis-next && npm run lint || true

js-format:
	cd web/kpis && npm run format || true
	cd web/kpis-next && npm run format || true

js-typecheck:
	cd web/kpis && npm run typecheck || true
	cd web/kpis-next && npm run typecheck || true

js-audit:
	cd web/kpis && npm run audit || true
	cd web/kpis-next && npm run audit || true

# Python tasks
py-lint:
	ruff check .

py-format:
	black .

all-checks: js-lint js-typecheck py-lint

.PHONY: js-test py-test

js-test:
	cd web/kpis && npm test --silent || true
	cd web/kpis-next && npm test --silent || true

py-test:
	pytest

.PHONY: airflow-up airflow-down airflow-init

airflow-up:
	cd data/airflow && docker compose up -d

airflow-down:
	cd data/airflow && docker compose down

airflow-init:
	cd data/airflow && docker compose up airflow-init
