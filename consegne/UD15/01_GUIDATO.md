# UD15 — Consegna laboratorio guidato

Partecipante: Jesus Alvarado
Data e fuso orario: 2026-11-04, Europe/Rome (CET, UTC+01:00)
Repository operativo: `/home/jj/Documenti/sviluppo/lab repo remoto/azure-devops-lab`

## Spiegazioni personali

Le prove dei comandi saranno aggiunte automaticamente dal guidato, nella parte successiva di questo file. Scrivi qui soltanto le brevi spiegazioni richieste:

- Come il selector del Service individua i Pod: il Service `web-intro` usa `selector: app: web-intro` e non il nome del Deployment. Il controller degli endpoint cerca nel namespace i Pod con quella label e con la condizione `Ready` vera; gli indirizzi trovati finiscono nell'EndpointSlice `web-intro-759lz` e vengono usati come backend sulla porta `targetPort: http` (80). Dopo il guasto di immagine i Pod sani sono rimasti tre proprio perché avevano ancora la label e la readiness richieste.
- Che cosa cambia con lo scaling e perché la revisione resta uguale: `kubectl scale` cambia solo `spec.replicas`. Il ReplicaSet `web-intro-846844b5c9` è passato da 1 a 3 Pod senza che cambiasse il template, quindi non è nata una nuova revisione né un nuovo `pod-template-hash`. La cronologia è rimasta alla revisione già presente; il cambio di immagine invece ha creato un nuovo ReplicaSet e una nuova revisione.
- Confronto fra immagine aggiornata e immagine dopo il rollback: l'immagine aggiornata è `nginx:1.29.0-alpine`, con ReplicaSet `web-intro-54449bc466` e risposta `Server: nginx/1.29.0`; dopo `rollout undo` il template è tornato a `nginx:1.28.0-alpine`, il ReplicaSet attivo è di nuovo `web-intro-846844b5c9` e la risposta è `Server: nginx/1.28.0`. Il rollback ha creato una nuova revisione che riusa il template precedente, non ha cancellato la storia.
- Causa del guasto letta negli eventi e disponibilità dei log: ho impostato `nginx:tag-ft152-che-non-esiste`. Gli eventi del Pod `web-intro-6d4c975bcd-28h75` riportano `ErrImagePull` e poi `ImagePullBackOff` con `failed to resolve reference ... not found`: il tag non esiste nel registry. Il container non è mai stato creato (`Container ID` vuoto), quindi `kubectl logs` non ha nulla da mostrare e `--previous` non avrebbe un'istanza precedente: la diagnosi sta in `describe pod` ed eventi.
- Esiti osservati nel browser per immagine iniziale, aggiornata e dopo rollback: in tutti e tre i casi la pagina predefinita "Welcome to nginx!" con `HTTP/1.1 200 OK`; cambia solo l'header `Server`, `nginx/1.28.0` prima, `nginx/1.29.0` dopo l'aggiornamento e di nuovo `nginx/1.28.0` dopo il rollback. La pagina è identica perché non abbiamo cambiato contenuti, solo la versione dell'immagine.
- Tempi effettivi e problemi incontrati: circa 8 minuti per installare Minikube e avviare il cluster, poi il guidato in circa 10 minuti. Il problema principale è stato l'installazione: `sudo` richiede password, quindi ho messo l'eseguibile in `~/.local/bin` e ho verificato lo SHA-256 pubblicato. Durante il guasto ho controllato anche `logs`, che era vuoto come atteso.
- Profilo che intendo conservare attivo/fermo a fine giornata: conservo il profilo `minikube` attivo, perché serve alla variante autonoma e alle letture di verifica; non eseguo `minikube delete`.
- Risorse Azure precedenti eventualmente ancora conservate: restano il resource group `rg-ud13-15-delivery`, l'ACR `acrud1315iwmnnz3ek6q7o`, lo storage account per lo stato Terraform e la managed identity `id-ud15-acrpull`. Non ho creato nuove risorse Azure in questa unità.

## Evidenze raccolte dal terminale

I blocchi del guidato aggiungono qui data/ora e output effettivi. Gli errori restano visibili insieme alla successiva prova corretta. Non sostituire un errore con un risultato atteso.

### Primo Deployment e collegamento ai Pod

```text
2026-11-04T09:15:00+01:00
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                SELECTOR
deployment.apps/web-intro   1/1     1            1           7s    web          nginx:1.28.0-alpine   app=web-intro

NAME                                   DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                SELECTOR
replicaset.apps/web-intro-846844b5c9   1         1         1       7s    web          nginx:1.28.0-alpine   app=web-intro,pod-template-hash=846844b5c9

NAME                             READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
pod/web-intro-846844b5c9-dnxw6   1/1     Running   0          7s    10.244.0.3   minikube   <none>           <none>
NAME                         READY   STATUS    RESTARTS   AGE   LABELS
web-intro-846844b5c9-dnxw6   1/1     Running   0          7s    app=web-intro,pod-template-hash=846844b5c9
Name:                   web-intro
Namespace:              ft152-ud15
CreationTimestamp:      Wed, 04 Nov 2026 09:14:53 +0100
Labels:                 <none>
Annotations:            deployment.kubernetes.io/revision: 1
Selector:               app=web-intro
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=web-intro
  Containers:
   web:
    Image:         nginx:1.28.0-alpine
    Port:          80/TCP (http)
    Host Port:     0/TCP (http)
    Environment:   <none>
    Mounts:        <none>
  Volumes:         <none>
  Node-Selectors:  <none>
  Tolerations:     <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
OldReplicaSets:  <none>
NewReplicaSet:   web-intro-846844b5c9 (1/1 replicas created)
Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  7s    deployment-controller  Scaled up replica set web-intro-846844b5c9 from 0 to 1
LAST SEEN   TYPE     REASON              OBJECT                            MESSAGE
7s          Normal   Scheduled           pod/web-intro-846844b5c9-dnxw6    Successfully assigned ft152-ud15/web-intro-846844b5c9-dnxw6 to minikube
7s          Normal   Pulling             pod/web-intro-846844b5c9-dnxw6    Pulling image "nginx:1.28.0-alpine"
7s          Normal   SuccessfulCreate    replicaset/web-intro-846844b5c9   Created pod: web-intro-846844b5c9-dnxw6
7s          Normal   ScalingReplicaSet   deployment/web-intro              Scaled up replica set web-intro-846844b5c9 from 0 to 1
4s          Normal   Pulled              pod/web-intro-846844b5c9-dnxw6    Successfully pulled image "nginx:1.28.0-alpine" in 2.599s (2.599s including waiting). Image size: 21015643 bytes.
4s          Normal   Created             pod/web-intro-846844b5c9-dnxw6    Container created
4s          Normal   Started             pod/web-intro-846844b5c9-dnxw6    Container started
```

