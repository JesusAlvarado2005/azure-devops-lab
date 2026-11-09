# UD18 — Prova di consolidamento operativo · Piano B

**90 minuti — 5 verifiche al terminale e 2 quesiti brevi**

Obiettivo: ricostruire le fasi più significative del percorso attraverso il rintracciamento delle informazioni contenute nelle unità didattiche e nei laboratori svolti, verificando i risultati nell’ambiente disponibile.

Nome: **Jesus Alvarado**  Data: **2026-11-09**

Puoi consultare materiali e attività già svolte: individua tu dove cercare. Rispondi in 2–3 righe per quesito, tenendo comandi e output separati. Descrivi operazioni e risultati senza dover citare il percorso formativo. Usa il contesto minikube, namespace ft152-catalogo, con ambiente UD16/UD17 già avviato. Non eseguire deploy, cancellazioni o modifiche. Registra eventuali errori; se l’ambiente impedisce un’operazione, indica il comando che useresti e segnala che il risultato non è stato verificato. Non consegnare credenziali o token.

Nota sull'ambiente. Al momento della prova il cluster era fermo dopo il riavvio del PC. L'ho riavviato con `minikube start -p minikube` e ho riattivato il container di ingresso già configurato. Non ho applicato manifest e non ho modificato risorse Kubernetes.

## Blocco 1 — Stato, configurazione e dati

Tempo indicativo per completare il blocco: **40 minuti**.

### P01 — Immagine e stato

Nel namespace ft152-catalogo individua l’immagine configurata per il backend e controlla lo stato dei suoi Pod. Riporta nome e tag dell’immagine, repliche pronte e un risultato che giustifichi la tua conclusione. Spiega perché la sola immagine configurata nel Deployment non dimostra che il servizio funzioni.

**Risposta:** Il Deployment `backend` usa l'immagine `catalog-backend:ud16` e ha una sola replica. Risulta `1/1` e il Pod `backend-75cfdd986d-twf8t` è `Running` e `1/1 Ready`. Il restart count è 1 e risale al riavvio del cluster, non a un errore dell'applicazione. L'immagine nel Deployment è solo lo stato desiderato e non dice se il container è partito, se la readiness passa o se il Service ha endpoint. Quindi da sola non prova che il servizio risponda.

**Comando o configurazione richiesta:**

```bash
kubectl --context=minikube -n ft152-catalogo get deployment backend -o wide
kubectl --context=minikube -n ft152-catalogo get pods -l app=backend -o wide
```

**Risultato osservato (estratto utile):**

```text
# rilevazione 2026-11-09 13:02 CET
NAME      READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS   IMAGES
backend   1/1     1            1           3d22h   backend      catalog-backend:ud16

NAME                       READY   STATUS    RESTARTS      AGE     IP
backend-75cfdd986d-twf8t   1/1     Running   1 (85m ago)   3d21h   10.244.0.9
```

**Materiale consultato (file e paragrafo):**

- `k8s/ud16/backend.yaml` sezione `containers` e campo `image`
- `UD16/partecipanti/02_LAB_GUIDATO.md` §3 Crea le immagini, il PVC e i due Deployment

### P02 — Configurazione

Recupera LOW_STOCK_THRESHOLD dal ConfigMap catalog-config e verifica il valore presente nell’ambiente del container backend. Confronta i due risultati e spiega se modificare il ConfigMap aggiornerebbe automaticamente la variabile nel processo già avviato. Non modificare la configurazione.

**Risposta:** Il ConfigMap `catalog-config` contiene `LOW_STOCK_THRESHOLD=5` e il container backend espone lo stesso valore, `5`. I due risultati coincidono e il Pod è partito con la configurazione attuale. Se modificassi il ConfigMap il processo già avviato continuerebbe a usare il valore letto alla partenza perché `envFrom` copia le variabili nell'ambiente del container una volta sola. Serve un riavvio dei Pod con `rollout restart` perché il backend legga il nuovo valore.

**Comando o configurazione richiesta:**

```bash
kubectl --context=minikube -n ft152-catalogo get configmap catalog-config \
  -o jsonpath='{.data.LOW_STOCK_THRESHOLD}{"\n"}'
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- \
  printenv LOW_STOCK_THRESHOLD
```

**Risultato osservato (estratto utile):**

```text
# rilevazione 2026-11-09 13:02 CET
5
5
```

**Materiale consultato (file e paragrafo):**

- `k8s/ud16/configmap.yaml` chiave `LOW_STOCK_THRESHOLD`
- `UD16/partecipanti/02_LAB_GUIDATO.md` §2 Configura il backend senza modificare l'immagine
- `consegne/UD16/02_LAB_AUTONOMO.md` §1 Configurazione: soglia 5 → 10 → 5

