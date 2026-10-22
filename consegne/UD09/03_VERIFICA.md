# UD09 — Verifica individuale

## 1.

B

## 2.

C

## 3.

A

## 4.

B

## 5.

B

## 6.

B

## 7.

B

## 8.

A

## 9.

A

## 10.

B

## 11.

B

## 12.

A

## 13.

Scrum lavora a sprint di durata fissa con ruoli ed eventi precisi, Kanban è un flusso continuo su una board e limita il lavoro in corso con il WIP

## 14.

Epic è un obiettivo grande, si divide in Feature che sono funzionalità, ogni Feature in User Story che è il valore per l'utente e le User Story in Task che sono il lavoro tecnico da fare

## 15.

la build è il processo che prende il codice e lo prepara, l'artifact è il risultato della build che passa alle fasi dopo, per esempio un'immagine o un pacchetto

## 16.

lo unit test prova un pezzo di codice da solo, l'integration test prova più componenti insieme, lo smoke test è un controllo veloce dopo il deploy per vedere che l'app risponde

## 17.

spostare test e controlli prima nel processo, così gli errori si trovano subito e costano meno che trovarli in produzione

## 18.

lo Stage è una fase grande della pipeline come build o deploy, dentro ci sono i Job che girano su un agent, e ogni Job è fatto di Step che sono i singoli comandi o task

## 19.

Repos è il version control di Azure DevOps, Pipelines fa CI/CD, Test Plans gestisce i test manuali e i piani di test, Artifacts conserva i pacchetti come npm, NuGet o pip

## 20.

l'Organization è il contenitore più grande, dentro ci sono i Project, l'Agent Pool è un gruppo di agent e l'Agent è la macchina o processo che esegue i job

## 21.

il Microsoft-hosted lo gestisce Microsoft, è una macchina nuova a ogni job e non devi fare manutenzione. Il self-hosted è una macchina mia, come il mio PC, la gestisco io ma ho controllo su software e rete

## 22.

perché così qualsiasi pipeline, anche nuova o di altri, può usare il pool e far girare comandi sulla mia macchina, è meglio autorizzare ogni pipeline esplicitamente

## 23.

perché il PAT serve solo per registrare l'agent, dopo l'agent usa le sue credenziali salvate nella sua cartella e resta Online anche col PAT revocato

## 24.

no, Azure Pipelines è il servizio che definisce e orchestra le pipeline, l'Agent è il programma che gira sulla macchina e esegue davvero i job

## 25.

- Azure Pipelines → Azure Pipelines Agent
- Jenkins → Jenkins Agent
- GitHub Actions → Runner
- GitLab CI/CD → GitLab Runner

## 26.

perché il concetto è lo stesso in tutti gli strumenti, c'è chi orchestra e chi esegue, e Jenkins è molto usato nelle aziende quindi è bene saperlo riconoscere

## 27.

in UD13 le validazioni dell'infrastruttura come codice, in UD14 test, build e push dell'immagine Docker, deploy e smoke test

## 28.

il self-hosted è sicuro di funzionare subito e lo usiamo come base, il Microsoft-hosted lo prepariamo per le UD dopo appena è disponibile, così se uno manca c'è l'altro

## 29.

il processo `run.sh` non è attivo quindi l'agent non è collegato. Vado nella cartella dell'agent e lancio `./run.sh`, poi controllo nel portale che torni Online

## 30.

perché la registrazione c'è ancora, manca solo il processo acceso. Rifare PAT e config è inutile e crea token nuovi da gestire

## Mappa finale

| Area | Strumento del percorso |
|---|---|
| Planning | Azure Boards, pianificare e tracciare il lavoro |
| Version Control | GitHub, tiene la storia delle versioni del codice con git |
| CI/CD | Azure Pipelines, la CI integra e testa in automatico, il deploy può essere automatico o con approvazione |
| Container | Docker, parte da un'immagine, più leggero di una VM perché condivide il kernel, si crea e si elimina facilmente |
| Registry | Azure Container Registry, dove si salvano le immagini dei container |
| IaC | Bicep e Terraform, l'infrastruttura scritta come codice |
| Runtime | Azure Container Apps, dove l'app gira davvero |
| Monitoring | Azure Monitor, log e metriche sull'andamento |
