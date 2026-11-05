# UD14 — Verifica finale

## Scenario 1

### 1.
La causa più probabile è un disallineamento tra la porta dichiarata nell'ingress della Container App (`target_port = 9999`) e la porta su cui il processo ascolta dentro il container (`8000`). Il probe di readiness sulla porta sbagliata non riesce, la nuova revision resta `Activating` e il traffico continua a essere servito dalla revision precedente: lo smoke test vede una versione diversa dal Build ID e fallisce.

### 2.
Non modificherei l'infrastruttura di supporto: service connection `sc-azure-ud13-15`, assegnazione `AcrPush`, managed identity `id-ud15-acrpull` con `AcrPull`, Storage Account/container dello state e agent. La correzione è una sola variabile: `targetPort` (o `target_port` in Terraform) riportato a `8000`.

## Scenario 2

### 3.
Controllerei `Storage Blob Data Contributor` (oppure `Storage Blob Data Owner`) sul container `tfstate` dello Storage Account, assegnato all'**object id del service principal** della service connection, non all'appId dell'app registrata. Verificherei anche che la service connection usata dallo stage sia quella giusta e che il backend dichiari `use_azuread_auth = true`.

### 4.
Perché lo state contiene lo stato completo dell'infrastruttura, può contenere valori sensibili e deve essere condiviso e bloccato durante le operazioni. Nel repository si avrebbero conflitti tra run concorrenti, nessun locking, esposizione nella storia Git e rischio di perdere o sovrascrivere lo stato. Lo state remoto su Blob Storage offre accesso controllato, versioning e lock.

## Scenario 3

### 5.
Controllerei la service connection `sc-azure-ud13-15` e il ruolo `AcrPush` assegnato sul registro al service principal della service connection. Verificherei anche che `az acr login` usi lo stesso registro (`acrud1315iwmnnz3ek6q7o`) e che l'immagine non venga pushata su un login server diverso.

### 6.
Perché l'admin user è una credenziale statica con permessi completi sul registro: non è tracciabile per identità, non scade, non si può limitare a un solo ruolo e va ruotata a mano. Con l'identità e i ruoli RBAC ogni permesso è esplicito, revocabile e auditabile.

## Scenario 4

### 7.
Confronto: il Build ID della pipeline, il tag dell'immagine in ACR e l'immagine della revision, la variabile `APP_VERSION` del container, `latestRevisionName`/`latestReadyRevisionName`, l'ora di creazione della revision, il risultato di `terraform output` e i log del container. Se la revision nuova non è pronta, confronto anche `healthState`, `runningState` e il traffico assegnato alle revision.

## Concetti finali

### 8.
La **Continuous Integration** verifica e costruisce ogni modifica (test, build, push dell'immagine). La **Continuous Delivery** porta lo stesso artefatto verificato fino a un ambiente distribuibile, applicando l'infrastruttura e verificando il deployment; la release resta una decisione esplicita.

### 9.
Perché lo state deve essere condiviso tra pipeline e persone, persistente tra agent effimeri, protetto da lock durante `plan`/`apply` e separato dal codice. Uno state locale su un agent verrebbe perso con il workspace e non permetterebbe collaborazione né locking.

### 10.
Perché è il backend di Terraform: Terraform non può creare lo storage che usa per il proprio state nella stessa esecuzione. Va preparato una volta, con container e permessi, prima di inizializzare il backend.

### 11.
Tramite la service connection Azure Resource Manager `sc-azure-ud13-15` (workload identity federation): il task `AzureCLI@2` esegue `az login`, imposta `ARM_USE_CLI=true`, `ARM_USE_AZUREAD=true` e il backend usa `use_azuread_auth = true`, quindi Terraform si autentica con l'identità della service connection.

### 12.
Sono **data source**: resource group, Azure Container Registry e managed identity (`azurerm_resource_group`, `azurerm_container_registry`, `azurerm_user_assigned_identity`). Sono **gestite** da Terraform: `azurerm_container_app_environment` e `azurerm_container_app`.

### 13.
Per intercettare subito errori di configurazione, permessi o backend prima di spendere tempo nella build dell'immagine. Inoltre il piano mostra il diff che verrà applicato e rende esplicito l'impatto della modifica.

### 14.
Perché ogni stage gira in un job separato con workspace pulito e processo nuovo: il piano dello stage `Deploy` è quello effettivamente applicato, calcolato sullo state aggiornato e sull'immagine appena costruita con il tag del Build ID.

### 15.
Perché la pipeline non fa solo build e push: deve autenticarsi ad Azure, leggere ACR e resource group, eseguire Terraform, leggere output e chiamare l'endpoint. `AzureCLI@2` fornisce `az login` con la service connection ARM e permette tutti questi comandi; `Docker@2` coprirebbe solo build/push.

### 16.
Il ruolo `AcrPush` sul registro, assegnato al service principal della service connection.

### 17.
Il ruolo `AcrPull` sul registro, assegnato alla managed identity `id-ud15-acrpull` usata dalla Container App per scaricare l'immagine.

### 18.
Perché `workspace: clean: all` pulisce la directory di lavoro dell'agent (`_work`), non il Blob Storage remoto. Lo state resta nel container `tfstate`; se fosse stato committato nel repository verrebbe cancellato insieme al workspace.

### 19.
Elimina le risorse gestite dalla configurazione Terraform: la Container App `catalog-api-ud15` (con le sue revision) e il Container App Environment `acaenv-ud15`. Non elimina ACR, Storage Account dello state, managed identity, resource group, service connection, agent e repository.

## Cleanup finale

- pipeline Terraform destroy: **non eseguita** — rimandata di proposito, come indicato nel laboratorio
- Container App rimossa: **no**, `catalog-api-ud15` è ancora presente e serve la versione `34`
- Environment rimosso: **no**, `acaenv-ud15` è ancora presente
- Resource Group eliminato: **no**, `rg-ud13-15-delivery` è ancora presente e non è gestito dal `terraform destroy`
- service connection rimosse: **no**, `sc-azure-ud13-15` resta disponibile
- Agent deregistrato: **no**, `linux-ud14-jj` resta nel pool `pool-ud09-wsl`
- repository conservato: **sì**, codice, pipeline e consegne restano nel repository
