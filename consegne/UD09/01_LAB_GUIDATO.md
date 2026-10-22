# UD09 — Consegna laboratorio guidato

## Organization

- nome: jesusalvaradojeanfra
- geography: Europe
- Azure subscription collegata: sì

## Project

- nome: az900-az104-devops
- visibility: private
- version control: Git
- process: Agile

## Gruppi

| Gruppo | Funzione essenziale |
|---|---|
| Project Administrators | gestiscono tutto il progetto, permessi e impostazioni |
| Contributors | lavorano sul progetto, codice, pipeline e work item |
| Readers | possono solo vedere |
| Build Administrators | gestiscono le pipeline e le build |

## GitHub

- repository: JesusAlvarado2005/azure-devops-lab
- repository privato: no, è pubblico e per questo non ci metto segreti
- `gh auth status`: loggato come JesusAlvarado2005
- `git fetch`: ok
- connessione OAuth/PAT creata in UD09: NO
- metodo raccomandato per CI futura: Azure Pipelines GitHub App

## Parallel jobs

- Microsoft-hosted: MICROSOFT_HOSTED_PENDING
- esito hosted: non ancora disponibile, intanto si va avanti con il self-hosted
- self-hosted: 1 job gratuito
- billing verificato: sì

## Agent Pool

- creato da Project settings: sì
- nome: pool-ud09-wsl
- tipo: Self-hosted
- accesso automatico a tutte le pipeline: no, lasciato disabilitato

## Autenticazione registrazione agent

- metodo usato: PAT
- PAT name, se usato: ud09-agent-registration
- PAT scope, se usato: Agent Pools Read & manage
- expiration: la più breve
- inserito in file/repository: NO
- PAT revocato, se usato: sì

## Agent

- nome: wsl-ud09-jesusalvaradojeanfra
- pool: pool-ud09-wsl
- OS: Linux, Fedora 44 nativo e non WSL2
- version: 5.281.0
- status: Online
- modalità: interattiva con `./run.sh`, non come servizio
- credenziale di registrazione chiusa e agent ancora Online: sì

Il primo tentativo l'avevo estratto nella cartella del repo, l'ho spostato in `~/azdo-agent` prima di configurarlo. Poi `VS30063 not authorized` perché nell'URL avevo messo anche il progetto, va solo `https://dev.azure.com/` più l'organization.

## Capability

- Agent.OS: Linux
- Agent.Version: 5.281.0
- git: 2.56.0
- python: 3.14.8
- PATH verificato: sì

## Readiness

- Organization: pronta e collegata alla subscription
- Project: privato, Git, Agile
- GitHub: repo pronto, l'integrazione si fa con la GitHub App alla prima pipeline
- hosted: pending
- self-hosted: pronto
- agent: Online, provato Ctrl+C e di nuovo `./run.sh` e torna Online senza rifare config
- security: PAT revocato, l'agent sta fuori dal repo, nessun segreto nei file
