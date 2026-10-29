# UD12 — Domande sui concetti

Rispondere dopo avere studiato `00_CONCETTI.md`. Non limitarsi a definizioni di una riga: quando possibile aggiungere un piccolo esempio.

## 1.
**Risposta:** con la configurazione manuale ogni volta clicchi o lanci comandi a mano e non sai se rifai uguale, con IaC l'infrastruttura è scritta in file versionati e si ricrea sempre uguale, per esempio lo stesso storage in un altro ambiente

## 2.
**Risposta:** imperativo è dire i passi uno dopo l'altro, tipo crea il gruppo poi crea lo storage, dichiarativo è descrivere come deve essere alla fine e lo strumento capisce cosa fare

## 3.
**Risposta:** perché serve per controllare chi sono, su che subscription sto e per verificare dopo che le risorse create dall'IaC siano davvero come le ho scritte

## 4.
**Risposta:** è il linguaggio di Microsoft per descrivere risorse Azure in modo dichiarativo, più leggibile del JSON ARM

## 5.
**Risposta:** no, Bicep viene trasformato in un template ARM e il deployment lo fa sempre Azure Resource Manager

## 6.
**Risposta:** è un parametro che si chiama location ed è una stringa, nel nostro file di default prende la location del resource group

## 7.
**Risposta:** serve a non scrivere valori fissi nel template, lo stesso file lo uso con nomi o regioni diverse, come storageName

## 8.
**Risposta:** controllano la lunghezza del valore prima del deployment, il nome dello storage deve stare tra 3 e 24 caratteri

## 9.
**Risposta:** è il nome simbolico della risorsa dentro il file Bicep, serve per richiamarla negli output o in altre risorse

## 10.
**Risposta:** è il tipo di risorsa, il provider Microsoft.Storage e il tipo storageAccounts

## 11.
**Risposta:** è la versione dell'API che si usa per quella risorsa, decide quali proprietà si possono usare

## 12.
**Risposta:** no, è solo la versione dell'API, non c'entra con quando viene creato lo storage

## 13.
**Risposta:** il nome simbolico è quello nel file, storage, il nome reale è quello che vedi in Azure, per esempio stud12b93265947 che arriva dal parametro

## 14.
**Risposta:** restituiscono valori dopo il deployment, come il nome dello storage e il blob endpoint, che poi posso riusare in altri passaggi

## 15.
**Risposta:** controlla il file e segnala errori e cattive pratiche prima di mandarlo ad Azure

## 16.
**Risposta:** fa vedere cosa cambierebbe in Azure se facessi il deployment, per esempio Create di uno storage account

## 17.
**Risposta:** no, mostra solo la previsione, non crea niente

## 18.
**Risposta:** what-if fa solo la previsione, create fa il deployment vero e crea o modifica le risorse

## 19.
**Risposta:** perché lo stato lo tiene Azure Resource Manager stesso, Bicep confronta il template con quello che c'è già in Azure

## 20.
**Risposta:** è uno strumento IaC di HashiCorp che funziona con tanti cloud e servizi, si scrive in HCL e tiene uno state

## 21.
**Risposta:** perché Terraform da solo non sa parlare con Azure o AWS, il provider è il pezzo che traduce le risorse nelle chiamate API di quel servizio

## 22.
**Risposta:** è il provider per Azure, sa creare risorse come azurerm_resource_group e azurerm_storage_account

## 23.
**Risposta:** la versione minima di Terraform, il provider AzureRM e il vincolo sulla sua versione, da noi ~> 5.4

## 24.
**Risposta:** configura il provider, da noi azurerm con features vuoto

## 25.
**Risposta:** perché il codice va nel repo e lo vedono tutti, le credenziali sono segreti, per questo il Subscription ID lo passo con ARM_SUBSCRIPTION_ID e non nei file

## 26.
**Risposta:** le variabili con tipo, descrizione, default e validazione, location, resource_group_name e storage_account_name

## 27.
**Risposta:** azurerm_resource_group è il tipo, lab è il nome simbolico, var.resource_group_name è la variabile che contiene il nome e rg-ud12-tf è il nome reale in Azure

## 28.
**Risposta:** il nome simbolico della risorsa dentro Terraform

## 29.
**Risposta:** no, si chiama rg-ud12-tf, lab vale solo dentro il codice

