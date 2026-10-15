# Consegna UD04 — Verifica

## Parte A — Scelta singola

Per le domande 1–8 riporta risposta e motivazione.

1. A perché Blob conserva i file come oggetti con un indirizzo HTTPS ed è quello che serve a un'applicazione per le immagini.
2. B perché Azure Files offre condivisioni di file che si montano via SMB come un disco di rete.
3. B perché Contributor è un ruolo del management plane e per leggere i blob con Entra ID serve un ruolo dati come Storage Blob Data Reader.
4. B perché ZRS tiene le copie in zone diverse della stessa region e se una zona si ferma i dati restano disponibili.
5. B perché la SAS è un token che permette solo certe operazioni su certe risorse e fino a una scadenza.
6. C perché il budget manda un avviso quando si supera la soglia ma non blocca né elimina niente.
7. B perché la regola agisce solo sui blob il cui percorso comincia con il prefisso indicato.
8. A perché dice alla CLI di usare la mia identità Entra e i miei ruoli dati invece della account key.

## Parte B — Risposte brevi

9. La ridondanza tiene più copie dei dati aggiornate di continuo, quindi se si rompe un disco o una zona o una region i dati restano disponibili. Però copia anche ogni modifica, quindi anche una cancellazione per errore o dei file cifrati da un malware. Il backup invece salva i dati in momenti diversi e mi permette di tornare a com'erano ieri o una settimana fa e recuperarli dopo un errore.

10. Il management plane serve a creare e configurare la risorsa e passa da Azure Resource Manager, per esempio az storage account show legge le proprietà dell'account. Il data plane serve a lavorare sui dati dentro la risorsa, per esempio az storage blob list --auth-mode login mostra i blob di un container. Hanno ruoli diversi perché sul primo valgono Owner e Contributor e sul secondo i ruoli Storage Blob Data.

11. Permessi minimi come la sola lettura, lo scope più piccolo possibile cioè un singolo blob o container e non tutto l'account, una scadenza breve e solo HTTPS. In più non va mai pubblicata ed è meglio una user delegation SAS firmata con Entra ID.

12. Perché Archive è offline e prima di leggere un blob bisogna reidratarlo su un tier come Hot o Cool, cosa che può richiedere ore. Se il dato mi serve subito devo aspettare e in più il recupero costa di più.

13. Perché sono credenziali e chi le trova entra nei dati senza bisogno di un'identità e senza che si sappia chi è. Il repository viene clonato e la cronologia di git tiene il segreto anche se poi lo cancello. La account key poi non scade e apre tutto l'account, quindi andrebbe ruotata e così si bloccano anche gli usi legittimi.

## Parte C — Caso situazionale

14. Contributor è un ruolo del management plane, quindi non serve a leggere i documenti e in più permette di modificare o eliminare lo storage account. Senza --auth-mode login la CLI può usare la account key invece della mia identità e così non si sa chi accede. La account key condivisa dà accesso completo a tutto l'account senza scadenza e senza sapere chi la usa. La SAS con permessi completi e senza scadenza breve, se finisce nelle mani sbagliate, permette per molto tempo di leggere modificare e cancellare i documenti privati.

15. All'applicazione o agli utenti darei Storage Blob Data Reader perché devono solo leggere i documenti. Non Reader, che è un ruolo del management plane e non legge i blob. Come scope userei il container dei documenti perché è il livello più piccolo che copre quello che serve, invece di tutto l'account o della sottoscrizione. Se un file va condiviso con qualcuno che non ha un'identità userei una user delegation SAS di sola lettura su un singolo blob e con scadenza breve. La account key non la darei a nessuno.

16. Per l'accesso controllo il ruolo con az role assignment list sullo scope del container usando --query e sed per nascondere l'ID della sottoscrizione, poi provo una lettura con az storage blob list --auth-mode login. La SAS la provo con curl e cmp tenendo l'URL solo in una variabile senza echo e poi faccio unset. Per il cleanup rimuovo il ruolo e controllo che non ci sia più, ruoto la account key che era stata condivisa così smette di funzionare, elimino il resource group e verifico che az group exists dia false. Prima del commit controllo con git diff che nel repository non ci siano chiavi, token o URL firmati.
