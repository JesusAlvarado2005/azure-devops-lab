# UD08 — Consegna laboratorio guidato

## Repository

- repository: JesusAlvarado2005/azure-devops-lab
- branch principale: main
- `gh auth status` verificato: sì
- working tree iniziale pulito: sì, git status senza modifiche su main allineata a origin

## Collaborazione ricevuta sul mio repository

- collaborator: GiulioCornelli
- invito accettato: sì
- branch contributor: feature/ud08-collab-GiulioCornelli
- numero PR: 1
- URL PR: https://github.com/JesusAlvarado2005/azure-devops-lab/pull/1
- prima review: Request changes
- modifica richiesta: completare il file docs/ud08-collaboration.md con la review e l'esito
- nuovo commit: f322195 docs: address UD08 review, comparso da solo nella stessa PR
- approvazione/commento finale: Approve
- merge: fatto da me, su main è fa36f5b UD08: collaboration evidence (#1)
- branch remota eliminata: sì, feature/ud08-collab-GiulioCornelli eliminata da origin
- collaboratore rimosso: sì, GiulioCornelli non è più tra i collaboratori

## Collaborazione eseguita sul repository altrui

- repository: GiulioCornelli/azure-devops-lab
- branch: feature/ud08-collab-JesusAlvarado2005
- numero PR: 1
- prima review ricevuta: Request changes
- correzione eseguita: ho aggiunto review alla lista e la sezione Esito in docs/ud08-collaboration.md, commit ab2a364 docs: address UD08 review pushato sullo stesso branch
- merge completato: sì, fatto da GiulioCornelli

## Conflitto locale

- branch A: lab/conflict-a con PORT=9000
- branch B: lab/conflict-b con PORT=7000, tutti e due partiti da lab/conflict-base con PORT=8000
- file: ud08-conflict.txt
- marker osservati: <<<<<<< HEAD con PORT=7000, ======= e >>>>>>> lab/conflict-a con PORT=9000
- contenuto finale scelto: PORT=8000, cioè la porta che usa davvero il Catalogo in config.json. Ho tolto tutti i marker e lasciato una riga sola. La prima volta avevo fatto git add subito e avevo committato il file con i marker dentro, così ho rifatto l'esercizio
- commit risoluzione: 080dcf5 lab: resolve port conflict
- cleanup completato: sì, eliminati lab/conflict-a, lab/conflict-b e lab/conflict-base e il file non è su main

## Catalogo prodotti

- server avviato: python3 server.py in ascolto su 127.0.0.1:8000
- `/health`: 200
- `/api/products`: 200
- `/api/products/P001`: 200
- `/api/products/XXX`: 404 che è giusto perché il prodotto non esiste
- frontend browser: la pagina carica e chiama /api/products con 200, la tabella mostra i prodotti. L'unico 404 è /favicon.ico che non esiste e non è un problema
- prodotti restituiti: 4
- prodotto LOW: P002 Monitor con stock 4 sotto la soglia 5

## Architettura

- frontend: static/index.html con il JavaScript che chiama /api/products
- backend/API: server.py, un solo programma Python che serve la pagina e risponde in JSON
- configurazione: config.json con host, porta 8000, api_prefix /api e soglia 5
- dati: data/products.json con i 4 prodotti, non c'è un database
- endpoint: GET /health, GET /api/products, GET /api/products/<id>, GET /

## Baseline Git

- commit: 01b61b6 feat: add local product catalog
- push/PR: catalogo pushato su main, poi la modifica a config.json è passata dalla PR 2
- stato finale main: 5fa100b allineato con origin/main e working tree pulito a parte le consegne
