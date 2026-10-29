# UD11 — Consegna laboratorio guidato

## Preflight

- Azure: loggato, Azure subscription 1
- Docker: 29.9.2, daemon ok
- containerapp extension: installata, è solo in preview
- Microsoft.App: NotRegistered all'inizio, registrato e poi Registered
- Microsoft.OperationalInsights: Registered

Anche Microsoft.ContainerRegistry era NotRegistered, l'ho registrato prima di creare l'ACR. Location northeurope perché westeurope in UD07 non mi accettava risorse nuove.

## ACR

- nome: acr1793119683ud11
- SKU: Basic
- login server: acr1793119683ud11.azurecr.io
- repository: catalog-backend
- tag v1: sì
- tag v2: sì
- admin user abilitato: NO

roleAssignmentMode risulta LegacyRegistryPermissions, cioè la modalità RBAC classica dove vale AcrPull

## v1

- local test: `docker run` su 127.0.0.1:18000, `/health` version v1
- push: `az acr login` con la mia identità poi tag e `docker push`
- ACR tag: v1
- ACA environment: acaenv-ud11, Succeeded
- Container App: catalog-api-ud11
- managed identity: SystemAssigned
- registry identity: system, sul login server dell'ACR
- ingress: external
- target port: 8000
- FQDN: catalog-api-ud11.calmrock-b45a45b3.northeurope.azurecontainerapps.io
- health: 200, status ok
- version: v1
- revision: catalog-api-ud11--v1, attiva e Healthy con 1 replica
- logs: `Catalog backend v1 listening on http://0.0.0.0:8000 threshold=5` e /api/products con 200 e count 4

## v2

- Dockerfile version: cambiato APP_VERSION=v1 in v2
- local test: su 127.0.0.1:18001, `/health` version v2
- push: tag v2 e `docker push`
- ACR tag: v2 e v1
- update: `az containerapp update` con l'immagine v2, APP_VERSION=v2 e suffisso v2
- revision: catalog-api-ud11--v2 attiva e Healthy, in Single mode la v1 non è più attiva
- health: 200
- version: v2

## Scaling

- minReplicas: 0
- maxReplicas: 1
- scale-to-zero possibile: sì, senza traffico scende a 0 repliche dopo il cooldown di 300 secondi
