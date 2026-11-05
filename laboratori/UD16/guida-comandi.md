# UD16 — Guida comandi (prima metà)

Comandi realmente usati per la prima metà della UD16: configurazione, immagini, PVC e persistenza del Catalogo prodotti su Minikube. La seconda metà (Service/DNS, Gateway API, ingresso persistente) è ancora da svolgere.

## 1. Controlli iniziali

```bash
docker version --format '{{.Server.Version}}'
minikube status -p minikube
kubectl --context=minikube get nodes
kubectl --context=minikube -n ft152-ud15 get deployment web-intro
kubectl --context=minikube get storageclass
kubectl --context=minikube -n kube-system get deployment coredns
```

Osservato: Docker `29.9.3`, Minikube `Running`, nodo `Ready` (`v1.37.0`), `web-intro 1/1`, StorageClass `standard` (default), CoreDNS `1/1`.

Prerequisiti della seconda metà:

```bash
command -v helm && helm version --short
kubectl --context=minikube get crd gatewayclasses.gateway.networking.k8s.io
kubectl --context=minikube get gatewayclass
```

Osservato: Helm `v4.2.2` presente, CRD Gateway API assenti, nessuna `GatewayClass`.

## 2. Copia dei materiali nel repository personale

```bash
export COURSE_UD16="/percorso/UD16/partecipanti"
mkdir -p consegne/UD16 k8s/ud16 app/catalogo-ud16 accesso/ud16

cp -rn "$COURSE_UD16/accesso/." accesso/ud16/
cp -n  "$COURSE_UD16"/modelli/*.md consegne/UD16/
cp -rn "$COURSE_UD16/k8s/ud16/." k8s/ud16/
cp -rn "$COURSE_UD16/app/catalogo-prodotti/." app/catalogo-ud16/
```

L'app è in `app/catalogo-ud16`, separata dal Catalogo delle UD precedenti; i manifest in `k8s/ud16`.

## 3. Namespace, ConfigMap e Secret

```bash
kubectl --context=minikube apply -f k8s/ud16/namespace.yaml
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/configmap.yaml
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/secret-demo.yaml
kubectl --context=minikube -n ft152-catalogo get configmap catalog-config
kubectl --context=minikube -n ft152-catalogo get secret catalog-demo
```

La ConfigMap `catalog-config` contiene `APP_HOST`, `APP_PORT`, `LOW_STOCK_THRESHOLD=5`, `RUNTIME_DIR`. Il Secret `catalog-demo` è didattico: il contenuto non va stampato come evidenza.

## 4. Immagini, PVC e Deployment

```bash
docker build -f app/catalogo-ud16/docker/backend.Dockerfile  -t catalog-backend:ud16  app/catalogo-ud16
docker build -f app/catalogo-ud16/docker/frontend.Dockerfile -t catalog-frontend:ud16 app/catalogo-ud16
minikube image load -p minikube catalog-backend:ud16 catalog-frontend:ud16
minikube image ls -p minikube | grep catalog-
```

```bash
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/pvc.yaml
kubectl --context=minikube -n ft152-catalogo get pvc
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/backend-service.yaml -f k8s/ud16/frontend-service.yaml
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/backend.yaml -f k8s/ud16/frontend.yaml
kubectl --context=minikube -n ft152-catalogo rollout status deployment/backend --timeout=180s
kubectl --context=minikube -n ft152-catalogo rollout status deployment/frontend --timeout=180s
kubectl --context=minikube -n ft152-catalogo get deployment,pods,pvc,services
```

Osservato: PVC `catalog-runtime` `Bound` (1Gi, `standard`), backend e frontend `1/1`, Service `backend:8000` e `frontend:80`.

Verifica della configurazione nel Pod:

```bash
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- ls -l /etc/catalog-config
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- printenv APP_HOST APP_PORT LOW_STOCK_THRESHOLD RUNTIME_DIR
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- sh -c 'test -n "$DEMO_SECRET" && echo "DEMO_SECRET presente"'
kubectl --context=minikube -n ft152-catalogo logs deployment/backend --tail=20
```

I file della ConfigMap compaiono in `/etc/catalog-config`; le variabili valgono `0.0.0.0`, `8000`, `5`, `/runtime`. Il log riporta `threshold=5 runtime=/runtime`.

## 5. Contatore e persistenza

Terminale A:

```bash
kubectl --context=minikube -n ft152-catalogo port-forward service/backend 8082:8000
```

Terminale B:

```bash
curl --max-time 15 --fail http://127.0.0.1:8082/api/counter
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- cat /runtime/counter.txt
kubectl --context=minikube -n ft152-catalogo get pods -l app=backend -o wide
```

Osservato prima della sostituzione: Pod `backend-5cfd7c8c-hdnmv`, risposta `{"counter": 1}`, file `1`.

Chiudere il port-forward con `Ctrl+C`, poi:

```bash
kubectl --context=minikube -n ft152-catalogo delete pod -l app=backend
kubectl --context=minikube -n ft152-catalogo rollout status deployment/backend --timeout=180s
kubectl --context=minikube -n ft152-catalogo get pods -l app=backend -o wide
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- cat /runtime/counter.txt
kubectl --context=minikube -n ft152-catalogo get pvc catalog-runtime
```

Osservato dopo: Pod `backend-5cfd7c8c-slk9c`, file ancora `1`, PVC `Bound` allo stesso volume `pvc-d764dc79-0308-43c7-a3a3-0f12e8d20410`. Il dato sopravvive alla sostituzione del Pod perché `/runtime` è sul PVC.

## 6. Prossimi passi (seconda metà)

- Service, EndpointSlice e risoluzione DNS del nome `backend`
- prova HTTP tramite il frontend (`/health`, `/api/products/P001`)
- installazione del controller Gateway API (CRD assenti) e creazione di Gateway/HTTPRoute
- configurazione di `accesso/ud16` e prova su `http://catalogo.lab:18016`
- laboratorio autonomo e verifica finale
