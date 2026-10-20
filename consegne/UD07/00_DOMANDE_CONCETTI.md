# UD07 — Risposte alle domande sui concetti

## 1.
**Risposta:** Perché con --query filtro i dati e chiedo ad Azure solo quello che mi serve invece di vedere tutto il JSON. Cercare a mano una stringa è lento e sbaglia facilmente, perché la stessa parola può comparire in più punti e se cambia l'ordine o il formato dell'output la ricerca non funziona più. Con --query indico il percorso preciso della proprietà, il risultato è sempre lo stesso e lo posso riusare in uno script.

## 2.
**Risposta:** table crea una tabella con intestazioni pensata per essere letta da una persona. tsv stampa solo i valori senza virgolette, parentesi o intestazioni ed è pensato per essere riusato, per esempio per mettere un ID o un IP in una variabile e passarlo al comando dopo.

## 3.
**Risposta:** Vuol dire che i comandi PowerShell non restituiscono righe di testo ma oggetti con delle proprietà. Se metto un resource group in una variabile posso leggere direttamente $rg.Location o $rg.Tags senza cercare nel testo, e posso passare l'oggetto intero al comando dopo con la pipeline. Con Bash e la CLI invece lavoro di solito con JSON, query e variabili di testo.

## 4.
**Risposta:** Vuol dire che posso eseguire la procedura una volta o più volte e arrivo sempre allo stesso stato finale senza effetti indesiderati. Per esempio prima controllo se il resource group esiste, se non c'è lo creo e se c'è lo riuso. Così se lo script si interrompe o lo rilancio per sbaglio non crea doppioni e non dà errori.

## 5.
**Risposta:** L'Activity Log registra le operazioni di gestione sulle risorse e sulla sottoscrizione, cioè chi ha creato modificato o eliminato una risorsa, quando e con quale esito. Le metriche sono valori numerici raccolti nel tempo come la CPU o il numero di transazioni e servono a vedere l'andamento e a creare alert. I Logs sono record più dettagliati di quello che succede dentro una risorsa o un'applicazione e si interrogano con KQL in un Log Analytics workspace.

## 6.
**Risposta:** È il posto dove vengono raccolti i log di risorse Azure e non Azure ed è lì che li interrogo e li filtro con KQL. Posso anche mettere insieme dati di risorse diverse nella stessa query.

## 7.
**Risposta:** Decide quali categorie di log o metriche di una risorsa inviare e verso quale destinazione, come un Log Analytics workspace, uno Storage Account o un Event Hub. È una regola di instradamento e non il posto dove i dati vengono salvati. Senza diagnostic setting molti log non arrivano nel workspace e non posso interrogarli.

## 8.
**Risposta:** L'Activity Log è il registro delle operazioni che consulto dal portale o dalla CLI. AzureActivity è la tabella di Log Analytics dove arrivano quegli eventi solo se ho configurato una diagnostic setting che li manda al workspace. Quindi i dati arrivano solo da quando esiste la diagnostic setting, con un po' di ritardo per l'ingestion, e lì li interrogo con KQL. Se la tabella è vuota non vuol dire che non ci sono eventi.

## 9.
**Risposta:** L'alert rule dice cosa osservare e quando la condizione è vera, per esempio una metrica sopra una soglia valutata ogni 5 minuti. L'action group dice cosa fare quando l'alert scatta, per esempio mandare una mail o un SMS, chiamare un webhook o avviare un'automazione. Sono separati così lo stesso action group si può usare per più alert.

## 10.
**Risposta:** Perché Fired vuol dire solo che la condizione della regola è diventata vera. Un incidente invece è un problema che ha un impatto reale sul servizio. Un alert può scattare per un picco normale di CPU o per una soglia impostata male, quindi va verificato prima di trattarlo come un incidente. Se troppi alert sono inutili gli operatori finiscono per ignorarli.

## 11.
**Risposta:** Correlazione vuol dire che due eventi succedono vicini nel tempo o insieme, per esempio una modifica alle 10:15 e un alert alle 10:25. Causalità vuol dire che uno ha davvero provocato l'altro. Per dire che c'è causalità servono altre prove, come capire cosa è stato modificato, se la metrica è collegata a quella modifica, se i log lo confermano o se tornando indietro il problema sparisce.

## 12.
**Risposta:** Descrivere il sintomo e il risultato atteso, raccogliere le evidenze prima di cambiare qualcosa, fare un'ipotesi e verificarla, applicare la correzione minima, ripetere il test e documentare tutto. Se la procedura viene scritta in un runbook con comandi, come leggere i risultati, correzione, verifica e rollback, può seguirla anche un'altra persona.
