# Consegna UD04 — Laboratorio guidato

## Contesto anonimizzato

- resource group: rg-cea-storage-3105028c creato da CLI con i tag course cloud-engineer-academy, unit UD04, environment lab e deleteAfter 2026-10-16
- storage account: stcea3105028c, prima ho controllato che il nome fosse libero con az storage account check-name
- region: italynorth
- tipo e ridondanza: StorageV2 con Standard_LRS che basta per un laboratorio con dati che posso ricreare

## Servizi e configurazione

| Elemento | Configurazione | Motivazione |
|---|---|---|
| Blob container | documents creato dal portale con accesso Private | i file del laboratorio si leggono via HTTPS e non serve una cartella da montare |
| access tier | Hot sia per l'account sia per i due blob | durante il laboratorio i file li leggo subito e più volte |
| accesso pubblico | allowBlobPublicAccess false | nessuno deve leggere i blob senza autenticarsi |
| trasferimento/TLS | https-only true e TLS minimo 1.2 | i dati viaggiano solo cifrati e con una versione di TLS sicura |

Ho controllato le proprietà con az storage account show senza leggere le chiavi. Nel container ci sono 01_DOCUMENTO_LAB.txt caricato dal portale e temporary/temporaneo.txt caricato da CLI.

## Autorizzazione e lifecycle

Dallo IAM mi sono assegnato Storage Blob Data Contributor sul resource group rg-cea-storage-3105028c, che contiene solo lo storage account del laboratorio. Anche se sono Owner della sottoscrizione mi serviva lo stesso, perché Owner vale sul management plane e non dà accesso ai blob con Entra ID. Con il ruolo dati az storage container list e az storage blob list con --auth-mode login hanno funzionato.

- Entra ID: l'accesso è legato alla mia identità e al mio ruolo, quindi si sa chi ha fatto cosa e il permesso si toglie rimuovendo il ruolo
- Shared Key: ho messo la chiave in una variabile solo per un az storage blob list con --auth-mode key e poi ho fatto unset. La chiave apre tutto l'account, non scade e non dice chi la sta usando
- SAS: ho generato una user delegation SAS firmata con la mia identità, di sola lettura sul solo blob 01_DOCUMENTO_LAB.txt e con scadenza di 30 minuti. Con curl ho scaricato il file e cmp non ha trovato differenze. L'URL non l'ho salvato da nessuna parte

La regola lifecycle si chiama delete-temporary, è abilitata e vale per i block blob con prefisso documents/temporary/. Elimina i blob un giorno dopo l'ultima modifica. Il prefisso serve a colpire solo i file temporanei e non il documento del laboratorio. La regola non parte subito, quindi ho controllato solo la configurazione con az storage account management-policy show.

## Verifiche, costi e cleanup

- ho scaricato il file con --auth-mode login e cmp non ha dato output, quindi è uguale all'originale
- anche il file letto con la SAS tramite curl è risultato identico
- i costi dipendono dallo spazio occupato, dalla ridondanza, dal tier, dal numero di operazioni e dal traffico in uscita. Qui sono due file piccolissimi in LRS e il costo è praticamente zero
- il cleanup l'ho fatto dopo il laboratorio autonomo e la verifica. Ho cancellato i file temporanei in /tmp e fatto unset di AZURE_STORAGE_KEY e SAS_URL, poi ho eliminato il resource group con az group delete --no-wait e ho aspettato con az group wait --deleted
- az group exists ha restituito false e nella sottoscrizione non risulta più nessuna assegnazione Storage Blob Data Contributor

## Rilevanza professionale

Per i documenti di un'applicazione sceglierei Blob, perché l'app li legge via HTTPS e non le serve una cartella montata. Come autorizzazione userei Entra ID con un ruolo dati come Storage Blob Data Reader o Contributor sullo scope più piccolo, così ogni accesso è legato a un'identità. Se devo far scaricare un file a qualcuno da fuori userei una user delegation SAS di sola lettura e con scadenza breve e mai la account key. Sceglierei Files invece se un programma o delle persone hanno bisogno di una cartella condivisa da montare via SMB.
