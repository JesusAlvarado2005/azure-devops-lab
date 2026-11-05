# UD16 — Esiti del laboratorio guidato

Data della prova: **2026-11-05**. Context Kubernetes: `minikube` (Kubernetes v1.37.0, nodo `Ready`). Namespace di lavoro: `ft152-catalogo`.

## Configurazione e avvio

- **ConfigMap**: `catalog-config`, con quattro chiavi non sensibili: `APP_HOST=0.0.0.0`, `APP_PORT=8000`, `LOW_STOCK_THRESHOLD=5`, `RUNTIME_DIR=/runtime`.
- **Secret dimostrativo**: `catalog-demo` (`Opaque`, 1 chiave `demo`). Il valore è dichiaratamente fittizio; non è stato stampato e non è una credenziale reale.
- **File montato**: la stessa ConfigMap è montata in sola lettura in `/etc/catalog-config`; dentro il Pod compaiono i file `APP_HOST`, `APP_PORT`, `LOW_STOCK_THRESHOLD`, `RUNTIME_DIR` (symlink a `..data`).
- **Variabili d'ambiente**: il backend riceve le chiavi della ConfigMap con `envFrom` e `DEMO_SECRET` con `secretKeyRef`. Verificato nel Pod senza mostrare il valore:
  - `APP_HOST=0.0.0.0`
  - `APP_PORT=8000`
  - `LOW_STOCK_THRESHOLD=5`
  - `RUNTIME_DIR=/runtime`
  - `DEMO_SECRET`: presente, valore non mostrato
- **Immagini**: `catalog-backend:ud16` e `catalog-frontend:ud16`, costruite da `app/catalogo-ud16` e caricate con `minikube image load`.
- **Avvio**: `deployment/backend` e `deployment/frontend` entrambi `1/1`; log del backend: `Catalog backend listening on http://0.0.0.0:8000 threshold=5 runtime=/runtime`.

## Persistenza prima/dopo

- **PVC**: `catalog-runtime`, `Bound` al volume `pvc-d764dc79-0308-43c7-a3a3-0f12e8d20410`, capacità `1Gi`, access mode `RWO`, StorageClass `standard` (`k8s.io/minikube-hostpath`).
- **Prima della sostituzione**:
  - Pod: `backend-5cfd7c8c-hdnmv`
  - `curl http://127.0.0.1:8082/api/counter` → `{"counter": 1}`
  - `/runtime/counter.txt` → `1`
- **Sostituzione**: chiuso il port-forward, eseguito `kubectl delete pod -l app=backend`; il Deployment ha creato un nuovo Pod.
- **Dopo la sostituzione**:
  - Pod: `backend-5cfd7c8c-slk9c` (nome nuovo)
  - `/runtime/counter.txt` → `1`
  - PVC ancora `Bound` allo stesso volume
- **Interpretazione**: il dato è sopravvissuto alla ricreazione del Pod perché `/runtime` è montato sul PVC e non sul layer scrivibile del container. Il solo stato `Bound` del PVC non sarebbe una prova: la prova è che lo stesso valore è stato riletto dopo la creazione di un Pod nuovo. Questo dimostra la persistenza alla sostituzione del Pod, **non** alla perdita del nodo o dell'intero cluster.

## Service, DNS e proxy

- **Service**: `backend` ClusterIP `10.99.242.43`, porta `8000` → `targetPort: http`; `frontend` ClusterIP `10.110.80.43`, porta `80`.
- **EndpointSlice backend**: `backend-6xd7p`, porta `8000`, endpoint `10.244.0.8` (IP del Pod backend in quella fase).
- **DNS interno**: eseguito dal Pod frontend, `getent hosts backend` ha restituito:

  ```text
  10.99.242.43  backend.ft152-catalogo.svc.cluster.local  backend
  ```

  Il nome breve `backend` viene risolto da CoreDNS nel namespace `ft152-catalogo`; il nome completo è `backend.ft152-catalogo.svc.cluster.local`.
- **Prova HTTP tramite il frontend** (port-forward `service/frontend 8081:80`, chiuso dopo la verifica):
  - `GET /health` → `200`, `{"status":"ok","service":"catalog-backend","version":"2.0"}`
  - `GET /api/products/P001` → `200`, `stock: 8`, `stock_status: OK` con soglia `5`
- **Interpretazione**: il frontend raggiunge il backend usando il nome del Service, non un IP di Pod; nginx inoltra `/api/` e `/health` a `http://backend:8000`.

## Gateway e HTTPRoute

- **Prerequisiti**: Helm `v4.2.2`; CRD Gateway API installate dal profilo standard di Nginx Gateway Fabric `v2.7.2` con `kubectl kustomize ... | kubectl apply -f -`; controller installato via Helm (`ngf`, chart `nginx-gateway-fabric-2.7.2`, namespace `nginx-gateway`, `--set nginx.service.type=NodePort`). Pod del controller `ngf-nginx-gateway-fabric-5f779b678d-665dx` `1/1`.
- **GatewayClass**: `nginx`, controller `gateway.nginx.org/nginx-gateway-controller`, `Accepted=True`.
- **Gateway**: `catalog`, class `nginx`, listener HTTP porta `80`, `allowedRoutes` dallo stesso namespace. Stato: `Programmed=True`, address `10.109.4.45`, `attachedRoutes=1`.
- **HTTPRoute**: `catalog`, `parentRefs: catalog`, hostname `catalogo.lab`, `PathPrefix /` → Service `frontend:80`. Stato: `Accepted=True`, `ResolvedRefs=True`.
- **Service del proxy**: `catalog-nginx`, NodePort `32483`.
- **Ingresso persistente**: `accesso/ud16/.env` configurato con `ENTRY_PORT=18016`, `GATEWAY_NODEPORT=32483`, rete Docker `minikube`; container `ft152-entry-ud16-ingresso-1` attivo su `127.0.0.1:18016`.
- **Prova con `Host: catalogo.lab`** (senza port-forward):
  - `GET /health` → `200`
  - `GET /api/products/P001` → `200`, `stock 8`, `stock_status: OK`
  - `GET /` → `HTTP 200`

Il percorso completo è: client → ingresso Compose `127.0.0.1:18016` → NodePort `32483` → Gateway `catalog` → HTTPRoute `catalog` → Service `frontend` → Pod frontend → Service `backend`.

## Collegamento architetturale e accesso

- **Oggetto configurato e componente che realizza il comportamento**: ConfigMap e Secret alimentano variabili e file del container backend; il PVC `catalog-runtime` realizza la persistenza di `/runtime`; il Deployment mantiene una replica e la ricrea quando il Pod viene eliminato; il Service e gli EndpointSlice collegano frontend e backend; Gateway, HTTPRoute e controller NGF realizzano l'accesso HTTP; il container Compose `ingresso` inoltra la porta locale alla rete Minikube.
- **Prova reale, momento e interpretazione**: contatore `1` riletto dal nuovo Pod dopo l'eliminazione del precedente; DNS `backend` → `10.99.242.43`; P001 `OK` con soglia 5; Gateway `Programmed=True` e HTTPRoute `Accepted/ResolvedRefs=True`; richieste `200` attraverso `catalogo.lab:18016`.
- **Indirizzo e percorso verificato**: `http://127.0.0.1:18016` con header `Host: catalogo.lab` — percorso **Gateway** completo e persistente; i port-forward `8081`/`8082` sono stati usati solo come diagnostica e chiusi.
- **Stato dell'ingresso locale e limiti della prova**: ingresso Compose attivo con `restart: unless-stopped`, `.env` locale escluso da Git. La prova riguarda Minikube su Docker locale; non dimostra alta disponibilità, resistenza alla perdita del nodo né esposizione Internet.
