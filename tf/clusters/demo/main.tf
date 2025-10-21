terraform {
  required_version = ">=1.8"
  backend "gcs" {
    bucket = "tf-state-bids-hub-demo"
    prefix = "tf/state"
  }
}

provider "google" {
  project = "bids-jupyterhub"
  region  = "us-central1"
  zone    = "us-central1-a"
}

locals {
  name = "demo"
}

module "hub_deploy" {
  source = "../../modules/hub_deploy"
  name   = local.name
}
