# UD13 — Risposte ai concetti di Continuous Integration

1. **Risposta:** lo scopo è trasformare ogni modifica del repository in una sequenza di controlli sempre uguali e ripetibili, test, build e push, così il risultato non dipende da chi lancia i comandi a mano.

2. **Risposta:** perché se i test falliscono non ha senso costruire e pubblicare un'immagine che non è verificata. Prima verifico, poi produco l'artefatto, e se il test è rosso lo stage BuildPush non parte.

3. **Risposta:** che tutti i controlli che ho messo nella pipeline sono passati, non che il software sia senza bug o sicuro. Dipende da quali test ho scritto: se sono incompleti anche un verde non dice tutto.

4. **Risposta:** Build.BuildId è il numero unico della run, quindi so da quale esecuzione viene quell'immagine e posso risalire a commit e log. latest può puntare a cose diverse nel tempo e non mi dice quale versione sto distribuendo.

5. **Risposta:** sc-azure-ud13-15 è la service connection Azure Resource Manager per gestire le risorse Azure, sc-acr-ud14 è una Docker Registry service connection che serve a Docker@2 per autenticarsi all'ACR durante build e push. Non sono ridondanti, hanno scopi diversi.

6. **Risposta:** perché l'admin user è una credenziale statica con accesso pieno al registry. Con WIF e i ruoli AcrPush e AcrPull non serve, quindi resta disabilitato e non metto password nel YAML.

7. **Risposta:** un commit su main avvia automaticamente la CI, quindi dopo il merge la modifica viene testata e costruita senza lanciare la pipeline a mano.

8. **Risposta:** perché con Microsoft-hosted ogni job può girare su una VM diversa e non vede i file del job precedente, quindi ognuno deve rifarsi la copia del repository da solo.

9. **Risposta:** che la VM esiste per quel job e poi viene eliminata. Non posso contare su file o modifiche lasciati da un job precedente, se servono li devo passare con artifact o rifare.

10. **Risposta:** l'agent esegue i task e i comandi, la service connection fornisce l'identità con cui quei task parlano con Azure o con l'ACR.

11. **Risposta:** per capire subito che ambiente ha l'agent e distinguere un errore dell'applicazione da un tool mancante. Se manca docker non ha senso guardare l'ACR, il task non è ancora arrivato al push.

12. **Risposta:** quando Microsoft-hosted non è disponibile, per esempio lo stato è ancora PENDING o non ho i Parallel Jobs hosted, e uso il pool-ud09-wsl già pronto.

13. **Risposta:** perché il self-hosted tiene i file tra una run e l'altra, così evito che uno step usi per caso qualcosa rimasto da prima e che la pipeline funzioni solo sulla mia macchina.

14. **Risposta:** fa la build dell'immagine, le mette il tag e la pubblica in ACR in un solo task, usando la Docker Registry service connection senza docker login scritto a mano.

15. **Risposta:** stage, job, step, comando e messaggio di errore, partendo dal primo step rosso per non inseguire le conseguenze degli step successivi.

16. **Risposta:** perché se il test fallisce la pipeline si ferma prima della build e del push, quindi l'ACR non è ancora stato coinvolto e devo guardare il test.

17. **Risposta:** dimostra che la pipeline non sa da sola se il software è giusto, esegue i test che ho scritto e si ferma quando non tornano. Se i test sono sbagliati anche il verde non basta.

18. **Risposta:** perché l'immagine pubblicata è l'input della Continuous Delivery della UD14, se cancello ACR o immagini il deployment non ha cosa distribuire.

19. **Risposta:** la UD14 prende l'immagine con tag BuildId dall'ACR e la usa nella Container App distribuita con Terraform, quindi la CI lascia pronto l'artefatto che la CD consuma.
