provider "azurerm" {
  use_cli                         = true
  resource_provider_registrations = "none"

  features {}
}