### Service web-intro e indirizzi dei Pod

```text
2026-11-04T09:15:07+01:00
Name:                     web-intro
Namespace:                ft152-ud15
Labels:                   <none>
Annotations:              <none>
Selector:                 app=web-intro
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.101.39.241
IPs:                      10.101.39.241
Port:                     http  80/TCP
TargetPort:               http/TCP
Endpoints:                10.244.0.3:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   <none>
NAME                         READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
web-intro-846844b5c9-dnxw6   1/1     Running   0          15s   10.244.0.3   minikube   <none>           <none>
apiVersion: v1
items:
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.0.3
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: minikube
    targetRef:
      kind: Pod
      name: web-intro-846844b5c9-dnxw6
      namespace: ft152-ud15
      uid: 6626c6d1-5b28-416b-9a65-6333a21f029a
  kind: EndpointSlice
  metadata:
    annotations:
      endpoints.kubernetes.io/last-change-trigger-time: "2026-11-04T08:15:04Z"
    creationTimestamp: "2026-11-04T08:15:04Z"
    generateName: web-intro-
    generation: 1
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: web-intro
    name: web-intro-759lz
    namespace: ft152-ud15
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: web-intro
      uid: bfaf2ce7-fd5e-4dd7-8c0b-04420473b2bd
    resourceVersion: "530"
    uid: 795065b7-74ba-47f8-bd4e-7655057559bd
  ports:
  - name: http
    port: 80
    protocol: TCP
kind: List
metadata:
  resourceVersion: ""
```

### Risposta HTTP della demo iniziale

```text
2026-11-04T09:15:16+01:00
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              0100    615 100    615   0      0 198.3k      0                              0100    615 100    615   0      0 196.7k      0                              0100    615 100    615   0      0 195.5k      0                              0
HTTP/1.1 200 OK
Server: nginx/1.28.0
Date: Wed, 04 Nov 2026 08:15:16 GMT
Content-Type: text/html
Content-Length: 615
Last-Modified: Wed, 23 Apr 2025 12:59:25 GMT
Connection: keep-alive
ETag: "6808e42d-267"
Accept-Ranges: bytes

<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

### Prima dello scaling: una replica e revisione corrente

```text
2026-11-04T09:15:21+01:00
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                SELECTOR
deployment.apps/web-intro   1/1     1            1           28s   web          nginx:1.28.0-alpine   app=web-intro

NAME                                   DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                SELECTOR
replicaset.apps/web-intro-846844b5c9   1         1         1       28s   web          nginx:1.28.0-alpine   app=web-intro,pod-template-hash=846844b5c9

NAME                             READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
pod/web-intro-846844b5c9-dnxw6   1/1     Running   0          28s   10.244.0.3   minikube   <none>           <none>
deployment.apps/web-intro 
REVISION  CHANGE-CAUSE
1         <none>

```

### Dopo lo scaling: tre Pod Nginx

```text
2026-11-04T09:15:28+01:00
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                SELECTOR
deployment.apps/web-intro   3/3     3            3           35s   web          nginx:1.28.0-alpine   app=web-intro

NAME                                   DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                SELECTOR
replicaset.apps/web-intro-846844b5c9   3         3         3       35s   web          nginx:1.28.0-alpine   app=web-intro,pod-template-hash=846844b5c9

NAME                             READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
pod/web-intro-846844b5c9-dnxw6   1/1     Running   0          35s   10.244.0.3   minikube   <none>           <none>
pod/web-intro-846844b5c9-lrtcs   1/1     Running   0          7s    10.244.0.5   minikube   <none>           <none>
pod/web-intro-846844b5c9-ndvdm   1/1     Running   0          7s    10.244.0.4   minikube   <none>           <none>
apiVersion: v1
items:
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.0.3
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: minikube
    targetRef:
      kind: Pod
      name: web-intro-846844b5c9-dnxw6
      namespace: ft152-ud15
      uid: 6626c6d1-5b28-416b-9a65-6333a21f029a
  - addresses:
    - 10.244.0.4
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: minikube
    targetRef:
      kind: Pod
      name: web-intro-846844b5c9-ndvdm
      namespace: ft152-ud15
      uid: 56a8d0cc-0517-4a42-9140-df13af19a731
  - addresses:
    - 10.244.0.5
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: minikube
    targetRef:
      kind: Pod
      name: web-intro-846844b5c9-lrtcs
      namespace: ft152-ud15
      uid: 7fe7fe25-5ec7-4b58-9380-9ae78f8628a0
  kind: EndpointSlice
  metadata:
    creationTimestamp: "2026-11-04T08:15:04Z"
    generateName: web-intro-
    generation: 3
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: web-intro
    name: web-intro-759lz
    namespace: ft152-ud15
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: web-intro
      uid: bfaf2ce7-fd5e-4dd7-8c0b-04420473b2bd
    resourceVersion: "580"
    uid: 795065b7-74ba-47f8-bd4e-7655057559bd
  ports:
  - name: http
    port: 80
    protocol: TCP
kind: List
metadata:
  resourceVersion: ""
deployment.apps/web-intro 
REVISION  CHANGE-CAUSE
1         <none>

