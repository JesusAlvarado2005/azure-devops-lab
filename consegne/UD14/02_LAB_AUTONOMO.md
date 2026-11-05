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
- Smoke: **Failed** (10:21:19Z)

## Evidenze

- evidenza ingress: `External=True`, `TargetPort=9999`, FQDN `catalog-api-ud15.wonderfuldesert-24121356.northeurope.azurecontainerapps.io`
- evidenza log: `F Catalog backend 28 listening on 0.0.0.0:8000` — l'applicazione ascolta su `8000`, non su `9999`
- revisione: `catalog-api-ud15--0000001` attiva ma `Health=None`, `RunningState=Activating`, 1 replica; la revision precedente `catalog-api-ud15--lyigbdm` (tag `26`) resta `Healthy` e continua a servire
- verifica manuale: `curl https://$FQDN/health` restituisce HTTP 200 con `version: 26`, mentre lo smoke si aspetta `28`; quindi lo stage `Smoke` fallisce sul confronto di versione perché la revision nuova non diventa raggiungibile

## Diagnosi

- causa: la `target_port` dell'ingress (`9999`) non corrisponde alla porta su cui il container ascolta (`8000`). Il probe di readiness sulla porta sbagliata impedisce alla revision nuova di passare a `Healthy`, quindi il traffico resta sulla revision precedente e la versione servita non coincide con il Build ID
- correzione minima: riportare `targetPort` a `'8000'` nella pipeline, senza toccare service connection, AcrPush, managed identity, AcrPull, state o agent

## Correzione

- branch correzione: `fix/ud15-target-port-correct`
- run finale:
- smoke finale:
