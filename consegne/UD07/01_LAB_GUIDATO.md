# UD07 — Consegna laboratorio guidato

## CLI

- prima esecuzione script: il resource group rg-ud07-cli-test non esisteva e lo script ha stampato Il Resource Group non esiste: lo creo, poi ha aggiornato i tag e lo stato finale era Succeeded
- seconda esecuzione: lo script ha stampato Il Resource Group esiste già: lo riutilizzo, ha aggiornato di nuovo i tag e lo stato finale era ancora Succeeded
- comportamento idempotente: lo script prima controlla con az group exists e poi decide se creare o riusare. Eseguito due volte arriva allo stesso stato senza errori e senza creare doppioni. Alla fine il gruppo ha i tag ManagedBy CLI, State Verified e UD 07
- esempio JMESPath: az group show con --query "{Name:name,Location:location,Provisioning:properties.provisioningState}" mostra solo nome, region e stato invece di tutto il JSON
- quando usare `tsv`: quando mi serve un valore da riusare in una variabile. --query name con -o tsv stampa rg-ud07-monitor senza virgolette mentre con -o json stampa "rg-ud07-monitor" con le virgolette. Per questo ho preso customerId del workspace e ID dello storage account con tsv

## PowerShell

- `Get-AzContext` verificato: sì, sottoscrizione Azure subscription 1
- Resource Group test: rg-ud07-ps-test in westeurope con i tag ManagedBy PowerShell, State Verified e UD 07
- prima esecuzione: il gruppo non esisteva e la sequenza l'ha creato con i tag
- seconda esecuzione: il gruppo esisteva già e la sequenza l'ha riusato aggiornando solo i tag
- perché il controllo `if` è utile: prima di creare controllo se il gruppo esiste già. Così posso rieseguire la sequenza senza errori e senza doppioni, ed è la stessa logica idempotente dello script CLI. In PowerShell però il risultato di Get-AzResourceGroup è un oggetto e leggo direttamente le sue proprietà

## Log Analytics

- workspace: law-ud07-1041 nel resource group rg-ud07-monitor con retention di 30 giorni
- regione: northeurope. In westeurope la creazione è stata rifiutata con RequestDisallowedByAzure perché la region non accettava nuovi clienti e nell'Activity Log risulta anche un 'deny' Policy action Failed. Ho cambiato LAB_LOCATION in northeurope e la creazione è riuscita. Alla prima creazione la CLI ha registrato da sola il resource provider Microsoft.OperationalInsights
- query `print`: print Course='AZ-104', UD=7, Status='OK' restituisce una riga con AZ-104, 7 e OK
- query `datatable`: tabella inventata con tre componenti API DB e WEB raggruppata con summarize count() by Status, il risultato è OK 2 e WARN 1
- risultato sintetico: il workspace risponde alle query KQL anche senza log reali, perché print e datatable creano i dati dentro la query. Il comando az monitor log-analytics query all'inizio falliva con Pip failed with status code 1. Con --debug si vedeva No module named pip, cioè sul mio Fedora mancava pip che la CLI usa per installare l'estensione log-analytics. Ho installato python3-pip e poi l'estensione log-analytics 1.0.0b3 che esiste solo in preview

## Activity Log

- evento osservato: Create Workspace sul resource group rg-ud07-monitor. Si vedono i primi tentativi in westeurope con Started e Failed e il 'deny' Policy action, poi il tentativo in northeurope con Started, Accepted e Succeeded
- status: Succeeded per la creazione finale del workspace
- timestamp: 2026-10-20T15:40:17Z
- dati personali omessi: sì

## Diagnostic Setting

- esito: creata ud07-activity-to-law a livello di sottoscrizione con le categorie Administrative, Policy, Alert, ServiceHealth e ResourceHealth. Dal portale la creazione dava errore e l'ho creata da CLI con az monitor diagnostic-settings subscription create, poi ho verificato con show che punti al workspace
- destinazione: Log Analytics workspace law-ud07-1041
- AzureActivity disponibile: sì, ma solo il giorno dopo e solo in parte
- fallback usato, se necessario: la query su AzureActivity non ha restituito righe neanche dopo circa 15 minuti, perché arrivano solo gli eventi successivi alla diagnostic setting e l'ingestion richiede tempo. Per gli eventi ho usato az monitor activity-log list che legge direttamente l'Activity Log. Una tabella vuota appena dopo la configurazione non vuol dire che la configurazione sia sbagliata

Il giorno dopo nella tabella AzureActivity c'erano 3 righe, tutte eventi di Resource Health del resource group rg-ud06-compute del giorno prima con stato Active e Updated. Gli eventi Administrative della UD07 come il tag sullo storage account non erano ancora arrivati. Questo conferma che l'ingestion non è immediata e che i dati arrivano nel workspace con tempi diversi a seconda della categoria.

## Metrics

- Storage Account: stud0792510358 StorageV2 Standard_LRS creato in northeurope come il workspace perché LAB_LOCATION era già cambiata
- metrica: UsedCapacity
- unità: Bytes
- aggregazione: Average con intervallo di un'ora
- punto dati disponibile: no
- interpretazione: con list-definitions ho visto prima quali metriche esistono, per esempio Transactions in Count con aggregazione Total e UsedCapacity in Bytes con Average. Per UsedCapacity è comparso solo il timestamp senza valore perché l'account era appena stato creato e questa metrica viene calcolata circa una volta all'ora. Un valore mancante non vuol dire capacità zero

## Alert

- nome: alert-ud07-storage-transactions
- scope corretto: sì, è lo storage account stud0792510358
- condition: metrica Transactions con aggregazione Total valutata ogni 5 minuti su una finestra di 5 minuti. Dal portale è rimasta la soglia dinamica invece della soglia statica Greater than 0 richiesta dalla guida
- severity: 3 Informational
- Action Group: assente. ag-ud07 esiste ed è abilitato con short name UD07AG, ma non ha destinatari perché non ho voluto mettere l'email personale nel laboratorio e non è collegato alla regola
- perché non è necessario che sia Fired: Enabled vuol dire che la regola è attiva e viene valutata, Fired vuol dire che la condizione è stata davvero soddisfatta. Qui serve verificare che la regola sia costruita bene su scope, metrica, condizione e severity. Se resta Enabled senza scattare vuol dire solo che la condizione non si è verificata

## Correlazione

- modifica osservata: ho aggiunto allo storage account il tag State=Changed con az storage account update alle 17:59 ora italiana
- evento Activity Log: Create/Update Storage Account con Started e Succeeded alle 15:59:58 UTC. Subito dopo la modifica nel list comparivano solo gli eventi della creazione delle 15:52 e l'evento del tag è comparso qualche minuto dopo
- la correlazione prova causalità?: no
- motivazione: l'Activity Log mi dice che c'è stata un'operazione di update sullo storage account in quel momento e con quale esito, ma non dice cosa ho cambiato né se quella modifica ha effetti su metriche o alert. Il tempo vicino è solo correlazione. Per parlare di causa servirebbero altre prove, come vedere il dettaglio della modifica, una metrica collegata o il comportamento che torna normale annullandola
