# Terraform Testing Guide

This guide covers testing strategies for Terraform configurations.

## 🧪 Testing Strategies

### 1. Static Analysis

**Terraform Validate**
```bash
terraform init -backend=false
terraform validate
```

**Terraform Format**
```bash
terraform fmt -check -recursive
```

**TFLint**
```bash
tflint --init
tflint
```

**Checkov (Security)**
```bash
pip install checkov
checkov -d . --framework terraform
```

### 2. Unit Testing with Terratest

Install Terratest:
```bash
go get github.com/gruntwork-io/terratest/modules/terraform
```

Example test:
```go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCCreation(t *testing.T) {
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/vpc",
        Vars: map[string]interface{}{
            "environment": "test",
            "vpc_cidr":    "10.0.0.0/16",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcId)
}
```

### 3. Integration Testing

**Using Kitchen-Terraform**
```bash
gem install kitchen-terraform
```

**Kitchen config** (`kitchen.yml`):
```yaml
driver:
  name: terraform
  root_module_directory: examples/vpc

provisioner:
  name: terraform

platforms:
  - name: aws

suites:
  - name: default
```

### 4. Pre-commit Hooks

Install pre-commit:
```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.81.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
      - id: terraform_docs
```

Install hooks:
```bash
pre-commit install
```

### 5. Test Structure

```
tests/
├── unit/
│   ├── test_vpc.go
│   └── test_s3.go
├── integration/
│   └── test_full_stack.go
└── fixtures/
    ├── vpc/
    └── eks/
```

## 🔍 Validation Scripts

Use the included validation scripts:

```bash
# Full validation
./scripts/validate-terraform.sh

# Pre-apply checks
./scripts/pre-apply-check.sh prod
```

## 📊 Test Coverage

Track test coverage:
- Validate all modules are tested
- Ensure all variables have tests
- Verify outputs are tested

## 🚀 CI/CD Testing

The GitHub Actions workflow runs:
1. Format check
2. Validation
3. Security scans (TFLint, Checkov)
4. Plan generation
5. Apply (on merge to main)

## 📚 Additional Resources

- [Terratest Documentation](https://terratest.gruntwork.io/)
- [Kitchen-Terraform](https://github.com/newcontext-oss/kitchen-terraform)
- [TFLint Rules](https://github.com/terraform-linters/tflint-ruleset-aws)