### P03 — Dato persistente

Individua il PVC usato dal backend, verifica dove viene montato e leggi il file del contatore in /runtime. Spiega che cosa dimostrano questi controlli sulla persistenza e quale prova ulteriore servirebbe per verificarla dopo una ricreazione. Non eliminare Pod o volumi e non chiamare l’endpoint del contatore.

**Risposta:** Il backend usa il PVC `catalog-runtime` e monta il volume `runtime` su `/runtime`. Il PVC è `Bound` al volume `pvc-d764dc79-0308-43c7-a3a3-0f12e8d20410` con 1Gi, `RWO` e classe `standard`. Il file `/runtime/counter.txt` contiene `3`. Questi controlli dimostrano che il volume è collegato e che il dato è presente adesso ma non provano da soli che il valore sopravviva a una ricreazione del Pod. Servirebbe eliminare il solo Pod backend, attendere il nuovo Pod e rileggere lo stesso file. Lo stato `Bound` da solo non basta perché non dice se l'applicazione ha scritto o se il mount è quello giusto.

**Comando o configurazione richiesta:**

```bash
kubectl --context=minikube -n ft152-catalogo get deployment backend \
  -o jsonpath='{.spec.template.spec.volumes[?(@.name=="runtime")].persistentVolumeClaim.claimName}{"\n"}'
kubectl --context=minikube -n ft152-catalogo get pvc catalog-runtime
kubectl --context=minikube -n ft152-catalogo get deployment backend \
  -o jsonpath='{range .spec.template.spec.containers[0].volumeMounts[*]}{.name}{" -> "}{.mountPath}{"\n"}{end}'
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- cat /runtime/counter.txt
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- df -h /runtime
```

**Risultato osservato (estratto utile):**

```text
# rilevazione 2026-11-09 13:02 CET
catalog-runtime

NAME              STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS
catalog-runtime   Bound    pvc-d764dc79-0308-43c7-a3a3-0f12e8d20410   1Gi        RWO            standard

runtime -> /runtime
config-file -> /etc/catalog-config

3

Filesystem                                             Size  Used Avail Use% Mounted on
/dev/mapper/luks-1cd54a68-1087-497d-aed8-d61e260be5c9  322G   35G  286G  11% /runtime
```

**Materiale consultato (file e paragrafo):**

- `k8s/ud16/pvc.yaml` e `k8s/ud16/backend.yaml` volume `runtime` e relativo mount
- `UD16/partecipanti/02_LAB_GUIDATO.md` §4 Scrivi un dato nel volume e §5 Sostituisci il Pod, non il volume
- `consegne/UD16/02_LAB_AUTONOMO.md` §2 Persistenza

## Blocco 2 — Rete e risposta applicativa

Tempo indicativo per completare il blocco: **30 minuti**.

### P04 — Comunicazione interna

Dal Pod frontend verifica la risoluzione del nome backend. Controlla poi il Service backend e i relativi EndpointSlice: associa almeno un indirizzo a un Pod e alla sua condizione di disponibilità. Spiega perché risolvere il nome non basta a dimostrare che l’applicazione risponda.

**Risposta:** Dal Pod frontend il nome `backend` risolve su `10.99.242.43` che è il ClusterIP del Service `backend`. Il Service seleziona i Pod con label `app=backend`. L'EndpointSlice `backend-6xd7p` contiene l'indirizzo `10.244.0.9` con `ready=true` e `targetRef` verso il Pod `backend-75cfdd986d-twf8t`. Lo stesso Pod ha IP `10.244.0.9` ed è `Ready=True`. Il DNS dimostra solo che il nome del Service esiste. Se il selector non corrisponde o gli endpoint non sono pronti il nome risolve comunque ma il frontend riceve un errore, come il `502` del guasto intenzionale sul selector.

**Comando o configurazione richiesta:**

```bash
kubectl --context=minikube -n ft152-catalogo exec deployment/frontend -- getent hosts backend
kubectl --context=minikube -n ft152-catalogo get service backend
kubectl --context=minikube -n ft152-catalogo get endpointslices \
  -l kubernetes.io/service-name=backend -o wide
kubectl --context=minikube -n ft152-catalogo get endpointslices \
  -l kubernetes.io/service-name=backend \
  -o jsonpath='{range .items[*]}{range .endpoints[*]}{"endpoint="}{.addresses[0]}{" ready="}{.conditions.ready}{" target="}{.targetRef.kind}{"/"}{.targetRef.name}{"\n"}{end}{end}'
kubectl --context=minikube -n ft152-catalogo get pods -l app=backend -o wide
```

