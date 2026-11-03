terraform {
  required_version = ">= 1.8.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 5.4.0"
    }
  }

  backend "azurerm" {
    use_cli          = true
    use_azuread_auth = true
  }
}
