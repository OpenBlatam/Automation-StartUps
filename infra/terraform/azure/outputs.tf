# ============================================================================
# Resource Group Outputs
# ============================================================================

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.rg.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.rg.location
}

# ============================================================================
# Networking Outputs
# ============================================================================

output "vnet_id" {
  description = "ID of the Virtual Network"
  value       = azurerm_virtual_network.vnet.id
}

output "vnet_name" {
  description = "Name of the Virtual Network"
  value       = azurerm_virtual_network.vnet.name
}

output "vnet_address_space" {
  description = "Address space of the Virtual Network"
  value       = azurerm_virtual_network.vnet.address_space
}

output "subnet_ids" {
  description = "Map of subnet names to IDs"
  value = {
    for name, subnet in azurerm_subnet.subnets : name => subnet.id
  }
}

# ============================================================================
# Kubernetes Outputs
# ============================================================================

output "aks_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "aks_id" {
  description = "ID of the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.id
}

output "aks_fqdn" {
  description = "FQDN of the AKS cluster"
  value       = azurerm_kubernetes_cluster.aks.fqdn
}

output "aks_host" {
  description = "Kubernetes API server host"
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].host
  sensitive   = false
}

output "aks_client_key" {
  description = "Base64 encoded client key"
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].client_key
  sensitive   = true
}

output "aks_client_certificate" {
  description = "Base64 encoded client certificate"
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate
  sensitive   = true
}

output "aks_cluster_ca_certificate" {
  description = "Base64 encoded cluster CA certificate"
  value       = azurerm_kubernetes_cluster.aks.kube_config[0].cluster_ca_certificate
  sensitive   = true
}

output "aks_identity" {
  description = "AKS managed identity"
  value = {
    principal_id = azurerm_kubernetes_cluster.aks.identity[0].principal_id
    tenant_id    = azurerm_kubernetes_cluster.aks.identity[0].tenant_id
  }
}

# ============================================================================
# Storage Outputs
# ============================================================================

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.adls.name
}

output "storage_account_id" {
  description = "ID of the storage account"
  value       = azurerm_storage_account.adls.id
}

output "adls_filesystem_name" {
  description = "Name of the ADLS Gen2 filesystem"
  value       = azurerm_storage_data_lake_gen2_filesystem.fs.name
}

output "adls_url" {
  description = "URL of the ADLS Gen2 storage account"
  value       = azurerm_storage_account.adls.primary_dfs_endpoint
}

# ============================================================================
# Container Registry Outputs
# ============================================================================

output "acr_name" {
  description = "Name of the Azure Container Registry"
  value       = azurerm_container_registry.acr.name
}

output "acr_login_server" {
  description = "Login server URL of the ACR"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_id" {
  description = "ID of the Azure Container Registry"
  value       = azurerm_container_registry.acr.id
}

# ============================================================================
# Monitoring Outputs
# ============================================================================

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics Workspace (if enabled)"
  value       = local.enable_aks_logging ? azurerm_log_analytics_workspace.main[0].id : null
}

# ============================================================================
# Common Outputs
# ============================================================================

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "location" {
  description = "Azure location"
  value       = var.location
}

output "tags" {
  description = "Common tags applied to resources"
  value       = local.tags
}

# ============================================================================
# Connection Information (for kubectl/helm)
# ============================================================================

output "kubeconfig_command" {
  description = "Command to configure kubectl"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.rg.name} --name ${azurerm_kubernetes_cluster.aks.name} --overwrite-existing"
}

output "kubeconfig_command_file" {
  description = "Command to save kubeconfig to file"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.rg.name} --name ${azurerm_kubernetes_cluster.aks.name} --file ~/.kube/config-aks-${var.environment}"
}

# ============================================================================
# Quick Reference Outputs
# ============================================================================

output "quick_reference" {
  description = "Quick reference information"
  value = {
    resource_group = azurerm_resource_group.rg.name
    aks_cluster    = azurerm_kubernetes_cluster.aks.name
    storage_account = azurerm_storage_account.adls.name
    acr_login      = azurerm_container_registry.acr.login_server
    location       = var.location
    environment    = var.environment
  }
}

