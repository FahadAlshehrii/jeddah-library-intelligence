variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "jeddah-library-rg"
}

variable "location" {
  description = "Azure region to deploy to"
  type        = string
  default     = "switzerlandnorth"
}

variable "acr_name" {
  description = "Azure Container Registry name (must be globally unique, alphanumeric only)"
  type        = string
  default     = "jeddahlibrariacr"
}

variable "app_name" {
  description = "Azure App Service name (must be globally unique)"
  type        = string
  default     = "jeddah-library-intel"
}

variable "image_name" {
  description = "Docker image name stored in ACR"
  type        = string
  default     = "jeddah-library-intelligence"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}
