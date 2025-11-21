# Module Name

Brief description of what this module does.

## Usage

```hcl
module "example" {
  source = "./modules/example"
  
  name        = "my-resource"
  environment = "dev"
  
  tags = {
    Project = "example"
  }
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| name | Resource name | `string` | - | yes |
| environment | Environment name | `string` | `"dev"` | no |
| tags | Additional tags | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| resource_id | ID of the created resource |
| resource_arn | ARN of the created resource |

## Requirements

- Terraform >= 1.6.0
- Provider specific requirements

## Examples

See `examples/` directory for usage examples.

