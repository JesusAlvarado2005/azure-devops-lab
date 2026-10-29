# UD12 — Consegna LAB guidato

## Preparazione

- materiali UD12: `~/workspace/azure-devops-k8s-01/UD12/partecipanti`
- repository personale: `~/workspace/azure-devops-lab`
- directory `infra/bicep`: creata con main.bicep
- directory `infra/terraform`: creata con main.tf, outputs.tf, providers.tf, variables.tf, versions.tf
- directory consegne: `consegne/UD12` con i 4 modelli

## Azure

- subscription verificata: Azure subscription 1
- identità verificata: sì, il mio utente

## Bicep

- Bicep version: 0.48.1, già installato con Azure CLI quindi niente reinstallazione
- lint: nessun errore
- Resource Group: rg-ud12-bicep in northeurope con tag Course=AZ104 UD=12 ManagedBy=CLI
- Storage Account: stud12b93265947
- What-If change type: Create su Microsoft.Storage/storageAccounts stud12b93265947, è quello che c'è nel file
- deployment: ud12-bicep-deploy Succeeded
- output `storageAccountName`: stud12b93265947
- output `blobEndpoint`: https://stud12b93265947.blob.core.windows.net/
- verifica CLI: northeurope, Standard_LRS, TLS1_2, PublicBlob False, uguale al file
- Resource Group Bicep eliminato: sì, dentro c'era solo lo storage dell'esercizio
- `az group exists`: false

Ho usato northeurope e non westeurope come dice la guida, perché in UD07 westeurope non mi accettava risorse nuove.

## Terraform

- Terraform version: 1.17.0, già presente e sopra la 1.6 quindi niente installazione
- provider AzureRM: 5.11.0 con vincolo ~> 5.4
- `terraform init`: ok, creati `.terraform/` e `.terraform.lock.hcl`
- `terraform fmt -check`: nessuna differenza
- `terraform validate`: Success!
- plan add: 2
- plan change: 0
- plan destroy: 0
- apply: del piano salvato ud12.tfplan, ok
- output Resource Group: rg-ud12-tf
- output Storage: stud12t93266025
- verifica CLI: rg-ud12-tf in northeurope con tag Course, UD e ManagedBy=Terraform, storage Standard_LRS in northeurope
- `terraform state list`: azurerm_resource_group.lab e azurerm_storage_account.lab

Il Subscription ID l'ho passato con `ARM_SUBSCRIPTION_ID` e la regione con `TF_VAR_location=northeurope`, niente nei file .tf.

## Fine LAB guidato

- risorse Terraform mantenute per LAB autonomo: sì