**Risultato osservato (estratto utile):**

```text
# rilevazione 2026-11-09 13:02 CET
10.99.242.43      backend.ft152-catalogo.svc.cluster.local  backend.ft152-catalogo.svc.cluster.local backend

NAME      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
backend   ClusterIP   10.99.242.43   <none>        8000/TCP   3d22h

NAME            ADDRESSTYPE   PORTS   ENDPOINTS    AGE
backend-6xd7p   IPv4          8000    10.244.0.9   3d22h

endpoint=10.244.0.9 ready=true target=Pod/backend-75cfdd986d-twf8t
backend-75cfdd986d-twf8t ip=10.244.0.9 ready=True phase=Running
```

**Materiale consultato (file e paragrafo):**

- `k8s/ud16/backend-service.yaml` voci `selector` e `targetPort`
- `UD16/partecipanti/02_LAB_GUIDATO.md` §6 Collega frontend e backend tramite Service e DNS
- `consegne/UD16/02_LAB_AUTONOMO.md` §3 Service: guasto intenzionale e recupero

### P05 — Accesso HTTP e riscontri

Usa curl per interrogare /health e /api/products/P001 passando dall’accesso locale sulla porta 18016 con Host catalogo.lab. Riporta stato HTTP e un dato utile della risposta; consulta poi gli ultimi log del backend. Se un controllo fallisce, conserva l’errore e indica il controllo successivo pertinente, senza modificare l’ambiente.

**Risposta:** Entrambe le richieste passano dall'ingresso locale sulla porta `18016` con header `Host: catalogo.lab` e restituiscono `HTTP/1.1 200 OK`. `/health` riporta `status: ok` e `version: 2.0`. `/api/products/P001` riporta `stock: 8` e `stock_status: OK` ed è coerente con la soglia `5`. Nei log del backend compaiono le richieste in arrivo dal Pod frontend `10.244.0.4` con risposta `200`. Il percorso Gateway → frontend → backend ha funzionato.

**Comando o configurazione richiesta:**

```bash
curl -i -H 'Host: catalogo.lab' http://127.0.0.1:18016/health
curl -i -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/products/P001
kubectl --context=minikube -n ft152-catalogo logs deployment/backend --tail=10
```

**Risultato osservato (estratto utile):**

```text
# rilevazione 2026-11-09 13:02 CET
HTTP/1.1 200 OK
Server: nginx/1.28.0
Content-Type: application/json; charset=utf-8

{
  "status": "ok",
  "service": "catalog-backend",
  "version": "2.0"
}

HTTP/1.1 200 OK
Server: nginx/1.28.0
Content-Type: application/json; charset=utf-8

{
  "id": "P001",
  "name": "Notebook Pro 14",
  "category": "Notebook",
  "price": 1299.0,
  "stock": 8,
  "stock_status": "OK"
}

[backend] 10.244.0.4 - "GET /health HTTP/1.1" 200 -
[backend] 10.244.0.4 - "GET /api/products/P001 HTTP/1.1" 200 -
```

**Materiale consultato (file e paragrafo):**

- `UD16/partecipanti/02_LAB_GUIDATO.md` §8 Crea Gateway e HTTPRoute e prova il percorso completo, con §8.1 e §8.2
- `laboratori/UD16/guida-comandi.md` §8 Gateway, HTTPRoute e ingresso persistente
- `accesso/ud16/README.md`

## Blocco 3 — Raccontare e motivare le operazioni

Tempo indicativo per completare il blocco: **20 minuti**.

### S01 — Dalla pipeline alla versione in esecuzione

Devi spiegare a un referente tecnico come distribuisci una nuova versione del backend. Ricostruisci il passaggio dal commit alla build, alla pubblicazione in ACR e alla distribuzione; indica quale controllo usi per confermare la versione in esecuzione. Recupera dalla pipeline una configurazione che colleghi questi passaggi.

**Risposta:** Un commit su `main` avvia la pipeline `azure-pipelines-delivery.yml`. Dopo `IaC` e `Test` lo stage `BuildPush` autentica l'ACR, costruisce l'immagine dal contesto `app/catalog-backend-ci` e la pubblica come `catalog-backend:$(Build.BuildId)`. Lo stage `Deploy` esegue Terraform con `image_tag=$(imageTag)` e la Container App punta alla stessa immagine. Il controllo finale è lo stage `Smoke` che interroga `https://$FQDN/health` e accetta la risposta solo quando `version` coincide con il Build ID atteso, cioè con il tag pubblicato.

**Comando o configurazione richiesta:**

