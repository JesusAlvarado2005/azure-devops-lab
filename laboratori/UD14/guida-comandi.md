# UD14 — Guida comandi (blocco CI)

Questa guida copre la UD14 completa: verifica della CI esistente, test rosso/verde, nuova run e la parte Continuous Delivery con Terraform, state remoto, Azure Container Apps e diagnosi dell'errore di target port.

## 1. Branch di lavoro

```bash
cd "$LAB_REPO"
git switch main
git pull --ff-only
git switch -c feature/ud14-ci-v2
```

Il branch tiene separati i due commit del laboratorio: prima l'app, poi il test.

## 2. Modifica l'applicazione

In `app/catalog-backend-ci/server.py`:

```python
APP_VERSION = os.getenv("APP_VERSION", "ci-v2")
```

Per coerenza ho aggiornato anche `APP_VERSION` nel `Dockerfile`, così l'immagine non continua a dichiarare `ci-v1`.

```bash
git add app/catalog-backend-ci/server.py app/catalog-backend-ci/Dockerfile
git commit -m "feat: bump catalog version to ci-v2"
```

## 3. Verifica il test rosso

```bash
python3 -m unittest discover \
  -s app/catalog-backend-ci/tests \
  -v
```

Atteso: `test_health_version` fallisce con `AssertionError: 'ci-v2' != 'ci-v1'`. È corretto: l'app è cambiata, il criterio del test no.

## 4. Allinea il test

In `app/catalog-backend-ci/tests/test_backend.py`:

```python
self.assertEqual(payload["version"], "ci-v2")
```

```bash
python3 -m unittest discover \
  -s app/catalog-backend-ci/tests \
  -v
```

Atteso: 3 test `ok`, `OK`.

```bash
git add app/catalog-backend-ci/tests/test_backend.py
git commit -m "test: align expected catalog version"
```

## 5. Prova locale dell'immagine

```bash
docker build -t catalog-backend:ud14-local app/catalog-backend-ci
docker run -d --name catalog-ud14-local -p 127.0.0.1:18015:8000 catalog-backend:ud14-local
curl -s http://127.0.0.1:18015/health
docker rm -f catalog-ud14-local
```

Atteso: `{"status": "ok", "service": "catalog-backend", "version": "ci-v2"}`.

## 6. Push, PR e merge

```bash
git push -u origin feature/ud14-ci-v2
```

Poi apro la PR verso `main` e completo il merge. Il YAML `pipelines/azure-pipelines-ci-selfhosted.yml` ha `trigger: main`, quindi la CI parte con il merge su `main`, non con la sola PR.

Nel mio caso la PR è la #5, mergiata il 2026-11-02 con merge commit `117bbeb`.

Con `UD14_AGENT_MODE=SELF_HOSTED_FALLBACK` l'agent deve essere online prima della run:

```bash
cd ~/azdo-agent && ./run.sh
```

Nel pool `pool-ud09-wsl` deve risultare `Online`. Il vecchio agent `wsl-ud09-jesusalvaradojeanfra` non era più presente su questa macchina, quindi ho registrato `linux-ud14-jj` in `/home/jj/azdo-agent`.

## 7. Verifica run e ACR

Nel portale seguo:

```text
Stage Test
→ Job PythonTests
→ Run Python tests

Stage BuildPush
→ Job DockerBuild
→ Docker@2
```

Poi:

```bash
export ACR_NAME=$(az acr list \
  --resource-group rg-ud13-15-delivery \
  --query "[0].name" \
  --output tsv)
```

```bash
az acr repository show-tags \
  --name "$ACR_NAME" \
  --repository catalog-backend \
  --orderby time_desc \
  --output table
```

Deve comparire il nuovo tag uguale al Build ID della run. Dopo il merge della PR #5 la build 14 (`20261102.3`) ha pubblicato il tag `14`; in ACR sono presenti anche `11`, `10` e `7`.

## 8. Nessun cleanup

Non eliminare ACR, immagini, `sc-acr-ud14`, `sc-azure-ud13-15`, agent o pipeline: servono al blocco CD.

---

# Parte CD — Terraform, ACR e Azure Container Apps

## 9. Controlli iniziali

```bash
export DELIVERY_RG=rg-ud13-15-delivery
export ACR_NAME=$(az acr list \
  --resource-group "$DELIVERY_RG" \
  --query "[0].name" \
  --output tsv)

az acr show \
  --name "$ACR_NAME" \
  --resource-group "$DELIVERY_RG" \
  --query "{Name:name,Location:location,Admin:adminUserEnabled,RoleAssignmentMode:roleAssignmentMode}" \
  --output table
```

