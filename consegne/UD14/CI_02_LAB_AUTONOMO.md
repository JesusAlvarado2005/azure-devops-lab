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
- PR: da aprire da `feature/ud14-ci-v2` verso `main` (a cura dell'utente dopo il push)
- merge: da completare secondo le policy del repo (a cura dell'utente)
- run CI: `ud13-ci` attivata da merge su `main` (da verificare dopo push; agent `wsl-ud09-jesusalvaradojeanfra` offline va riavviato se in modalità `SELF_HOSTED_FALLBACK`)
- nuovo tag ACR: da annotare dopo la run CI (Build ID)
- cleanup eseguito: NO