```

### File riallineato a tre repliche

```text
2026-11-04T09:15:28+01:00
# Micro-demo: Nginx standard, non il frontend completo del Catalogo.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-intro
  namespace: ft152-ud15
spec:
  replicas: 3
  # Conserviamo i template precedenti per l'esercizio di rollback.
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: web-intro
  template:
    metadata:
      labels:
        app: web-intro
    spec:
      containers:
        - name: web
          image: nginx:1.28.0-alpine
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 80
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
web-intro   3/3     3            3           36s
```

### Prima dell’aggiornamento immagine

```text
2026-11-04T09:15:33+01:00
deployment.apps/web-intro 
REVISION  CHANGE-CAUSE
1         <none>

apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: "1"
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"web-intro","namespace":"ft152-ud15"},"spec":{"replicas":3,"revisionHistoryLimit":5,"selector":{"matchLabels":{"app":"web-intro"}},"template":{"metadata":{"labels":{"app":"web-intro"}},"spec":{"containers":[{"image":"nginx:1.28.0-alpine","imagePullPolicy":"IfNotPresent","name":"web","ports":[{"containerPort":80,"name":"http"}]}]}}}}
  creationTimestamp: "2026-11-04T08:14:53Z"
  generation: 3
  name: web-intro
  namespace: ft152-ud15
  resourceVersion: "591"
  uid: 4b66c092-0403-4b17-a566-f8715b75ea2c
spec:
  progressDeadlineSeconds: 600
  replicas: 3
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: web-intro
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: web-intro
    spec:
      containers:
      - image: nginx:1.28.0-alpine
        imagePullPolicy: IfNotPresent
        name: web
        ports:
        - containerPort: 80
          name: http
          protocol: TCP
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
status:
  availableReplicas: 3
  conditions:
  - lastTransitionTime: "2026-11-04T08:14:53Z"
    lastUpdateTime: "2026-11-04T08:14:56Z"
    message: ReplicaSet "web-intro-846844b5c9" has successfully progressed.
    reason: NewReplicaSetAvailable
    status: "True"
    type: Progressing
  - lastTransitionTime: "2026-11-04T08:15:21Z"
    lastUpdateTime: "2026-11-04T08:15:21Z"
    message: Deployment has minimum availability.
    reason: MinimumReplicasAvailable
    status: "True"
    type: Available
  observedGeneration: 3
  readyReplicas: 3
  replicas: 3
  terminatingReplicas: 0
  updatedReplicas: 3
```

### Immagine aggiornata e Pod avviati

```text
2026-11-04T09:15:43+01:00
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                SELECTOR
deployment.apps/web-intro   3/3     3            3           50s   web          nginx:1.29.0-alpine   app=web-intro

NAME                                   DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                SELECTOR
replicaset.apps/web-intro-54449bc466   3         3         3       10s   web          nginx:1.29.0-alpine   app=web-intro,pod-template-hash=54449bc466
replicaset.apps/web-intro-846844b5c9   0         0         0       50s   web          nginx:1.28.0-alpine   app=web-intro,pod-template-hash=846844b5c9

NAME                             READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
pod/web-intro-54449bc466-49ntp   1/1     Running   0          6s    10.244.0.8   minikube   <none>           <none>
pod/web-intro-54449bc466-5z49c   1/1     Running   0          7s    10.244.0.7   minikube   <none>           <none>
pod/web-intro-54449bc466-q7qk6   1/1     Running   0          10s   10.244.0.6   minikube   <none>           <none>
apiVersion: v1
items:
- apiVersion: v1
  kind: Pod
  metadata:
    creationTimestamp: "2026-11-04T08:15:37Z"
    generateName: web-intro-54449bc466-
    generation: 1
    labels:
      app: web-intro
      pod-template-hash: 54449bc466
    name: web-intro-54449bc466-49ntp
    namespace: ft152-ud15
    ownerReferences:
    - apiVersion: apps/v1
      blockOwnerDeletion: true
      controller: true
      kind: ReplicaSet
      name: web-intro-54449bc466
      uid: 856fba94-6935-4577-ac8d-93933f2c32d3
    resourceVersion: "687"
    uid: 795f3f77-95c1-4fbf-9661-ad6a035f0329
  spec:
    containers:
    - image: nginx:1.29.0-alpine
      imagePullPolicy: IfNotPresent
      name: web
      ports:
      - containerPort: 80
        name: http
        protocol: TCP
      resources: {}
      terminationMessagePath: /dev/termination-log
      terminationMessagePolicy: File
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: kube-api-access-wdjs6
        readOnly: true
    dnsPolicy: ClusterFirst
    enableServiceLinks: true
    nodeName: minikube
    preemptionPolicy: PreemptLowerPriority
    priority: 0
    restartPolicy: Always
    schedulerName: default-scheduler
    securityContext: {}
    serviceAccount: default
    serviceAccountName: default
    terminationGracePeriodSeconds: 30
    tolerations:
    - effect: NoExecute
      key: node.kubernetes.io/not-ready
      operator: Exists
      tolerationSeconds: 300
    - effect: NoExecute
      key: node.kubernetes.io/unreachable
      operator: Exists
      tolerationSeconds: 300
    volumes:
    - name: kube-api-access-wdjs6
      projected:
        defaultMode: 420
        sources:
        - serviceAccountToken:
            expirationSeconds: 3607
            path: token
        - configMap:
            items:
            - key: ca.crt
              path: ca.crt
            name: kube-root-ca.crt
        - downwardAPI:
            items:
            - fieldRef:
                apiVersion: v1
                fieldPath: metadata.namespace
              path: namespace
  status:
    conditions:
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:37Z"
      observedGeneration: 1
      status: "True"
      type: PodReadyToStartContainers
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:37Z"
      observedGeneration: 1
      status: "True"
      type: Initialized
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:37Z"
      observedGeneration: 1
      status: "True"
      type: Ready
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:37Z"
      observedGeneration: 1
      status: "True"
      type: ContainersReady
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:37Z"
      observedGeneration: 1
      status: "True"
      type: PodScheduled
    containerStatuses:
    - containerID: containerd://224d3cc9233bd54838195dc41baf7a92af83058a48636c553f07e651e588c2eb
      image: docker.io/library/nginx:1.29.0-alpine
      imageID: docker.io/library/nginx@sha256:d67ea0d64d518b1bb04acde3b00f722ac3e9764b3209a9b0a98924ba35e4b779
      lastState: {}
      name: web
      ready: true
      resources: {}
      restartCount: 0
      started: true
      state:
        running:
          startedAt: "2026-11-04T08:15:37Z"
      user:
        linux:
          gid: 0
          supplementalGroups:
          - 0
          - 1
          - 2
          - 3
          - 4
          - 6
          - 10
          - 11
          - 20
          - 26
          - 27
          uid: 0
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: kube-api-access-wdjs6
        readOnly: true
        recursiveReadOnly: Disabled
    hostIP: 192.168.49.2
    hostIPs:
    - ip: 192.168.49.2
    observedGeneration: 1
    phase: Running
    podIP: 10.244.0.8
    podIPs:
    - ip: 10.244.0.8
    qosClass: BestEffort
    resources: {}
    startTime: "2026-11-04T08:15:37Z"
