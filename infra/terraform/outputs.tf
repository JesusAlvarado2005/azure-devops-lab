output "resource_group_name" {
  description = "Resource Group creato da Terraform."
  value       = azurerm_resource_group.lab.name
}

output "storage_account_name" {
  description = "Storage Account creato da Terraform."
  value       = azurerm_storage_account.lab.name
}

output "storage_primary_blob_endpoint" {
  description = "Endpoint Blob primario."
  value       = azurerm_storage_account.lab.primary_blob_endpoint
}
