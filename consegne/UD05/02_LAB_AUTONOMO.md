# Consegna UD05 — Laboratorio autonomo

## Inventario iniziale

Ho usato le risorse del guidato nel resource group rg-cea-network-4756a8 e ho ricostruito tutto da CLI con az resource list, az network vnet show, az network vnet subnet show, az network nic show e az network nsg rule list. Dagli ID ho tolto quello della sottoscrizione con sed.

| Elemento | Configurazione |
|---|---|
| VNet vnet-cea-4756a8 | 10.50.0.0/16 |
| subnet snet-web | 10.50.10.0/24 senza NSG e senza route table |
| subnet snet-data | 10.50.20.0/24 con NSG nsg-data-4756a8 e senza route table |
| nic-web-01 | in snet-web con IP 10.50.10.4, nessun IP pubblico e nessun NSG sulla NIC |
| nic-data-01 | in snet-data con IP 10.50.20.4, nessun IP pubblico, nessun NSG sulla NIC e nessuna VM collegata |
| regole di nsg-data-4756a8 | solo Allow-Web-Postgres con priorità 300 Inbound TCP da 10.50.10.0/24 sulla porta 5432 |

snet-web non ha un NSG perché qui si protegge la destinazione. La regola è Inbound su snet-data e controlla chi entra nella subnet del database.

## Guasto e diagnosi

- regola introdotta: Deny-Web-Postgres-Auto con priorità 250 Inbound TCP da 10.50.10.0/24 sulla porta 5432, cioè la stessa origine e la stessa porta della regola Allow
- ordine di priorità osservato: con az network nsg rule list ordinato per priorità la 250 Deny compare sopra la 300 Allow
- sintomo: il web non potrebbe collegarsi al database sulla 5432
- ipotesi: una regola con un numero più basso dell'Allow blocca lo stesso flusso. Un pacchetto da 10.50.10.4 verso 10.50.20.4 sulla 5432 TCP corrisponde alla 250 e l'NSG si ferma lì, quindi la 300 non viene nemmeno letta
- controllo: ho verificato che l'NSG fosse associato a snet-data, che nic-data-01 fosse in quella subnet senza un NSG suo, che non ci fosse una route table e ho letto le regole in ordine di priorità. Sono letture della configurazione e non i report effettivi, che richiedono una VM in esecuzione e sono rinviati alla UD06
- correzione minima: ho eliminato solo Deny-Web-Postgres-Auto usando il suo nome senza toccare la regola Allow
- verifica dopo la correzione: nel rule list è rimasta solo Allow-Web-Postgres 300, che è di nuovo la prima regola personalizzata che corrisponde al flusso

Il conflitto l'ho trovato leggendo le regole perché l'ordine delle priorità è scritto nella configurazione. Questa però è una deduzione e non un test. IP Flow Verify prova un pacchetto su una NIC collegata a una VM in esecuzione e senza VM non c'è niente su cui provarlo. In più dalla lettura dell'NSG non vedo un eventuale NSG sulla NIC della futura VM, le route effettive, il firewall del sistema operativo e se un servizio ascolta davvero sulla 5432. Per questo dichiaro configurazione NSG e associazioni verificate e prova del flusso rinviata alla UD06.

## Casi ulteriori

**InvalidAddressPrefix**
- livello: indirizzamento CIDR, l'errore esce quando creo la VNet o una subnet
- causa: il prefisso è scritto male oppure non è allineato, come 10.50.20.5/24 invece di 10.50.20.0/24, oppure la subnet esce dallo spazio della VNet o si sovrappone a un'altra subnet
- controllo: confronto primo e ultimo indirizzo della subnet con lo spazio della VNet e con le altre subnet usando az network vnet show
- correzione minima: scegliere un prefisso valido dentro la VNet che non si sovrapponga

**SecurityRuleConflict**
- livello: regole NSG
- causa: provo a creare una regola con la stessa priorità e la stessa direzione di una regola già presente nello stesso NSG. Due regole non possono avere lo stesso numero perché Azure non saprebbe quale leggere prima
- controllo: az network nsg rule list ordinato per priorità per vedere i numeri già usati
- correzione minima: dare alla nuova regola un numero libero scelto in base a quando deve essere valutata rispetto alle altre

**Un nome DNS non viene risolto**
- livello: DNS, prima ancora di route e NSG
- causa: non è un problema di filtro e non vuol dire che la risorsa non abbia un IP. Il nome non viene tradotto in indirizzo perché è scritto male, manca il record o la VNet usa un DNS configurato male
- controllo: provo a risolvere il nome con nslookup o dig e guardo i server DNS impostati sulla VNet e se il record esiste. Se usando direttamente l'IP la connessione funziona allora il problema è solo il DNS
- correzione minima: correggere il nome, creare il record mancante o sistemare la configurazione DNS della VNet

**La porta risulta filtrata da un NSG**
- livello: NSG
- causa: una regola Deny corrisponde al flusso prima di una regola Allow, come nel guasto della 250
- controllo: vedo quali NSG ci sono sul percorso, sulla subnet e sulla NIC, e leggo le regole in ordine di priorità. Con una VM in UD06 si può confermare con effective security rules e IP Flow Verify
- correzione minima: togliere o correggere la regola che blocca, oppure aggiungere un Allow limitato a quella origine e porta con un numero più basso del Deny. Non si elimina l'NSG intero perché toglierebbe tutta la protezione

Per completare la catena, un problema di route si vede quando l'NSG permette il traffico ma il pacchetto va verso un next hop sbagliato. Si controlla la route table associata alla subnet, che oggi è vuota, e le route effettive con la VM. Un servizio non in ascolto invece si vede quando rete e NSG sono a posto ma sulla porta non risponde nessuno. Questi due casi oggi non sono provabili perché non c'è una VM né un'applicazione.

## Cleanup e risultato finale

- regola autonoma rimossa: Deny-Web-Postgres-Auto eliminata, nell'NSG resta solo Allow-Web-Postgres 300
- cleanup verificato: ho eliminato il resource group rg-cea-network-4756a8 con VNet, NSG e le due NIC. az group exists ha restituito false e non risultano più resource group rg-cea
- hash abbreviato e messaggio del commit: 635537f Completa laboratorio reti Azure e NSG
