# Guida comandi — UD13

Terraform in pipeline, service connection WIF, ACR persistente e preparazione della CI del Catalogo prodotti. La pipeline IaC valida Terraform e distribuisce con Bicep; la CI testa, costruisce e pubblica l'immagine.

⚠️ A fine UD13 **non** si elimina `rg-ud13-15-delivery`, l'ACR, le service connection, le pipeline e l'agent: servono alla UD14. Si eliminano solo le risorse Terraform temporanee.

---

## 1. PREPARO

```bash
export COURSE_UD13="$HOME/workspace/azure-devops-k8s-01/UD13/partecipanti"
export LAB_REPO="$HOME/workspace/azure-devops-lab"
export LAB_SUBMISSION="$LAB_REPO/consegne/UD13"
mkdir -p "$LAB_SUBMISSION"
test -f "$COURSE_UD13/infra/bicep/delivery.bicep"
git -C "$LAB_REPO" rev-parse --show-toplevel
```

I modelli `00`–`03` sono già nella consegna. Nella seconda parte si aggiungono `04_PREPARAZIONE_CI.md` e `05_DOMANDE_CI.md`. Se esistono già non li sovrascrivo.

Su zsh `read -r -p "..."` dà `no coprocess`: uso export diretti.

---

## 2. TERRAFORM

```bash
cd "$LAB_REPO"
cp -n "$COURSE_UD13/infra/terraform/network.tf" infra/terraform/network.tf
cd infra/terraform

az account show --query "{Subscription:name,User:user.name}" -o table
export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
export TF_VAR_location="northeurope"                              # non westeurope
export TF_VAR_storage_account_name="stud13$(date +%s | tail -c 10)"

terraform init
terraform fmt
terraform validate
terraform plan -out=ud13.tfplan      # 4 to add: RG, storage, VNet, subnet
terraform apply ud13.tfplan
```

Verifico la rete:

```bash
az network vnet show -g rg-ud12-tf -n vnet-ud13 \
  --query "{Name:name,Address:addressSpace.addressPrefixes}" -o jsonc

az network vnet subnet show -g rg-ud12-tf --vnet-name vnet-ud13 --name snet-app \
  --query "{Name:name,Prefix:addressPrefixes[0]}" -o table
```

Poi distruggo solo l'infrastruttura temporanea:

```bash
terraform plan -destroy             # devono essere solo le 4 risorse dell'esercizio
terraform destroy
az group exists -n rg-ud12-tf       # false
```

Il codice `.tf` resta nel repo.

---

## 3. DELIVERY PERSISTENTE

```bash
export DELIVERY_RG="rg-ud13-15-delivery"
export DELIVERY_LOCATION="northeurope"

az group create -n "$DELIVERY_RG" -l "$DELIVERY_LOCATION" \
  --tags Course=AZ104 Purpose=FinalDelivery -o table
```

Questo Resource Group non si elimina.

---

## 4. BICEP

```bash
cd "$LAB_REPO"
cp -n "$COURSE_UD13/infra/bicep/delivery.bicep" infra/bicep/delivery.bicep
az bicep lint --file infra/bicep/delivery.bicep
```

Il nome ACR è `acrud1315` + `uniqueString(resourceGroup().id)`, quindi non lo scelgo a mano. SKU Basic, admin user `false`, `roleAssignmentMode: LegacyRegistryPermissions`.

Se la service connection non è utilizzabile posso creare l'ACR in locale, ma nella consegna resta un fallback e non una pipeline riuscita:

```bash
az deployment group what-if -g "$DELIVERY_RG" \
  --template-file infra/bicep/delivery.bicep --parameters location="$DELIVERY_LOCATION"

az deployment group create -n ud13-delivery-fallback -g "$DELIVERY_RG" \
  --template-file infra/bicep/delivery.bicep --parameters location="$DELIVERY_LOCATION" -o table
```

---

## 5. SERVICE CONNECTION ARM (portale)