Atteso: `Admin = false`, `RoleAssignmentMode = LegacyRegistryPermissions`.

```bash
az identity show \
  --name id-ud15-acrpull \
  --resource-group "$DELIVERY_RG" \
  --query "{name:name,principalId:principalId,clientId:clientId}" \
  --output table
```

Ruoli sul registro e sul container dello state:

```bash
az role assignment list \
  --scope "/subscriptions/6e08fcb1-163b-497b-a25f-e1303a09c245/resourceGroups/$DELIVERY_RG/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME" \
  --query "[].{principal:principalId,role:roleDefinitionName}" \
  --output table

az role assignment list \
  --scope "/subscriptions/6e08fcb1-163b-497b-a25f-e1303a09c245/resourceGroups/$DELIVERY_RG/providers/Microsoft.Storage/storageAccounts/sttf156e08fcb1163b497b/blobServices/default/containers/tfstate" \
  --query "[].{principal:principalId,role:roleDefinitionName}" \
  --output table
```

Atteso: `AcrPush` sul registro al service principal di `sc-azure-ud13-15`, `AcrPull` alla managed identity, `Storage Blob Data Contributor` sul container `tfstate` **all'object id del service principal**.

## 10. Terraform in locale

```bash
cd infra/terraform/ud15

terraform init -backend=false -input=false
terraform fmt -check
terraform validate
```

Il backend vero viene configurato dalla pipeline con `-backend-config`; in locale `-backend=false` serve solo a validare la configurazione.

## 11. Pipeline di delivery

File: `pipelines/azure-pipelines-delivery.yml`. Il trigger è su `main`, quindi ogni merge fa partire la delivery senza cliccare **Run**.

Stage:

```text
IaC       → terraform init, fmt, validate, plan
Test      → unittest Python
BuildPush → docker build + docker push su ACR, tag = Build ID
Deploy    → terraform init + plan + apply
Smoke     → curl https://$FQDN/health e confronto con il Build ID
```

Verifica che il pool sia quello dell'agent:

```bash
grep -n "name: pool-ud09-wsl" pipelines/azure-pipelines-delivery.yml
```

Se la run fallisce subito con `Could not find a pool with name ...`, il YAML contiene il nome della pipeline al posto del pool: riportare `pool-ud09-wsl`.

## 12. Verifica del deployment

```bash
az containerapp env list --query "[].{name:name,stato:properties.provisioningState}" -o table
az containerapp list --query "[].{name:name,fqdn:properties.configuration.ingress.fqdn,targetPort:properties.configuration.ingress.targetPort}" -o table
```

```bash
FQDN=$(az containerapp show \
  --name catalog-api-ud15 \
  --resource-group "$DELIVERY_RG" \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

curl -s "https://$FQDN/health" | python3 -m json.tool

az containerapp revision list \
  --name catalog-api-ud15 \
  --resource-group "$DELIVERY_RG" \
  --query "[].{name:name,active:properties.active,health:properties.healthState,traffic:properties.trafficWeight,image:properties.template.containers[0].image,created:properties.createdTime}" \
  --output table

az acr repository show-tags \
  --name "$ACR_NAME" \
  --repository catalog-backend \
  --orderby time_desc \
  --top 5 \
  --output table

az storage blob show \
  --account-name sttf156e08fcb1163b497b \
  --container-name tfstate \
  --name ud15.tfstate \
  --auth-mode key \
  --query "{modified:properties.lastModified,size:properties.contentLength}" \
  --output table
```

La versione in `/health` deve coincidere con il tag dell'immagine e con il Build ID della run.

## 13. Esperimento target port

```bash
cd "$LAB_REPO"
git switch main
git pull --ff-only
git switch -c fix/ud15-target-port
```

In `pipelines/azure-pipelines-delivery.yml`:

```yaml
targetPort: '9999'
```

```bash
git add pipelines/azure-pipelines-delivery.yml
git commit -m "test: introduce wrong target port"
git push -u origin fix/ud15-target-port
```

Apro la PR, faccio il merge su `main` e seguo la run. Esito osservato: `IaC`, `Test`, `BuildPush`, `Deploy` verdi; `Smoke` rosso.

Evidenze:

