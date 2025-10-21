variable "name" {
  type        = string
  description = "Name of the deployment"
}

variable "gke_location" {
  type        = string
  description = "GKE location for cluster if different from provider zone, e.g. us-central1 for regional cluster"
  default     = null
}

variable "registry_location" {
  type        = string
  description = "Registry location for cluster if different from provider region, e.g. us for multi-region"
  default     = null
}
