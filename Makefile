SHELL := /bin/bash

TF_DIR ?= infra/terraform
K8S_DIR ?= kubernetes
ANSIBLE_DIR ?= infra/ansible
SALT_DIR ?= infra/salt
PUPPET_DIR ?= infra/puppet

.PHONY: help
help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Terraform
# ============================================================================
.PHONY: tf-init tf-plan tf-apply tf-destroy tf-fmt tf-validate tf-output
.PHONY: tf-backend-bootstrap-aws tf-backend-bootstrap-azure tf-init-backend
.PHONY: tf-state-list tf-state-show tf-state-refresh

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

tf-output:
	cd $(TF_DIR) && terraform output -json > terraform-output.json

# Terraform State Management
# Usage: make tf-backend-bootstrap-aws ENV=dev REGION=us-east-1
tf-backend-bootstrap-aws: ## Bootstrap AWS backend (S3 + DynamoDB) for Terraform state
	@if [ -z "$(ENV)" ]; then echo "Usage: make tf-backend-bootstrap-aws ENV=dev REGION=us-east-1"; exit 1; fi
	cd $(TF_DIR)/scripts && ./bootstrap-backend-aws.sh $(ENV) $(REGION)

tf-backend-bootstrap-azure: ## Bootstrap Azure backend (Storage Account) for Terraform state
	@if [ -z "$(ENV)" ]; then echo "Usage: make tf-backend-bootstrap-azure ENV=dev LOCATION=eastus"; exit 1; fi
	cd $(TF_DIR)/scripts && ./bootstrap-backend-azure.sh $(ENV) $(LOCATION)

# Usage: make tf-init-backend PROVIDER=aws ENV=dev
tf-init-backend: ## Initialize Terraform with remote backend
	@if [ -z "$(PROVIDER)" ] || [ -z "$(ENV)" ]; then echo "Usage: make tf-init-backend PROVIDER=aws ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./init-backend.sh $(PROVIDER) $(ENV)

tf-state-list: ## List all resources in Terraform state
	cd $(TF_DIR)/scripts && ./state-management.sh list

tf-state-show: ## Show details of a Terraform resource (usage: make tf-state-show RESOURCE=aws_s3_bucket.datalake)
	@if [ -z "$(RESOURCE)" ]; then echo "Usage: make tf-state-show RESOURCE=aws_s3_bucket.datalake"; exit 1; fi
	cd $(TF_DIR)/scripts && ./state-management.sh show $(RESOURCE)

tf-state-refresh: ## Refresh Terraform state to match real infrastructure
	cd $(TF_DIR)/scripts && ./state-management.sh refresh

tf-validate-config: ## Validate Terraform configuration (format, syntax, security)
	cd $(TF_DIR)/scripts && ./validate-terraform.sh

tf-pre-apply-check: ## Run safety checks before applying (usage: make tf-pre-apply-check ENV=prod)
	@if [ -z "$(ENV)" ]; then echo "Usage: make tf-pre-apply-check ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./pre-apply-check.sh $(ENV)

tf-migrate-backend: ## Migrate Terraform state between backends (usage: make tf-migrate-backend FROM=local TO=remote PROVIDER=aws ENV=dev)
	@if [ -z "$(FROM)" ] || [ -z "$(TO)" ] || [ -z "$(PROVIDER)" ] || [ -z "$(ENV)" ]; then \
		echo "Usage: make tf-migrate-backend FROM=local TO=remote PROVIDER=aws ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./migrate-backend.sh $(FROM) $(TO) $(PROVIDER) $(ENV)

tf-health-check: ## Run infrastructure health check (usage: make tf-health-check PROVIDER=aws ENV=dev)
	@if [ -z "$(PROVIDER)" ] || [ -z "$(ENV)" ]; then echo "Usage: make tf-health-check PROVIDER=aws ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./health-check.sh $(PROVIDER) $(ENV)

tf-cleanup: ## Clean up Terraform workspace (usage: make tf-cleanup [--all|--cache|--state])
	cd $(TF_DIR)/scripts && ./cleanup.sh $(ARGS)

