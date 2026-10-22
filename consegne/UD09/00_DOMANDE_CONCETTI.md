# UD09 — Risposte alle domande sui concetti

## 1.
**Risposta:** Perché DevOps è un modo di lavorare fatto di cultura, processi e pratiche. Un prodotto può aiutare ad applicarlo ma non lo sostituisce, se compro Azure DevOps ma i team non collaborano e non c'è feedback non sto facendo DevOps.

## 2.
**Risposta:** Cultura, cioè collaborazione, responsabilità condivisa e feedback. Processi, cioè planning, versioning, review, test, release e operation. Tecnologia, cioè Git, pipeline, container, IaC, monitoraggio e automazione della sicurezza.

## 3.
**Risposta:** Perché non finisce con il deploy. Il monitoraggio e il feedback producono bug, problemi di prestazioni e richieste degli utenti che tornano nella pianificazione e diventano nuovo lavoro, quindi il ciclo riparte.

## 4.
**Risposta:** Agile riguarda soprattutto come si pianifica e si sviluppa, con iterazioni brevi e feedback continuo dal cliente. DevOps allarga lo stesso principio fino al rilascio e alla gestione in produzione, unendo sviluppo e operations.

## 5.
**Risposta:** È la lista ordinata per priorità di tutto il lavoro ancora da fare, come funzionalità, bug e miglioramenti. Si aggiorna continuamente e da lì si prende il lavoro per ogni iterazione.

## 6.
**Risposta:** È un'iterazione di durata fissa e breve, di solito una o due settimane, in cui il team si impegna a completare una parte del backlog e alla fine ha qualcosa di funzionante da mostrare.

## 7.
**Risposta:** Scrum lavora a sprint di durata fissa con ruoli precisi come Product Owner e Scrum Master ed eventi come planning, daily e review. Kanban invece è un flusso continuo senza sprint, si visualizza il lavoro su una board a colonne e si limita il lavoro in corso per ogni colonna.

## 8.
**Risposta:** L'Epic è un obiettivo grande che dura mesi. La Feature è una funzionalità che fa parte di un Epic. La User Story descrive un bisogno dal punto di vista dell'utente, come utente voglio questo per ottenere quello. Il Task è il lavoro tecnico concreto per completare una storia. Il Bug è un difetto da correggere.

## 9.
**Risposta:** Dicono quando una User Story è davvero completa, con condizioni verificabili. Così sviluppatore, tester e cliente sono d'accordo su cosa deve funzionare e si può testare in modo oggettivo.

## 10.
**Risposta:** Perché anche l'infrastruttura e le pipeline sono codice. Avendole in Git ho la storia delle modifiche, posso fare review con le Pull Request, tornare indietro e ricreare tutto uguale, invece di modifiche a mano che nessuno ricorda.

## 11.
**Risposta:** La build è il processo che prende il codice sorgente e lo compila o lo impacchetta. L'artifact è il risultato della build, per esempio un pacchetto o un'immagine, versionato e pronto per essere testato e rilasciato senza ricompilarlo.

## 12.
**Risposta:** Lo unit test controlla un pezzo piccolo di codice da solo, come una funzione. L'integration test controlla che più parti funzionino insieme, per esempio backend e dati. Lo smoke test è un controllo veloce dopo il deploy per vedere che il servizio sia su e risponda, come curl su /health.

## 13.
**Risposta:** Vuol dire spostare test e controlli di sicurezza il prima possibile nel ciclo, cioè a sinistra della linea del tempo. Un errore trovato durante lo sviluppo costa molto meno che trovarlo in produzione.

## 14.
**Risposta:** Vuol dire integrare spesso piccole modifiche nel branch principale, e ogni volta build e test automatici controllano che non si rompa niente. Così gli errori si trovano subito e non alla fine.

## 15.
**Risposta:** Lo Stage è una fase grande della pipeline come build, test o deploy. Il Job è un insieme di passi che gira su un agent dentro uno stage. Lo Step è il singolo passo, come un comando o un task.

## 16.
**Risposta:** Con la Continuous Delivery ogni versione è sempre pronta per la produzione ma il deploy parte dopo un'approvazione. Con il Continuous Deployment se passa tutti i controlli va in produzione da sola senza approvazione.

## 17.
**Risposta:** Il Dockerfile è il file di testo con le istruzioni per costruire l'immagine. L'image è il pacchetto immutabile che si ottiene con la build, con applicazione e dipendenze. Il container è l'immagine in esecuzione, e dalla stessa immagine posso avviare più container.

## 18.
**Risposta:** È il posto dove si salvano e si distribuiscono le immagini dei container con le loro versioni, come Docker Hub o Azure Container Registry. La pipeline fa push dell'immagine e l'ambiente di esecuzione fa pull da lì.

## 19.
**Risposta:** Gestisce molti container su più macchine. Li avvia, li riavvia se cadono, li scala in base al carico e distribuisce il traffico, cose che a mano con tanti container non si possono fare. Un esempio è Kubernetes.

