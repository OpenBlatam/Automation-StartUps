# ============================================================================
# Resource Group
# ============================================================================

resource "azurerm_resource_group" "rg" {
  name     = local.resource_group_name
  location = var.location

  tags = local.tags
}

# ============================================================================
# Virtual Network and Subnets
# ============================================================================

resource "azurerm_virtual_network" "vnet" {
  name                = local.vnet_name
  address_space       = [var.vnet_cidr]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = merge(
    local.tags,
    {
      Name = local.vnet_name
    }
  )
}

resource "azurerm_subnet" "subnets" {
  for_each = toset(var.subnet_cidrs)

  name                 = lower("subnet-${replace(replace(each.value, "/", "-"), ".", "-")}")
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [each.value]
}

# ============================================================================
# AKS Cluster
# ============================================================================

resource "azurerm_kubernetes_cluster" "aks" {
  name                = local.aks_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = lower(substr("bizauto-${var.environment}", 0, 54))
  kubernetes_version  = var.kubernetes_version

  # System-assigned managed identity
  identity {
    type = "SystemAssigned"
  }

  # Network configuration
  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
  }

  # RBAC configuration
  role_based_access_control_enabled = true

  # Azure Monitor integration (logging)
  dynamic "oms_agent" {
    for_each = local.enable_aks_logging ? [1] : []
    content {
      log_analytics_workspace_id = azurerm_log_analytics_workspace.main[0].id
    }
  }

  # Azure Monitor metrics and logs (modern approach - use both for compatibility)
  dynamic "azure_monitor_metrics" {
    for_each = local.enable_aks_logging ? [1] : []
    content {
      log_analytics_workspace_id = azurerm_log_analytics_workspace.main[0].id
    }
  }

  dynamic "azure_monitor_logs" {
    for_each = local.enable_aks_logging ? [1] : []
    content {
      log_analytics_workspace_id = azurerm_log_analytics_workspace.main[0].id
    }
  }

  # Default node pool
  default_node_pool {
    name                = "system"
    node_count          = var.aks_node_pools["default"].node_count
    vm_size             = var.aks_node_pools["default"].vm_size
    os_disk_size_gb     = var.aks_node_pools["default"].os_disk_size_gb
    vnet_subnet_id      = values(azurerm_subnet.subnets)[0].id
    enable_auto_scaling = var.aks_node_pools["default"].enable_auto_scaling
    min_count           = var.aks_node_pools["default"].min_count
    max_count           = var.aks_node_pools["default"].max_count
    node_labels         = merge(
      {
        Environment = var.environment
        ManagedBy   = "terraform"
      },
      var.aks_node_pools["default"].node_labels
    )
    node_taints = var.aks_node_pools["default"].node_taints
    tags        = local.tags
  }

  # Additional node pools
  dynamic "node_pool" {
    for_each = { for k, v in var.aks_node_pools : k => v if k != "default" }
    content {
      name                = node_pool.key
      node_count          = node_pool.value.node_count
      vm_size             = node_pool.value.vm_size
      os_disk_size_gb     = node_pool.value.os_disk_size_gb
      enable_auto_scaling = node_pool.value.enable_auto_scaling
      min_count           = node_pool.value.min_count
      max_count           = node_pool.value.max_count
      node_labels         = merge(
        {
          Environment = var.environment
          ManagedBy   = "terraform"
        },
        node_pool.value.node_labels
      )
      node_taints = node_pool.value.node_taints
      tags        = local.tags
    }
  }

  tags = local.tags
}

# ============================================================================
# Azure Monitor / Log Analytics Workspace (for AKS logging)
# ============================================================================

resource "azurerm_log_analytics_workspace" "main" {
  count               = local.enable_aks_logging ? 1 : 0
  name                = lower("law-${local.name_prefix}")
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = var.environment == "prod" ? 90 : 30

  tags = local.tags
}

# ============================================================================
# Azure Data Lake Storage Gen2
# ============================================================================

resource "azurerm_storage_account" "adls" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_account_replication_type
  account_kind             = "StorageV2"
  is_hns_enabled           = true

  # Security: Enable blob public access restrictions
  allow_nested_items_to_be_public = false

  # Encryption
  dynamic "encryption" {
    for_each = local.enable_storage_encryption ? [1] : []
    content {
      key_source = "Microsoft.Storage"
      services {
        blob {
          enabled = true
        }
        file {
          enabled = true
        }
      }
    }
  }

  # Network rules (restrict access if needed)
  # network_rules {
  #   default_action = "Deny"
  #   ip_rules       = []
  # }

  tags = merge(
    local.tags,
    {
      Name        = local.storage_account_name
      Description = "Data Lake Storage Gen2 account"
    }
  )

  lifecycle {
    ignore_changes = [
      # Ignore changes to tags as they may be updated externally
      tags,
    ]
  }
}

resource "azurerm_storage_data_lake_gen2_filesystem" "fs" {
  name               = var.datalake_fs_name
  storage_account_id = azurerm_storage_account.adls.id

  properties = {
    # Optional: Add properties like retention policies
  }
}

# ============================================================================
# Azure Container Registry
# ============================================================================

resource "azurerm_container_registry" "acr" {
  name                = local.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = var.acr_sku
  admin_enabled       = false # Use managed identity instead

  # Security: Enable network restrictions if needed
  # network_rule_set {
  #   default_action = "Deny"
  # }

  # Retention policies
  retention_policy {
    days    = var.environment == "prod" ? 30 : 7
    enabled = true
  }

  tags = merge(
    local.tags,
    {
      Name = local.acr_name
    }
  )
}

# ============================================================================
# ACR Integration with AKS (Workload Identity)
# ============================================================================

resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}

# ============================================================================
# Kubernetes Provider Configuration
# ============================================================================

provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.aks.kube_config[0].host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = azurerm_kubernetes_cluster.aks.kube_config[0].host
    client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config[0].cluster_ca_certificate)
  }
}


