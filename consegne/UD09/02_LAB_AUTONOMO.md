# UD09 — Consegna laboratorio autonomo

## 1. Organization e Project

- Organization: jesusalvaradojeanfra
- Project: az900-az104-devops
- Visibility: private
- Source repository: GitHub, JesusAlvarado2005/azure-devops-lab

1. perché dentro ci saranno pipeline, agent e configurazioni del corso e non devono vederle tutti, e per i progetti privati c'è il free tier dei parallel job
2. perché il codice sta già su GitHub, Azure DevOps lo usiamo solo per le pipeline e così non ho due copie da tenere allineate

## 2. Gruppi

| Gruppo | Scopo | Tutti? |
|---|---|---|
| Project Administrators | gestiscono permessi e impostazioni del progetto | no, solo chi amministra, è il gruppo con più potere |
| Contributors | lavorano su codice, pipeline e work item | no, solo chi lavora davvero al progetto |
| Readers | vedono senza modificare | sì, è il meno rischioso, ma sempre a chi serve |
| Build Administrators | gestiscono pipeline e build | no, se no chiunque può cambiare cosa si esegue sugli agent |

## 3. GitHub integration readiness

- repository: JesusAlvarado2005/azure-devops-lab
- private: no, il repo è pubblico quindi niente segreti dentro
- gh auth: loggato come JesusAlvarado2005
- git fetch: ok

La prima volta i comandi mi hanno dato `non è un repository Git` perché ero ancora in `~/azdo-agent`, vanno lanciati dalla cartella del repo.

1. perché per la CI Microsoft consiglia la GitHub App e una connessione OAuth o PAT fatta adesso poi non la useremmo
2. Azure Pipelines GitHub App, si collega quando creo la prima pipeline e scelgo il repo
3. perché avrei due copie del codice e dovrei tenerle sincronizzate, la fonte resta una sola

## 4. Parallel jobs

- hosted: pending
- self-hosted: 1

1. no, si va avanti con il self-hosted e l'hosted si usa quando diventa disponibile
2. uno solo alla volta, gli altri aspettano in coda
3. no, gli agent sono chi esegue ma quanti job partono insieme lo decide il numero di parallel job, con 1 parallel job anche con 3 agent ne gira uno

## 5. Agent audit

- pool: pool-ud09-wsl
- agent: wsl-ud09-jesusalvaradojeanfra
- status: Online
- version: 5.281.0
- Agent.OS: Linux
- Agent.Version: 5.281.0
- git: 2.56.0
- python: 3.14.8

## 6. Registration authentication audit

- metodo: PAT
- status PAT, se applicabile: revocato

1. perché il PAT serve solo a registrare l'agent, dopo l'agent usa le sue credenziali salvate nella cartella dell'agent
2. perché all'agent serve solo Agent Pools Read & manage, un Full access se finisce in giro dà accesso a tutta l'organization
3. perché non lascia un token in giro e non apre la policy a tutti, allargare la policy PAT vale per tutta l'organization

## 7. Offline/Online

- stop: Ctrl+C nel terminale di `./run.sh`
- stato: Offline
- restart: `./run.sh` dalla cartella dell'agent, senza rifare config
- stato: Online

## 8. Troubleshooting

1. il processo `run.sh` gira? se il terminale è chiuso l'agent è Offline, basta riavviarlo
2. la macchina arriva a `dev.azure.com` in HTTPS? rete, proxy, DNS
3. l'URL dell'organization è giusto? solo `https://dev.azure.com/` più il nome, senza progetto
4. il pool è quello giusto e l'agent c'è ancora dentro?
5. sono nella cartella giusta dell'agent e ci sono ancora `.agent` e `.credentials`?
6. `./run.sh --diagnostics` e i log in `_diag`, solo dopo si pensa a rimuovere e registrare di nuovo

## 9. Readiness

| Controllo | PASS/FAIL | Nota |
|---|---|---|
| Organization | PASS | collegata alla subscription |
| Project | PASS | privato, Git, Agile |
| GitHub readiness | PASS | auth e fetch ok, repo pubblico senza segreti |
| Hosted | PASS | stato documentato, pending |
| Pool | PASS | pool-ud09-wsl self-hosted |
| Agent | PASS | Online |
| PAT / Device Code Flow | PASS | PAT revocato |
| Capability | PASS | OS, versione, git e python visti |
| Restart | PASS | Offline e di nuovo Online |
| Secrets | PASS | agent fuori dal repo, niente token nei file |
