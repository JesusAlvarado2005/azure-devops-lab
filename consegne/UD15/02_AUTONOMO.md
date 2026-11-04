# UD15 — Consegna laboratorio autonomo

Partecipante, data/ora/fuso: Jesus Alvarado, 2026-11-04, Europe/Rome (CET, UTC+01:00)  
Percorsi: `k8s/ud15/autonomo/deployment.yaml` e `service.yaml`.

| Requisito | Configurazione e output che lo dimostrano |
|---|---|
| Due repliche web-autonomo, immagine iniziale | Nel manifest `replicas: 2` e `image: nginx:1.28.0-alpine`. Dopo l'apply: `deployment.apps/web-autonomo 2/2 2 2` e due Pod `1/1 Running`, entrambi con `containerd://...` e immagine `nginx:1.28.0-alpine` nel `describe pod`. |
| Label component=frontend sui Pod | La label è nel `template.metadata.labels` del Deployment, quindi compare sui Pod: `kubectl get pods -l component=frontend --show-labels` restituisce solo `web-autonomo-85f6469d54-dtmdk` e `web-autonomo-85f6469d54-pkwz7`, con `app=web-autonomo,component=frontend,pod-template-hash=85f6469d54`. `web-intro` non ha quella label e non viene incluso. |
| Service con endpoint della variante, HTTP 200 su 8082 | `describe service web-autonomo` mostra `Selector: app=web-autonomo`, `Port: http 80/TCP`, `TargetPort: http/TCP`, `Endpoints: 10.244.0.14:80,10.244.0.13:80`; l'EndpointSlice `web-autonomo-jdf6c` elenca gli stessi due IP dei Pod. `curl -i http://127.0.0.1:8082/` risponde `HTTP/1.1 200 OK` con `Server: nginx/1.28.0`. |

Differenza fra questa micro-demo e il frontend del Catalogo: la variante è ancora Nginx con la pagina predefinita, due repliche e un Service ClusterIP interno. Non contiene il codice del frontend del Catalogo, non ha un'immagine applicativa pubblicata da noi, non ha configurazione esterna né un Ingress che la esponga dal browser; serve solo a esercitare label, selector e collegamento Service–Pod. La label `component: frontend` anticipa la separazione dei ruoli, ma la migrazione del Catalogo non è dichiarata completata.  
Workload guidato conservato a una replica: dopo l'apply della variante, `kubectl get deployment web-intro web-autonomo` mostra `web-intro 1/1` con immagine `nginx:1.28.0-alpine` e `web-autonomo 2/2`. Il Service `web-intro` conserva `Endpoints: 10.244.0.10:80`, quindi i due workload restano separati nonostante vivano nello stesso namespace.  
Problema eventualmente incontrato, diagnosi, correzione e nuovo test: in questa variante non ho incontrato errori: i due file sono stati preparati leggendo il guidato e il primo apply è andato a buon fine. Il guasto di immagine documentato nel guidato (`nginx:tag-ft152-che-non-esiste`) è stato intenzionale e non appartiene a questa variante; qui non l'ho ripetuto.  
Tempo impiegato: preparazione / applicazione e test / consegna: circa 10 minuti per i manifest, 5 minuti per apply e controlli, 10 minuti per la consegna.  
Port-forward terminato e risorse conservate: il port-forward su 8082 è stato chiuso e `ss -ltn '( sport = :8082 )'` non mostra più listener. Conservo cluster, namespace `ft152-ud15`, `web-intro` a una replica, `web-autonomo` a due repliche e i manifest nel repository.  
Commit finale: commit unico della UD15, creato nella chiusura comune di `04_VERIFICA.md` §4 e pubblicato su `main`.

## Ambiente di partenza

