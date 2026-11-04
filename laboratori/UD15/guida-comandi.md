# UD15 — Guida comandi

Comandi realmente usati per il primo workload Kubernetes su Minikube. Il cluster resta locale: in questa unità non si creano risorse Azure.

## 1. Installazione di Minikube

`sudo` richiedeva password, quindi l'eseguibile è stato installato a livello utente in `~/.local/bin`.

```bash
curl -fL https://github.com/kubernetes/minikube/releases/download/v1.39.0/minikube-linux-amd64 \
  -o /tmp/opencode/ft152-minikube
curl -fL https://github.com/kubernetes/minikube/releases/download/v1.39.0/minikube-linux-amd64.sha256 \
  -o /tmp/opencode/ft152-minikube.sha256
sha256sum /tmp/opencode/ft152-minikube
cat /tmp/opencode/ft152-minikube.sha256
install -m 0755 /tmp/opencode/ft152-minikube "$HOME/.local/bin/minikube"
minikube version
```

Lo SHA-256 calcolato è `b738496da01be06bbaf80c688f57ce25acd3849fbb518155f3a88e03ef555aa4`, uguale a quello pubblicato.

## 2. Avvio del cluster

```bash
minikube start -p minikube --driver=docker --container-runtime=containerd \
  --kubernetes-version=v1.37.0 --cpus=2 --memory=4096
minikube status -p minikube
kubectl config get-contexts
kubectl --context=minikube get nodes -o wide
kubectl --context=minikube get pods -n kube-system
```

Il client `kubectl` è `v1.36.5`, il server `v1.37.0`: differenza entro una minor, accettabile. Il nodo è `Ready` e usa `containerd://2.3.4`.

## 3. Namespace e primo Deployment

```bash
cd "$LAB_REPO"
kubectl --context=minikube apply -f k8s/ud15/namespace.yaml
kubectl --context=minikube apply -f k8s/ud15/deployment.yaml
kubectl --context=minikube -n ft152-ud15 rollout status deployment/web-intro --timeout=120s
kubectl --context=minikube -n ft152-ud15 get deployment,replicaset,pods -o wide
kubectl --context=minikube -n ft152-ud15 describe deployment web-intro
kubectl --context=minikube -n ft152-ud15 get events --sort-by=.metadata.creationTimestamp
```

## 4. Service e test HTTP

```bash
kubectl --context=minikube apply -f k8s/ud15/service.yaml
kubectl --context=minikube -n ft152-ud15 describe service web-intro
kubectl --context=minikube -n ft152-ud15 get endpointslices -l kubernetes.io/service-name=web-intro -o wide
kubectl --context=minikube -n ft152-ud15 port-forward --address=127.0.0.1 service/web-intro 8081:80
```

In un secondo terminale:

```bash
curl -i http://127.0.0.1:8081/
```

Atteso `HTTP/1.1 200 OK` e `Server: nginx/1.28.0`. Il port-forward si chiude con `Ctrl+C`.

## 5. Scaling a tre repliche

```bash
kubectl --context=minikube -n ft152-ud15 scale deployment/web-intro --replicas=3
kubectl --context=minikube -n ft152-ud15 rollout status deployment/web-intro --timeout=120s
kubectl --context=minikube -n ft152-ud15 get deployment,replicaset,pods -o wide
```

Il ReplicaSet resta lo stesso: cambia solo il numero di Pod e la revisione non cambia.

## 6. Aggiornamento immagine

```bash
kubectl --context=minikube -n ft152-ud15 set image deployment/web-intro web=nginx:1.29.0-alpine
kubectl --context=minikube -n ft152-ud15 rollout status deployment/web-intro --timeout=180s
kubectl --context=minikube -n ft152-ud15 rollout history deployment/web-intro
```

Atteso un nuovo ReplicaSet con `pod-template-hash` diverso e `Server: nginx/1.29.0` nel test HTTP.

