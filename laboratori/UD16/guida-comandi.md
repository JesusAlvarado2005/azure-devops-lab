# UD16 — Guida comandi

Comandi realmente usati per la UD16: configurazione, immagini, PVC e persistenza del Catalogo prodotti su Minikube, più Service/DNS, Gateway API, ingresso persistente, laboratorio autonomo e verifica finale.

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

Prerequisiti Gateway verificati **prima** dell'installazione:

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

## 6. Service, EndpointSlice e DNS

```bash
kubectl --context=minikube -n ft152-catalogo get service backend frontend
kubectl --context=minikube -n ft152-catalogo get endpointslices -l kubernetes.io/service-name=backend -o wide
kubectl --context=minikube -n ft152-catalogo exec deployment/frontend -- getent hosts backend
```

Osservato: `backend` ClusterIP `10.99.242.43:8000`, EndpointSlice `backend-6xd7p` con endpoint `10.244.0.8`, risoluzione `backend` → `10.99.242.43` (`backend.ft152-catalogo.svc.cluster.local`).

Prova HTTP tramite il frontend (port-forward diagnostico, poi chiuso):

```bash
kubectl --context=minikube -n ft152-catalogo port-forward service/frontend 8081:80
curl --max-time 15 --fail http://127.0.0.1:8081/health
curl --max-time 15 --fail http://127.0.0.1:8081/api/products/P001
pkill -x kubectl
```

Osservato: `/health` → `{"status":"ok","service":"catalog-backend","version":"2.0"}`; P001 `stock 8`, `stock_status: OK`.

## 7. Gateway API e controller

Le CRD Gateway API non erano presenti. Installato il profilo standard di Nginx Gateway Fabric `v2.7.2` e il controller via Helm:

```bash
kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.7.2" \
  | kubectl --context=minikube apply -f -

helm install ngf oci://ghcr.io/nginx/charts/nginx-gateway-fabric --version 2.7.2 \
  --kube-context minikube -n nginx-gateway --create-namespace \
  --set nginx.service.type=NodePort --wait --timeout 5m

kubectl --context=minikube -n nginx-gateway get deployment,pods
kubectl --context=minikube get gatewayclass nginx -o wide
```

Osservato: controller `ngf-nginx-gateway-fabric` `1/1`, `GatewayClass nginx` `Accepted=True`, Helm `v4.2.2` con chart `nginx-gateway-fabric-2.7.2`.

## 8. Gateway, HTTPRoute e ingresso persistente

```bash
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/gateway.yaml -f k8s/ud16/httproute.yaml
kubectl --context=minikube -n ft152-catalogo get gateway,httproute -o wide
kubectl --context=minikube -n ft152-catalogo get service catalog-nginx
```

Osservato: Gateway `catalog` `Programmed=True`, address `10.109.4.45`, `attachedRoutes=1`; HTTPRoute `catalog` `Accepted=True`, `ResolvedRefs=True`; Service proxy `catalog-nginx` NodePort `32483`.

Ingresso locale persistente (container Compose, non port-forward):

```bash
bash accesso/ud16/configura.sh ft152-catalogo catalog-nginx 18016 ft152-entry-ud16
cd accesso/ud16 && docker compose up -d && docker compose ps
curl --max-time 15 --fail -H 'Host: catalogo.lab' http://127.0.0.1:18016/health
curl --max-time 15 --fail -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/products/P001
curl -s -o /dev/null -w 'HTTP %{http_code}\n' -H 'Host: catalogo.lab' http://127.0.0.1:18016/
```

Osservato: container `ft152-entry-ud16-ingresso-1` Up su `127.0.0.1:18016`, `/health` e P001 `200`, home `HTTP 200`. Il `.env` locale è escluso da Git (`accesso/ud16/.gitignore`).

## 9. Laboratorio autonomo

### 9.1 Soglia 5 → 10 → 5

```bash
# modifica k8s/ud16/configmap.yaml: LOW_STOCK_THRESHOLD: '10'
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/configmap.yaml
curl -s -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/products/P001
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- printenv LOW_STOCK_THRESHOLD

kubectl --context=minikube -n ft152-catalogo rollout restart deployment/backend
kubectl --context=minikube -n ft152-catalogo rollout status deployment/backend --timeout=180s
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- printenv LOW_STOCK_THRESHOLD
curl -s -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/products/P001
```

