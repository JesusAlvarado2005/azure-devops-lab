# UD16 — Verifica individuale

Prove osservate il **2026-11-05** su Minikube (`context=minikube`, Kubernetes v1.37.0), namespace `ft152-catalogo`.

## Risposte 1–4

**1. Quale vantaggio offre mantenere la soglia del Catalogo in una ConfigMap anziché nel Dockerfile?**

La ConfigMap separa la configurazione dal codice e dall'immagine: la stessa immagine `catalog-backend:ud16` può girare con soglie diverse senza rebuild né nuovo push nel registry. Nel laboratorio ho cambiato `LOW_STOCK_THRESHOLD` da `5` a `10` e poi di nuovo a `5` modificando solo `k8s/ud16/configmap.yaml` e applicando il manifest; l'immagine è rimasta identica. Inoltre la configurazione è versionata e revisionabile insieme ai manifest, e può essere diversa per ambiente.

**2. Perché aggiornare una ConfigMap usata come variabile d'ambiente non modifica necessariamente il comportamento di un processo già avviato?**

Le variabili con `envFrom`/`env` vengono materializzate nell'ambiente del container alla sua partenza. Il processo legge quei valori una volta e non riceve notifiche quando la ConfigMap cambia. L'ho verificato: dopo `kubectl apply` con soglia `10`, `printenv LOW_STOCK_THRESHOLD` nel Pod restituiva ancora `5` e P001 restava `OK`; solo dopo `kubectl rollout restart deployment/backend` l'ambiente è diventato `10` e P001 è passato a `LOW`. Il file montato in `/etc/catalog-config` ha un comportamento diverso (il kubelet può aggiornarlo), ma serve comunque che l'applicazione lo rilegga.

**3. Quale differenza di scopo esiste fra ConfigMap e Secret? Perché Base64 non protegge una password?**

La ConfigMap è pensata per configurazione non riservata (host, porta, soglia, directory); il Secret è pensato per dati che non devono essere pubblici (password, token, chiavi). Nel laboratorio `catalog-config` conteneva valori leggibili e `catalog-demo` un dato dichiaratamente fittizio, mai stampato come prova. Base64 è solo una codifica reversibile: chiunque legga il manifest o il Secret può decodificarlo. La protezione reale viene da RBAC, gestione sicura delle credenziali e cifratura dello storage del cluster, non dalla codifica.

**4. Che cosa rappresentano StorageClass, PersistentVolume e PersistentVolumeClaim? In quale ordine entrano in gioco nel nostro esempio?**

La **StorageClass** descrive come provisionare il volume (provisioner e parametri); il **PersistentVolume (PV)** è la risorsa di storage effettiva; il **PersistentVolumeClaim (PVC)** è la richiesta di storage (capacità, modalità di accesso) che un Pod monta. Nel nostro esempio il PVC `catalog-runtime` (1Gi, `RWO`) è stato creato per primo; la StorageClass `standard` (`k8s.io/minikube-hostpath`) ha creato dinamicamente il PV, identificato dal volume `pvc-d764dc79-0308-43c7-a3a3-0f12e8d20410`; il PVC è passato a `Bound` e il Deployment backend lo ha montato su `/runtime`.

## Risposte 5–8

**5. Quale prova dimostra la sopravvivenza del contatore dopo la ricreazione del Pod? Perché `PVC Bound` da solo non basta?**

La prova è aver letto lo stesso valore da un Pod **nuovo**. Ho incrementato il contatore a `2`, eliminato il solo Pod backend (`backend-7cc7db44c6-jbcvm`, IP `10.244.0.12`), atteso il nuovo Pod (`backend-7cc7db44c6-vxwhf`, IP `10.244.0.13`) e riletto `/runtime/counter.txt`: conteneva ancora `2`. Successivamente un altro riavvio ha conservato il valore `3`. `PVC Bound` dimostra solo che esiste un'associazione con un volume: non dimostra che l'applicazione abbia scritto lì, né che il mount sia corretto. Servono il mount sul percorso usato dall'app e la rilettura dopo la sostituzione del Pod.

**6. Perché il Service `backend` è un riferimento migliore dell'IP di un Pod?**

L'IP del Pod cambia a ogni ricreazione (nel laboratorio è passato da `10.244.0.12` a `10.244.0.13` e poi `10.244.0.14`), mentre il Service mantiene un nome DNS stabile (`backend`) e un ClusterIP stabile (`10.99.242.43`). Il frontend usa `http://backend:8000` e non deve essere riconfigurato quando i Pod cambiano. Il Service inoltre seleziona i Pod tramite label e aggiorna gli EndpointSlice: se un Pod non è pronto o la label non corrisponde, il traffico non viene inviato a un IP sbagliato.

**7. Se il DNS interno risolve `backend`, ma il frontend riceve un `502`, quali due livelli controlleresti prima di cambiare i manifest?**

