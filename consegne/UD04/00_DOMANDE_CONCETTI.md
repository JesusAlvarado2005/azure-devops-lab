# Consegna UD04 — Domande sui concetti

Per ciascuna domanda 1–8 riporta una risposta motivata.

1. Perché sono due modi diversi di conservare e usare i dati. Blob è object storage: i dati stanno come oggetti dentro container e si raggiungono tramite HTTPS e API, quindi è adatto ad applicazioni. Azure Files invece offre una condivisione di file con cartelle che si monta via SMB o NFS come un disco di rete, e ci si lavora direttamente come in una cartella. Un programma che si aspetta una cartella non può usare un container, e viceversa.

2. Il management plane riguarda la gestione della risorsa: creare lo storage account, cambiarne ridondanza o rete, leggerne le proprietà. Passa da Azure Resource Manager. Il data plane riguarda le operazioni sui dati dentro la risorsa, come caricare, leggere o eliminare un blob. Passa dall'endpoint del servizio, per esempio blob.core.windows.net, e ha ruoli suoi.

3. Perché Contributor è un ruolo del management plane: permette di gestire lo storage account ma non dà accesso ai dati con Entra ID. Per leggere o scrivere i blob con la propria identità servono ruoli del data plane, come Storage Blob Data Reader o Storage Blob Data Contributor. Nel laboratorio infatti, pur essendo Owner della sottoscrizione, ho dovuto assegnarmi Storage Blob Data Contributor per leggere i blob con --auth-mode login.

4. La geo-ridondanza tiene copie in un'altra region e protegge se una region intera ha un guasto, ma replica ogni modifica, quindi copia anche una cancellazione o un file corrotto. Il backup invece conserva copie del passato a cui tornare, e serve proprio a recuperare dopo un errore, una cancellazione o un dato rovinato.

5. Valuterei quanto spesso dovrò leggere quei dati e per quanto tempo li terrò. Archive costa poco per la conservazione, ma leggere e recuperare i dati costa di più ed è lento, perché è offline e serve la reidratazione, che può richiedere ore. Va bene solo per dati che non devo consultare quasi mai e che posso aspettare.

6. Perché la account key dà accesso completo a tutto lo storage account e a tutti i suoi dati, e non scade. Se viene persa o rubata non si capisce chi la usa, e l'unico rimedio è ruotarla, interrompendo anche chi la usava in modo legittimo. Una SAS limitata invece vale solo per certe operazioni, su certe risorse e per un tempo breve, quindi il danno possibile è molto più piccolo.

7. Permessi minimi, per esempio solo lettura, scope più ristretto possibile, cioè un container o un blob e non tutto l'account, scadenza breve e solo HTTPS. In più non va mai pubblicata nel repository o negli screenshot. Quando si può è meglio una user delegation SAS, firmata con le credenziali Entra invece che con la account key.

8. Perché la policy lifecycle non è un'operazione immediata: Azure la elabora in modo periodico e possono passare ore, anche fino a 24, prima che venga applicata. In più le regole agiscono in base all'età dei blob, quindi un file caricato da pochi minuti non soddisfa ancora la condizione. Per questo nel laboratorio ho verificato solo che la regola fosse configurata bene, con il prefisso giusto e un giorno dall'ultima modifica.