- apiVersion: v1
  kind: Pod
  metadata:
    creationTimestamp: "2026-11-04T08:15:36Z"
    generateName: web-intro-54449bc466-
    generation: 1
    labels:
      app: web-intro
      pod-template-hash: 54449bc466
    name: web-intro-54449bc466-5z49c
    namespace: ft152-ud15
    ownerReferences:
    - apiVersion: apps/v1
      blockOwnerDeletion: true
      controller: true
      kind: ReplicaSet
      name: web-intro-54449bc466
      uid: 856fba94-6935-4577-ac8d-93933f2c32d3
    resourceVersion: "652"
    uid: 0ed9db2a-0e40-447a-8aaf-321d823d6f87
  spec:
    containers:
    - image: nginx:1.29.0-alpine
      imagePullPolicy: IfNotPresent
      name: web
      ports:
      - containerPort: 80
        name: http
        protocol: TCP
      resources: {}
      terminationMessagePath: /dev/termination-log
      terminationMessagePolicy: File
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: kube-api-access-tb5wx
        readOnly: true
    dnsPolicy: ClusterFirst
    enableServiceLinks: true
    nodeName: minikube
    preemptionPolicy: PreemptLowerPriority
    priority: 0
    restartPolicy: Always
    schedulerName: default-scheduler
    securityContext: {}
    serviceAccount: default
    serviceAccountName: default
    terminationGracePeriodSeconds: 30
    tolerations:
    - effect: NoExecute
      key: node.kubernetes.io/not-ready
      operator: Exists
      tolerationSeconds: 300
    - effect: NoExecute
      key: node.kubernetes.io/unreachable
      operator: Exists
      tolerationSeconds: 300
    volumes:
    - name: kube-api-access-tb5wx
      projected:
        defaultMode: 420
        sources:
        - serviceAccountToken:
            expirationSeconds: 3607
            path: token
        - configMap:
            items:
            - key: ca.crt
              path: ca.crt
            name: kube-root-ca.crt
        - downwardAPI:
            items:
            - fieldRef:
                apiVersion: v1
                fieldPath: metadata.namespace
              path: namespace
  status:
    conditions:
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:37Z"
      observedGeneration: 1
      status: "True"
      type: PodReadyToStartContainers
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:36Z"
      observedGeneration: 1
      status: "True"
      type: Initialized
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:37Z"
      observedGeneration: 1
      status: "True"
      type: Ready
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:37Z"
      observedGeneration: 1
      status: "True"
      type: ContainersReady
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:36Z"
      observedGeneration: 1
      status: "True"
      type: PodScheduled
    containerStatuses:
    - containerID: containerd://7a1492dba11556303e257888a06bb20643d02281215d067fbb5c541b10d2a020
      image: docker.io/library/nginx:1.29.0-alpine
      imageID: docker.io/library/nginx@sha256:d67ea0d64d518b1bb04acde3b00f722ac3e9764b3209a9b0a98924ba35e4b779
      lastState: {}
      name: web
      ready: true
      resources: {}
      restartCount: 0
      started: true
      state:
        running:
          startedAt: "2026-11-04T08:15:37Z"
      user:
        linux:
          gid: 0
          supplementalGroups:
          - 0
          - 1
          - 2
          - 3
          - 4
          - 6
          - 10
          - 11
          - 20
          - 26
          - 27
          uid: 0
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: kube-api-access-tb5wx
        readOnly: true
        recursiveReadOnly: Disabled
    hostIP: 192.168.49.2
    hostIPs:
    - ip: 192.168.49.2
    observedGeneration: 1
    phase: Running
    podIP: 10.244.0.7
    podIPs:
    - ip: 10.244.0.7
    qosClass: BestEffort
    resources: {}
    startTime: "2026-11-04T08:15:36Z"
