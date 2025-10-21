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

enable GKE at https://console.developers.google.com/apis/api/container.googleapis.com/overview?project=bids-jupyterhub

Create cluster with OpenTofu (`nox tf`)
