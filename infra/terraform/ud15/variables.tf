variable "resource_group_name" {
  type    = string
  default = "rg-ud13-15-delivery"
}

variable "acr_name" {
  type = string
}

variable "environment_name" {
  type    = string
  default = "acaenv-ud15"
}

variable "container_app_name" {
  type    = string
  default = "catalog-api-ud15"
}

variable "managed_identity_name" {
  type    = string
  default = "id-ud15-acrpull"
}

variable "image_repository" {
  type    = string
  default = "catalog-backend"
}

variable "image_tag" {
  type = string
}

variable "target_port" {
  type    = number
  default = 8000
}