- apiVersion: v1
  kind: Pod
  metadata:
    creationTimestamp: "2026-11-04T08:15:33Z"
    generateName: web-intro-54449bc466-
    generation: 1
    labels:
      app: web-intro
      pod-template-hash: 54449bc466
    name: web-intro-54449bc466-q7qk6
    namespace: ft152-ud15
    ownerReferences:
    - apiVersion: apps/v1
      blockOwnerDeletion: true
      controller: true
      kind: ReplicaSet
      name: web-intro-54449bc466
      uid: 856fba94-6935-4577-ac8d-93933f2c32d3
    resourceVersion: "618"
    uid: e9465568-8aff-45b4-a8e8-49d8dbb1f8d9
  spec:
    containers:
    - image: nginx:1.29.0-alpine
      imagePullPolicy: IfNotPresent
      name: web
      ports:
      - containerPort: 80
        name: http
        protocol: TCP
      resources: {}
      terminationMessagePath: /dev/termination-log
      terminationMessagePolicy: File
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: kube-api-access-jck9m
        readOnly: true
    dnsPolicy: ClusterFirst
    enableServiceLinks: true
    nodeName: minikube
    preemptionPolicy: PreemptLowerPriority
    priority: 0
    restartPolicy: Always
    schedulerName: default-scheduler
    securityContext: {}
    serviceAccount: default
    serviceAccountName: default
    terminationGracePeriodSeconds: 30
    tolerations:
    - effect: NoExecute
      key: node.kubernetes.io/not-ready
      operator: Exists
      tolerationSeconds: 300
    - effect: NoExecute
      key: node.kubernetes.io/unreachable
      operator: Exists
      tolerationSeconds: 300
    volumes:
    - name: kube-api-access-jck9m
      projected:
        defaultMode: 420
        sources:
        - serviceAccountToken:
            expirationSeconds: 3607
            path: token
        - configMap:
            items:
            - key: ca.crt
              path: ca.crt
            name: kube-root-ca.crt
        - downwardAPI:
            items:
            - fieldRef:
                apiVersion: v1
                fieldPath: metadata.namespace
              path: namespace
  status:
    conditions:
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:33Z"
      observedGeneration: 1
      status: "True"
      type: PodReadyToStartContainers
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:33Z"
      observedGeneration: 1
      status: "True"
      type: Initialized
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:36Z"
      observedGeneration: 1
      status: "True"
      type: Ready
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:36Z"
      observedGeneration: 1
      status: "True"
      type: ContainersReady
    - lastProbeTime: null
      lastTransitionTime: "2026-11-04T08:15:33Z"
      observedGeneration: 1
      status: "True"
      type: PodScheduled
    containerStatuses:
    - containerID: containerd://0ebff4f2947b5c3e1b54872dcf055509bfac996acbd9491fcbf23ee6f42fed9a
      image: docker.io/library/nginx:1.29.0-alpine
      imageID: docker.io/library/nginx@sha256:d67ea0d64d518b1bb04acde3b00f722ac3e9764b3209a9b0a98924ba35e4b779
      lastState: {}
      name: web
      ready: true
      resources: {}
      restartCount: 0
      started: true
      state:
        running:
          startedAt: "2026-11-04T08:15:36Z"
      user:
        linux:
          gid: 0
          supplementalGroups:
          - 0
          - 1
          - 2
          - 3
          - 4
          - 6
          - 10
          - 11
          - 20
          - 26
          - 27
          uid: 0
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: kube-api-access-jck9m
        readOnly: true
        recursiveReadOnly: Disabled
    hostIP: 192.168.49.2
    hostIPs:
    - ip: 192.168.49.2
    observedGeneration: 1
    phase: Running
    podIP: 10.244.0.6
    podIPs:
    - ip: 10.244.0.6
    qosClass: BestEffort
    resources: {}
    startTime: "2026-11-04T08:15:33Z"
kind: List
metadata:
  resourceVersion: ""
deployment.apps/web-intro 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

```

### Test HTTP dopo aggiornamento immagine

```text
2026-11-04T09:15:47+01:00
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              0100    615 100    615   0      0 234.6k      0                              0100    615 100    615   0      0 233.1k      0                              0100    615 100    615   0      0 232.1k      0                              0
HTTP/1.1 200 OK
Server: nginx/1.29.0
Date: Wed, 04 Nov 2026 08:15:47 GMT
Content-Type: text/html
Content-Length: 615
Last-Modified: Tue, 24 Jun 2025 17:57:38 GMT
Connection: keep-alive
ETag: "685ae712-267"
Accept-Ranges: bytes

<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

### Dopo il rollback dell’immagine

```text
2026-11-04T09:15:52+01:00
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                SELECTOR
deployment.apps/web-intro   3/3     3            3           59s   web          nginx:1.28.0-alpine   app=web-intro

NAME                                   DESIRED   CURRENT   READY   AGE   CONTAINERS   IMAGES                SELECTOR
replicaset.apps/web-intro-54449bc466   0         0         0       19s   web          nginx:1.29.0-alpine   app=web-intro,pod-template-hash=54449bc466
replicaset.apps/web-intro-846844b5c9   3         3         3       59s   web          nginx:1.28.0-alpine   app=web-intro,pod-template-hash=846844b5c9

NAME                             READY   STATUS        RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
pod/web-intro-54449bc466-49ntp   0/1     Completed     0          15s   10.244.0.8    minikube   <none>           <none>
pod/web-intro-54449bc466-q7qk6   1/1     Terminating   0          19s   10.244.0.6    minikube   <none>           <none>
pod/web-intro-846844b5c9-bs55z   1/1     Running       0          1s    10.244.0.10   minikube   <none>           <none>
pod/web-intro-846844b5c9-gpwnv   1/1     Running       0          0s    10.244.0.11   minikube   <none>           <none>
pod/web-intro-846844b5c9-vtsgr   1/1     Running       0          1s    10.244.0.9    minikube   <none>           <none>
deployment.apps/web-intro 
REVISION  CHANGE-CAUSE
2         <none>
3         <none>

```

### Test HTTP dopo rollback

```text
2026-11-04T09:16:00+01:00
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              0100    615 100    615   0      0 194.3k      0                              0100    615 100    615   0      0 193.0k      0                              0100    615 100    615   0      0 192.3k      0                              0
HTTP/1.1 200 OK
Server: nginx/1.28.0
Date: Wed, 04 Nov 2026 08:16:00 GMT
Content-Type: text/html
Content-Length: 615
Last-Modified: Wed, 23 Apr 2025 12:59:25 GMT
Connection: keep-alive
ETag: "6808e42d-267"
Accept-Ranges: bytes

<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

### Guasto di immagine: stato e messaggio osservati

```text
2026-11-04T09:16:32+01:00
NAME                         READY   STATUS             RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
web-intro-6d4c975bcd-28h75   0/1     ImagePullBackOff   0          24s   10.244.0.12   minikube   <none>           <none>
web-intro-846844b5c9-bs55z   1/1     Running            0          41s   10.244.0.10   minikube   <none>           <none>
web-intro-846844b5c9-gpwnv   1/1     Running            0          40s   10.244.0.11   minikube   <none>           <none>
web-intro-846844b5c9-vtsgr   1/1     Running            0          41s   10.244.0.9    minikube   <none>           <none>
Name:             web-intro-6d4c975bcd-28h75
Namespace:        ft152-ud15
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Wed, 04 Nov 2026 09:16:08 +0100
Labels:           app=web-intro
                  pod-template-hash=6d4c975bcd
