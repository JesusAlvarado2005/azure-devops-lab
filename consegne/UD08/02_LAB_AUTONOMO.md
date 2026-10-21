# UD08 — Consegna laboratorio autonomo

## Baseline

- health: 200
- products: 200 con i 4 prodotti

## Errore introdotto

- configurazione modificata: in config.json api_prefix da /api a /api-v2 senza toccare il frontend
- endpoint funzionante: /api-v2/products 200 e /health 200
- endpoint non funzionante: /api/products 404
- comportamento frontend: la pagina / si carica con 200 ma il JavaScript fa fetch("/api/products") che dà 404, quindi la tabella dei prodotti non si riempie

## Diagnosi

1. /health dà 200 quindi il server è acceso e raggiungibile, non è un problema di rete o di processo
2. /api-v2/products dà 200 quindi il backend risponde e legge i dati
3. /api/products dà 404 quindi il vecchio percorso non esiste più
4. in index.html il frontend chiama fetch("/api/products") cioè il percorso vecchio
5. frontend e backend non usano più lo stesso prefisso, il problema è la configurazione e il contratto API

## Fix

- causa: api_prefix in config.json cambiato in /api-v2 mentre il frontend usa ancora /api
- fix: ho rimesso "api_prefix": "/api" e git diff è diventato vuoto perché il file era tornato uguale a main
- environment aggiunto: "environment": "local" in config.json come modifica reale da versionare, il server la ignora

## Test finali

- `/health`: 200
- `/api/products`: 200
- `/api/products/P001`: 200
- `/api/products/XXX`: 404 corretto perché il prodotto non esiste
- browser: la pagina / risponde 200 e chiama /api/products che risponde 200

## Git

- branch: fix/ud08-api-prefix
- `git diff` verificato: sì, solo config.json con la riga environment e la virgola sulla riga prima
- commit: 3ac2ff1 config: add local environment to catalog
- push: git push -u origin fix/ud08-api-prefix
- PR: https://github.com/JesusAlvarado2005/azure-devops-lab/pull/2
- `gh pr diff` verificato: sì, un solo file config.json con la riga environment e nessun dato sensibile
- merge: squash merge della PR 2 con eliminazione del branch, su main è 5fa100b config: add local environment to catalog (#2)
- main sincronizzata: sì, git pull --ff-only e main locale uguale a origin/main su 5fa100b

## Distinzione

- review collaborativa: un'altra persona legge la mia modifica, può chiedere correzioni e approvare, come ha fatto Giulio sulla PR 1
- auto-verifica PR individuale: autore e revisore sono la stessa persona, quindi non è una review indipendente ma solo un controllo consapevole del diff prima del merge