Osservato: subito dopo `apply` l'ambiente del Pod era ancora `5` e P001 `OK`; dopo il riavvio `10` e P001 `LOW`. La ConfigMap da sola non cambia il processo già avviato.

### 9.2 Persistenza del contatore

```bash
curl -s -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/counter
kubectl --context=minikube -n ft152-catalogo get pods -l app=backend -o wide
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- cat /runtime/counter.txt
kubectl --context=minikube -n ft152-catalogo delete pod -l app=backend
kubectl --context=minikube -n ft152-catalogo rollout status deployment/backend --timeout=180s
kubectl --context=minikube -n ft152-catalogo get pods -l app=backend -o wide
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- cat /runtime/counter.txt
kubectl --context=minikube -n ft152-catalogo get pvc catalog-runtime
```

Osservato: contatore `2`; Pod `backend-7cc7db44c6-jbcvm` → `backend-7cc7db44c6-vxwhf`; file ancora `2`; PVC `Bound` allo stesso volume.

### 9.3 Guasto intenzionale del Service

```bash
# in k8s/ud16/backend-service.yaml: selector app: backend-guasto
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/backend-service.yaml
kubectl --context=minikube -n ft152-catalogo get service backend -o wide
kubectl --context=minikube -n ft152-catalogo get endpointslices -l kubernetes.io/service-name=backend -o wide
curl -s -o /dev/null -w 'HTTP %{http_code}\n' -H 'Host: catalogo.lab' http://127.0.0.1:18016/health
curl -s -o /dev/null -w 'HTTP %{http_code}\n' -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/products/P001
```

Osservato: Service esistente con selector errato, EndpointSlice senza endpoint, `HTTP 502` su entrambe le richieste; il Pod frontend era `Running`.

Ripristino nel manifest e nel cluster:

```bash
# in k8s/ud16/backend-service.yaml: selector app: backend
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/backend-service.yaml
kubectl --context=minikube -n ft152-catalogo get endpointslices -l kubernetes.io/service-name=backend -o wide
curl -s -H 'Host: catalogo.lab' http://127.0.0.1:18016/health
curl -s -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/products/P001
```

Osservato: EndpointSlice di nuovo popolato, `/health` e P001 `200`.

### 9.4 Ripristino finale

```bash
# in k8s/ud16/configmap.yaml: LOW_STOCK_THRESHOLD: '5'
kubectl --context=minikube -n ft152-catalogo apply -f k8s/ud16/configmap.yaml
kubectl --context=minikube -n ft152-catalogo rollout restart deployment/backend
kubectl --context=minikube -n ft152-catalogo rollout status deployment/backend --timeout=180s
kubectl --context=minikube -n ft152-catalogo exec deployment/backend -- printenv LOW_STOCK_THRESHOLD
curl -s -H 'Host: catalogo.lab' http://127.0.0.1:18016/api/products/P001
```

Osservato: ambiente `5`, P001 `OK`, Pod finale `backend-75cfdd986d-twf8t`, contatore `3` conservato. Lasciati attivi namespace, Deployment, Service, PVC e Gateway; nessun port-forward.

## 10. Controllo dello stato finale

```bash
kubectl --context=minikube -n ft152-catalogo get deployment,pods,services,pvc
kubectl --context=minikube -n ft152-catalogo get endpointslices -l kubernetes.io/service-name=backend
kubectl --context=minikube get gatewayclass nginx
kubectl --context=minikube -n ft152-catalogo get gateway,httproute
docker compose -f accesso/ud16/compose.yaml ps
ss -ltn '( sport = :8081 or sport = :8082 or sport = :18016 )'
pgrep -x kubectl || echo "nessun port-forward"
```

Osservato: tre Deployment `1/1` (backend, frontend, catalog-nginx), PVC `Bound`, EndpointSlice `8000 → 10.244.0.14`, `GatewayClass nginx` `Accepted=True`, Gateway `Programmed=True`, HTTPRoute `Accepted/ResolvedRefs=True`, ingresso attivo su `18016`, porte `8081`/`8082` libere.