tf-backup-state: ## Backup Terraform state (usage: make tf-backup-state PROVIDER=aws ENV=dev)
	@if [ -z "$(PROVIDER)" ] || [ -z "$(ENV)" ]; then echo "Usage: make tf-backup-state PROVIDER=aws ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./backup-state.sh $(PROVIDER) $(ENV)

tf-quick-start: ## Interactive Terraform setup wizard
	cd $(TF_DIR)/scripts && ./quick-start.sh

tf-export-outputs: ## Export Terraform outputs (usage: make tf-export-outputs FORMAT=json FILE=outputs.json)
	cd $(TF_DIR)/scripts && ./export-outputs.sh $(FORMAT) $(FILE)

tf-cost-estimate: ## Estimate infrastructure costs (usage: make tf-cost-estimate PROVIDER=aws)
	cd $(TF_DIR)/scripts && ./cost-estimate.sh $(PROVIDER)

tf-drift-detection: ## Detect infrastructure drift (usage: make tf-drift-detection PROVIDER=aws ENV=dev)
	@if [ -z "$(PROVIDER)" ] || [ -z "$(ENV)" ]; then echo "Usage: make tf-drift-detection PROVIDER=aws ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./drift-detection.sh $(PROVIDER) $(ENV)

tf-audit-security: ## Run security audit (usage: make tf-audit-security)
	cd $(TF_DIR)/scripts && ./audit-security.sh

tf-plan-report: ## Generate HTML plan report (usage: make tf-plan-report PLAN=tfplan)
	cd $(TF_DIR)/scripts && ./generate-plan-report.sh $(PLAN)

tf-lock-state: ## Lock Terraform state for maintenance (usage: make tf-lock-state REASON="Maintenance")
	cd $(TF_DIR)/scripts && ./lock-state.sh "$(REASON)"

tf-unlock-state: ## Unlock Terraform state
	cd $(TF_DIR)/scripts && ./unlock-state.sh

tf-resource-inventory: ## Generate resource inventory (usage: make tf-resource-inventory PROVIDER=aws FORMAT=json)
	cd $(TF_DIR)/scripts && ./resource-inventory.sh $(PROVIDER) $(FORMAT)

tf-dependency-graph: ## Generate dependency graph (usage: make tf-dependency-graph FORMAT=dot)
	cd $(TF_DIR)/scripts && ./dependency-graph.sh $(FORMAT)

tf-auto-document: ## Auto-generate documentation from code (usage: make tf-auto-document FILE=DOC.md)
	cd $(TF_DIR)/scripts && ./auto-document.sh $(FILE)

tf-check-dependencies: ## Check all required dependencies and tools
	cd $(TF_DIR)/scripts && ./check-dependencies.sh

tf-version-check: ## Check Terraform and provider versions
	cd $(TF_DIR)/scripts && ./version-check.sh

tf-test-infrastructure: ## Test infrastructure after deployment (usage: make tf-test-infrastructure PROVIDER=aws ENV=dev)
	@if [ -z "$(PROVIDER)" ] || [ -z "$(ENV)" ]; then echo "Usage: make tf-test-infrastructure PROVIDER=aws ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./test-infrastructure.sh $(PROVIDER) $(ENV)

tf-summary: ## Show comprehensive infrastructure summary (usage: make tf-summary PROVIDER=aws)
	cd $(TF_DIR)/scripts && ./summary.sh $(PROVIDER)

tf-validate-modules: ## Validate Terraform modules (usage: make tf-validate-modules MODULE_DIR=modules)
	cd $(TF_DIR)/scripts && ./validate-modules.sh $(MODULE_DIR)

tf-quick-fix: ## Quick fix common issues (usage: make tf-quick-fix ISSUE=format)
	cd $(TF_DIR)/scripts && ./quick-fix.sh $(ISSUE)

tf-find-unused-variables: ## Find unused variables
	cd $(TF_DIR)/scripts && ./find-unused-variables.sh

tf-check-resources: ## Check resources exist in cloud (usage: make tf-check-resources PROVIDER=aws ENV=dev)
	@if [ -z "$(PROVIDER)" ] || [ -z "$(ENV)" ]; then echo "Usage: make tf-check-resources PROVIDER=aws ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./check-resources.sh $(PROVIDER) $(ENV)

