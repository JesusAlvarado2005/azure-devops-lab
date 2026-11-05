# Ingresso locale persistente verso il Gateway

Questo componente serve al solo laboratorio Docker Desktop/WSL. Un container Nginx esterno a Kubernetes pubblica una porta su 127.0.0.1 e inoltra al NodePort del proxy Gateway, sulla rete Docker del nodo Minikube. Non effettua port-forward a un Pod e non sostituisce il controller Gateway. Il modello standard applicativo rimane Gateway/HTTPRoute/Service; l'adattatore è specifico della postazione locale.

`configura.sh` legge il nodo Docker `minikube`, la rete effettiva e la porta NodePort del Service indicato. Scrive `.env` (senza credenziali), verifica Compose e si ferma. `compose.yaml` avvia l'ingresso; il template Nginx preserva Host e percorso. La scelta del Service è esplicita nel guidato. Se il profilo non usa Docker, il nodo ha nome diverso o più reti, interrompere e adattare la predisposizione: non cancellare il cluster.

La configurazione assume un engine Docker condiviso fra postazione e Minikube. `docker context show`, `docker inspect minikube` e `docker network inspect` permettono di verificarlo. La pubblicazione è locale al PC che ospita Docker, non al PC2 collegato via SSH. Un browser su un secondo PC richiede un progetto di rete distinto, non un cambio automatico a 0.0.0.0.

## Verifica e ripresa

Dalla cartella che contiene `.env`: `docker compose ps`, `docker compose logs --tail=30 ingresso` e `docker compose exec -T ingresso nginx -t`. Il proxy rimane attivo dopo la chiusura del terminale. Se Docker o Minikube vengono fermati, il servizio non è disponibile: avvia il profilo già esistente, verifica il NodePort e riesegui la configurazione. Se `.env` differisce, il programma non la sovrascrive: conserva il file precedente fuori da Git e valuta il cambiamento. Dopo cambio IP del nodo, usa `docker compose restart ingresso` per rinnovare la risoluzione del nome. Dopo cambio delle variabili usa `docker compose up -d`.

Un errore di porta occupata va diagnosticato su Windows e Docker (`Get-NetTCPConnection -LocalPort PORTA`, `docker ps`), non risolto terminando processi sconosciuti. Un 502 può nascere nell'ingresso esterno, nel Gateway o nel frontend: confronta log e prove del singolo livello. Nel terminale dell'ingresso, `docker compose exec -T ingresso wget -S -O - --header='Host: HOST_DELLA_ROUTE' http://NOME_NODO:NODEPORT/health` verifica direttamente il NodePort usando i valori reali di `.env`.

Su Docker Desktop il browser Windows raggiunge la porta pubblicata su localhost. Il localhost WSL può avere un comportamento diverso secondo NAT/mirrored e integrazione: prova anche con `curl.exe` da PowerShell. Non sostituire la prova mancante con un tunnel presentato come pubblicazione completata.

## Chiusura

`docker compose stop` ferma il solo ingresso di questo progetto; `docker compose up -d` lo riprende. Alla fine del corso `docker compose down` rimuove il proxy del progetto, senza eliminare la rete esterna Minikube e senza cancellare i PVC. Eseguire solo dalla cartella corretta, dopo aver letto `docker compose ps`. Non usare `down -v` su altri progetti.

## Fonti

- https://docs.docker.com/compose/how-tos/networking/
- https://docs.docker.com/engine/network/port-publishing/
- https://hub.docker.com/_/nginx
- https://docs.nginx.com/nginx-gateway-fabric/get-started/