Annotations:      <none>
Status:           Pending
IP:               10.244.0.12
IPs:
  IP:           10.244.0.12
Controlled By:  ReplicaSet/web-intro-6d4c975bcd
Containers:
  web:
    Container ID:   
    Image:          nginx:tag-ft152-che-non-esiste
    Image ID:       
    Port:           80/TCP (http)
    Host Port:      0/TCP (http)
    State:          Waiting
      Reason:       ImagePullBackOff
    Ready:          False
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-zrkd2 (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True 
  Initialized                 True 
  Ready                       False 
  ContainersReady             False 
  PodScheduled                True 
Volumes:
  kube-api-access-zrkd2:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age               From               Message
  ----     ------     ----              ----               -------
  Normal   Scheduled  25s               default-scheduler  Successfully assigned ft152-ud15/web-intro-6d4c975bcd-28h75 to minikube
  Normal   BackOff    24s               kubelet            spec.containers{web}: Back-off pulling image "nginx:tag-ft152-che-non-esiste"
  Warning  Failed     24s               kubelet            spec.containers{web}: Error: ImagePullBackOff
  Normal   Pulling    8s (x2 over 25s)  kubelet            spec.containers{web}: Pulling image "nginx:tag-ft152-che-non-esiste"
  Warning  Failed     7s (x2 over 24s)  kubelet            spec.containers{web}: Failed to pull image "nginx:tag-ft152-che-non-esiste": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:tag-ft152-che-non-esiste": failed to resolve reference "docker.io/library/nginx:tag-ft152-che-non-esiste": docker.io/library/nginx:tag-ft152-che-non-esiste: not found
  Warning  Failed     7s (x2 over 24s)  kubelet            spec.containers{web}: Error: ErrImagePull
LAST SEEN   TYPE      REASON              OBJECT                            MESSAGE
42s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled up replica set web-intro-846844b5c9 from 0 to 1
100s        Normal    Pulling             pod/web-intro-846844b5c9-dnxw6    Pulling image "nginx:1.28.0-alpine"
100s        Normal    SuccessfulCreate    replicaset/web-intro-846844b5c9   Created pod: web-intro-846844b5c9-dnxw6
100s        Normal    Scheduled           pod/web-intro-846844b5c9-dnxw6    Successfully assigned ft152-ud15/web-intro-846844b5c9-dnxw6 to minikube
97s         Normal    Created             pod/web-intro-846844b5c9-dnxw6    Container created
97s         Normal    Started             pod/web-intro-846844b5c9-dnxw6    Container started
97s         Normal    Pulled              pod/web-intro-846844b5c9-dnxw6    Successfully pulled image "nginx:1.28.0-alpine" in 2.599s (2.599s including waiting). Image size: 21015643 bytes.
72s         Normal    Scheduled           pod/web-intro-846844b5c9-lrtcs    Successfully assigned ft152-ud15/web-intro-846844b5c9-lrtcs to minikube
72s         Normal    Created             pod/web-intro-846844b5c9-lrtcs    Container created
72s         Normal    SuccessfulCreate    replicaset/web-intro-846844b5c9   Created pod: web-intro-846844b5c9-ndvdm
72s         Normal    Pulled              pod/web-intro-846844b5c9-ndvdm    Container image "nginx:1.28.0-alpine" already present on machine and can be accessed by the pod
72s         Normal    Created             pod/web-intro-846844b5c9-ndvdm    Container created
72s         Normal    Started             pod/web-intro-846844b5c9-ndvdm    Container started
72s         Normal    Scheduled           pod/web-intro-846844b5c9-ndvdm    Successfully assigned ft152-ud15/web-intro-846844b5c9-ndvdm to minikube
72s         Normal    Pulled              pod/web-intro-846844b5c9-lrtcs    Container image "nginx:1.28.0-alpine" already present on machine and can be accessed by the pod
72s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled up replica set web-intro-846844b5c9 from 1 to 3
72s         Normal    Started             pod/web-intro-846844b5c9-lrtcs    Container started
72s         Normal    SuccessfulCreate    replicaset/web-intro-846844b5c9   Created pod: web-intro-846844b5c9-lrtcs
60s         Normal    SuccessfulCreate    replicaset/web-intro-54449bc466   Created pod: web-intro-54449bc466-q7qk6
60s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled up replica set web-intro-54449bc466 from 0 to 1
60s         Normal    Pulling             pod/web-intro-54449bc466-q7qk6    Pulling image "nginx:1.29.0-alpine"
60s         Normal    Scheduled           pod/web-intro-54449bc466-q7qk6    Successfully assigned ft152-ud15/web-intro-54449bc466-q7qk6 to minikube
57s         Normal    SuccessfulDelete    replicaset/web-intro-846844b5c9   Deleted pod: web-intro-846844b5c9-ndvdm
57s         Normal    Killing             pod/web-intro-846844b5c9-ndvdm    Stopping container web
57s         Normal    SuccessfulCreate    replicaset/web-intro-54449bc466   Created pod: web-intro-54449bc466-5z49c
57s         Normal    Started             pod/web-intro-54449bc466-q7qk6    Container started
57s         Normal    Created             pod/web-intro-54449bc466-q7qk6    Container created
57s         Normal    Pulled              pod/web-intro-54449bc466-q7qk6    Successfully pulled image "nginx:1.29.0-alpine" in 2.804s (2.804s including waiting). Image size: 22414794 bytes.
57s         Normal    Scheduled           pod/web-intro-54449bc466-5z49c    Successfully assigned ft152-ud15/web-intro-54449bc466-5z49c to minikube
57s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled down replica set web-intro-846844b5c9 from 3 to 2
57s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled up replica set web-intro-54449bc466 from 1 to 2
56s         Normal    Killing             pod/web-intro-846844b5c9-dnxw6    Stopping container web
56s         Normal    Pulled              pod/web-intro-54449bc466-5z49c    Container image "nginx:1.29.0-alpine" already present on machine and can be accessed by the pod
56s         Normal    Started             pod/web-intro-54449bc466-5z49c    Container started
56s         Normal    SuccessfulCreate    replicaset/web-intro-54449bc466   Created pod: web-intro-54449bc466-49ntp
56s         Normal    Created             pod/web-intro-54449bc466-5z49c    Container created
56s         Normal    SuccessfulDelete    replicaset/web-intro-846844b5c9   Deleted pod: web-intro-846844b5c9-lrtcs
56s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled down replica set web-intro-846844b5c9 from 1 to 0
56s         Normal    Scheduled           pod/web-intro-54449bc466-49ntp    Successfully assigned ft152-ud15/web-intro-54449bc466-49ntp to minikube
56s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled up replica set web-intro-54449bc466 from 2 to 3
56s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled down replica set web-intro-846844b5c9 from 2 to 1
56s         Normal    Pulled              pod/web-intro-54449bc466-49ntp    Container image "nginx:1.29.0-alpine" already present on machine and can be accessed by the pod
56s         Normal    Created             pod/web-intro-54449bc466-49ntp    Container created
56s         Normal    Started             pod/web-intro-54449bc466-49ntp    Container started
56s         Normal    SuccessfulDelete    replicaset/web-intro-846844b5c9   Deleted pod: web-intro-846844b5c9-dnxw6
56s         Normal    Killing             pod/web-intro-846844b5c9-lrtcs    Stopping container web
42s         Normal    SuccessfulCreate    replicaset/web-intro-846844b5c9   Created pod: web-intro-846844b5c9-vtsgr
42s         Normal    SuccessfulCreate    replicaset/web-intro-846844b5c9   Created pod: web-intro-846844b5c9-bs55z
42s         Normal    Killing             pod/web-intro-54449bc466-5z49c    Stopping container web
42s         Normal    ScalingReplicaSet   deployment/web-intro              Scaled down replica set web-intro-54449bc466 from 3 to 2
42s         Normal    Scheduled           pod/web-intro-846844b5c9-bs55z    Successfully assigned ft152-ud15/web-intro-846844b5c9-bs55z to minikube
42s         Normal    SuccessfulDelete    replicaset/web-intro-54449bc466   Deleted pod: web-intro-54449bc466-5z49c
42s         Normal    Pulled              pod/web-intro-846844b5c9-bs55z    Container image "nginx:1.28.0-alpine" already present on machine and can be accessed by the pod
42s         Normal    Scheduled           pod/web-intro-846844b5c9-vtsgr    Successfully assigned ft152-ud15/web-intro-846844b5c9-vtsgr to minikube
42s         Normal    Pulled              pod/web-intro-846844b5c9-vtsgr    Container image "nginx:1.28.0-alpine" already present on machine and can be accessed by the pod
42s         Normal    Created             pod/web-intro-846844b5c9-vtsgr    Container created
42s         Normal    Started             pod/web-intro-846844b5c9-vtsgr    Container started
25s         Normal    ScalingReplicaSet   deployment/web-intro              (combined from similar events): Scaled up replica set web-intro-6d4c975bcd from 0 to 1
41s         Normal    SuccessfulCreate    replicaset/web-intro-846844b5c9   Created pod: web-intro-846844b5c9-gpwnv
41s         Normal    Pulled              pod/web-intro-846844b5c9-gpwnv    Container image "nginx:1.28.0-alpine" already present on machine and can be accessed by the pod
41s         Normal    SuccessfulDelete    replicaset/web-intro-54449bc466   Deleted pod: web-intro-54449bc466-49ntp
41s         Normal    SuccessfulDelete    replicaset/web-intro-54449bc466   Deleted pod: web-intro-54449bc466-q7qk6
41s         Normal    Created             pod/web-intro-846844b5c9-bs55z    Container created
41s         Normal    Scheduled           pod/web-intro-846844b5c9-gpwnv    Successfully assigned ft152-ud15/web-intro-846844b5c9-gpwnv to minikube
41s         Normal    Killing             pod/web-intro-54449bc466-q7qk6    Stopping container web
41s         Normal    Started             pod/web-intro-846844b5c9-bs55z    Container started
41s         Normal    Created             pod/web-intro-846844b5c9-gpwnv    Container created
41s         Normal    Killing             pod/web-intro-54449bc466-49ntp    Stopping container web
41s         Normal    Started             pod/web-intro-846844b5c9-gpwnv    Container started
8s          Normal    Pulling             pod/web-intro-6d4c975bcd-28h75    Pulling image "nginx:tag-ft152-che-non-esiste"
25s         Normal    SuccessfulCreate    replicaset/web-intro-6d4c975bcd   Created pod: web-intro-6d4c975bcd-28h75
25s         Normal    Scheduled           pod/web-intro-6d4c975bcd-28h75    Successfully assigned ft152-ud15/web-intro-6d4c975bcd-28h75 to minikube
24s         Normal    BackOff             pod/web-intro-6d4c975bcd-28h75    Back-off pulling image "nginx:tag-ft152-che-non-esiste"
7s          Warning   Failed              pod/web-intro-6d4c975bcd-28h75    Error: ErrImagePull
7s          Warning   Failed              pod/web-intro-6d4c975bcd-28h75    Failed to pull image "nginx:tag-ft152-che-non-esiste": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:tag-ft152-che-non-esiste": failed to resolve reference "docker.io/library/nginx:tag-ft152-che-non-esiste": docker.io/library/nginx:tag-ft152-che-non-esiste: not found
24s         Warning   Failed              pod/web-intro-6d4c975bcd-28h75    Error: ImagePullBackOff
```

### Conclusione del guidato: riferimento conservato

```text
2026-11-04T09:17:18+01:00
# Micro-demo: Nginx standard, non il frontend completo del Catalogo.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-intro
  namespace: ft152-ud15
spec:
  replicas: 1
  # Conserviamo i template precedenti per l'esercizio di rollback.
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: web-intro
  template:
    metadata:
      labels:
        app: web-intro
    spec:
      containers:
        - name: web
          image: nginx:1.28.0-alpine
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 80
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS   IMAGES                SELECTOR
deployment.apps/web-intro   1/1     1            1           2m25s   web          nginx:1.28.0-alpine   app=web-intro

NAME                                   DESIRED   CURRENT   READY   AGE     CONTAINERS   IMAGES                           SELECTOR
replicaset.apps/web-intro-54449bc466   0         0         0       105s    web          nginx:1.29.0-alpine              app=web-intro,pod-template-hash=54449bc466
replicaset.apps/web-intro-6d4c975bcd   0         0         0       70s     web          nginx:tag-ft152-che-non-esiste   app=web-intro,pod-template-hash=6d4c975bcd
replicaset.apps/web-intro-846844b5c9   1         1         1       2m25s   web          nginx:1.28.0-alpine              app=web-intro,pod-template-hash=846844b5c9

NAME                             READY   STATUS      RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
pod/web-intro-846844b5c9-bs55z   1/1     Running     0          87s   10.244.0.10   minikube   <none>           <none>
pod/web-intro-846844b5c9-gpwnv   0/1     Completed   0          86s   10.244.0.11   minikube   <none>           <none>
pod/web-intro-846844b5c9-vtsgr   0/1     Completed   0          87s   10.244.0.9    minikube   <none>           <none>
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: "5"
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"web-intro","namespace":"ft152-ud15"},"spec":{"replicas":1,"revisionHistoryLimit":5,"selector":{"matchLabels":{"app":"web-intro"}},"template":{"metadata":{"labels":{"app":"web-intro"}},"spec":{"containers":[{"image":"nginx:1.28.0-alpine","imagePullPolicy":"IfNotPresent","name":"web","ports":[{"containerPort":80,"name":"http"}]}]}}}}
  creationTimestamp: "2026-11-04T08:14:53Z"
  generation: 8
  name: web-intro
  namespace: ft152-ud15
  resourceVersion: "987"
  uid: 4b66c092-0403-4b17-a566-f8715b75ea2c