```text
Project settings → Service connections → New service connection
→ Azure Resource Manager → App registration (automatic)
→ Credential: Workload identity federation
→ Scope: subscription del corso + Resource group rg-ud13-15-delivery
→ Name: sc-azure-ud13-15
→ "Grant access permission to all pipelines": NO
```

Se la creazione automatica WIF è bloccata dall'account, annoto `BLOCKED_BY_SERVICE_CONNECTION` e uso il fallback locale per l'ACR. Non creo client secret o PAT usati come credenziale Azure.

---

## 6. PIPELINE IAC

```bash
cd "$LAB_REPO"
cp -n "$COURSE_UD13/pipeline/azure-pipelines-iac.yml" pipelines/azure-pipelines-iac.yml
diff -u "$COURSE_UD13/pipeline/azure-pipelines-iac.yml" pipelines/azure-pipelines-iac.yml
```

Nel YAML: `trigger: none`, pool `pool-ud09-wsl`, `workspace: clean: all`, stage `Validate` e `Deploy`, `AzureCLI@2` con `sc-azure-ud13-15`. La location nel mio file è `northeurope`.

Commit:

```bash
git add infra/terraform/network.tf infra/bicep/delivery.bicep \
  pipelines/azure-pipelines-iac.yml
git commit -m "feat: add IaC validation pipeline baseline"
git push
```

Portale:

```text
Pipelines → New pipeline → GitHub → repository personale
→ Existing Azure Pipelines YAML file → /pipelines/azure-pipelines-iac.yml
```

La pipeline IaC resta manuale. Alla prima run autorizzo solo questa pipeline a usare `sc-azure-ud13-15`.

Nei log `Validate` cerco `Agent.Name`, `Agent.OS`, `Build.SourcesDirectory`, `terraform version`, `az version`, `az bicep version`, poi `fmt -check`, `init -backend=false`, `validate`, `az bicep lint`. In `Deploy` cerco what-if e deployment.

Verifico l'ACR senza fidarmi solo del verde:

```bash
export ACR_NAME=$(az acr list -g "$DELIVERY_RG" --query "[0].name" -o tsv)
az acr list -g "$DELIVERY_RG" \
  --query "[].{Name:name,SKU:sku.name,Admin:adminUserEnabled}" -o table
az acr show -n "$ACR_NAME" -g "$DELIVERY_RG" --query roleAssignmentMode -o tsv
az acr show -n "$ACR_NAME" --query loginServer -o tsv
```

Atteso: SKU Basic, Admin false, `LegacyRegistryPermissions`.

---

## 7. LAB AUTONOMO — ERRORE DI PERCORSO

```bash
cd "$LAB_REPO"
git switch -c fix/ud13-pipeline-path
# in pipelines/azure-pipelines-iac.yml:
# infra/bicep/delivery.bicep → infra/bicep/delivery-NON-ESISTE.bicep
git add pipelines/azure-pipelines-iac.yml
git commit -m "test: introduce UD13 pipeline path error"
git push -u origin fix/ud13-pipeline-path
```

Avvio la pipeline a mano su questa branch. Il primo step rosso è `Bicep lint` nel job `ValidateIaC` dello stage `Validate`:

```text
ERROR: An error occurred reading file. Could not find file '.../infra/bicep/delivery-NON-ESISTE.bicep'.
```

Non è Azure, non è l'agent e non è la service connection: è il path nel repository. Correggo solo quello:

```bash
# rimetto infra/bicep/delivery.bicep
git add pipelines/azure-pipelines-iac.yml
git commit -m "fix: restore Bicep pipeline path"
git push
```

Rieseguo sulla stessa branch, poi apro la PR verso `main` e faccio il merge. Dopo il merge la pipeline IaC non parte da sola perché ha `trigger: none`.

---

## 8. PREPARAZIONE CI

### 8.1 App e test locali

```bash
cd "$LAB_REPO"
cp -R "$COURSE_UD13/app/catalog-backend-ci" app/
python3 -m unittest discover -s app/catalog-backend-ci/tests -v   # 3 test, OK
```

### 8.2 Docker locale

