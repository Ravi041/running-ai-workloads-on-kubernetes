variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Google Cloud zone"
  type        = string
  default     = "us-central1-a"
}

variable "network" {
  description = "VPC network name"
  type        = string
  default     = "default"
}

variable "subnetwork" {
  description = "Subnetwork name"
  type        = string
  default     = "default"
}

variable "cluster_secondary_range_name" {
  description = "Secondary range for cluster pods"
  type        = string
  default     = "default"
}

variable "services_secondary_range_name" {
  description = "Secondary range for services"
  type        = string
  default     = "default"
}

variable "node_count" {
  description = "Node count for the primary pool"
  type        = number
  default     = 2
}

variable "node_machine_type" {
  description = "Machine type for the node pool"
  type        = string
  default     = "e2-standard-4"
}