## 20.
**Risposta:** Vuol dire descrivere l'infrastruttura come reti, VM e storage in file di codice, con strumenti come Bicep o Terraform, invece di crearla a mano dal portale. Così è ripetibile, versionata in Git e revisionabile.

## 21.
**Risposta:** Mette la sicurezza dentro ogni fase del ciclo invece di controllarla solo alla fine, per esempio controllo dei segreti nel codice, scansione delle dipendenze e delle immagini, permessi minimi nelle pipeline.

## 22.
**Risposta:** È l'insieme di strumenti diversi usati insieme lungo il ciclo, per esempio Azure Boards per il planning, GitHub per il codice, Azure Pipelines per CI e CD, Docker, Azure Container Registry, Terraform o Bicep e Azure Monitor.

## 23.
**Risposta:** Azure Boards, Azure Repos, Azure Pipelines, Azure Test Plans e Azure Artifacts.

## 24.
**Risposta:** Serve a pianificare e seguire il lavoro con backlog, work item come Epic, Feature, User Story, Task e Bug, board e sprint.

## 25.
**Risposta:** Perché GitHub è già il nostro repository ufficiale con branch, Pull Request e review. Mettere lo stesso codice anche in Azure Repos creerebbe confusione, sincronizzazioni inutili e il rischio che le due copie diventino diverse.

## 26.
**Risposta:** Azure Test Plans serve per i test manuali ed esplorativi, con piani e casi di test eseguiti da persone. I test automatici in pipeline sono codice che gira da solo a ogni build, come gli unit test.

## 27.
**Risposta:** Azure Artifacts conserva pacchetti di librerie come npm, NuGet, Maven o Python. Azure Container Registry conserva immagini dei container.

## 28.
**Risposta:** L'Organization è il contenitore principale con utenti, permessi, agent pool e fatturazione. Il Project sta dentro l'organization ed è lo spazio di un prodotto o team con le sue board, pipeline e permessi.

## 29.
**Risposta:** L'Agent è il programma che esegue i job. L'Agent Pool è il gruppo di agent da cui la pipeline ne sceglie uno. Il Parallel Job è quanti job possono girare contemporaneamente nell'organization.

## 30.
**Risposta:** Il Microsoft-hosted è una macchina gestita da Microsoft, nuova e pulita per ogni job e con molti tool già installati. Il self-hosted è una macchina gestita da noi, persistente e con i tool che vogliamo, ma patch, sicurezza e disponibilità sono responsabilità nostra.

## 31.
**Risposta:** È un collegamento autenticato tra Azure DevOps e un sistema esterno come GitHub, Azure o un registry, così la pipeline può usarlo senza scrivere credenziali nel codice. È meglio non darlo a tutte le pipeline ma solo a quelle che servono.

## 32.
**Risposta:** Perché il PAT serve solo durante la registrazione. Una volta registrato l'agent usa le sue credenziali per collegarsi, quindi il PAT si può revocare e l'agent resta Online. Così non resta in giro un token che non serve più.

## 33.
**Risposta:** Perché DevOps è un insieme di pratiche e Azure DevOps è solo una delle piattaforme che le supportano. Le stesse pratiche si possono fare con GitHub Actions, GitLab o Jenkins.

## 34.
**Risposta:** Azure Pipelines è il servizio che definisce le pipeline, mette in coda i job e mostra i risultati. L'Azure Pipelines Agent è il programma installato su una macchina che prende un job e lo esegue davvero.

## 35.
**Risposta:** Sono la stessa idea con strumenti diversi. In ognuno c'è un servizio centrale che gestisce le pipeline e un programma esecutore installato su una macchina che prende i job ed esegue i comandi.

## 36.
**Risposta:** In UD13 eseguirà validazioni IaC con Bicep e Terraform e i primi job di pipeline preparando i test CI. In UD14 eseguirà test, Docker build e push, deploy e smoke test della pipeline completa.

## 37.
**Risposta:** Perché ogni job Microsoft-hosted gira su una macchina nuova che poi viene buttata. I file del job precedente non ci sono più, quindi quello che serve va passato come artifact o rigenerato.

## 38.
**Risposta:** Perché in un team l'agent self-hosted sta su una VM o un server gestito dall'organizzazione e condiviso da tutti. Il mio WSL2 è un PC personale che si spegne e lo gestisco solo io, nel corso è una simulazione di un build host aziendale.

## 39.
**Risposta:** Con un pool di più agent su VM o server dell'azienda, per esempio pool-linux-build con build-agent-01, 02 e 03. Gli sviluppatori fanno push, Azure Pipelines mette il job in coda e lo assegna a un agent libero compatibile, e il pool si può condividere tra più progetti in base ai permessi.

## 40.
**Risposta:** Perché ogni agent esegue un job alla volta ma quanti job girano insieme lo decide la capacità di Parallel Job dell'organization. Con tre agent e un solo parallel job gira comunque un job alla volta e gli altri restano in coda.
