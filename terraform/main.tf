terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}

# ─── Resource Group ────────────────────────────────────────────────────────────
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    project   = "jeddah-library-intelligence"
    author    = "FahadAlshehri"
    env       = var.environment
  }
}

# ─── Azure Container Registry ──────────────────────────────────────────────────
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = azurerm_resource_group.main.tags
}

# ─── App Service Plan ──────────────────────────────────────────────────────────
resource "azurerm_service_plan" "main" {
  name                = "${var.app_name}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "B1"          # Basic — cheapest plan with container support

  tags = azurerm_resource_group.main.tags
}

# ─── App Service (Web App for Containers) ─────────────────────────────────────
resource "azurerm_linux_web_app" "main" {
  name                = var.app_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    always_on = false   # keep off for Basic plan (free tier workaround)

    application_stack {
      docker_image_name        = "${var.acr_name}.azurecr.io/${var.image_name}:latest"
      docker_registry_url      = "https://${azurerm_container_registry.acr.login_server}"
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
    }
  }

  app_settings = {
    WEBSITES_PORT                     = "8501"
    DOCKER_REGISTRY_SERVER_URL        = "https://${azurerm_container_registry.acr.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME   = azurerm_container_registry.acr.admin_username
    DOCKER_REGISTRY_SERVER_PASSWORD   = azurerm_container_registry.acr.admin_password
    DOCKER_ENABLE_CI                  = "true"
  }

  tags = azurerm_resource_group.main.tags
}
