# UD14 — Consegna LAB guidato

## Controlli iniziali

- ACR: `acrud1315iwmnnz3ek6q7o`, località `northeurope`, `Admin = false`, `RoleAssignmentMode = LegacyRegistryPermissions`
- `LegacyRegistryPermissions`: confermato con `az acr show`; l'ACR non usa il nuovo modello RBAC per il registry
- `sc-azure-ud13-15`: service connection Azure Resource Manager con workload identity federation; il service principal associato è `sc-azure-ud13-15` (appId `5583c139-034d-45f0-a07f-96cdb90ac529`, objectId `7ddcc4d7-1b4e-458a-b733-d5a9a186d118`)
- `AcrPush`: assegnato sull'ACR a `sc-azure-ud13-15` (principal `7ddcc4d7-1b4e-458a-b733-d5a9a186d118`)
- Storage state: `sttf156e08fcb1163b497b`, `Standard_LRS`, TLS 1.2, accesso pubblico ai blob disabilitato
- container state: `tfstate`
- `Storage Blob Data Contributor`: assegnato sul container `tfstate` a `sc-azure-ud13-15` (principal `5583c139-034d-45f0-a07f-96cdb90ac529`)
- managed identity: `id-ud15-acrpull`, principal `2ea95100-d52a-46ab-9919-d4f87fcb019b`, client `ec1966a8-c6ed-4b00-9146-ad59814994d2`
- `AcrPull`: assegnato sull'ACR a `id-ud15-acrpull` (principal `2ea95100-d52a-46ab-9919-d4f87fcb019b`)
- Agent: `linux-ud14-jj` (AgentId 18), pool `pool-ud09-wsl`, macchina `jj-host`, online il 2026-11-05 alle 08:13Z

## Terraform

- init: `terraform init -backend=false` riuscito; provider `hashicorp/azurerm` versione 5.4.0
- validate: `Success! The configuration is valid.`
- plan iniziale: eseguito dallo stage `IaC` della pipeline di delivery
- apply: eseguito dallo stage `Deploy` della pipeline di delivery
- state remoto: blob `ud15.tfstate` nel container `tfstate` dello storage account `sttf156e08fcb1163b497b`

## Pipeline

- Build ID: da registrare dopo la run
- IaC: da registrare dopo la run
- Test: da registrare dopo la run
- BuildPush: da registrare dopo la run
- Deploy: da registrare dopo la run
- Smoke: da registrare dopo la run

## Deployment

- image tag: da registrare dopo la run
- FQDN: da registrare dopo la run
- APP_VERSION: da registrare dopo la run
- revision: da registrare dopo la run
- health: da registrare dopo la run
