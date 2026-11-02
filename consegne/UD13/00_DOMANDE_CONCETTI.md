# UD13 — Domande concetti

## 1.
**Risposta:** lo state è il collegamento tra il blocco scritto nel codice e la risorsa vera in Azure, per esempio azurerm_resource_group.lab con rg-ud12-tf. In locale va bene se lavoro da solo, ma se due persone hanno due copie diverse non sanno più quale è aggiornata e la pipeline non può leggere lo state che sta sul mio PC.

## 2.
**Risposta:** il backend remoto tiene lo state in una posizione condivisa, su Azure un blob, e il locking con un lease evita che due esecuzioni lo aggiornino insieme. Va progettato anche l'accesso perché lo state può contenere valori sensibili e va protetto e recuperabile, quindi servono storage, autenticazione, permessi e versioning.

## 3.
**Risposta:** Terraform riconosce la dipendenza quando una risorsa usa un attributo di un'altra, per esempio resource_group_name = azurerm_resource_group.lab.name, e la mette nel grafo. Spostare codice da main.tf a network.tf non crea un modulo perché tutti i .tf della stessa directory sono un'unica configurazione, un modulo esiste solo se lo chiami con un blocco module.

## 4.
**Risposta:** nella pipeline IaC Validate è lo stage, ValidateIaC è il job che gira sull'agent e "Terraform fmt and validate" è lo step con dentro i comandi. Lo stage raggruppa una fase, il job una sequenza di step eseguita su un agent, lo step è la singola operazione.

## 5.
**Risposta:** perché in UD13 voglio vedere i comandi eseguiti sul WSL2 preparato prima e usare il Terraform, Azure CLI e Bicep che ho già installato lì. La postazione deve essere accesa, WSL e agent Online, e l'utente che esegue l'agent deve trovare i tool nel PATH, altrimenti lo step fallisce con command not found.

## 6.
**Risposta:** il pool è il gruppo di macchine dove Azure DevOps cerca un agent libero, il nome non identifica un PC preciso. Tre agent possono fare tre job insieme solo se ci sono abbastanza Parallel Jobs e i job non dipendono l'uno dall'altro, altrimenti restano in coda.

## 7.
**Risposta:** cambia la macchina, non la logica: con vmImage: ubuntu-latest la VM la gestisce Microsoft, è nuova a ogni job e alla fine sparisce, quindi i tool dipendono dall'immagine e non dai file rimasti da prima. Con il self-hosted i file restano e i tool li mantengo io.

## 8.
**Risposta:** checkout: self prende il repository collegato alla pipeline e ne mette una copia nell'area di lavoro dell'agent, nel commit scelto per la run. Un file che ho sul PC ma non ho committato non esiste in quel commit, quindi la pipeline non lo vede.

## 9.
**Risposta:** Agent.Name dice quale agent sta eseguendo il job, Agent.OS il sistema operativo e Build.SourcesDirectory dove è finito il checkout. Uso queste variabili invece di ~/workspace/azure-devops-lab perché quel percorso esiste solo sul mio PC e su un altro agent non c'è.

## 10.
**Risposta:** workspace clean: all pulisce tutto il Pipeline.Workspace prima del job, checkout clean: true pulisce e ripristina solo la copia Git. Fuori dal workspace restano comunque Terraform, Azure CLI, Docker e gli altri programmi installati sul self-hosted, quelli li gestisce chi mantiene l'agent.

## 11.
**Risposta:** la Azure Pipelines GitHub App serve a far leggere il repository privato ad Azure Pipelines senza mettere un PAT nel YAML, e se posso limito l'accesso al solo repo del corso. Leggere il codice non dà nessun permesso su Azure, per creare risorse serve un'altra identità con altri ruoli.

## 12.
**Risposta:** la service connection è la configurazione con cui i task si autenticano ad Azure con l'identità prevista. Azure DevOps decide se quella pipeline può usarla, Azure decide cosa quell'identità può fare: può essere autorizzata ma senza il ruolo giusto, o avere i ruoli ma non essere autorizzata alla pipeline.

## 13.
**Risposta:** con WIF l'identità dimostra chi è con un token temporaneo e una relazione di fiducia, senza client secret statico da conservare. Il token dice solo chi sta operando: se poi manca il ruolo o lo scope giusto Azure risponde con un errore di autorizzazione.

## 14.
**Risposta:** perché la pipeline deve creare l'ACR solo in rg-ud13-15-delivery e non amministrare tutta la subscription, è minimo privilegio. Creare risorse e assegnare ruoli sono operazioni diverse: Contributor crea risorse ma non può creare assegnazioni RBAC, per quelle serve Owner o User Access Administrator.

## 15.
**Risposta:** fmt -check controlla solo la formattazione senza riscrivere, init -backend=false prepara provider e moduli senza backend, validate controlla sintassi e riferimenti della configurazione. Nessuno dei tre applica su Azure: non guardano quote, policy, nomi occupati o risorse reali, quindi non equivalgono a un deployment Terraform.

## 16.
**Risposta:** il lint controlla il codice Bicep, what-if chiede ad Azure cosa cambierebbe senza creare niente, il deployment crea davvero. L'ACR nella pipeline di questa UD lo crea il deployment Bicep, non Terraform e non what-if.

## 17.
**Risposta:** trigger: none disabilita l'avvio automatico sui push, quindi la pipeline IaC la lancio a mano. La CI invece con trigger: main parte da sola quando arriva un commit su main, per esempio dopo il merge di una Pull Request.

## 18.
**Risposta:** l'ACR resta perché la CI di questa UD ci pubblica l'immagine e la UD14 la usa per il deployment. Creare il registry, fare push dell'immagine e fare pull dall'app sono passaggi diversi e possono usare identità diverse: il deployment crea, AcrPush pubblica, AcrPull scarica.

## 19.
**Risposta:** lo impostiamo per usare il modello RBAC classico dove valgono AcrPush e AcrPull, coerente con il resto del percorso. Se il registry fosse in modalità ABAC quei ruoli legacy non varrebbero per i repository e servirebbero i ruoli nuovi, quindi push e pull potrebbero rompersi.

## 20.
**Risposta:** a fine UD13 elimino le risorse Terraform temporanee dell'esercizio, cioè rg-ud12-tf con VNet e subnet, mentre tengo rg-ud13-15-delivery, ACR, service connection, pipeline e agent. Il cleanup deve rispettare le dipendenze perché la CI e la UD14 hanno bisogno dell'ACR e delle connessioni, se li cancello interrompo il percorso.

## 21.
**Risposta:** parto dall'esterno: se la run non parte guardo trigger e branch, se il job resta in attesa guardo pool, agent Online, demands e Parallel Jobs. Poi checkout e autorizzazione GitHub, poi directory e file del commit, poi tool mancanti nell'agent, e solo alla fine service connection e permessi Azure. Leggo il primo step rosso e il suo messaggio, non tutto il rosso della pipeline.
