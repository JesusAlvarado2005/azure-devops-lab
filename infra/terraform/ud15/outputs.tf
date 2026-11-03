output "environment_name" {
  value = azurerm_container_app_environment.delivery.name
}

output "container_app_name" {
  value = azurerm_container_app.api.name
}

output "fqdn" {
  value = azurerm_container_app.api.ingress[0].fqdn
}

output "latest_revision_name" {
  value = azurerm_container_app.api.latest_revision_name
}

output "image" {
  value = "${data.azurerm_container_registry.acr.login_server}/${var.image_repository}:${var.image_tag}"
}