```bash
az containerapp ingress show \
  --name catalog-api-ud15 \
  --resource-group "$DELIVERY_RG" \
  --query "{External:external,TargetPort:targetPort,FQDN:fqdn}" \
  --output table

az containerapp revision list \
  --name catalog-api-ud15 \
  --resource-group "$DELIVERY_RG" \
  --query "[].{name:name,health:properties.healthState,running:properties.runningState,image:properties.template.containers[0].image}" \
  --output table

az containerapp logs show \
  --name catalog-api-ud15 \
  --resource-group "$DELIVERY_RG" \
  --tail 30
```

Nel log compare `Catalog backend <tag> listening on 0.0.0.0:8000`: l'app ascolta su `8000`, l'ingress punta a `9999`, la revision nuova resta `Activating` e il traffico resta sulla precedente.

## 14. Correzione

```bash
git switch main
git pull --ff-only
git switch -c fix/ud15-target-port-correct
```

Ripristino `targetPort: '8000'`, commit `fix: restore container app target port`, push, PR e merge.

Con `revision_mode = Single` la revision precedente continua a rispondere finché la nuova non è pronta. Se lo `Smoke` fa un solo `curl`, può leggere la versione vecchia e fallire anche con la configurazione corretta. Il test va quindi reso paziente: ripetere `curl /health` finché `version` non coincide con il Build ID.

```bash
for attempt in $(seq 1 40); do
  RESPONSE=$(curl --fail --silent --show-error "https://$FQDN/health" || true)
  VERSION=$(echo "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("version",""))' 2>/dev/null || true)
  echo "tentativo $attempt/40: versione '${VERSION:-nessuna}', attesa '$(imageTag)'"
  [ "$VERSION" = "$(imageTag)" ] && exit 0
  sleep 5
done
exit 1
```

Con questa correzione la run finale arriva a `Smoke → succeeded` e `/health` restituisce la versione del Build ID.

## 15. Cleanup (non eseguito)

Il cleanup della delivery è la pipeline `pipelines/azure-pipelines-cleanup.yml` con `terraform destroy`: elimina solo la Container App e il Container App Environment. ACR, Storage Account, managed identity, resource group, service connection e agent restano.

In questa sessione il cleanup **non** è stato eseguito: le risorse servono ancora. Prima di lanciarlo verificare che non ci siano altre UD che usano ACR o lo state.

## Errori incontrati nella CD

| Errore | Causa | Soluzione |
|---|---|---|
| `Could not find a pool with name ud14-delivery` | il nome della pipeline era finito nel campo `pool` del YAML | riportare `pool: name: pool-ud09-wsl` |
| `IaC` fallisce in pochi secondi con 403 sul blob dello state | `Storage Blob Data Contributor` assegnato all'appId dell'app invece che all'object id del service principal | assegnare il ruolo a `7ddcc4d7-1b4e-458a-b733-d5a9a186d118` |
| `Smoke` fallisce con `targetPort 9999` | porta dell'ingress diversa dalla porta di ascolto (`8000`) | ripristinare `targetPort: '8000'` |
| `Smoke` fallisce anche con `targetPort 8000` | race: la revision precedente serve ancora mentre la nuova è `Activating` | ripetere il controllo di `/health` finché la versione coincide con il Build ID |
| `az storage blob show` risponde 403 come utente | l'utente non ha un ruolo dati sullo storage | usare `--auth-mode key` per la verifica manuale, senza cambiare il backend |

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `test_health_version` fallisce con `'ci-v2' != 'ci-v1'` | il test prevedeva ancora la versione vecchia | aggiornare l'aspettativa a `ci-v2` |
| `Endpoint auth data not present` in `Docker@2` | service connection non autorizzata per la pipeline | autorizzare `sc-acr-ud14` solo su `ud13-ci` |
| `401` o `403` sul push ACR | ruolo `AcrPush` o service connection mancante | controllare identità, ruolo e autorizzazione |
| Job in attesa | agent offline o pool sbagliato | avviare `./run.sh` e verificare `pool-ud09-wsl` |
| `cd: /home/jj_yts/azdo-agent: file o directory non esistente` | l'agent della UD13 era nel WSL, non in questo Linux | aprire WSL oppure registrare un agent Linux in `~/azdo-agent` |
| `docker: command not found` | Docker non avviato o non nel PATH dell'agent | avviare Docker e controllare l'ambiente dell'agent |
| file vecchi nella run | workspace self-hosted non pulito | usare `workspace: clean: all` e `checkout` pulito |
