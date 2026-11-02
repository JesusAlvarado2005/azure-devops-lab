# UD14 — Consegna LAB guidato (CI)

## Ambiente e agent

- `UD14_AGENT_MODE`: `SELF_HOSTED_FALLBACK`
- pool: `pool-ud09-wsl`
- agent usato: `linux-ud14-jj` (AgentId 18), OS `Linux`, macchina `jj-host`
- il vecchio agent `wsl-ud09-jesusalvaradojeanfra` non era più disponibile su questa macchina: la cartella `/home/jj_yts/azdo-agent` non esiste. Ho configurato un agent nuovo in `/home/jj/azdo-agent`, registrato nello stesso pool, e l'ho avviato con `./run.sh`
- motivi del fallback: lo stato Microsoft-hosted resta `MICROSOFT_HOSTED_PENDING`, quindi la pipeline collegata è `ud13-ci` con `pipelines/azure-pipelines-ci-selfhosted.yml`

## Run CI osservata

- pipeline: `ud13-ci` (definition id 2)
- PR: #5, `feature/ud14-ci-v2` → `main`, merge completato il 2026-11-02T17:15:03Z con commit `117bbeb`
- build 14 (numero `20261102.3`), partita dopo il merge su `main`
- link run: `https://dev.azure.com/jesusalvaradojeanfra/7fff3d33-1e96-42fb-84d0-85807ec88012/_build/results?buildId=14`
- stage `Test` → job `PythonTests` → step `Run Python tests`: riuscito (3 test del repository, già `ok` in locale)
- stage `BuildPush` → job `DockerBuild` → task `Docker@2`: riuscito, step `Build and push to ACR` completato alle 17:16:00Z
- tag pubblicato dalla run del merge: `catalog-backend:14`
- run precedenti utili: build 10, tag `catalog-backend:10`; build 11, tag `catalog-backend:11` (run precedente al merge)
- `Agent.Name=linux-ud14-jj`, `Agent.OS=Linux`, `Agent.MachineName=jj-host`, `AgentId=18`
- tool dell'agent: `Python 3.14.8`, `Docker version 29.9.2, build a82e528`

## ACR verificato ora

```text
acrud1315iwmnnz3ek6q7o.azurecr.io
SKU Basic, admin user False
repository catalog-backend
tag: 14, 11, 10, 7
tag 14 creato: 2026-11-02T17:16:00Z
digest tag 14: sha256:0640d6573abc3b71328fac60c2a936cfa72015073240e59defcb6f7de4efc4f5
```

## Risultato

```text
UD14_FINAL_IMAGE_TAG=14
```

La CI del blocco UD14 è verde: il merge della PR #5 ha attivato la pipeline, `Test` è passato e `BuildPush` ha pubblicato l'immagine con il tag uguale al Build ID.

## Cleanup

Nessun cleanup: ACR, immagini, `sc-acr-ud14`, `sc-azure-ud13-15`, agent e pipeline restano per il blocco CD.
