# Notes from deployment

First step: [setup sops](https://github.com/getsops/sops?tab=readme-ov-file#encrypting-using-gcp-kms)

GCP Project: `bids-jupyterhub`

```
gcloud kms keyrings create sops --location global
gcloud kms keys create sops-key --location global --keyring sops --purpose encryption
gcloud kms keys list --location global --keyring sops
```

Create bucket for OpenTofu state:

```
gcloud storage buckets create --public-access-prevention gs://tf-state-bids-hub-demo 
```

## General design

1. OpenTofu to create clusters
1. OpenTofu cluster deploy includes cert-manager
1. each cluster deploys a 'support' chart with ingress controller, analytics
1. hubs are deployed in namespaces on clusters (one or more per cluster)

Details:

- nox encapsulates steps
- sops encrypts secrets
- deploy from GitHub Actions
