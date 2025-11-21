# Políticas de Vault para diferentes roles y servicios
# Estas políticas controlan qué secretos pueden leer/escribir cada aplicación

# Política para External Secrets Operator
# Permite leer secretos necesarios para sincronización
path "secret/data/*" {
  capabilities = ["read"]
}

path "secret/metadata/*" {
  capabilities = ["list", "read"]
}

# Política para Airflow workers
# Acceso a secretos de integraciones y conexiones
path "secret/data/airflow/*" {
  capabilities = ["read"]
}

path "secret/data/crm/*" {
  capabilities = ["read"]
}

path "secret/data/databases/*" {
  capabilities = ["read"]
}

path "secret/data/notifications/*" {
  capabilities = ["read"]
}

# Política para workflows (Kestra, Camunda, Flowable)
path "secret/data/bpm/*" {
  capabilities = ["read"]
}

path "secret/data/rpa/*" {
  capabilities = ["read"]
}

path "secret/data/messaging/*" {
  capabilities = ["read"]
}

path "secret/data/ai/*" {
  capabilities = ["read"]
}

# Política para servicios de integración
path "secret/data/integration/*" {
  capabilities = ["read"]
}

path "secret/data/google/*" {
  capabilities = ["read"]
}

# Política de administración (solo para ops)
# Permite leer y escribir todos los secretos
path "secret/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/*" {
  capabilities = ["list", "read", "delete"]
}

path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "sys/*" {
  capabilities = ["read"]
}


