# UD10 — Consegna laboratorio autonomo

## Baseline

- compose ps: backend Up (healthy), frontend Up su 127.0.0.1:8080
- health: 200

## Errore

- variabile: LOW_STOCK_THRESHOLD
- valore errato: "not-a-number"
- stato backend: non parte, il container esce subito e non diventa healthy quindi il frontend non viene avviato
- log/errore: `ValueError: LOW_STOCK_THRESHOLD deve essere un intero, ricevuto: 'not-a-number'`

## Diagnosi

- Sintomo: `docker compose up -d` dà errore e lo stack non risponde
- Risultato atteso: backend healthy e `/health` 200
- Evidenza: nei log del backend il ValueError su LOW_STOCK_THRESHOLD, in `docker compose config` il valore è "not-a-number"
- Ipotesi: la variabile nel compose non è un numero
- Causa: il server fa `int()` della variabile all'avvio e con un testo va in errore

## Fix

- modifica minima: rimesso `LOW_STOCK_THRESHOLD: "5"` nel compose.yaml e `docker compose up -d`
- rebuild necessario?: no
- motivazione: la variabile è configurazione di runtime nel compose, l'immagine non cambia, basta ricreare il container e compose lo fa da solo con `up -d`

## Test

- backend healthy: sì
- health: 200
- products: 200, 4 prodotti
- browser: http://127.0.0.1:8080/ mostra i 4 prodotti

## Modifica conservata

- APP_ENV: "local-docker" aggiunta nello stesso blocco environment del backend
- compose config: la variabile c'è, dentro il container `APP_ENV=local-docker`
- test: `/health` 200

## Git

- branch: fix/ud10-invalid-threshold
- commit: fix: validate Docker runtime configuration
- PR: #3 UD10: validate Docker runtime configuration
- diff verificato: sì con `gh pr diff`, dentro c'è anche il commit del guidato perché non l'avevo pushato prima
- merge: squash e branch cancellato. Il main locale poi non andava in fast forward perché aveva ancora il commit del guidato, l'ho riallineato a origin/main visto che lo squash conteneva già tutto

## Passaggio alla verifica

- stack mantenuto attivo: sì