tf-export-resource-list: ## Export resource list (usage: make tf-export-resource-list FORMAT=json FILE=resources.json)
	cd $(TF_DIR)/scripts && ./export-resource-list.sh $(FORMAT) $(FILE)

tf-compliance-check: ## Run compliance check (usage: make tf-compliance-check STANDARD=aws-well-architected)
	cd $(TF_DIR)/scripts && ./compliance-check.sh $(STANDARD)

tf-architecture-diagram: ## Generate architecture diagram (usage: make tf-architecture-diagram FILE=diagram.dot)
	cd $(TF_DIR)/scripts && ./generate-architecture-diagram.sh $(FILE)

tf-dr-plan: ## Generate disaster recovery plan (usage: make tf-dr-plan FILE=DR_PLAN.md)
	cd $(TF_DIR)/scripts && ./disaster-recovery-plan.sh $(FILE)

tf-validate-cloud: ## Validate for Terraform Cloud compatibility
	cd $(TF_DIR)/scripts && ./validate-terraform-cloud.sh

tf-metrics: ## Collect infrastructure metrics (usage: make tf-metrics FORMAT=json)
	cd $(TF_DIR)/scripts && ./metrics-collector.sh $(FORMAT)

tf-sync-remote: ## Sync local state to remote backend
	cd $(TF_DIR)/scripts && ./sync-to-remote.sh

tf-backup-all: ## Backup all environments (usage: make tf-backup-all PROVIDER=aws)
	cd $(TF_DIR)/scripts && ./backup-all-environments.sh $(PROVIDER)

tf-cloud-setup: ## Setup Terraform Cloud (usage: make tf-cloud-setup ORG=my-org WS=workspace)
	@if [ -z "$(ORG)" ] || [ -z "$(WS)" ]; then echo "Usage: make tf-cloud-setup ORG=my-org WS=workspace"; exit 1; fi
	cd $(TF_DIR)/scripts && ./terraform-cloud-setup.sh $(ORG) $(WS)

tf-daily-maintenance: ## Run daily maintenance tasks (usage: make tf-daily-maintenance PROVIDER=aws ENV=dev)
	@if [ -z "$(PROVIDER)" ] || [ -z "$(ENV)" ]; then echo "Usage: make tf-daily-maintenance PROVIDER=aws ENV=dev"; exit 1; fi
	cd $(TF_DIR)/scripts && ./daily-maintenance.sh $(PROVIDER) $(ENV)

tf-cost-breakdown: ## Detailed cost breakdown by resource (usage: make tf-cost-breakdown PROVIDER=aws)
	cd $(TF_DIR)/scripts && ./resource-cost-breakdown.sh $(PROVIDER)

tf-validate-outputs: ## Validate Terraform outputs
	cd $(TF_DIR)/scripts && ./validate-outputs.sh

tf-variables-docs: ## Generate variables documentation (usage: make tf-variables-docs FILE=VARIABLES.md)
	cd $(TF_DIR)/scripts && ./generate-variables-docs.sh $(FILE)

tf-check-version: ## Check Terraform version compatibility
	cd $(TF_DIR)/scripts && ./check-terraform-version.sh

tf-find-deprecated: ## Find potentially deprecated resources
	cd $(TF_DIR)/scripts && ./find-deprecated-resources.sh

tf-export-modules: ## Export module list (usage: make tf-export-modules FORMAT=json)
	cd $(TF_DIR)/scripts && ./export-module-list.sh $(FORMAT)

# ============================================================================
# Kubernetes
# ============================================================================
.PHONY: k8s-namespaces k8s-ingress k8s-integration k8s-kafka k8s-kafka-topics k8s-connect

k8s-namespaces:
	kubectl apply -f $(K8S_DIR)/namespaces.yaml

k8s-ingress:
	kubectl apply -f $(K8S_DIR)/ingress/nginx-ingress.yaml

k8s-integration:
	kubectl apply -f $(K8S_DIR)/integration/healthz.yaml

k8s-kafka:
	kubectl apply -f $(K8S_DIR)/kafka/strimzi-kafka.yaml

k8s-kafka-topics:
	kubectl apply -f $(K8S_DIR)/kafka/topics/orders.yaml

k8s-connect:
	kubectl apply -f $(K8S_DIR)/kafka/connect/deployment.yaml

