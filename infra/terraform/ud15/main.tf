data "azurerm_resource_group" "delivery" {
  name = var.resource_group_name
}

data "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = data.azurerm_resource_group.delivery.name
}

data "azurerm_user_assigned_identity" "pull" {
  name                = var.managed_identity_name
  resource_group_name = data.azurerm_resource_group.delivery.name
}

resource "azurerm_container_app_environment" "delivery" {
  name                = var.environment_name
  location            = data.azurerm_container_registry.acr.location
  resource_group_name = data.azurerm_resource_group.delivery.name

  tags = {
    Course    = "AZ104"
    UD        = "15"
    ManagedBy = "Terraform"
  }
}

resource "azurerm_container_app" "api" {
  name                         = var.container_app_name
  container_app_environment_id = azurerm_container_app_environment.delivery.id
  resource_group_name          = data.azurerm_resource_group.delivery.name
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [data.azurerm_user_assigned_identity.pull.id]
  }

  registry {
    server   = data.azurerm_container_registry.acr.login_server
    identity = data.azurerm_user_assigned_identity.pull.id
  }

  template {
    min_replicas = 0
    max_replicas = 1

    container {
      name   = "catalog-backend"
      image  = "${data.azurerm_container_registry.acr.login_server}/${var.image_repository}:${var.image_tag}"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "APP_VERSION"
        value = var.image_tag
      }

      env {
        name  = "LOW_STOCK_THRESHOLD"
        value = "5"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = var.target_port

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  tags = {
    Course    = "AZ104"
    UD        = "15"
    ManagedBy = "Terraform"
  }
}