```text
2026-11-04T09:17:32+01:00
/home/jj/Documenti/sviluppo/lab repo remoto/azure-devops-lab
/home/jj/Documenti/sviluppo/lab repo remoto/azure-devops-lab
29.9.3 client / 29.9.3 server
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured

CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         minikube   minikube   minikube   default
NAME       STATUS   ROLES           AGE     VERSION
minikube   Ready    control-plane   3m22s   v1.37.0
NAME                               READY   STATUS    RESTARTS   AGE
coredns-559f6c778d-ccdp9           1/1     Running   0          3m13s
etcd-minikube                      1/1     Running   0          3m19s
kindnet-h66gw                      1/1     Running   0          3m13s
kube-apiserver-minikube            1/1     Running   0          3m21s
kube-controller-manager-minikube   1/1     Running   0          3m19s
kube-proxy-65kvd                   1/1     Running   0          3m13s
kube-scheduler-minikube            1/1     Running   0          3m19s
storage-provisioner                1/1     Running   0          3m17s
NAME         STATUS   AGE
ft152-ud15   Active   2m40s
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web-intro   1/1     1            1           2m40s

NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/web-intro   ClusterIP   10.101.39.241   <none>        80/TCP    2m29s

NAME                             READY   STATUS    RESTARTS   AGE
pod/web-intro-846844b5c9-bs55z   1/1     Running   0          102s
-rw-r--r--. 1 jj jj 2331  4 nov 09.17 consegne/UD15/02_AUTONOMO.md
-rw-r--r--. 1 jj jj  583  4 nov 09.17 k8s/ud15/deployment.yaml
-rw-r--r--. 1 jj jj  273  4 nov 09.14 k8s/ud15/service.yaml
State Recv-Q Send-Q Local Address:Port Peer Address:Port
```

## File della variante prima dell’applicazione

```text
2026-11-04T09:17:38+01:00
# Variante individuale: secondo frontend Nginx accanto a web-intro.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-autonomo
  namespace: ft152-ud15
spec:
  replicas: 2
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: web-autonomo
  template:
    metadata:
      labels:
        app: web-autonomo
        # Label aggiuntiva solo sui Pod della variante: distingue il frontend
        # dal workload del guidato, che non ha component=frontend.
        component: frontend
    spec:
      containers:
        - name: web
          image: nginx:1.28.0-alpine
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 80
apiVersion: v1
kind: Service
metadata:
  name: web-autonomo
  namespace: ft152-ud15
spec:
  type: ClusterIP
  # Stesso nome del Deployment, ma il collegamento dipende dal selector.
  selector:
    app: web-autonomo
  ports:
    - name: http
      port: 80
      targetPort: http
```

## Oggetti creati e collegamento Service–Pod

