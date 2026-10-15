# Consegna UD04 — Domande sui concetti

Per ciascuna domanda 1–8 riporta una risposta motivata.

1. Perché sono due modi diversi di conservare e usare i dati. Con Blob i dati sono oggetti dentro un container e si raggiungono via HTTPS, quindi è adatto alle applicazioni. Azure Files invece è una cartella condivisa che si monta via SMB o NFS come un disco di rete e ci si lavora come in una cartella normale. Un programma che si aspetta una cartella non può usare un container e viceversa.

2. Il management plane serve a gestire la risorsa, per esempio creare lo storage account, cambiare la ridondanza o leggerne le proprietà, e passa da Azure Resource Manager. Il data plane serve a lavorare sui dati dentro la risorsa come caricare leggere o eliminare un blob. Passa dall'endpoint del servizio come blob.core.windows.net e ha dei ruoli suoi.

3. Perché Contributor è un ruolo del management plane e permette di gestire lo storage account ma non di leggere i dati con Entra ID. Per leggere o scrivere i blob con la propria identità servono ruoli del data plane come Storage Blob Data Reader o Storage Blob Data Contributor. Infatti nel laboratorio anche se ero Owner della sottoscrizione ho dovuto assegnarmi Storage Blob Data Contributor per leggere i blob con --auth-mode login.

4. La geo-ridondanza tiene una copia in un'altra region e protegge se una region intera si ferma. Però copia ogni modifica e quindi anche una cancellazione o un file rovinato. Il backup invece conserva copie del passato a cui posso tornare e serve proprio a recuperare i dati dopo un errore o una cancellazione.

5. Valuterei quanto spesso dovrò leggere quei dati e per quanto tempo li terrò. Archive costa poco per conservare ma leggere i dati costa di più ed è lento, perché è offline e prima serve la reidratazione che può durare ore. Va bene solo per dati che non consulto quasi mai e per cui posso aspettare.

6. Perché la account key apre tutto lo storage account e tutti i suoi dati e non scade. Se viene persa o rubata non si sa chi la sta usando e l'unico rimedio è ruotarla, così si blocca anche chi la usava in modo legittimo. Una SAS limitata invece vale solo per certe operazioni su certe risorse e per poco tempo, quindi il danno possibile è molto più piccolo.

7. Permessi minimi come la sola lettura, lo scope più piccolo possibile cioè un container o un blob e non tutto l'account, una scadenza breve e solo HTTPS. In più non va mai pubblicata nel repository o negli screenshot. Quando si può è meglio una user delegation SAS firmata con Entra ID invece che con la account key.

8. Perché la policy lifecycle non parte subito. Azure la esegue periodicamente e possono passare ore, anche fino a 24, prima che venga applicata. In più la regola guarda l'età dei blob e un file caricato da pochi minuti non è ancora abbastanza vecchio. Per questo nel laboratorio ho controllato solo che la regola fosse configurata bene con il prefisso giusto e un giorno dall'ultima modifica.