# ============================================================================
# Kustomize
# ============================================================================
.PHONY: kustomize-dev kustomize-stg kustomize-prod kustomize-validate-dev kustomize-validate-stg kustomize-validate-prod

kustomize-dev:
	kubectl apply -k $(K8S_DIR)/overlays/dev

kustomize-stg:
	kubectl apply -k $(K8S_DIR)/overlays/stg

kustomize-prod:
	kubectl apply -k $(K8S_DIR)/overlays/prod

kustomize-validate-dev:
	kubectl kustomize $(K8S_DIR)/overlays/dev | kubectl apply --dry-run=client -f -

kustomize-validate-stg:
	kubectl kustomize $(K8S_DIR)/overlays/stg | kubectl apply --dry-run=client -f -

kustomize-validate-prod:
	kubectl kustomize $(K8S_DIR)/overlays/prod | kubectl apply --dry-run=client -f -

# ============================================================================
# Helmfile
# ============================================================================
.PHONY: helmfile-apply helmfile-diff

helmfile-apply:
	helmfile apply

helmfile-diff:
	helmfile diff

# ============================================================================
# Code Quality
# ============================================================================
.PHONY: js-lint js-format js-typecheck js-audit py-lint py-format all-checks js-test py-test

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

py-lint:
	ruff check .

py-format:
	black .

all-checks: js-lint js-typecheck py-lint

js-test:
	cd web/kpis && npm test --silent || true
	cd web/kpis-next && npm test --silent || true

py-test:
	pytest

# ============================================================================
# Airflow
# ============================================================================
.PHONY: airflow-up airflow-down airflow-init

airflow-up:
	cd data/airflow && docker compose up -d

airflow-down:
	cd data/airflow && docker compose down

airflow-init:
	cd data/airflow && docker compose up airflow-init

# ============================================================================
# Ansible
# ============================================================================
.PHONY: ansible-install ansible-playbook-k8s ansible-playbook-airflow ansible-ping ansible-update-inventory ansible-validate-terraform ansible-lint

ansible-install: ## Instalar Ansible y dependencias
	pip install ansible ansible-lint

ansible-playbook-k8s: ## Configurar nodos Kubernetes con Ansible
	cd $(ANSIBLE_DIR) && ansible-playbook -i inventory/hosts.ini playbooks/k8s-node-setup.yml

ansible-playbook-airflow: ## Configurar servidor Airflow con Ansible
	cd $(ANSIBLE_DIR) && ansible-playbook -i inventory/hosts.ini playbooks/airflow-server-setup.yml

ansible-ping: ## Verificar conectividad con todos los hosts
	cd $(ANSIBLE_DIR) && ansible all -i inventory/hosts.ini -m ping

ansible-update-inventory: tf-output ## Actualizar inventario desde Terraform outputs
	cd $(ANSIBLE_DIR) && python3 scripts/update-inventory-from-terraform.py

ansible-validate-terraform: ## Validar outputs de Terraform
	@cd $(ANSIBLE_DIR) && python3 -c "import json, sys; json.load(open('../terraform/terraform-output.json')); print('✅ JSON válido')" || echo "❌ Error: terraform-output.json no encontrado o inválido"

