# UD11 — Consegna laboratorio autonomo

## Baseline

- status: ok
- version: v2
- target port: 8000

## Errore

- nuovo target port: 9999
- sintomo: l'app non risponde più dal FQDN
- HTTP/timeout: 503 subito, `upstream connect error ... Connection refused`

## Evidenze

- running status: Running
- revision: catalog-api-ud11--v2 attiva e Healthy
- health: 503 dal FQDN
- log listen port: `Catalog backend v2 listening on http://0.0.0.0:8000`
- ingress target port: 9999

## Diagnosi

- Sintomo: 503 su /health dopo il cambio dell'ingress
- Risultato atteso: 200 con version v2
- Evidenza: l'app è Running e la revision è Healthy, il backend nei log ascolta sulla 8000 ma l'ingress manda sulla 9999
- Ipotesi: l'ingress punta a una porta dove non c'è nessuno
- Causa: target port 9999 diverso dalla porta dell'app 8000
- Correzione minima: `az containerapp ingress update --target-port 8000`

## Verifica

- target port: 8000
- health: 200 status ok
- version: v2

## Domande

1. no, l'immagine era giusta, il problema era nella configurazione dell'ingress
2. no, v2 in ACR andava bene, non serviva nessuna v3
3. ingress, ACR e identità funzionavano perché la revision era Healthy e il container partito
4. il confronto tra il log che dice listening sulla 8000 e l'ingress con target port 9999
5. perché se cambio più cose insieme non so quale ha risolto, e magari ne rompo un'altra, una modifica alla volta e poi verifico


## Passaggio alla verifica

- target port ripristinato a 8000: sì
- health v2 nuovamente OK: sì
- Resource Group mantenuto disponibile: sì
