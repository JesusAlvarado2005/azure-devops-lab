# UD11 — Risposte alle domande sui concetti

## 1.
**Risposta:** il registry è il servizio che ospita le immagini, per esempio myregistry.azurecr.io, il repository raggruppa le versioni della stessa immagine come catalog-backend, il tag è un'etichetta leggibile come v1 e il digest è lo sha256 che identifica proprio il contenuto

## 2.
**Risposta:** perché latest è solo un tag come gli altri, non vuol dire che sia la versione più nuova o approvata e può puntare a contenuti diversi nel tempo, così non sai quale versione sta girando

## 3.
**Risposta:** perché il login server è un valore che dà Azure e non è per forza uguale al nome della risorsa, se lo leggo con az acr show uso quello vero e non sbaglio

## 4.
**Risposta:** l'Environment è l'ambiente condiviso dove vivono una o più app, la Container App è l'applicazione vera con immagine, variabili, CPU, ingress e scaling

## 5.
**Risposta:** la revision è una versione fissa della configurazione dell'app, la replica è un'istanza che gira davvero di quella revision, una revision può avere più repliche o anche zero

## 6.
**Risposta:** serve a far arrivare il traffico HTTP da fuori al container, con l'external ingress l'app ha un indirizzo HTTPS raggiungibile da internet

## 7.
**Risposta:** perché l'ingress manda il traffico su quella porta, se l'app ascolta sulla 8000 e il target port è 9999 non c'è nessuno che risponde anche se l'app e la revision esistono

## 8.
**Risposta:** perché così non uso username e password del registry, l'identità è della risorsa e i permessi si danno con RBAC, niente segreti statici in giro

## 9.
**Risposta:** dà il permesso di scaricare le immagini dal registry, è il minimo che serve alla Container App perché lei deve solo leggere e non pubblicare

## 10.
**Risposta:** viene creata una nuova revision con la nuova immagine e in single revision mode diventa lei quella attiva al posto della vecchia

## 11.
**Risposta:** perché prima di automatizzare bisogna capire cosa si sta automatizzando, facendolo a mano vedo chi fa push, chi fa pull, che identità si usa e che porta serve

## 12.
**Risposta:** con RBAC Registry Permissions si usano AcrPull e AcrPush per l'accesso alle immagini, con RBAC+ABAC quei ruoli non valgono per i repository e si usano i nuovi come Container Registry Repository Reader e Writer. Noi usiamo il primo per semplicità

## 13.
**Risposta:** perché in UD11 i comandi li lancio io dal mio terminale, l'agent serve quando queste operazioni le farà una pipeline in UD13 e UD14, e userà lo stesso Docker della mia macchina

## 14.
**Risposta:** la system-assigned è legata alla risorsa e se elimino la Container App sparisce anche lei, la user-assigned è una risorsa a parte che si può preparare prima e riusare su più risorse

## 15.
**Risposta:** con min replicas a 0 l'app scende a zero repliche quando non c'è traffico e non usa compute, ma ACR e le altre risorse restano e costano, per pulire davvero si elimina il resource group

## 16.
**Risposta:** seguo il percorso della richiesta, ingress external, target port giusto, revision attiva e healthy, repliche, log dell'app, immagine e tag presenti in ACR, identità con AcrPull e variabili, senza cambiare subito l'immagine