## 7. Rollback

```bash
kubectl --context=minikube -n ft152-ud15 rollout undo deployment/web-intro
kubectl --context=minikube -n ft152-ud15 rollout status deployment/web-intro --timeout=180s
kubectl --context=minikube -n ft152-ud15 get deployment,replicaset,pods -o wide
```

Atteso il ritorno a `nginx:1.28.0-alpine`, con una nuova revisione che riusa il template precedente.

## 8. Guasto controllato di immagine e recupero

```bash
kubectl --context=minikube -n ft152-ud15 set image deployment/web-intro web=nginx:tag-ft152-che-non-esiste
kubectl --context=minikube -n ft152-ud15 get pods -l app=web-intro -o wide
kubectl --context=minikube -n ft152-ud15 describe pod web-intro-6d4c975bcd-28h75
kubectl --context=minikube -n ft152-ud15 get events --sort-by=.metadata.creationTimestamp
kubectl --context=minikube -n ft152-ud15 logs web-intro-6d4c975bcd-28h75 -c web --tail=10
```

I vecchi Pod restano `Running` e il servizio risponde, mentre il nuovo Pod è `ImagePullBackOff`. `logs` è vuoto perché il container non è mai stato creato. Recupero:

```bash
kubectl --context=minikube apply -f k8s/ud15/deployment.yaml
kubectl --context=minikube -n ft152-ud15 rollout status deployment/web-intro --timeout=180s
```

## 9. Variante autonoma

```bash
kubectl --context=minikube apply -f k8s/ud15/autonomo/deployment.yaml
kubectl --context=minikube apply -f k8s/ud15/autonomo/service.yaml
kubectl --context=minikube -n ft152-ud15 rollout status deployment/web-autonomo --timeout=120s
kubectl --context=minikube -n ft152-ud15 get pods -l app=web-autonomo --show-labels -o wide
kubectl --context=minikube -n ft152-ud15 get pods -l component=frontend --show-labels -o wide
kubectl --context=minikube -n ft152-ud15 describe service web-autonomo
kubectl --context=minikube -n ft152-ud15 get endpointslices -l kubernetes.io/service-name=web-autonomo -o wide
kubectl --context=minikube -n ft152-ud15 port-forward --address=127.0.0.1 service/web-autonomo 8082:80
```

In un secondo terminale:

```bash
curl -i http://127.0.0.1:8082/
kubectl --context=minikube -n ft152-ud15 get deployment web-intro web-autonomo
```

Atteso `HTTP/1.1 200 OK`, due Pod autonomi `1/1 Running`, `web-intro` ancora a una replica.

## 10. Chiusura

```bash
ss -ltn '( sport = :8081 or sport = :8082 )'
minikube status -p minikube
kubectl --context=minikube -n ft152-ud15 get deployment,service,pods -o wide
```

Conservo il profilo attivo. Se servisse liberare memoria: `minikube stop -p minikube`, che ferma il nodo senza distruggere il profilo. Non usare `minikube delete`.

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `sudo: è necessaria una password` | l'utente non ha sudo senza password | installare Minikube in `~/.local/bin` con `install -m 0755` |
| `ImagePullBackOff` / `ErrImagePull` sul Pod nuovo | tag `nginx:tag-ft152-che-non-esiste` inesistente | riapplicare il manifest con `nginx:1.28.0-alpine` |
| `logs` vuoto sul Pod in errore | il container non è mai stato creato | usare `describe pod` e gli eventi, non i log |
| `Address already in use` sul port-forward | porta 8081/8082 già occupata | identificare il processo, chiudere il forward precedente |
| `rollout undo` con avviso su `last-applied-configuration` | il Deployment era gestito con `apply` | dopo il rollback riapplicare il file con `kubectl apply` |
| Service senza endpoint | selector diverso dalle label dei Pod | correggere `selector` o label e riapplicare solo il file necessario |
