resource "azurerm_virtual_network" "lab" {
  name                = "vnet-ud13"
  address_space       = ["10.13.0.0/16"]
  location            = azurerm_resource_group.lab.location
  resource_group_name = azurerm_resource_group.lab.name

  tags = {
    Course    = "AZ104"
    UD        = "13"
    ManagedBy = "Terraform"
  }
}

resource "azurerm_subnet" "app" {
  name                 = "snet-app"
  resource_group_name  = azurerm_resource_group.lab.name
  virtual_network_name = azurerm_virtual_network.lab.name
  address_prefixes     = ["10.13.1.0/24"]
}
