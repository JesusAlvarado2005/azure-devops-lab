# UD13 — Verifica

## 1.

Perché se due persone hanno due copie diverse dello state non sanno più quale è aggiornata, e una pipeline non può leggere lo state che sta sul mio PC. Serve un backend condiviso, con locking e protezione dei dati.

## 2.

Lo stage è la fase logica, per esempio Validate o Deploy. Il job è il gruppo di step eseguito su un agent, per esempio ValidateIaC o DeployIaC. Lo step è la singola operazione, per esempio checkout, terraform validate o bicep lint.

## 3.

Prende il repository collegato alla pipeline e ne mette una copia nell'area di lavoro dell'agent, nel commit scelto per la run. Non usa la cartella del mio PC.

## 4.

Per minimo privilegio: la pipeline deve creare l'ACR solo in rg-ud13-15-delivery e non può toccare tutta la subscription. Così se sbaglia qualcosa resta dentro quel Resource Group.

## 5.

Perché evita un client secret statico e usa un token temporaneo con una relazione di fiducia. L'autenticazione riesce, ma i permessi restano quelli dell'identità: se manca il ruolo l'operazione viene negata lo stesso.

## 6.

Perché in UD13 la pipeline controlla solo il codice Terraform, non gestisce lo state condiviso e non vuole modificare risorse. L'ACR lo crea Bicep. Per applicare Terraform servirebbero plan e apply nell'ambiente giusto.

## 7.

rg-ud13-15-delivery con l'ACR, perché la CI pubblica lì l'immagine e la UD14 la usa per il deployment. Tengo anche service connection, pipeline, immagini e agent.

## 8.

È un problema di percorso o filesystem, non di Azure: il file non esiste nel checkout o il path è sbagliato, quindi lo step non arriva nemmeno a parlare con Azure.

## 9.

Per vedere i comandi eseguiti sul WSL2 preparato nelle UD precedenti e usare il Terraform, Azure CLI e Bicep che ho già installato lì.

## 10.

Pulisce tutto il Pipeline.Workspace prima del job, così il self-hosted non si porta dietro file rimasti da run precedenti e la pipeline non funziona per caso solo sulla mia macchina.

## 11.

La GitHub App dà ad Azure Pipelines l'accesso in lettura al repository. La service connection ARM dà l'identità per operare sulle risorse Azure. Sono due autorizzazioni separate: leggere il codice non autorizza a creare risorse.

## 12.

Perché quel percorso esiste solo sul mio PC e su un altro agent o su Microsoft-hosted non c'è. Uso Build.SourcesDirectory, che indica dove è finito il checkout su quell'agent.

## 13.

Cambia l'agent: la VM è nuova a ogni job, gestita da Microsoft, i tool dipendono dall'immagine e i file non restano tra job. Non serve il mio WSL acceso, ma devo rifare il checkout in ogni job.

## Passaggio alla preparazione CI

- agent Online: sì durante le run, `wsl-ud09-jesusalvaradojeanfra`, OS Linux. Ora è Offline perché ho fermato `run.sh`.
- rg-ud13-15-delivery presente: sì, in northeurope con i tag `Course=AZ104` e `Purpose=FinalDelivery`.
- ACR Basic presente: sì, `acrud1315iwmnnz3ek6q7o`.
- admin user ACR: `false`.
- sc-azure-ud13-15 presente: sì, `azurerm` con WIF, `isReady: true`, `isShared: false`. L'identità ha `Contributor` solo su `rg-ud13-15-delivery`.
- pipeline IaC riuscita: sì, `ud13-iac` build 5 e build 9, entrambe con `Validate` e `Deploy` riusciti. La build 9 è quella dopo la correzione del path.
- cleanup: no, ACR, service connection, pipeline e agent restano per la UD14.

## Gate finale UD13 — preparazione CI

- applicazione e tre test eseguiti localmente: sì, 3 test `ok` e `OK`.
- build Docker locale ed endpoint `/health`: sì, `catalog-backend:ud13-local`, `/health` con `status ok`, `service catalog-backend`, `version ci-v1`.
- Docker Registry service connection creata oppure blocco esterno documentato: creata `sc-acr-ud14` con WIF, `isReady: true`, `isShared: false`, login server `acrud1315iwmnnz3ek6q7o.azurecr.io`; nessun blocco esterno.
- scelta motivata `MICROSOFT_HOSTED` oppure `SELF_HOSTED_FALLBACK`: `SELF_HOSTED_FALLBACK`, perché lo stato Microsoft-hosted è `MICROSOFT_HOSTED_PENDING`; uso `pool-ud09-wsl`.
- una sola pipeline CI collegata al repository: sì, `ud13-ci` (id 2) con `pipelines/azure-pipelines-ci-selfhosted.yml`.
- prima run e relativo stato, senza dichiarare riuscito ciò che non è stato verificato: build 6 fallita in `BuildPush` con `Endpoint auth data not present`, perché `sc-acr-ud14` non era ancora autorizzata; poi build 7 riuscita dopo l'autorizzazione. Build 10 automatica su `main` riuscita, tag ACR `7` e `10`.
- cleanup: no.
