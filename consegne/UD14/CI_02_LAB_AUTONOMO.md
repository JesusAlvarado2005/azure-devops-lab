# UD14 — Consegna LAB autonomo (CI)

- branch: `feature/ud14-ci-v2`
- modifica app: `app/catalog-backend-ci/server.py` e `app/catalog-backend-ci/Dockerfile` — cambiato default/env `APP_VERSION` da `ci-v1` a `ci-v2`
- test fallito: `test_health_version` fallito localmente dopo la modifica all'app (`'ci-v2' != 'ci-v1'`)
- causa: il test prevedeva ancora `version: "ci-v1"` mentre l'app restituiva `ci-v2`
- modifica test: `app/catalog-backend-ci/tests/test_backend.py` aggiornato a `self.assertEqual(payload["version"], "ci-v2")`
- test finale: `python3 -m unittest discover -s app/catalog-backend-ci/tests -v` → 3 test, tutti `ok`, `OK`
- commit app: `6804bf8 feat: bump catalog version to ci-v2`
- commit test: `587cfa8 test: align expected catalog version`
- verifica locale immagine: `docker build -t catalog-backend:ud14-local app/catalog-backend-ci`, container su `127.0.0.1:18015`, `/health` → `{"status": "ok", "service": "catalog-backend", "version": "ci-v2"}`
- PR: #5, `https://github.com/JesusAlvarado2005/azure-devops-lab/pull/5`
- merge: completato il 2026-11-02T17:15:03Z con merge commit `117bbeb`
- run CI: `ud13-ci` build 14 (numero `20261102.3`), attivata dal merge su `main`; `Test` riuscito e `BuildPush` riuscito sull'agent `linux-ud14-jj`
- nuovo tag ACR: `catalog-backend:14`, creato il 2026-11-02T17:16:00Z
- cleanup eseguito: NO
