# UD12 — Consegna LAB autonomo

## Baseline

- `terraform plan`: No changes
- stato atteso: codice, state e Azure uguali
- stato osservato: uguali, nessuna modifica proposta

## Modifica

- tag aggiunto: Environment = "Training" sullo storage
- plan add: 0
- plan change: 1
- plan destroy: 0
- motivazione change e non recreate: i tag si possono cambiare sulla risorsa esistente, quindi Terraform fa update in-place, la ricrea solo se cambia una cosa che non si può modificare come il nome o la location

## Apply e verifica

- apply: del piano ud12-change.tfplan, 0 added 1 changed 0 destroyed
- tag verificato con Azure CLI: sì, Environment Training insieme a Course, UD e ManagedBy

## Errore controllato

- riferimento errato: `azurerm_resource_group.training.location` al posto di `lab`
- messaggio `terraform validate`: `Reference to undeclared resource`, A managed resource "azurerm_resource_group" "training" has not been declared in the root module, main.tf riga 15
- causa: nel codice c'è solo il resource group lab, training non esiste
- correzione: rimesso `azurerm_resource_group.lab.location`
- validate finale: Success! e plan senza modifiche

## Git

- `.gitignore` verificato: c'erano già `.terraform/`, `*.tfstate` e `*.tfstate.*`, ho aggiunto `*.tfplan`
- state non committato: sì, nel commit solo .gitignore, main.bicep, i 5 file .tf e il lock file
- lock file: committato
- commit: feat: add Bicep and Terraform infrastructure baseline
- push/PR: push su main

## Cleanup Terraform

- `terraform plan -destroy`: 2 to destroy
- risorse previste: azurerm_storage_account.lab e azurerm_resource_group.lab, nel gruppo c'era solo lo storage dell'esercizio
- `terraform destroy`: Destroy complete, 2 destroyed
- `az group exists`: false
- `terraform state list` finale: vuoto

## Elementi conservati per le nuove UD13–UD14

- Bicep: 0.48.1 installato
- Terraform: 1.17.0 installato
- file IaC: infra/bicep e infra/terraform nel repo con il lock file
- agent configurato: sì, ~/azdo-agent, nessun nuovo config o PAT
