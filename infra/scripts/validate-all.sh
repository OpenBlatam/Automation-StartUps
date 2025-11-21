#!/bin/bash
# Script para validar todas las configuraciones de infraestructura

set -euo pipefail

echo "🔍 Validando configuraciones de infraestructura..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de errores
ERRORS=0

# Función para validar
validate() {
    local name=$1
    local command=$2
    
    echo -n "Validando $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        ERRORS=$((ERRORS + 1))
    fi
}

# Terraform
echo "📦 Terraform"
validate "Terraform sintaxis" "terraform -chdir=terraform validate"
validate "Terraform formato" "terraform -chdir=terraform fmt -check"
echo ""

# Ansible
echo "📦 Ansible"
validate "Ansible sintaxis" "ansible-lint ansible/playbooks/*.yml" || true
if [[ -f "terraform/terraform-output.json" ]]; then
    validate "Ansible inventory" "python3 -c 'import json; json.load(open(\"terraform/terraform-output.json\"))'"
else
    echo -e "${YELLOW}⚠️  terraform-output.json no encontrado${NC}"
fi
echo ""

# Salt
echo "📦 Salt"
if [[ -f "salt/top.sls" ]]; then
    echo -e "${GREEN}✅${NC} Salt top.sls encontrado"
else
    echo -e "${RED}❌${NC} Salt top.sls no encontrado"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Puppet
echo "📦 Puppet"
if [[ -f "puppet/manifests/site.pp" ]]; then
    echo -e "${GREEN}✅${NC} Puppet site.pp encontrado"
    validate "Puppet sintaxis" "puppet parser validate puppet/manifests/site.pp" || true
else
    echo -e "${RED}❌${NC} Puppet site.pp no encontrado"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Resumen
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✅ Todas las validaciones pasaron${NC}"
    exit 0
else
    echo -e "${RED}❌ Se encontraron $ERRORS errores${NC}"
    exit 1
fi