```yaml
# pipelines/azure-pipelines-delivery.yml
variables:
  imageTag: '$(Build.BuildId)'

# stage BuildPush
IMAGE="$ACR_LOGIN/$(imageRepository):$(imageTag)"
docker build --file "$(dockerfilePath)" --tag "$IMAGE" "$(buildContext)"
docker push "$IMAGE"

# stage Deploy
terraform plan ... -var="image_tag=$(imageTag)" -out=ud15-apply.tfplan
terraform apply ... ud15-apply.tfplan

# stage Smoke: ripete curl finché version == $(imageTag)
VERSION=$(echo "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("version",""))')
```

**Risultato osservato (estratto utile):**

```text
# run finale UD14 del 2026-11-05, non rieseguita oggi
Build ID: 34
immagine: catalog-backend:34
revisione: catalog-api-ud15--0000003, Healthy, 100% traffico
curl https://$FQDN/health
{"status":"ok","service":"catalog-backend","version":"34"}
```

**Materiale consultato (file e paragrafo):**

- `pipelines/azure-pipelines-delivery.yml` variabile `imageTag` e stage `IaC`, `Test`, `BuildPush`, `Deploy`, `Smoke`
- `UD14/partecipanti/02B_LAB_GUIDATO_CD.md` §7 Leggere lo stage BuildPush, §8 Leggere lo stage Deploy e §14 Verificare immagine e versione
- `consegne/UD14/02_LAB_AUTONOMO.md` sezione Ripristino verificato

### S02 — Prima di modificare l’infrastruttura

Hai una configurazione Bicep e una Terraform già predisposte. Recupera per ciascuna il comando che permette di esaminare le modifiche previste prima di applicarle. Spiega quale risultato controlleresti dopo l’applicazione e a che cosa serve lo state di Terraform. Non eseguire le modifiche.

**Risposta:** Per Bicep il controllo preventivo è `az deployment group what-if` che elenca resource type, change type e nome delle risorse che verrebbero create, modificate o cancellate. Per Terraform è `terraform plan` con piano salvato che riporta il riepilogo `add/change/destroy`. Dopo l'applicazione controlleri che il risultato coincida con il piano. Per Bicep lo stato `Succeeded` del deployment e le proprietà o gli output attesi. Per Terraform controlleri che gli output corrispondano al piano, e per la delivery `infra/terraform/ud15` in particolare `fqdn`, `latest_revision_name` e `image` insieme alla revisione della Container App. Lo state tiene la corrispondenza tra configurazione e risorse reali con attributi e dipendenze. Serve a calcolare il diff e a non ricreare ciò che esiste. Nel nostro caso è condiviso su Azure Blob con lock.

**Comando o configurazione richiesta:**

```bash
# Bicep: modifiche previste, senza applicare
az deployment group what-if \
  --resource-group "$BICEP_RG" \
  --template-file infra/bicep/main.bicep \
  --parameters location="$LAB_LOCATION" storageName="$BICEP_STG"

# Terraform: piano salvato, senza applicare
cd infra/terraform
terraform init -input=false
terraform plan -input=false \
  -var="location=$LAB_LOCATION" \
  -var="storage_account_name=$STORAGE_NAME" \
  -out=ud12-plan.tfplan
```

**Risultato osservato (estratto utile):**

```text
# riferimenti dalle attività UD12 e UD14, non rieseguiti oggi
# Bicep what-if
Create
→ Microsoft.Storage/storageAccounts

# Terraform plan
Plan: 2 to add, 0 to change, 0 to destroy

# Output verificati dopo l'apply Terraform in UD12
resource_group_name             = rg-ud12-tf
storage_account_name            = stud12t93266025
storage_primary_blob_endpoint   = https://stud12t93266025.blob.core.windows.net/

# Output attesi per la delivery ud15, dalla run 34
fqdn                 = catalog-api-ud15.<...>.azurecontainerapps.io
latest_revision_name = catalog-api-ud15--0000003
image                = <acr>.azurecr.io/catalog-backend:34
```

**Materiale consultato (file e paragrafo):**

- `infra/bicep/main.bicep` e `infra/bicep/delivery.bicep`
- `infra/terraform/main.tf` e `infra/terraform/outputs.tf`
- `infra/terraform/ud15/main.tf` e `infra/terraform/ud15/outputs.tf`
- `pipelines/azure-pipelines-delivery.yml` stage `IaC` e `Deploy`
- `UD12/partecipanti/02_LAB_GUIDATO.md` §6 What-If: osservare prima di applicare, §16 Plan e §17 Apply del piano salvato
- `UD14/partecipanti/02B_LAB_GUIDATO_CD.md` §12 Verificare lo state remoto