## 30.
**Risposta:** dal default della variabile resource_group_name in variables.tf

## 31.
**Risposta:** il nome reale del resource group che Terraform ha creato con il blocco lab

## 32.
**Risposta:** così lo storage va nel resource group creato da Terraform e Terraform capisce che deve creare prima il gruppo

## 33.
**Risposta:** la location del resource group, così lo storage sta nella stessa regione

## 34.
**Risposta:** perché lo storage usa attributi del resource group, se una risorsa si riferisce a un'altra Terraform crea prima quella

## 35.
**Risposta:** blocca prima del plan un nome sbagliato, solo minuscole e numeri tra 3 e 24 caratteri, così non arrivo all'errore di Azure

## 36.
**Risposta:** mostrano valori dopo l'apply, come nome del gruppo, nome dello storage e blob endpoint, e si leggono con terraform output

## 37.
**Risposta:** prepara la cartella, scarica il provider AzureRM e crea o aggiorna il lock file

## 38.
**Risposta:** .terraform/ contiene i provider scaricati e non va nel repo, .terraform.lock.hcl fissa le versioni dei provider e si committa

## 39.
**Risposta:** sistema la formattazione dei file .tf, con -check controlla soltanto senza cambiare

## 40.
**Risposta:** controlla che la configurazione sia corretta, sintassi e riferimenti, senza toccare Azure

## 41.
**Risposta:** confronta codice, state e Azure e dice cosa farebbe, quante risorse aggiunge, cambia o distrugge

## 42.
**Risposta:** perché lì vedo se succede quello che mi aspetto, se vedo destroy che non volevo mi fermo prima di fare danni

## 43.
**Risposta:** così l'apply fa esattamente il piano che ho letto e non uno nuovo calcolato dopo

## 44.
**Risposta:** applica le modifiche in Azure e aggiorna lo state

## 45.
**Risposta:** è il file dove Terraform si salva cosa gestisce e come sono le risorse

## 46.
**Risposta:** tra le risorse scritte nel codice e quelle reali in Azure, per esempio azurerm_resource_group.lab con rg-ud12-tf

## 47.
**Risposta:** perché può contenere dati sensibili e cambia a ogni apply, non è codice scritto da me, per questo è nel .gitignore

## 48.
**Risposta:** le risorse che Terraform sta gestendo, da noi azurerm_resource_group.lab e azurerm_storage_account.lab

## 49.
**Risposta:** no, solo quelle gestite da quella configurazione

## 50.
**Risposta:** no, elimina le risorse in Azure, i file .tf restano

## 51.
**Risposta:** Bicep diventa ARM e lo stato lo tiene Azure, Terraform chiama le API Azure tramite il provider e lo stato lo tiene lui nel tfstate

## 52.
**Risposta:** tutti e due fanno vedere cosa cambierà prima di applicare

## 53.
**Risposta:** what-if confronta il template con Azure, plan confronta codice, state e Azure, e funzionano con motori diversi

## 54.
**Risposta:** in un'azienda che usa solo Azure e vuole restare sugli strumenti Microsoft

## 55.
**Risposta:** in un'azienda che usa più cloud o servizi diversi e vuole un solo strumento per tutti

## 56.
**Risposta:** perché dipende dal contesto, dal team e dai cloud che si usano, tutti e due fanno bene il loro lavoro

## 57.
**Risposta:** perché sono il modo di ricreare l'infrastruttura e li useranno le pipeline, le risorse si distruggono ma il codice resta

## 58.
**Risposta:** no, si riusano quelli che ho messo nel repo in UD12

## 59.
**Risposta:** perché il self-hosted agent gira sul mio stesso ambiente, quindi le pipeline potranno usare il Terraform che ho installato

## 60.
**Risposta:** sull'agent che prende il job, self-hosted o Microsoft-hosted

## 61.
**Risposta:** è la macchina dell'agent self-hosted, con i tool che ci ho installato io

## 62.
**Risposta:** il self-hosted tiene tool e file tra un job e l'altro, il Microsoft-hosted è una macchina nuova a ogni job e i tool dipendono dall'immagine

## 63.
**Risposta:** perché le risorse sono in Azure e il codice è nel repo, se le distruggo le posso ricreare uguali col codice