spec:
  progressDeadlineSeconds: 600
  replicas: 1
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: web-intro
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: web-intro
    spec:
      containers:
      - image: nginx:1.28.0-alpine
        imagePullPolicy: IfNotPresent
        name: web
        ports:
        - containerPort: 80
          name: http
          protocol: TCP
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
status:
  availableReplicas: 1
  conditions:
  - lastTransitionTime: "2026-11-04T08:15:21Z"
    lastUpdateTime: "2026-11-04T08:15:21Z"
    message: Deployment has minimum availability.
    reason: MinimumReplicasAvailable
    status: "True"
    type: Available
  - lastTransitionTime: "2026-11-04T08:14:53Z"
    lastUpdateTime: "2026-11-04T08:16:33Z"
    message: ReplicaSet "web-intro-846844b5c9" has successfully progressed.
    reason: NewReplicaSetAvailable
    status: "True"
    type: Progressing
  observedGeneration: 8
  readyReplicas: 1
  replicas: 1
  terminatingReplicas: 0
  updatedReplicas: 1
Name:                     web-intro
Namespace:                ft152-ud15
Labels:                   <none>
Annotations:              <none>
Selector:                 app=web-intro
Type:                     ClusterIP
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.101.39.241
IPs:                      10.101.39.241
Port:                     http  80/TCP
TargetPort:               http/TCP
Endpoints:                10.244.0.10:80
Session Affinity:         None
Internal Traffic Policy:  Cluster
Events:                   <none>
apiVersion: v1
items:
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.0.10
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: minikube
    targetRef:
      kind: Pod
      name: web-intro-846844b5c9-bs55z
      namespace: ft152-ud15
      uid: b6056b63-20a3-4168-b89c-31a3d28b7311
  kind: EndpointSlice
  metadata:
    annotations:
      endpoints.kubernetes.io/last-change-trigger-time: "2026-11-04T08:17:18Z"
    creationTimestamp: "2026-11-04T08:15:04Z"
    generateName: web-intro-
    generation: 27
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: web-intro
    name: web-intro-759lz
    namespace: ft152-ud15
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: web-intro
      uid: bfaf2ce7-fd5e-4dd7-8c0b-04420473b2bd
    resourceVersion: "985"
    uid: 795065b7-74ba-47f8-bd4e-7655057559bd
  ports:
  - name: http
    port: 80
    protocol: TCP
