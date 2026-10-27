# UD10 — Consegna laboratorio guidato

## Preflight

- `docker version`: 29.9.1
- `docker compose version`: v5.6.0
- daemon: raggiungibile
- WSL2: no, sono su Fedora e Docker gira direttamente sul sistema senza Docker Desktop
- RESULT: OK

## Build backend

- image: catalog-backend
- tag: ud10
- build context: `app/catalogo-prodotti`
- Dockerfile: `docker/backend.Dockerfile`
- layer/history osservati: parte da python slim che è leggera, nella dir app copia server.py, poi crea l'utente appuser e gli dà i permessi su /app e /runtime, passa a quell'utente, setta le variabili e la porta 8000 e CMD avvia il server con python

## Container singolo

- nome: catalog-backend-ud10
- porta: 127.0.0.1:8000 → 8000
- health: 200, status ok
- products: 200, 4 prodotti, P002 e P004 LOW con soglia 5
- log: `Catalog backend listening on http://0.0.0.0:8000 threshold=5 runtime=/runtime`
- environment verificato: APP_PORT=8000, LOW_STOCK_THRESHOLD=5, RUNTIME_DIR=/runtime

il `grep -E` mi dava errore perché da me grep è ripgrep, con `command grep -E` funziona

## Compose

- backend: catalog-backend:ud10, solo `expose 8000` e non pubblicato fuori
- frontend: catalog-frontend:ud10, nginx su 127.0.0.1:8080 → 80
- rete: catalogo-prodotti_catalog-net, bridge
- volume: catalogo-prodotti_catalog-runtime su /runtime
- frontend URL: http://127.0.0.1:8080/
- backend healthy: sì, il frontend parte solo dopo per il depends_on service_healthy
- `/health`: 200
- `/api/products`: 200
- P001: 200
- XXX: 404

## Networking

- `backend` risolto dal frontend: sì, 172.19.0.2 e `/health` risponde ok
- `localhost:8000` dal frontend: Connection refused
- spiegazione: dentro il frontend localhost è il container frontend stesso, il backend è un altro container e si raggiunge col nome del servizio grazie al DNS di Docker

## Environment

- threshold iniziale: 5
- threshold temporaneo: 10
- effetto osservato: con 10 anche P001 che ha stock 8 diventa LOW, senza rifare la build basta `docker compose up -d`
- valore ripristinato: 5

## Volume

- counter before: 3
- counter after recreate: 4
- persistenza PASS/FAIL: PASS
- volume: catalogo-prodotti_catalog-runtime, `docker compose down` toglie container e rete ma il volume resta

## Lifecycle

- restart test: `docker compose restart backend`, torna healthy e `/health` da 8080 dà 200
- log backend: avvio con threshold=5 e le richieste a /health e /api/counter con 200
- log frontend: nginx parte con la configurazione e logga la GET /api/counter con 200

## Git

- commit: d2b8e79 feat: containerize product catalog with Docker Compose
- push/PR: non l'avevo pushato a parte, è finito dentro la PR #3 dell'autonomo con lo squash merge
