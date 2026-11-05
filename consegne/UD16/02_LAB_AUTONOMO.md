# UD16 — Laboratorio autonomo

Data della prova: **2026-11-05**. Context Kubernetes: `minikube` (Kubernetes v1.37.0, nodo `Ready`). Namespace: `ft152-catalogo`. Ingresso persistente: `http://127.0.0.1:18016` con header `Host: catalogo.lab`.

## Stato di partenza

Prima di modificare qualsiasi file:

- `deployment/backend` e `deployment/frontend` entrambi `1/1`.
- Pod backend: `backend-7cc7db44c6-vxwhf`; Pod frontend: `frontend-649cdc7bcd-spmlc`.
- PVC `catalog-runtime` `Bound` al volume `pvc-d764dc79-0308-43c7-a3a3-0f12e8d20410`, 1Gi, StorageClass `standard`.
- ConfigMap `catalog-config` con `LOW_STOCK_THRESHOLD=5`; P001 con `stock: 8` e `stock_status: OK`.
- Service `backend` con selector `app=backend` e EndpointSlice con l'IP del Pod.
- Gateway `catalog` `Programmed=True` (address `10.109.4.45`), HTTPRoute `catalog` `Accepted/ResolvedRefs=True`, Service `catalog-nginx` NodePort `32483`.
- Contatore su `/runtime/counter.txt`: `2`.

## 1. Configurazione: soglia 5 → 10 → 5

**Valore iniziale**: `LOW_STOCK_THRESHOLD=5` nella ConfigMap `catalog-config`; con `stock: 8` il prodotto P001 risultava `OK`.

**Modifica motivata**: il responsabile chiede di considerare "scorte basse" anche un prodotto con 8 unità. La soglia è stata portata a `10` nel manifest `k8s/ud16/configmap.yaml`, senza toccare il Dockerfile né ricostruire l'immagine:

```yaml
data:
  LOW_STOCK_THRESHOLD: '10'
```

Applicazione:

```bash
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/configmap.yaml
```

**Prova prima/dopo**:

- Subito dopo `apply`, senza riavviare il processo:
  - `printenv LOW_STOCK_THRESHOLD` nel Pod → `5`
  - `GET /api/products/P001` → `"stock_status": "OK"`
- Dopo `kubectl rollout restart deployment/backend`:
  - `printenv LOW_STOCK_THRESHOLD` → `10`
  - `GET /api/products/P001` → `"stock_status": "LOW"`

Dopo il riavvio è comparso un `502` transitorio (pochi secondi), rientrato appena il nuovo Pod è stato pronto e inserito negli EndpointSlice.

**Perché la sola ConfigMap non basta**: il backend legge la variabile all'avvio del processo. `envFrom` copia il valore nell'ambiente del container quando il container parte; modificare la ConfigMap aggiorna l'oggetto nel cluster, ma il processo già in esecuzione continua a usare il valore con cui è stato avviato. Il riavvio dei Pod è ciò che rende effettiva la nuova soglia. Il file montato in `/etc/catalog-config` verrebbe aggiornato dal kubelet, ma anche in quel caso l'applicazione dovrebbe rileggerlo: qui la logica usa la variabile d'ambiente.

## 2. Persistenza

**Incremento**: `GET /api/counter` tramite l'ingresso persistente ha restituito `{"counter": 2}`; `/runtime/counter.txt` conteneva `2`.

**Sostituzione del solo Pod backend** (Deployment e PVC intatti):

```bash
kubectl --context=minikube -n ft152-catalogo delete pod -l app=backend
kubectl --context=minikube -n ft152-catalogo rollout status deployment/backend --timeout=180s
```

- Pod prima: `backend-7cc7db44c6-jbcvm` (IP `10.244.0.12`).
- Pod dopo: `backend-7cc7db44c6-vxwhf` (IP `10.244.0.13`) — nome e IP nuovi, quindi il Pod è stato realmente ricreato.
- `/runtime/counter.txt` dopo: `2`.
- PVC: ancora `Bound` allo stesso volume `pvc-d764dc79-0308-43c7-a3a3-0f12e8d20410`.

**Distinzione importante**: `PVC Bound` dimostra solo che il volume è associato e disponibile; non dimostra che l'applicazione abbia scritto e riletto il dato. La prova di persistenza è il valore `2` riletto dal **nuovo** Pod dopo la sostituzione. Non è stata provata la resistenza alla perdita del nodo o a un backup: fuori dagli obiettivi del laboratorio.

## 3. Service: guasto intenzionale e recupero

**Sintomo introdotto**: modificato deliberatamente il selector del Service `backend` da `app: backend` a `app: backend-guasto` nel manifest `k8s/ud16/backend-service.yaml` e applicato al cluster. Il Service è rimasto esistente:

```text
NAME      TYPE        CLUSTER-IP     PORT(S)   SELECTOR
backend   ClusterIP   10.99.242.43   8000/TCP   app=backend-guasto
```

ma l'EndpointSlice è diventato vuoto:

