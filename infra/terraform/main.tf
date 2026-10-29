resource "azurerm_resource_group" "lab" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Course    = "AZ104"
    UD        = "12"
    ManagedBy = "Terraform"
  }
}

resource "azurerm_storage_account" "lab" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.lab.name
  location                 = azurerm_resource_group.lab.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false

  tags = {
    Course      = "AZ104"
    UD          = "12"
    ManagedBy   = "Terraform"
    Environment = "Training"
  }
}
