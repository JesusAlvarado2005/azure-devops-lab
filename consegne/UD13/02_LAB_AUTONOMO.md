# UD13 — Consegna LAB autonomo

- branch: `fix/ud13-pipeline-path`, creata da `main` e pubblicata con `git push -u origin fix/ud13-pipeline-path`.
- path errato: in `pipelines/azure-pipelines-iac.yml` ho cambiato `infra/bicep/delivery.bicep` in `infra/bicep/delivery-NON-ESISTE.bicep` solo nello step di lint.
- stage: `Validate`, stage `Validate IaC`.
- job: `ValidateIaC`, display `Validate Terraform and Bicep`.
- step: `Bicep lint`.
- messaggio: `ERROR: An error occurred reading file. Could not find file '/home/jj_yts/azdo-agent/_work/1/s/infra/bicep/delivery-NON-ESISTE.bicep'.` e poi `##[error]Bash exited with code '1'.` La run è la build 8 (`20261030.6`), fallita in 48 secondi. Il job girava su `Agent.Name=wsl-ud09-jesusalvaradojeanfra`, `Agent.OS=Linux`, `Build.SourcesDirectory=/home/jj_yts/azdo-agent/_work/1/s`.
- classe del problema: path/filesystem del repository, non Azure, non il pool, non l'agent e non la service connection. Il file nel checkout non esiste con quel nome, quindi `az bicep lint` non arriva nemmeno a leggere il template.
- correzione: ho rimesso `infra/bicep/delivery.bicep` nel YAML, commit `cf2baa4 fix: restore Bicep pipeline path`, push sulla stessa branch. Non ho toccato né l'agent né la service connection.
- run finale: build 9 (`20261030.7`) sulla branch `fix/ud13-pipeline-path`, `Succeeded` in 2 minuti. `Validate` riuscito (Terraform fmt/init/validate e Bicep lint) e `Deploy` riuscito (What-If + deployment `ud13-delivery-9`, Succeeded). `Deploy` è partito solo dopo `Validate`.
- PR/merge: PR #4 da `fix/ud13-pipeline-path` verso `main`, merge completato con commit `6137c80`. Dopo il merge la pipeline IaC non è ripartita da sola perché ha `trigger: none`; la pipeline CI `ud13-ci` invece è partita in automatico con la build 10.