```bash
docker build -t catalog-backend:ud13-local app/catalog-backend-ci
docker run -d --rm --name catalog-ud13-local -p 127.0.0.1:18014:8000 \
  catalog-backend:ud13-local
curl -s http://127.0.0.1:18014/health | python3 -m json.tool   # status ok, version ci-v1
docker stop catalog-ud13-local
```

### 8.3 Docker Registry service connection

```text
Project settings → Service connections → New service connection
→ Docker Registry → Azure Container Registry
→ Authentication: Workload identity federation
→ subscription del corso + ACR creato in UD13
→ Name: sc-acr-ud14
→ accesso a tutte le pipeline: NO
```

Se WIF è bloccata annoto `BLOCKED_BY_DOCKER_SERVICE_CONNECTION`. Admin user ACR resta `false`, niente password nel YAML.

### 8.4 YAML e pipeline

```bash
cp -n "$COURSE_UD13/pipeline/azure-pipelines-ci.yml" pipelines/azure-pipelines-ci.yml
cp -n "$COURSE_UD13/pipeline/azure-pipelines-ci-selfhosted.yml" pipelines/azure-pipelines-ci-selfhosted.yml

git add app/catalog-backend-ci pipelines/azure-pipelines-ci.yml \
  pipelines/azure-pipelines-ci-selfhosted.yml
git commit -m "feat: add catalog CI pipeline"
git push
```

Scelgo **un solo** file:

| Stato Microsoft-hosted | File | Modalità |
|---|---|---|
| `MICROSOFT_HOSTED_READY` | `azure-pipelines-ci.yml` | `MICROSOFT_HOSTED` |
| non disponibile | `azure-pipelines-ci-selfhosted.yml` | `SELF_HOSTED_FALLBACK` |

Nel mio caso lo stato è `MICROSOFT_HOSTED_PENDING`, quindi uso il fallback con `pool-ud09-wsl` e `workspace: clean: all`. Prima avvio l'agent in un terminale dedicato:

```bash
cd ~/azdo-agent && ./run.sh      # Listening for Jobs
```

Portale: `Pipelines → New pipeline → GitHub → Existing Azure Pipelines YAML file` e scelgo il file. Autorizzo solo questa pipeline a usare `sc-acr-ud14`.

La prima run deve fare:

```text
Test (PythonTests) → BuildPush (DockerBuild)
```

Se `Test` fallisce, `BuildPush` non parte. Nei log leggo `Agent.Name`, `Agent.OS`, `Agent.MachineName`, `python3 --version` o `docker --version`. Nel fallback self-hosted `Agent.MachineName` è la mia macchina; con Microsoft-hosted i due job possono avere MachineName diversi.

Nel mio caso la build 6 è fallita in `BuildPush` con `Endpoint auth data not present`, perché `sc-acr-ud14` non era ancora autorizzata per la pipeline. Dopo l'autorizzazione la build 7 è riuscita e ha pubblicato `catalog-backend:7`. Dopo il merge la build 10 è partita da sola su `main` e ha pubblicato `catalog-backend:10`.

---

## 9. GIT

```bash
git status
git log --oneline -5
```

Nel commit non finiscono state, `.terraform/`, `*.tfplan`, segreti o token. L'ACR e le immagini restano per la UD14.

---

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `Could not find file '.../delivery-NON-ESISTE.bicep'` | path sbagliato nel YAML, non Azure | ripristinare `infra/bicep/delivery.bicep` |
| `terraform: command not found` nell'agent | tool non nel PATH dell'utente che esegue l'agent | verificare `terraform version` da WSL e riavviare `run.sh` |
| `Job` in attesa | agent Offline o pool sbagliato | `./run.sh` e controllare `pool-ud09-wsl` |
| `Endpoint auth data not present` in `Docker@2` | la service connection `sc-acr-ud14` non è ancora autorizzata per quella pipeline | autorizzare solo la pipeline e rieseguire |
| `401/403` sul push ACR | service connection o ruolo AcrPush mancante | autorizzare la pipeline e assegnare AcrPush all'identità |
| `westeurope` rifiuta risorse nuove | limite della subscription | usare `northeurope` |
