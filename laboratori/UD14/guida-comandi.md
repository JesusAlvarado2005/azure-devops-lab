# UD14 — Guida comandi (blocco CI)

Questa guida copre solo la prima metà della UD14: verifica della CI esistente, test rosso/verde e nuova run. La parte Continuous Delivery con Terraform e state remoto resta da svolgere.

## 1. Branch di lavoro

```bash
cd "$LAB_REPO"
git switch main
git pull --ff-only
git switch -c feature/ud14-ci-v2
```

Il branch tiene separati i due commit del laboratorio: prima l'app, poi il test.

## 2. Modifica l'applicazione

In `app/catalog-backend-ci/server.py`:

```python
APP_VERSION = os.getenv("APP_VERSION", "ci-v2")
```

Per coerenza ho aggiornato anche `APP_VERSION` nel `Dockerfile`, così l'immagine non continua a dichiarare `ci-v1`.

```bash
git add app/catalog-backend-ci/server.py app/catalog-backend-ci/Dockerfile
git commit -m "feat: bump catalog version to ci-v2"
```

## 3. Verifica il test rosso

```bash
python3 -m unittest discover \
  -s app/catalog-backend-ci/tests \
  -v
```

Atteso: `test_health_version` fallisce con `AssertionError: 'ci-v2' != 'ci-v1'`. È corretto: l'app è cambiata, il criterio del test no.

## 4. Allinea il test

In `app/catalog-backend-ci/tests/test_backend.py`:

```python
self.assertEqual(payload["version"], "ci-v2")
```

```bash
python3 -m unittest discover \
  -s app/catalog-backend-ci/tests \
  -v
```

Atteso: 3 test `ok`, `OK`.

```bash
git add app/catalog-backend-ci/tests/test_backend.py
git commit -m "test: align expected catalog version"
```

## 5. Prova locale dell'immagine

```bash
docker build -t catalog-backend:ud14-local app/catalog-backend-ci
docker run -d --name catalog-ud14-local -p 127.0.0.1:18015:8000 catalog-backend:ud14-local
curl -s http://127.0.0.1:18015/health
docker rm -f catalog-ud14-local
```

Atteso: `{"status": "ok", "service": "catalog-backend", "version": "ci-v2"}`.

## 6. Push, PR e merge

```bash
git push -u origin feature/ud14-ci-v2
```

Poi apro la PR verso `main` e completo il merge. Il YAML `pipelines/azure-pipelines-ci-selfhosted.yml` ha `trigger: main`, quindi la CI parte con il merge su `main`, non con la sola PR.

Con `UD14_AGENT_MODE=SELF_HOSTED_FALLBACK` l'agent deve essere online prima della run:

```bash
cd ~/azdo-agent && ./run.sh
```

Nel pool `pool-ud09-wsl` deve risultare `Online`.

## 7. Verifica run e ACR

Nel portale seguo:

```text
Stage Test
→ Job PythonTests
→ Run Python tests

Stage BuildPush
→ Job DockerBuild
→ Docker@2
```

Poi:

```bash
export ACR_NAME=$(az acr list \
  --resource-group rg-ud13-15-delivery \
  --query "[0].name" \
  --output tsv)
```

```bash
az acr repository show-tags \
  --name "$ACR_NAME" \
  --repository catalog-backend \
  --orderby time_desc \
  --output table
```

Deve comparire il nuovo tag uguale al Build ID della run. Prima di questa modifica in ACR c'erano i tag `10` e `7`, con ultimo aggiornamento `2026-10-30T15:35:38Z`.

## 8. Nessun cleanup

Non eliminare ACR, immagini, `sc-acr-ud14`, `sc-azure-ud13-15`, agent o pipeline: servono al blocco CD.

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `test_health_version` fallisce con `'ci-v2' != 'ci-v1'` | il test prevedeva ancora la versione vecchia | aggiornare l'aspettativa a `ci-v2` |
| `Endpoint auth data not present` in `Docker@2` | service connection non autorizzata per la pipeline | autorizzare `sc-acr-ud14` solo su `ud13-ci` |
| `401` o `403` sul push ACR | ruolo `AcrPush` o service connection mancante | controllare identità, ruolo e autorizzazione |
| Job in attesa | agent offline o pool sbagliato | avviare `./run.sh` e verificare `pool-ud09-wsl` |
| `docker: command not found` | Docker non avviato o non nel PATH dell'agent | avviare Docker e controllare l'ambiente dell'agent |
| file vecchi nella run | workspace self-hosted non pulito | usare `workspace: clean: all` e `checkout` pulito |
