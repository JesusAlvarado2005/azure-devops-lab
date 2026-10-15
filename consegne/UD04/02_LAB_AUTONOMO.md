# Consegna UD04 — Laboratorio autonomo

## Scelta del servizio e della ridondanza

Il requisito è conservare documenti che un'applicazione consulta spesso per 30 giorni, file temporanei da eliminare dopo un giorno, utenti che leggono senza ricevere la account key e nessun accesso pubblico.

Scelgo Blob perché i documenti sono file interi che l'applicazione legge via HTTPS. Azure Files serve quando qualcuno deve montare una cartella condivisa via SMB o NFS, e qui non serve. Queue contiene piccoli messaggi che un programma consuma e cancella, non documenti da conservare. Table contiene righe di dati strutturati con chiave e attributi, non file. Con Blob ho anche quello che serve al resto dello scenario: SAS su un singolo blob per non dare la chiave, ruoli dati con Entra ID e lifecycle per prefisso per i file temporanei. Il fatto che i documenti si leggano spesso decide invece il tier, che è Hot.

In produzione, se il requisito comprende la resilienza a un guasto di zona, userei ZRS, che tiene tre copie in tre zone diverse della stessa region, quindi se una zona si ferma i dati restano disponibili. LRS invece tiene le tre copie nello stesso datacenter e protegge solo da un guasto dell'hardware. Nel laboratorio uso LRS perché i file li ricreo in un attimo e restano solo un giorno, quindi pagare di più per più zone non proteggerebbe niente di importante.

## Operazioni e verifica

Ho usato lo storage account stcea3105028c del guidato, sempre con --auth-mode login.

- container archive creato da CLI con az storage container create, privato come tutto l'account, risposta created true
- blob current/documento.txt caricato da consegne/UD04/01_DOCUMENTO_LAB.txt. Con az storage blob list risulta BlockBlob, tier Hot, 49 byte, gli stessi del file originale
- SAS: user delegation firmata con la mia identità, solo lettura r, solo sul blob archive/current/documento.txt e con scadenza di 15 minuti. La prima l'ho lasciata scadere prima di provarla, quindi ne ho generata una nuova. Con curl ho scaricato il blob senza errori e cmp non ha dato output, quindi il file è identico all'originale. Subito dopo ho fatto unset di SAS_URL e l'URL non l'ho salvato da nessuna parte

## Diagnosi

**AuthorizationPermissionMismatch**
- sintomo: un comando sui blob con --auth-mode login viene rifiutato
- piano: data plane
- causa: sono autenticato ma la mia identità non ha un ruolo dati su quell'account. Owner o Contributor non bastano perché valgono sul management plane. Può anche essere un ruolo assegnato da poco e non ancora attivo, oppure su un altro account o scope
- controllo: az role assignment list sullo scope dello storage account con --include-inherited, cercando un ruolo Storage Blob Data
- correzione: assegnare Storage Blob Data Reader o Contributor con lo scope minimo e aspettare qualche minuto, senza dare ruoli più ampi

**ResourceNotFound: The specified container does not exist**
- sintomo: Azure risponde che il container non esiste
- piano: data plane
- causa: non è un problema di permessi, la richiesta arriva ma il container cercato non c'è. Di solito il nome è scritto male, è l'account sbagliato oppure il container non è ancora stato creato o è stato eliminato
- controllo: az storage container list sull'account per vedere i nomi veri, e controllo che $LAB_STORAGE sia l'account giusto
- correzione: usare il nome corretto oppure creare il container

**curl: (22) The requested URL returned error: 403**
- sintomo: curl con l'URL della SAS viene rifiutato
- piano: data plane, con autorizzazione tramite SAS
- causa: il token non autorizza quella richiesta. Può essere scaduto, cosa facile con 15 minuti, non avere il permesso giusto, essere generato per un altro blob o essere stato copiato male
- controllo: scadenza, permessi e nome del blob usati per generarla, senza stampare il token
- correzione: generare una nuova SAS corretta, sempre di sola lettura e breve, senza allungare la durata o aggiungere permessi

## Lifecycle, costi e cleanup

La regola delete-temporary guarda il percorso completo del blob, cioè container più nome, e agisce solo sui blob che iniziano con documents/temporary/. archive/current/documento.txt inizia con archive/, quindi la regola non lo tocca. Il prefisso è proprio quello che limita la regola: senza prefisso varrebbe per tutti i blob dell'account.

I costi dipendono dallo spazio occupato, dalla ridondanza, dal tier, dal numero di operazioni come upload, list e download e dai dati letti o trasferiti fuori da Azure. Qui sono pochi file da 49 byte in LRS, quindi il costo è praticamente zero.

Ordine del cleanup:

1. unset di SAS_URL, la SAS comunque scade da sola
2. rimuovere la role assignment Storage Blob Data Contributor
3. cancellare i file temporanei in /tmp
4. controllare nome e tag del resource group con az group show
5. eliminare il resource group, che contiene account, container, blob e regola lifecycle, poi az group wait --deleted e az group exists che deve dare false

Alla fine ho cancellato i file in /tmp, fatto unset delle variabili e eliminato il resource group. Dopo az group wait --deleted, az group exists ha restituito false. Non risultano più resource group rg-cea né assegnazioni Storage Blob Data Contributor.

## Risultato finale

- nessun segreto pubblicato: nel file non ci sono chiavi, token SAS, URL firmati né ID della sottoscrizione
- hash abbreviato e messaggio del commit:
