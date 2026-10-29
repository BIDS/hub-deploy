terraform {
  required_version = ">=1.8"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.7.0"
    }
  }
}

data "google_client_config" "provider" {}

resource "google_kms_key_ring" "keyring" {
  name     = "sops"
  location = "global"
}

resource "google_kms_crypto_key" "sops-key" {
  name     = "sops-key"
  key_ring = google_kms_key_ring.keyring.id

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github"
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions"
  display_name                       = "GitHub Actions OIDC"
  description                        = "GitHub Actions identity pool provider for CI Deploy from BIDS repos"
  attribute_condition                = <<EOT
    assertion.repository_owner == "BIDS"
EOT
  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.repo_environment" = "assertion.repository + '::' + assertion.environment"
    "attribute.actor"            = "assertion.actor"
    "attribute.aud"              = "assertion.aud"
    "attribute.environment"      = "assertion.environment"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_kms_crypto_key_iam_member" "github_sops_decrypt" {
  crypto_key_id = google_kms_crypto_key.sops-key.id
  role          = "roles/cloudkms.cryptoKeyDecrypter"
  member        = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repo_environment/BIDS/hub-deploy::deploy"
}

resource "google_project_iam_member" "github_deploy" {
  project = data.google_client_config.provider.project
  role    = "roles/container.admin"
  member  = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repo_environment/BIDS/hub-deploy::deploy"
}
