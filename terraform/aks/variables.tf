variable "resource_group_name" {
  description = "Azure resource group name."
  type        = string
  default     = "rg-ai-on-k8s"
}

variable "location" {
  description = "Azure region."
  type        = string
  default     = "eastus"
}

variable "cluster_name" {
  description = "AKS cluster name."
  type        = string
  default     = "aks-ai-on-k8s"
}

variable "acr_name" {
  description = "Globally unique Azure Container Registry name."
  type        = string
}

variable "node_count" {
  description = "Default node pool node count."
  type        = number
  default     = 2
}

variable "node_vm_size" {
  description = "Default node pool VM size."
  type        = string
  default     = "Standard_DS3_v2"
}

variable "kubernetes_version" {
  description = "Optional AKS Kubernetes version. Leave null to use the Azure default."
  type        = string
  default     = null
}
