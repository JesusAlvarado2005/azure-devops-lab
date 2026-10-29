# Guida comandi — UD12

Infrastructure as Code con Bicep e Terraform: scrivo → valido → vedo cosa cambierà → applico → verifico → distruggo. Il codice resta nel repo per le pipeline di UD13–UD14.

---

## 1. PREPARO

```bash
export COURSE_UD12="$HOME/workspace/azure-devops-k8s-01/UD12/partecipanti"
export LAB_REPO="$HOME/workspace/azure-devops-lab"
mkdir -p "$LAB_REPO/infra/bicep" "$LAB_REPO/infra/terraform"
cp -n "$COURSE_UD12/infra/bicep/main.bicep" "$LAB_REPO/infra/bicep/"
cp -n "$COURSE_UD12/infra/terraform/"*.tf "$LAB_REPO/infra/terraform/"

az bicep version          # se c'è già non reinstallare
terraform version         # >= 1.6, su Fedora non serve il repository apt della guida
```

---

## 2. BICEP

```bash
export BICEP_RG="rg-ud12-bicep" LAB_LOCATION="northeurope"
export BICEP_STG="stud12b$(date +%s | tail -c 9)"
az group create -n "$BICEP_RG" -l "$LAB_LOCATION" --tags Course=AZ104 UD=12 ManagedBy=CLI -o table

cd "$LAB_REPO/infra/bicep"
az bicep lint --file main.bicep
az deployment group what-if -g "$BICEP_RG" --template-file main.bicep --parameters location="$LAB_LOCATION" storageName="$BICEP_STG"
az deployment group create -n ud12-bicep-deploy -g "$BICEP_RG" --template-file main.bicep --parameters location="$LAB_LOCATION" storageName="$BICEP_STG" -o table
az deployment group show -n ud12-bicep-deploy -g "$BICEP_RG" --query properties.outputs -o jsonc

az group delete -n "$BICEP_RG" --yes          # le risorse vanno, main.bicep resta
```

- **What-If** non crea niente: dice Create/Modify/Delete. Domanda giusta: "è quello che ho scritto nel file?"
- `storage` nel file = nome simbolico, `stud12b...` = nome reale in Azure
- `@2023-05-01` = versione API, non data di creazione

---

## 3. TERRAFORM

```bash
cd "$LAB_REPO/infra/terraform"
export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)    # mai nei file .tf
export TF_VAR_location="northeurope"                                # il default è westeurope
export TF_VAR_storage_account_name="stud12t$(date +%s | tail -c 9)"

terraform init                   # provider AzureRM + .terraform.lock.hcl
terraform fmt && terraform fmt -check
terraform validate
terraform plan -out=ud12.tfplan  # Plan: 2 to add, 0 to change, 0 to destroy
terraform apply ud12.tfplan      # applica ESATTAMENTE il piano letto
terraform output
terraform state list             # azurerm_resource_group.lab, azurerm_storage_account.lab
```

In un terminale nuovo: `export TF_VAR_storage_account_name=$(terraform output -raw storage_account_name)`.

| Nel codice | Cosa è |
|---|---|
| `azurerm_resource_group` | tipo di risorsa |
| `lab` | nome simbolico |
| `var.resource_group_name` | variabile |
| `rg-ud12-tf` | nome reale in Azure |
| `azurerm_resource_group.lab.name` | riferimento → dipendenza implicita |

---

## 4. MODIFICA, ERRORE, DESTROY

```bash
# tag Environment = "Training" → plan: 0 add, 1 change, 0 destroy (update in-place)
terraform plan -out=ud12-change.tfplan && terraform apply ud12-change.tfplan

# azurerm_resource_group.training.location → validate: "Reference to undeclared resource"

terraform plan -destroy          # solo le 2 risorse attese?
terraform destroy                # elimina in Azure, i file .tf restano
az group exists -n rg-ud12-tf    # false
```

⚠️ Se il plan mostra **destroy** che non ti aspetti, non fare apply.

---

## 5. GIT

`.gitignore`: `**/.terraform/`, `*.tfstate`, `*.tfstate.*`, `*.tfplan`. Si committano i `.tf`, `main.bicep` e `.terraform.lock.hcl`. **Mai lo state.**

---

## 6. GATE 2

```bash
terraform version; az version; az bicep version; git --version; python3 --version; docker --version
cd ~/azdo-agent && ./run.sh      # rilegge i tool, niente config.sh né PAT nuovo
```

Microsoft-hosted: nuova macchina a ogni job, i tool vanno verificati nella pipeline.