```text
NAME            ADDRESSTYPE   PORTS     ENDPOINTS
backend-6xd7p   IPv4          <unset>   <unset>
```

`kubectl get endpoints backend` riportava `<none>`. Il Pod backend aveva ancora la label `app=backend`, quindi non era selezionato.

**Ipotesi**: il DNS continua a risolvere il nome `backend` (il Service esiste), ma senza endpoint il frontend non ha un Pod a cui inoltrare il traffico; ci si aspetta un errore del proxy del frontend.

**Prova scelta**: due richieste attraverso l'ingresso persistente, senza port-forward:

```bash
curl -i -H 'Host: catalogo.lab' http://127.0.0.1:18016/health
curl -i -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/products/P001
```

Entrambe hanno restituito `HTTP 502` con pagina `502 Bad Gateway` di nginx; il Pod `frontend` era `Running` e il suo EndpointSlice conteneva il suo IP. Il guasto era quindi nel collegamento frontend → Service `backend`, non nel frontend o nel Gateway.

**Correzione**: ripristinato il selector `app: backend` **sia nel manifest versionato sia nel cluster**:

```bash
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/backend-service.yaml
```

**Verifica finale**:

```text
service/backend   ClusterIP   10.99.242.43   8000/TCP   app=backend
EndpointSlice backend-6xd7p: 10.244.0.13
GET /health            → 200, {"status":"ok","service":"catalog-backend","version":"2.0"}
GET /api/products/P001 → 200, stock 8, stock_status LOW (soglia ancora 10 in quella fase)
GET /                  → HTTP 200
```

Il `LOW` è coerente: in quel momento la ConfigMap era ancora a `10`; la soglia è stata riportata a `5` nel passo 4.

## 4. Gateway e stato finale

**Percorso HTTP verificato**: client → ingresso Compose persistente (`127.0.0.1:18016`, rete Docker `minikube`) → NodePort `32483` del Service `catalog-nginx` → Gateway `catalog` → HTTPRoute `catalog` (host `catalogo.lab`) → Service `frontend:80` → frontend nginx → Service `backend:8000`.

**Risultato osservato**: `/health`, `/api/products/P001` e `/` hanno risposto `200` con `Host: catalogo.lab`, senza alcun `kubectl port-forward`. Gateway `Programmed=True`, HTTPRoute `Accepted=True` e `ResolvedRefs=True`, controller `ngf-nginx-gateway-fabric` `1/1`.

**Ripristino della soglia**: `LOW_STOCK_THRESHOLD` riportato a `5` nel manifest e applicato; `rollout restart deployment/backend`; nuovo Pod `backend-75cfdd986d-twf8t`; `printenv LOW_STOCK_THRESHOLD` → `5`; P001 → `stock_status: OK`. Un'ulteriore lettura di `/api/counter` ha portato il contatore a `3`, riletto come `3` dal nuovo Pod: la persistenza ha retto anche questo secondo riavvio.

**Stato lasciato attivo**: namespace `ft152-catalogo`, Deployment `backend`/`frontend`/`catalog-nginx` `1/1`, Service `backend`/`frontend`/`catalog-nginx`, PVC `catalog-runtime` `Bound`, Gateway/HTTPRoute `Programmed`/`Accepted`, ingresso Compose `ft152-entry-ud16-ingresso-1` attivo. Nessun port-forward aperto; porte `8081`/`8082` libere, solo `18016` in ascolto. `web-intro` della UD15 non è stato toccato.

**Eventuali blocchi**: nessun prerequisito bloccante. Il `502` transitorio dopo i riavvii è stato riassorbito in pochi secondi ed è stato verificato con una richiesta successiva riuscita.

## Collegamento architetturale e accesso

- **Oggetto configurato e componente che realizza il comportamento**: la ConfigMap `catalog-config` cambia la soglia letta dal backend all'avvio; il PVC `catalog-runtime` realizza la persistenza di `/runtime`; il Service `backend` e il suo EndpointSlice realizzano il collegamento interno; Gateway, HTTPRoute e controller NGF realizzano l'ingresso HTTP; il container Compose `ingresso` inoltra `127.0.0.1:18016` alla rete Minikube.
- **Prova reale, momento e interpretazione**: soglia 10 con `OK` prima del riavvio e `LOW` dopo; contatore `2` riletto dal Pod `vxwhf` dopo l'eliminazione di `jbcvm`; `502` con EndpointSlice vuoto e `200` dopo il ripristino del selector; `200` finale via `catalogo.lab:18016` con soglia 5.
- **Indirizzo e percorso verificato**: `http://127.0.0.1:18016` con `Host: catalogo.lab` — percorso **Gateway** completo, non diagnostica diretta. I port-forward `8081`/`8082` usati nelle fasi guidate sono stati chiusi.
- **Stato dell'ingresso locale e limiti della prova**: ingresso Compose attivo e persistente (`restart: unless-stopped`), `.env` locale escluso da Git. La prova vale per Minikube su Docker locale e per il nome `catalogo.lab`; non dimostra alta disponibilità, resistenza alla perdita del nodo né esposizione Internet.
