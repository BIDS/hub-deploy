terraform {
  required_version = ">=1.8"
  backend "gcs" {
    bucket = "tf-state-bids-biojupyer"
    prefix = "tf/state"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.7.0"
    }
  }
}

provider "google" {
  project = "bids-biojupyter"
  region  = "us-west2"
  zone    = "us-west2-c"
}

locals {
  name = "biojupyter-hub"
}

data "google_client_config" "provider" {}

module "gke_cluster" {
  source = "../../modules/gke_cluster"
  name   = local.name
  hub_nfs_disks = {
    hd = {
      name = "hub-nfs-${local.name}-hyperdisk"
      type = "hyperdisk-balanced"
      size = 50
    }
  }
}

resource "google_container_node_pool" "core-2610" {
  name     = "core-2610"
  cluster  = module.gke_cluster.cluster.id
  location = module.gke_cluster.cluster.location
  # node_locations lets us specify a single-zone regional cluster:
  node_locations = [data.google_client_config.provider.zone]

  lifecycle {
    ignore_changes = [node_count]
  }

  autoscaling {
    min_node_count = 1
    max_node_count = 3
  }
  node_count = 1

  node_config {
    machine_type = "n4-standard-2"
    disk_size_gb = 30
    disk_type    = "hyperdisk-balanced"

    # Required with Workload Identity: the GKE metadata server hands
    # pods their namespace identity instead of the node SA.
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = {
      "hub.jupyter.org/node-purpose" = "core"
    }
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = module.gke_cluster.service_accounts["gke-node"]
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_container_node_pool" "user-2610" {
  name     = "user-202610"
  cluster  = module.gke_cluster.cluster.id
  location = module.gke_cluster.cluster.location
  # node_locations lets us specify a single-zone regional cluster:
  node_locations = [data.google_client_config.provider.zone]

  lifecycle {
    ignore_changes = [node_count]
  }

  autoscaling {
    min_node_count = 0
    max_node_count = 5
  }

  node_config {
    # See tf/modules/gke_cluster: required with Workload Identity.
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    machine_type = "n4-standard-4"
    disk_size_gb = 100
    disk_type    = "hyperdisk-balanced"

    labels = {
      "hub.jupyter.org/node-purpose" = "user"
    }

    service_account = module.gke_cluster.service_accounts["gke-node"]
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
