# UD14 — Domande concetti

## 1. Qual è la differenza tra CI e Continuous Delivery?
**Risposta:** la CI prende ogni modifica, la integra, esegue i test e produce un artefatto (qui l'immagine Docker con tag = Build ID). La Continuous Delivery porta quell'artefatto già validato fino all'ambiente, in modo automatico e ripetibile: qui Terraform applica l'immagine ad Azure Container Apps e uno smoke test verifica che risponda. In CI il risultato è "il codice è buono"; in CD il risultato è "il servizio è raggiungibile e nella versione giusta".

## 2. Quale service connection utilizza la pipeline UD14?
**Risposta:** `sc-azure-ud13-15`, una sola per tutto: login ACR, build/push e Terraform passano da `AzureCLI@2` con quella connessione (Workload Identity Federation).

## 3. Perché la pipeline non utilizza `Docker@2`?
**Risposta:** `Docker@2` avrebbe bisogno di una Docker Registry service connection separata (`sc-acr-ud14`) e di una seconda autenticazione. Con `AzureCLI@2` faccio `az acr login`, `docker build` e `docker push` dentro la stessa sessione Azure, quindi la pipeline usa una sola identità e un solo meccanismo di autenticazione (WIF) anche per Terraform.

## 4. Quale ruolo deve avere l'identità della pipeline sull'ACR?
**Risposta:** `AcrPush`, assegnato al service principal di `sc-azure-ud13-15` sull'ACR `acrud1315iwmnnz3ek6q7o`.

## 5. Perché Terraform usa uno state remoto?
**Risposta:** perché lo state deve essere unico e condiviso tra gli stage e tra le run. Con `workspace: clean: all` la cartella di lavoro viene svuotata a ogni job, quindi uno state locale sparirebbe. Il backend AzureRM mette anche il lock: due apply non possono girare insieme sullo stesso state.

## 6. Dove viene conservato lo state UD14?
**Risposta:** nello Storage Account `sttf156e08fcb1163b497b`, container `tfstate`, chiave `ud15.tfstate`.

## 7. Quale ruolo permette alla pipeline di utilizzare lo state Blob?
**Risposta:** `Storage Blob Data Contributor` assegnato sul solo container `tfstate` al service principal di `sc-azure-ud13-15`. Non serve un ruolo sull'intero Storage Account.

## 8. Come si autentica Terraform durante la pipeline?
**Risposta:** con la sessione Azure CLI aperta da `AzureCLI@2` tramite `sc-azure-ud13-15`. Nel job esporto `ARM_USE_CLI=true` e `ARM_USE_AZUREAD=true`, e il backend ha `use_cli = true` e `use_azuread_auth = true`: niente secret nel repository.

## 9. Quali risorse vengono lette come esistenti?
**Risposta:** il Resource Group `rg-ud13-15-delivery`, l'ACR `acrud1315iwmnnz3ek6q7o` e la managed identity `id-ud15-acrpull`, tutti letti con `data`.

## 10. Quali risorse vengono gestite da Terraform?
**Risposta:** due: la Container Apps Environment `acaenv-ud15` e la Container App `catalog-api-ud15`.

## 11. Perché la Container App utilizza una managed identity?
**Risposta:** per scaricare l'immagine dall'ACR senza credenziali nel codice o nella configurazione e senza l'admin user dell'ACR. L'identità `id-ud15-acrpull` è assegnata alla Container App e ha `AcrPull` sul registry.

## 12. Quale ruolo ha questa identità sull'ACR?
**Risposta:** `AcrPull`, sul solo ACR del laboratorio.

## 13. Perché viene eseguito `terraform plan` nello stage iniziale?
**Risposta:** per verificare subito sintassi, provider, backend e permessi contro lo state reale, prima di spendere tempo in test e build. Se c'è un errore di configurazione o un 403 sullo state, la pipeline si ferma allo stage `IaC` senza costruire un'immagine inutile.

## 14. Perché viene ricreato il piano nello stage Deploy?
**Risposta:** perché tra lo stage `IaC` e il `Deploy` passa tempo e la realtà può essere cambiata (un'altra run, una modifica manuale). Inoltre il tag dell'immagine esiste solo dopo `BuildPush`. Il piano del `Deploy` è quello che viene applicato: plan e apply stanno nello stesso job, così applico esattamente ciò che ho pianificato.

## 15. Che relazione esiste tra Build ID, tag e `APP_VERSION`?
**Risposta:** sono lo stesso valore: `$(Build.BuildId)` diventa il tag dell'immagine (`catalog-backend:<Build ID>`) e viene passato a Terraform come `image_tag`, che lo usa sia nell'immagine sia nella variabile `APP_VERSION` del container. Così `/health` restituisce la versione e lo smoke test può confrontarla con il Build ID.

## 16. Perché uno smoke test può fallire dopo un apply riuscito?
**Risposta:** perché `terraform apply` dice solo che Azure ha accettato la configurazione, non che l'applicazione risponde. Può mancare il pull dell'immagine, il container può non partire, oppure l'ingress può puntare a una porta sbagliata: l'apply è verde e il servizio resta irraggiungibile.

## 17. Perché `workspace: clean: all` rende importante lo state remoto?
**Risposta:** perché cancella la directory di lavoro a ogni job/stage. Se lo state fosse locale, ogni stage ripartirebbe da zero, senza sapere cosa esiste già, e il `Deploy` proverebbe a ricreare risorse già presenti. Con lo state remoto ogni job ritrova lo stesso stato e il lock.

## 18. Che cosa dimostra l'errore sulla target port?
**Risposta:** che un deploy tecnicamente riuscito non è un servizio funzionante. Con `targetPort: '9999'` l'ingress inoltra il traffico su una porta dove l'app non ascolta (ascolta su `8000`): `Deploy` passa, `Smoke` fallisce. È il motivo per cui la verifica end-to-end non può essere solo `terraform apply`.

## 19. Che cosa elimina `terraform destroy` a fine UD14?
**Risposta:** solo le risorse presenti nello state: la Container App `catalog-api-ud15` e la Container Apps Environment `acaenv-ud15`. ACR, managed identity, Storage Account, container `tfstate` e Resource Group restano.
