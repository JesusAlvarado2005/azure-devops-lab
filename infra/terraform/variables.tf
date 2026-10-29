variable "location" {
  description = "Regione Azure del laboratorio."
  type        = string
  default     = "westeurope"
}

variable "resource_group_name" {
  description = "Nome del Resource Group gestito da Terraform."
  type        = string
  default     = "rg-ud12-tf"
}

variable "storage_account_name" {
  description = "Nome globalmente univoco dello Storage Account."
  type        = string

  validation {
    condition = (
      length(var.storage_account_name) >= 3 &&
      length(var.storage_account_name) <= 24 &&
      can(regex("^[a-z0-9]+$", var.storage_account_name))
    )

    error_message = "Il nome Storage deve contenere 3-24 caratteri, solo lettere minuscole e numeri."
  }
}
