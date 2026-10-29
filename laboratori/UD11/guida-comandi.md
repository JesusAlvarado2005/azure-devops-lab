# Guida comandi — UD11

Azure Container Registry e Azure Container Apps: build locale, push in un registry privato, Container App con managed identity, ingress HTTPS, revision v1 → v2 e troubleshooting del target port.

⚠️ ACR Basic costa finché esiste: cleanup del Resource Group lo stesso giorno.

---

## 1. PREPARO

```bash
export COURSE_UD11="$HOME/workspace/azure-devops-k8s-01/UD11/partecipanti"
export LAB_REPO="$HOME/workspace/azure-devops-lab"
export LAB_LOCATION="northeurope"           # non westeurope
export LAB_RG="rg-ud11-containers"
export ACA_ENV="acaenv-ud11"
export ACA_APP="catalog-api-ud11"
export IMAGE_REPO="catalog-backend"
export ACR="acr$(date +%s)ud11"             # in un terminale nuovo rimettere lo STESSO nome, non rigenerarlo

az extension add --name containerapp --upgrade --yes        # esiste solo in preview
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.ContainerRegistry
az provider show --namespace Microsoft.App --query registrationState -o tsv   # aspettare Registered
```

---

## 2. BUILD LOCALE E PUSH

```bash
cd "$LAB_REPO/app/catalog-backend-cloud"
docker build -t catalog-backend:ud11-v1 .
docker run -d --rm --name catalog-backend-ud11-v1 -p 127.0.0.1:18000:8000 catalog-backend:ud11-v1
curl -s http://127.0.0.1:18000/health          # version v1
docker stop catalog-backend-ud11-v1

az group create --name "$LAB_RG" --location "$LAB_LOCATION" --tags Course=AZ104 UD=11 -o table
az acr create -g "$LAB_RG" -n "$ACR" --sku Basic -l "$LAB_LOCATION" --role-assignment-mode rbac -o table
export ACR_LOGIN=$(az acr show -n "$ACR" -g "$LAB_RG" --query loginServer -o tsv)   # letto, non costruito
az acr login --name "$ACR"                     # push con la MIA identità
export IMAGE_V1="$ACR_LOGIN/$IMAGE_REPO:v1"
docker tag catalog-backend:ud11-v1 "$IMAGE_V1"
docker push "$IMAGE_V1"
az acr repository show-tags -n "$ACR" --repository "$IMAGE_REPO" -o table
```

`registry/repository:tag` → `acr...azurecr.io` / `catalog-backend` / `v1`. Admin user **sempre false**.

---

## 3. CONTAINER APP

```bash
az containerapp env create -n "$ACA_ENV" -g "$LAB_RG" -l "$LAB_LOCATION"     # qualche minuto, crea anche Log Analytics

az containerapp create -n "$ACA_APP" -g "$LAB_RG" --environment "$ACA_ENV" \
  --image "$IMAGE_V1" --registry-server "$ACR_LOGIN" --registry-identity system \
  --ingress external --target-port 8000 \
  --env-vars APP_VERSION=v1 LOW_STOCK_THRESHOLD=5 RUNTIME_DIR=/tmp/runtime \
  --min-replicas 0 --max-replicas 1 --revision-suffix v1

export ACA_FQDN=$(az containerapp show -n "$ACA_APP" -g "$LAB_RG" --query properties.configuration.ingress.fqdn -o tsv)
curl -s "https://$ACA_FQDN/health"             # la prima volta può metterci un po' (scale da 0)
az containerapp revision list -n "$ACA_APP" -g "$LAB_RG" --query "[].{Name:name,Active:properties.active,Health:properties.healthState}" -o table
az containerapp logs show -n "$ACA_APP" -g "$LAB_RG" --tail 30
```

| Concetto | Cosa è |
|---|---|
| Environment | dove vivono le app |
| Container App | l'app: immagine, variabili, ingress, scaling |
| Revision | versione fissa della configurazione (`--v1`, `--v2`) |
| Replica | istanza che gira davvero |
| `--registry-identity system` | managed identity + AcrPull, niente password |

---

## 4. V2

```bash
# Dockerfile: APP_VERSION=v1 → v2
docker build -t catalog-backend:ud11-v2 .
export IMAGE_V2="$ACR_LOGIN/$IMAGE_REPO:v2"
docker tag catalog-backend:ud11-v2 "$IMAGE_V2" && docker push "$IMAGE_V2"
az containerapp update -n "$ACA_APP" -g "$LAB_RG" --image "$IMAGE_V2" --set-env-vars APP_VERSION=v2 --revision-suffix v2
```

Nuova immagine → nuova revision. In Single mode la v2 diventa l'unica attiva.

---

## 5. GUASTO TARGET PORT

```bash
az containerapp ingress update -n "$ACA_APP" -g "$LAB_RG" --target-port 9999 -o none
curl -i --max-time 20 "https://$ACA_FQDN/health"     # 503 upstream connect error ... Connection refused
# app Running, revision Healthy, log "listening on 0.0.0.0:8000" → ingress e app non coincidono
az containerapp ingress update -n "$ACA_APP" -g "$LAB_RG" --target-port 8000 -o none
```

Niente nuova immagine e niente push: era solo configurazione dell'ingress.

---

## 6. ELIMINO E CONFERMO

```bash
az resource list -g "$LAB_RG" -o table        # solo ACR, Log Analytics, Environment, Container App
az group delete --name "$LAB_RG" --yes --no-wait
az group exists --name "$LAB_RG"              # false quando ha finito, l'Environment ci mette parecchio
docker image rm catalog-backend:ud11-v1 catalog-backend:ud11-v2 "$IMAGE_V1" "$IMAGE_V2"
```

---

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `read: -p: no coprocess` | sintassi bash in zsh | export diretto |
| `cp: impossibile eseguire stat di '/app/...'` | `COURSE_UD11` vuota | rifare l'export |
| `cd: /app/catalog-backend-cloud` | `LAB_REPO` vuota dopo il riavvio | rifare tutti gli export |
| `zsh: 4.: comando non trovato` | incollato anche il titolo della guida | copiare solo i comandi |
| provider `NotRegistered` | Microsoft.App e ContainerRegistry mai usati | `az provider register` e aspettare |
