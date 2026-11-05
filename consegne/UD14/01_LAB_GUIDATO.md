# UD14 — Consegna LAB guidato

## Controlli iniziali

- ACR: `acrud1315iwmnnz3ek6q7o`, località `northeurope`, `Admin = false`, `RoleAssignmentMode = LegacyRegistryPermissions`
- `LegacyRegistryPermissions`: confermato con `az acr show`; l'ACR non usa il nuovo modello RBAC per il registry
- `sc-azure-ud13-15`: service connection Azure Resource Manager con workload identity federation; il service principal associato è `sc-azure-ud13-15` (appId `5583c139-034d-45f0-a07f-96cdb90ac529`, objectId `7ddcc4d7-1b4e-458a-b733-d5a9a186d118`)
- `AcrPush`: assegnato sull'ACR a `sc-azure-ud13-15` (principal `7ddcc4d7-1b4e-458a-b733-d5a9a186d118`)
- Storage state: `sttf156e08fcb1163b497b`, `Standard_LRS`, TLS 1.2, accesso pubblico ai blob disabilitato
- container state: `tfstate`
- `Storage Blob Data Contributor`: assegnato sul container `tfstate` al service principal `sc-azure-ud13-15` (objectId `7ddcc4d7-1b4e-458a-b733-d5a9a186d118`). La prima assegnazione era stata fatta per errore sull'appId `5583c139-034d-45f0-a07f-96cdb90ac529`, che non è un principal: il primo stage `IaC` falliva per 403 sul blob dello state. Dopo la correzione il SP può leggere e scrivere `ud15.tfstate`.
- managed identity: `id-ud15-acrpull`, principal `2ea95100-d52a-46ab-9919-d4f87fcb019b`, client `ec1966a8-c6ed-4b00-9146-ad59814994d2`
- `AcrPull`: assegnato sull'ACR a `id-ud15-acrpull` (principal `2ea95100-d52a-46ab-9919-d4f87fcb019b`)
- Agent: `linux-ud14-jj` (AgentId 18), pool `pool-ud09-wsl`, macchina `jj-host`, online il 2026-11-05 alle 08:13Z

## Terraform

- init: `terraform init -backend=false` locale riuscito; provider `hashicorp/azurerm` versione 5.4.0
- validate: `Success! The configuration is valid.`
- plan iniziale: eseguito dallo stage `IaC` della pipeline di delivery; al momento del piano Environment e Container App non esistevano (verificato con `az containerapp env list` e `az containerapp list`, entrambi vuoti prima della run)
- apply: eseguito dallo stage `Deploy`; a fine stage esistono `acaenv-ud15` e `catalog-api-ud15` con immagine `catalog-backend:26` e `target_port = 8000`
- state remoto: blob `ud15.tfstate` nel container `tfstate` di `sttf156e08fcb1163b497b`, ultima modifica `2026-11-05T10:14:46Z`, 16.337 byte

## Pipeline

- Build ID: **26** (tag immagine `26`)
- IaC: Succeeded (10:09:54Z → 10:10:26Z)
- Test: Succeeded (10:10:56Z → 10:11:05Z)
- BuildPush: Succeeded (10:11:12Z → 10:11:44Z)
- Deploy: Succeeded (10:11:50Z → 10:14:54Z)
- Smoke: Succeeded (10:15:00Z → 10:15:32Z)

## Deployment

- image tag: `26` — `acrud1315iwmnnz3ek6q7o.azurecr.io/catalog-backend:26`
- FQDN: `catalog-api-ud15.wonderfuldesert-24121356.northeurope.azurecontainerapps.io`
- APP_VERSION: `26`
- revision: `catalog-api-ud15--lyigbdm`, attiva, creata `2026-11-05T10:14:36Z`, 1 replica
- health: HTTP 200, `{"status":"ok","service":"catalog-backend","version":"26"}` — la versione corrisponde al Build ID della run
