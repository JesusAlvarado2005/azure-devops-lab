# UD14 — Consegna LAB guidato (CI)

## Ambiente e agent

- `UD14_AGENT_MODE`: `SELF_HOSTED_FALLBACK`
- pool: `pool-ud09-wsl`
- agent: `wsl-ud09-jesusalvaradojeanfra`, OS `Linux`, macchina `Host-001`
- stato a fine UD13: `Offline`; per la nuova run va avviato con `cd ~/azdo-agent && ./run.sh` e verificato `Online`
- motivi del fallback: lo stato Microsoft-hosted resta `MICROSOFT_HOSTED_PENDING`, quindi la pipeline collegata è `ud13-ci` con `pipelines/azure-pipelines-ci-selfhosted.yml`

## Run CI già osservata

- pipeline: `ud13-ci` (definition id 2)
- build: 10, partita in automatico dopo il merge della PR #4 su `main`
- stage `Test` → job `PythonTests` → step `Run Python tests`: riuscito, 3 test `ok`, `Ran 3 tests`, `OK`
- stage `BuildPush` → job `DockerBuild` → task `Docker@2`: riuscito
- tag pubblicato: `catalog-backend:10`
- build precedente utile: build 7, tag `catalog-backend:7`
- `Agent.Name=wsl-ud09-jesusalvaradojeanfra`, `Agent.OS=Linux`, `Agent.MachineName=Host-001`, `Build.SourcesDirectory=/home/jj_yts/azdo-agent/_work/2/s`
- tool osservati nei log: `Python 3.14.8`, `Docker version 29.9.2, build a82e528`

## ACR verificato ora

```text
acrud1315iwmnnz3ek6q7o.azurecr.io
SKU Basic, admin user False
repository catalog-backend
tag: 10, 7
lastUpdateTime: 2026-10-30T15:35:38Z
```

## Dopo il push

La nuova run CI e il nuovo tag Build ID non sono ancora osservabili: il branch `feature/ud14-ci-v2` è solo locale e l'agent è offline. Dopo push, PR, merge e avvio dell'agent, annotare:

```text
UD14_FINAL_IMAGE_TAG=<Build ID della nuova run>
```

## Cleanup

Nessun cleanup: ACR, immagini, `sc-acr-ud14`, `sc-azure-ud13-15`, agent e pipeline restano per il blocco CD.
