# UD16 — Esiti del laboratorio guidato

Data della prova: **2026-11-05**. Context Kubernetes: `minikube` (Minikube v1.39.0, Kubernetes v1.37.0, nodo `Ready`). Namespace di lavoro: `ft152-catalogo`.

> Nota: questa consegna copre la **prima metà** del guidato (§0–§5: configurazione, immagini, PVC, persistenza). Le sezioni Service/DNS e Gateway/HTTPRoute sono ancora da svolgere.

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
- **Service**: `backend` ClusterIP `10.99.242.43:8000`, `frontend` ClusterIP `10.110.80.43:80`.

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

**Non ancora svolto** — fa parte della seconda metà del guidato.

## Gateway e HTTPRoute

**Non ancora svolto** — fa parte della seconda metà del guidato. Stato attuale dei prerequisiti: Helm presente (`v4.2.2`), CRD Gateway API assenti, nessuna `GatewayClass`, CoreDNS `1/1`.

## Collegamento architetturale e accesso

- **Oggetto configurato e componente che realizza il comportamento**: ConfigMap e Secret alimentano variabili e file del container backend; il PVC `catalog-runtime` realizza la persistenza di `/runtime`; il Deployment mantiene una replica e la ricrea quando il Pod viene eliminato.
- **Prova reale, momento e interpretazione**: incremento del contatore via `/api/counter`, eliminazione del Pod e rilettura dello stesso valore dal nuovo Pod. Il dato resta perché vive sul volume, non nel container.
- **Indirizzo e percorso verificato**: `http://127.0.0.1:8082/api/counter` tramite `kubectl port-forward service/backend 8082:8000` — prova diagnostica diretta, chiusa dopo la verifica. Non è ancora attivo il percorso Gateway/ingresso locale.
- **Stato dell'ingresso locale e limiti della prova**: `accesso/ud16` è stato copiato ma il progetto Compose non è stato configurato né avviato; la porta `18016` è libera. La seconda metà del guidato completerà Gateway, HTTPRoute e ingresso persistente.
