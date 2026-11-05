# UD14 — Consegna LAB autonomo

## Errore introdotto

- branch errore: `fix/ud15-target-port` (commit `b11803d`, PR #6, merge `ae55231` su `main`)
- target port errato: `9999` al posto di `8000` in `pipelines/azure-pipelines-delivery.yml`

## Esito della pipeline con l'errore

- differenza nel Terraform plan: il piano prevede la modifica del `target_port` dell'ingress da `8000` a `9999`; dopo l'apply `az containerapp ingress show` restituisce `TargetPort 9999`
- IaC: Succeeded (10:18:36Z)
- Test: Succeeded (10:19:03Z)
- BuildPush: Succeeded (10:19:32Z), immagine tag `28`
- Deploy: Succeeded (10:20:51Z), nuova revision `catalog-api-ud15--0000001` creata alle 10:20:30Z
- Smoke: **Failed** (10:21:19Z), Build ID della run `28`

## Evidenze

- evidenza ingress: `External=True`, `TargetPort=9999`, FQDN `catalog-api-ud15.wonderfuldesert-24121356.northeurope.azurecontainerapps.io`
- evidenza log: `F Catalog backend 28 listening on 0.0.0.0:8000` — l'applicazione ascolta su `8000`, non su `9999`
- revisione: `catalog-api-ud15--0000001` attiva ma `Health=None`, `RunningState=Activating`, 1 replica; la revision precedente `catalog-api-ud15--lyigbdm` (tag `26`) resta `Healthy`
- verifica manuale: `curl https://$FQDN/health` restituisce HTTP 200 con `version: 26`, mentre lo smoke si aspetta `28`; lo stage `Smoke` fallisce perché la revision nuova non diventa raggiungibile e il traffico resta sulla precedente

## Diagnosi

- causa: la `target_port` dell'ingress (`9999`) non corrisponde alla porta su cui il container ascolta (`8000`). Il probe sulla porta sbagliata impedisce alla revision nuova di passare a `Healthy`, quindi il traffico resta sulla revision precedente e la versione servita non coincide con il Build ID
- correzione minima: riportare `targetPort` a `'8000'` nella pipeline, senza toccare service connection, AcrPush, managed identity, AcrPull, state o agent

## Correzione

- branch correzione: `fix/ud15-target-port-correct` (commit `2dac4c8`, PR #7, merge `0dbd5da`)
- run correzione: Build ID `30`, immagine `catalog-backend:30`
  - IaC Succeeded, Test Succeeded, BuildPush Succeeded, Deploy Succeeded
  - Smoke **Failed**: la nuova revision `catalog-api-ud15--0000002` era ancora `Activating` e la vecchia revision `26` continuava a servire `/health`; lo script confrontava subito la versione e vedeva `26` invece di `30`
- causa della seconda failure: race dello stage `Smoke`, non un errore di configurazione. Con `revision_mode = Single` la revision precedente resta al 100% del traffico finché la nuova non è pronta; il test faceva un solo `curl` e non riprovava quando la risposta era 200 ma con versione vecchia
- fix dello smoke: branch `fix/ud14-smoke-wait` (commit `e4f6ba6`, PR #8, merge `0d13bfc`); lo stage ora ripete `curl /health` fino a 40 volte (5 secondi di pausa, 200 secondi totali) e passa solo quando `version` coincide con il Build ID

## Ripristino verificato

- run finale: Build ID `34`, immagine `catalog-backend:34`
  - IaC Succeeded (10:32:32Z)
  - Test Succeeded (10:32:58Z)
  - BuildPush Succeeded (10:33:36Z)
  - Deploy Succeeded (10:34:56Z)
  - Smoke Succeeded (10:35:23Z)
- ingress finale: `TargetPort=8000`, `External=True`
- revision finale: `catalog-api-ud15--0000003`, `Healthy`, 100% traffico, immagine `catalog-backend:34`, creata `2026-11-05T10:34:39Z`
- smoke finale: `curl https://$FQDN/health` → `{"status":"ok","service":"catalog-backend","version":"34"}`, corrispondente al Build ID `34`
- state remoto: `ud15.tfstate` aggiornato alle `2026-11-05T10:34:49Z`