kind: List
metadata:
  resourceVersion: ""
State Recv-Q Send-Q Local Address:Port Peer Address:Port
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured

```

### Chiusura comune della giornata: ambiente conservato

```text
2026-11-04T09:19:17+01:00
State Recv-Q Send-Q Local Address:Port Peer Address:Port
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured

NAME                           READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS   IMAGES                SELECTOR
deployment.apps/web-autonomo   2/2     2            2           100s    web          nginx:1.28.0-alpine   app=web-autonomo
deployment.apps/web-intro      1/1     1            1           4m25s   web          nginx:1.28.0-alpine   app=web-intro

NAME                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE     SELECTOR
service/web-autonomo   ClusterIP   10.105.116.11   <none>        80/TCP    100s    app=web-autonomo
service/web-intro      ClusterIP   10.101.39.241   <none>        80/TCP    4m14s   app=web-intro

NAME                                READY   STATUS    RESTARTS   AGE     IP            NODE       NOMINATED NODE   READINESS GATES
pod/web-autonomo-85f6469d54-dtmdk   1/1     Running   0          100s    10.244.0.13   minikube   <none>           <none>
pod/web-autonomo-85f6469d54-pkwz7   1/1     Running   0          100s    10.244.0.14   minikube   <none>           <none>
pod/web-intro-846844b5c9-bs55z      1/1     Running   0          3m27s   10.244.0.10   minikube   <none>           <none>
```
