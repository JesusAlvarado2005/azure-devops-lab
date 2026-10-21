# Consegna UD04 — Laboratorio autonomo

## Scelta del servizio e della ridondanza

Il requisito è conservare per 30 giorni dei documenti che un'applicazione legge spesso e cancellare dopo un giorno i file temporanei. Gli utenti devono leggere senza avere la account key e non ci deve essere accesso pubblico.

Scelgo Blob perché i documenti sono file interi che l'applicazione legge via HTTPS. Azure Files serve quando qualcuno deve montare una cartella condivisa via SMB o NFS e qui non serve. Queue contiene piccoli messaggi che un programma consuma e cancella e Table contiene righe di dati strutturati, quindi nessuno dei due va bene per dei documenti. Con Blob ho anche la SAS su un singolo blob per non dare la chiave, i ruoli dati con Entra ID e la lifecycle per prefisso per i file temporanei. Il fatto che i documenti si leggano spesso invece decide il tier, che è Hot.

In produzione userei ZRS se serve resistere al guasto di una zona. ZRS tiene tre copie in tre zone diverse della stessa region e se una zona si ferma i dati restano disponibili. LRS tiene le tre copie nello stesso datacenter e protegge solo da un guasto dell'hardware. Nel laboratorio uso LRS perché i file li ricreo in un attimo e restano solo un giorno, quindi pagare di più non proteggerebbe niente di importante.

## Operazioni e verifica

Ho usato lo storage account stcea3105028c del guidato e sempre --auth-mode login.

- ho creato da CLI il container privato archive e la risposta è stata created true
- ho caricato consegne/UD04/01_DOCUMENTO_LAB.txt come current/documento.txt e az storage blob list lo mostra come BlockBlob in tier Hot da 49 byte come l'originale
- ho generato una user delegation SAS firmata con la mia identità di sola lettura sul solo blob archive/current/documento.txt e con scadenza di 15 minuti. La prima è scaduta prima che la provassi e ne ho generata un'altra. Con curl ho scaricato il blob senza errori e cmp non ha dato output quindi il file è identico all'originale. Subito dopo ho fatto unset di SAS_URL e l'URL non l'ho salvato da nessuna parte

## Diagnosi

**AuthorizationPermissionMismatch**
- sintomo: un comando sui blob con --auth-mode login viene rifiutato
- piano: data plane
- causa: sono autenticato ma non ho un ruolo dati su quell'account. Owner o Contributor non bastano perché valgono sul management plane. Può anche essere un ruolo appena assegnato e non ancora attivo oppure assegnato su un altro account
- controllo: az role assignment list sullo storage account con --include-inherited per vedere se c'è un ruolo Storage Blob Data
- correzione: assegnare Storage Blob Data Reader o Contributor con lo scope minimo e aspettare qualche minuto senza dare ruoli più ampi

**ResourceNotFound: The specified container does not exist**
- sintomo: Azure risponde che il container non esiste
- piano: data plane
- causa: non è un problema di permessi perché la richiesta arriva ma il container non c'è. Di solito il nome è scritto male oppure è l'account sbagliato o il container non è stato creato
- controllo: az storage container list per vedere i nomi veri e controllare che $LAB_STORAGE sia l'account giusto
- correzione: usare il nome giusto oppure creare il container

**curl: (22) The requested URL returned error: 403**
- sintomo: curl con l'URL della SAS viene rifiutato
- piano: data plane con autorizzazione tramite SAS
- causa: il token non vale per quella richiesta. Può essere scaduto, cosa facile con 15 minuti, oppure non avere il permesso giusto, essere stato generato per un altro blob o essere stato copiato male
- controllo: guardo scadenza permessi e nome del blob usati per generarla senza stampare il token
- correzione: generare una nuova SAS corretta sempre di sola lettura e breve senza allungare la durata o aggiungere permessi

## Lifecycle, costi e cleanup

La regola delete-temporary guarda il percorso completo del blob cioè container più nome e agisce solo sui blob che iniziano con documents/temporary/. Il blob archive/current/documento.txt inizia con archive/ quindi la regola non lo tocca. È proprio il prefisso a limitare la regola e senza prefisso varrebbe per tutti i blob dell'account.

I costi dipendono dallo spazio occupato, dalla ridondanza, dal tier, dal numero di operazioni come upload list e download e dai dati trasferiti fuori da Azure. Qui sono pochi file da 49 byte in LRS quindi il costo è praticamente zero.

L'ordine del cleanup è questo

1. unset di SAS_URL anche se la SAS scade da sola
2. rimuovere la role assignment Storage Blob Data Contributor
3. cancellare i file temporanei in /tmp
4. controllare nome e tag del resource group con az group show
5. eliminare il resource group che contiene account container blob e regola lifecycle, poi az group wait --deleted e az group exists che deve dare false

Alla fine ho cancellato i file in /tmp, ho fatto unset delle variabili e ho eliminato il resource group. Dopo az group wait --deleted il comando az group exists ha restituito false. Non risultano più resource group rg-cea né assegnazioni Storage Blob Data Contributor.

## Risultato finale

- nessun segreto pubblicato: nel file non ci sono chiavi né token SAS né URL firmati né ID della sottoscrizione
- hash abbreviato e messaggio del commit: 392cde6 Completa laboratorio autonomo e verifica UD04