ansible-lint: ## Lint playbooks de Ansible
	cd $(ANSIBLE_DIR) && ansible-lint playbooks/*.yml || true

# ============================================================================
# Salt
# ============================================================================
.PHONY: salt-master-install salt-minion-install salt-apply salt-state salt-test salt-pillar

salt-master-install: ## Mostrar instrucciones para instalar Salt master
	@echo "Instalar Salt master: curl -L https://bootstrap.saltproject.io | sudo sh -s -- -M"

salt-minion-install: ## Mostrar instrucciones para instalar Salt minion
	@echo "Instalar Salt minion: curl -L https://bootstrap.saltproject.io | sudo sh -s -- minion"

salt-apply: ## Aplicar todos los estados de Salt
	salt '*' state.apply

salt-state: ## Aplicar estado específico (uso: make salt-state STATE=k8s.node)
	@if [ -z "$(STATE)" ]; then echo "❌ Especifica STATE, ejemplo: make salt-state STATE=k8s.node"; exit 1; fi
	salt '*' state.apply $(STATE)

salt-test: ## Test connectivity con Salt
	salt '*' test.ping

salt-pillar: ## Ver pillar data
	salt '*' pillar.items

# ============================================================================
# Puppet
# ============================================================================
.PHONY: puppet-master-install puppet-agent-install puppet-apply puppet-facts puppet-hiera

puppet-master-install: ## Mostrar instrucciones para instalar Puppet master
	@echo "Instalar Puppet master: sudo apt-get install puppetserver"

puppet-agent-install: ## Mostrar instrucciones para instalar Puppet agent
	@echo "Instalar Puppet agent: sudo apt-get install puppet-agent"

puppet-apply: ## Aplicar configuración de Puppet
	puppet agent -t

puppet-facts: ## Ver facts de Puppet
	facter

puppet-hiera: ## Ver datos de Hiera
	puppet lookup --explain k8s_version

# ============================================================================
# Chef
# ============================================================================
.PHONY: chef-client-install chef-upload chef-apply chef-knife

chef-client-install: ## Mostrar instrucciones para instalar Chef client
	@echo "Instalar Chef client: curl -L https://www.chef.io/chef/install.sh | sudo bash"

chef-upload: ## Mostrar instrucciones para subir cookbooks
	@echo "Subir cookbooks: knife cookbook upload -a"

chef-apply: ## Mostrar instrucciones para aplicar configuración
	@echo "Aplicar configuración: sudo chef-client"

chef-knife: ## Mostrar comandos útiles de knife
	@echo "Comandos útiles:"
	@echo "  knife node list"
	@echo "  knife node show <node-name>"
	@echo "  knife bootstrap <host> --node-name <name> --run-list 'recipe[k8s-node]'"

# ============================================================================
# Jenkins
# ============================================================================
.PHONY: jenkins-up jenkins-down jenkins-logs jenkins-plugins

jenkins-up: ## Iniciar Jenkins (si está configurado)
	@if [ -f infra/jenkins/docker-compose.yml ]; then \
		cd infra/jenkins && docker-compose up -d; \
	else \
		echo "⚠️  Jenkins no está configurado. Crea infra/jenkins/docker-compose.yml"; \
	fi

jenkins-down: ## Detener Jenkins
	@if [ -f infra/jenkins/docker-compose.yml ]; then \
		cd infra/jenkins && docker-compose down; \
	else \
		echo "⚠️  Jenkins no está configurado"; \
	fi

jenkins-logs: ## Ver logs de Jenkins
	@if [ -f infra/jenkins/docker-compose.yml ]; then \
		cd infra/jenkins && docker-compose logs -f; \
	else \
		echo "⚠️  Jenkins no está configurado"; \
	fi

jenkins-plugins: ## Mostrar plugins recomendados
	@echo "Plugins recomendados:"
	@echo "  - kubernetes"
	@echo "  - terraform"
	@echo "  - ansible"
	@echo "  - docker-workflow"
	@echo "  - pipeline"

# ============================================================================
# Flujos Completos
# ============================================================================
.PHONY: infra-complete ansible-complete salt-complete

infra-complete: ## Flujo completo: Terraform + Ansible
	@echo "🚀 Iniciando despliegue completo..."
	$(MAKE) tf-init
	$(MAKE) tf-plan
	@read -p "¿Aplicar cambios de Terraform? (y/N): " confirm && [ "$$confirm" = "y" ] && $(MAKE) tf-apply || echo "Cancelado"
	$(MAKE) tf-output
	$(MAKE) ansible-update-inventory
	$(MAKE) ansible-ping
	@read -p "¿Configurar servidores con Ansible? (y/N): " confirm && [ "$$confirm" = "y" ] && $(MAKE) ansible-playbook-k8s || echo "Cancelado"

ansible-complete: tf-output ansible-update-inventory ansible-ping ## Setup completo con Ansible
	@echo "✅ Listo para ejecutar playbooks"
	@echo "Ejecuta: make ansible-playbook-k8s"

salt-complete: ## Setup completo con Salt
	@echo "🔧 Verificando conectividad con Salt..."
	$(MAKE) salt-test
	@echo "✅ Aplicando estados..."
	$(MAKE) salt-apply