```text
2026-11-04T09:17:38+01:00
NAME                           READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS   IMAGES                SELECTOR
deployment.apps/web-autonomo   2/2     2            2           0s      web          nginx:1.28.0-alpine   app=web-autonomo
deployment.apps/web-intro      1/1     1            1           2m45s   web          nginx:1.28.0-alpine   app=web-intro

NAME                                      DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES                           SELECTOR
replicaset.apps/web-autonomo-85f6469d54   2         2         2       0s      web          nginx:1.28.0-alpine              app=web-autonomo,pod-template-hash=85f6469d54
replicaset.apps/web-intro-54449bc466      0         0         0       2m5s    web          nginx:1.29.0-alpine              app=web-intro,pod-template-hash=54449bc466
replicaset.apps/web-intro-6d4c975bcd      0         0         0       90s     web          nginx:tag-ft152-che-non-esiste   app=web-intro,pod-template-hash=6d4c975bcd
replicaset.apps/web-intro-846844b5c9      1         1         1       2m45s   web          nginx:1.28.0-alpine              app=web-intro,pod-template-hash=846844b5c9

NAME                                READY   STATUS    RESTARTS   AGE    IP            NODE       NOMINATED NODE   READINESS GATES
pod/web-autonomo-85f6469d54-dtmdk   1/1     Running   0          0s     10.244.0.13   minikube   <none>           <none>
pod/web-autonomo-85f6469d54-pkwz7   1/1     Running   0          0s     10.244.0.14   minikube   <none>           <none>
pod/web-intro-846844b5c9-bs55z      1/1     Running   0          107s   10.244.0.10   minikube   <none>           <none>
NAME                            READY   STATUS    RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES   LABELS
web-autonomo-85f6469d54-dtmdk   1/1     Running   0          0s    10.244.0.13   minikube   <none>           <none>            app=web-autonomo,component=frontend,pod-template-hash=85f6469d54
web-autonomo-85f6469d54-pkwz7   1/1     Running   0          0s    10.244.0.14   minikube   <none>           <none>            app=web-autonomo,component=frontend,pod-template-hash=85f6469d54
NAME                            READY   STATUS    RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES   LABELS
web-autonomo-85f6469d54-dtmdk   1/1     Running   0          0s    10.244.0.13   minikube   <none>           <none>            app=web-autonomo,component=frontend,pod-template-hash=85f6469d54
web-autonomo-85f6469d54-pkwz7   1/1     Running   0          0s    10.244.0.14   minikube   <none>           <none>            app=web-autonomo,component=frontend,pod-template-hash=85f6469d54
Name:                     web-autonomo
Namespace:                ft152-ud15
Labels:                   <none>
Annotations:              <none>
Selector:                 app=web-autonomo
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.105.116.11
IPs:                      10.105.116.11
Port:                     http  80/TCP
TargetPort:               http/TCP
Endpoints:                10.244.0.14:80,10.244.0.13:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   <none>
NAME                 ADDRESSTYPE   PORTS   ENDPOINTS                 AGE
web-autonomo-jdf6c   IPv4          80      10.244.0.14,10.244.0.13   0s
apiVersion: v1
items:
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.0.14
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: minikube
    targetRef:
      kind: Pod
      name: web-autonomo-85f6469d54-pkwz7
      namespace: ft152-ud15
      uid: 3122920f-cba3-42c6-9e94-7eaeab28ab87
  - addresses:
    - 10.244.0.13
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: minikube
    targetRef:
      kind: Pod
      name: web-autonomo-85f6469d54-dtmdk
      namespace: ft152-ud15
      uid: 3ef44a8a-cc5d-434a-9b51-ce860f09cd9b
  kind: EndpointSlice
  metadata:
    creationTimestamp: "2026-11-04T08:17:38Z"
    generateName: web-autonomo-
    generation: 3
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: web-autonomo
    name: web-autonomo-jdf6c
    namespace: ft152-ud15
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: web-autonomo
      uid: ec98879b-37fe-4743-950d-f4ce3f1b87b1
    resourceVersion: "1047"
    uid: 5c6c15c2-9de3-4437-a34e-6cda241647d0
  ports:
  - name: http
    port: 80
    protocol: TCP
kind: List
metadata:
  resourceVersion: ""
```

## Prova HTTP su 8082 e separazione dal guidato

```text
2026-11-04T09:17:46+01:00
State  Recv-Q Send-Q Local Address:Port Peer Address:Port
LISTEN 0      4096       127.0.0.1:8082      0.0.0.0:*   
HTTP 200 da 127.0.0.1:8082
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              0100    615 100    615   0      0 358.1k      0                              0100    615 100    615   0      0 351.4k      0                              0100    615 100    615   0      0 346.1k      0                              0
HTTP/1.1 200 OK
Server: nginx/1.28.0
Date: Wed, 04 Nov 2026 08:17:46 GMT
Content-Type: text/html
Content-Length: 615
Last-Modified: Wed, 23 Apr 2025 12:59:25 GMT
Connection: keep-alive
ETag: "6808e42d-267"
Accept-Ranges: bytes
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
web-intro      1/1     1            1           2m53s
web-autonomo   2/2     2            2           8s
NAME                            READY   STATUS    RESTARTS   AGE    IP            NODE       NOMINATED NODE   READINESS GATES   LABELS
web-autonomo-85f6469d54-dtmdk   1/1     Running   0          8s     10.244.0.13   minikube   <none>           <none>            app=web-autonomo,component=frontend,pod-template-hash=85f6469d54
web-autonomo-85f6469d54-pkwz7   1/1     Running   0          8s     10.244.0.14   minikube   <none>           <none>            app=web-autonomo,component=frontend,pod-template-hash=85f6469d54
web-intro-846844b5c9-bs55z      1/1     Running   0          115s   10.244.0.10   minikube   <none>           <none>            app=web-intro,pod-template-hash=846844b5c9
```
