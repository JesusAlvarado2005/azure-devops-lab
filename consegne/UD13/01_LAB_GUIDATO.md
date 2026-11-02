# UD13 — Consegna LAB guidato

## Terraform
- network.tf: copiato da `$COURSE_UD13/infra/terraform/network.tf` in `infra/terraform/network.tf`. Aggiunge `azurerm_virtual_network.lab` `vnet-ud13` (10.13.0.0/16) e `azurerm_subnet.app` `snet-app` (10.13.1.0/24), in dipendenza da `azurerm_resource_group.lab` (`rg-ud12-tf`).
- plan: `terraform plan -out=ud13.tfplan` con `TF_VAR_location="northeurope"`, `TF_VAR_storage_account_name="stud13793615099"`. Piano: 4 da aggiungere (Resource Group, Storage Account, VNet, subnet), 0 da cambiare, 0 da distruggere.
- apply: `terraform apply ud13.tfplan` → Apply complete! Resources: 4 added, 0 changed, 0 destroyed.
- VNet verificata: `az network vnet show -g rg-ud12-tf -n vnet-ud13` → Name `vnet-ud13`, Location `northeurope`, Address `["10.13.0.0/16"]`, Tags `Course=AZ104`, `UD=13`, `ManagedBy=Terraform`.
- subnet verificata: `az network vnet subnet show -g rg-ud12-tf --vnet-name vnet-ud13 --name snet-app` → Name `snet-app`, Prefix `10.13.1.0/24`, State `Succeeded`.
- destroy: dopo verifica, `terraform plan -destroy -var="storage_account_name=stud13793615099"` poi `terraform apply` del piano di destroy. Distrutte 4 risorse (subnet, storage, vnet, resource group).
- RG Terraform eliminato: sì. `az group exists -n rg-ud12-tf` → `false`. Codice Terraform rimane nel repo.

## Delivery persistente
- Resource Group: `rg-ud13-15-delivery` in `northeurope`, Tags `Course=AZ104`, `Purpose=FinalDelivery`. Creato prima della pipeline e **non eliminato**.
- service connection: `sc-azure-ud13-15` (Azure Resource Manager), tipo `azurerm`, auth `WorkloadIdentityFederation`, scope dichiarato `Subscription` su `Azure subscription 1` ma l'identità `sc-azure-ud13-15` ha ruolo `Contributor` solo su `rg-ud13-15-delivery`, verificato con `az role assignment list`; isReady `true`, isShared `false`.
- WIF: sì, Workload Identity Federation configurato con issuer Entra ID e subject legato alla service endpoint. Nessun client secret/PAT usato come credenziale Azure.
- scope: effettivo Resource Group `rg-ud13-15-delivery` (non tutta la subscription). La service connection è registrata a livello subscription, ma l'identità ha `Contributor` solo su quel Resource Group.
- accesso globale a tutte le pipeline: NO.

## Pipeline
- YAML: `pipelines/azure-pipelines-iac.yml` (copiato dai materiali), `trigger: none`, pool `pool-ud09-wsl`, `workspace: clean: all`, stage `Validate` (job `ValidateIaC`) e `Deploy` (job `DeployIaC`, dipende da Validate). `AzureCLI@2` usa `sc-azure-ud13-15`.
- agent pool: `pool-ud09-wsl` (self-hosted). Agente `wsl-ud09-jesusalvaradojeanfra`, OS `Linux`, status `Offline` al momento della query ma usato per le run riuscite.
- Validate: Terraform `fmt -check`, `init -backend=false`, `validate` (tutti riusciti). Bicep lint su `infra/bicep/delivery.bicep` riuscito. Nei log: `Agent.Name`, `Agent.OS`, `Build.SourcesDirectory`, `Terraform v1.17.0`, `Azure CLI 2.83.0`, `Bicep CLI 0.48.1`.
- Deploy: `Bicep What-If and deployment` con `AzureCLI@2`, deployment eseguito con nome `ud13-delivery-$(Build.BuildId)`.
- What-If: build 5 `1 to create` (ACR nuovo); build 9 `1 to modify` (ACR già esistente).
- deployment: `ud13-delivery-5` (2026-10-30T15:07:28.747408+00:00, Succeeded) creato l'ACR; `ud13-delivery-9` (2026-10-30T15:34:12.106571+00:00, Succeeded) aggiornato.
- ACR: `acrud1315iwmnnz3ek6q7o`, login server `acrud1315iwmnnz3ek6q7o.azurecr.io`
- SKU: `Basic`
- admin user: `false` (roleAssignmentMode `LegacyRegistryPermissions`)

## Fine UD13
- risorse delivery conservate: sì. `rg-ud13-15-delivery`, ACR, service connection `sc-azure-ud13-15`, pipeline `ud13-iac`/`ud13-ci`, pool `pool-ud09-wsl` restano per CI e UD14. Sono state distrutte solo le risorse Terraform temporanee di `rg-ud12-tf`.