Prima il **Service e i suoi EndpointSlice**: il nome può risolvere anche con endpoint vuoti. Nel guasto intenzionale il Service esisteva e il DNS lo risolveva, ma il selector `app=backend-guasto` non corrispondeva alla label `app=backend`, quindi `get endpointslices` mostrava `ENDPOINTS <unset>` e `get endpoints` riportava `<none>`. Poi il **proxy del frontend e la sua configurazione**: nginx inoltra `/api/` e `/health` a `http://backend:8000`; con endpoint vuoti restituiva `502 Bad Gateway`. Solo dopo aver escluso questi due livelli ha senso modificare i manifest. Il ripristino del selector ha riportato l'EndpointSlice a `10.244.0.13` e le risposte a `200`.

**8. Quali ruoli hanno GatewayClass, Gateway, HTTPRoute e controller? Che cosa controlli prima di affermare che la route HTTP funziona?**

La **GatewayClass** dichiara l'implementazione (nel laboratorio `nginx`, controller `gateway.nginx.org/nginx-gateway-controller`); il **Gateway** definisce i listener (HTTP porta 80, namespace ammessi) e riceve un indirizzo; l'**HTTPRoute** collega host e path a un Service di backend (`catalogo.lab` → `frontend:80`); il **controller** (Nginx Gateway Fabric) riconcilia gli oggetti e configura il proxy. Prima di affermare che la route funziona controllo: `GatewayClass` `Accepted=True`, Gateway `Programmed=True` con listener e `attachedRoutes=1`, HTTPRoute `Accepted=True` e `ResolvedRefs=True`, Pod del controller `1/1`, Service del proxy con NodePort, e infine una richiesta HTTP reale con `Host: catalogo.lab` che restituisca `200`.

## Domande di raccordo architetturale

**Quale prova distingue port-forward e ingresso persistente?**

Il port-forward è un processo `kubectl` legato al terminale: inoltra una porta locale al Pod/Service e termina quando il processo viene chiuso. L'ho usato nelle fasi guidate (`8081`, `8082`) e dopo `pkill -x kubectl` le porte risultavano libere. L'ingresso persistente è un container Compose (`ft152-entry-ud16-ingresso-1`) che inoltra `127.0.0.1:18016` al NodePort `32483` della rete Minikube e resta attivo con `restart: unless-stopped`. La prova che distingue i due è aver chiuso i port-forward, verificato che `8081`/`8082` non fossero in ascolto e ottenuto comunque `200` su `http://127.0.0.1:18016/health` con `Host: catalogo.lab`. Il percorso passa da Gateway e HTTPRoute, non da un tunnel `kubectl`.

**CSI, PVC e dati applicativi sono la stessa cosa?**

No. Il **CSI** è l'interfaccia/driver che permette a Kubernetes di provisionare e montare volumi; in Minikube la StorageClass `standard` usa il provisioner `k8s.io/minikube-hostpath`, quindi non è un CSI cloud reale. Il **PVC** è la richiesta di storage e il suo binding a un PV; nel laboratorio `catalog-runtime` è `Bound` al volume `pvc-d764dc79-...`. I **dati applicativi** sono i file scritti dall'applicazione nel filesystem montato, nel nostro caso `/runtime/counter.txt`. Il PVC è il contenitore logico, il CSI è il meccanismo che lo realizza, i dati sono il contenuto: la prova che i tre collaborano è il contatore riletto dopo la sostituzione del Pod.

## Stato finale e considerazioni

Stato verificato dopo il laboratorio autonomo, con i comandi richiesti:

```text
deployment.apps/backend          1/1
deployment.apps/frontend         1/1
deployment.apps/catalog-nginx    1/1
pod/backend-75cfdd986d-twf8t     Running
pod/frontend-649cdc7bcd-spmlc    Running
pod/catalog-nginx-55b7697488-qjx6t Running
service/backend        ClusterIP 10.99.242.43:8000   selector app=backend
service/frontend       ClusterIP 10.110.80.43:80
service/catalog-nginx  NodePort  80:32483/TCP
pvc/catalog-runtime    Bound, 1Gi, standard
EndpointSlice backend  8000 → 10.244.0.14
gatewayclass nginx     Accepted=True
gateway/catalog        Programmed=True, address 10.109.4.45
httproute/catalog      Accepted=True, ResolvedRefs=True, host catalogo.lab
```

Configurazione finale: `LOW_STOCK_THRESHOLD=5`, ambiente del Pod `5`, P001 `stock 8` → `stock_status: OK`, contatore `3` su `/runtime/counter.txt`. Ingresso Compose attivo su `127.0.0.1:18016`; `/health`, `/api/products/P001` e `/` rispondono `200` con `Host: catalogo.lab`. Nessun port-forward aperto (`8081`/`8082` libere); `web-intro` della UD15 è rimasto `1/1`.

Non ho distrutto il PVC, il namespace né le risorse della UD15: l'ambiente resta pronto per la UD17. Limiti dichiarati: la prova di persistenza riguarda la sostituzione del Pod, non la perdita del nodo o un backup; l'ingresso è locale su Minikube e non rappresenta un'esposizione Internet.
