# UD07 — Consegna laboratorio autonomo

## 1. Script CLI idempotente

- logica: az group exists, se false creo il gruppo altrimenti lo riuso, poi metto i tag ManagedBy=Autonomo e UD=07 e mostro nome location e stato
- prima esecuzione: Il Resource Group non esiste: lo creo
- seconda esecuzione: Il Resource Group esiste già: lo riutilizzo
- verifica: tutte e due le volte rg-ud07-auto northeurope Succeeded con gli stessi tag

## 2. PowerShell equivalente

- controllo esistenza: Get-AzResourceGroup con -ErrorAction SilentlyContinue, se non c'è creo con New-AzResourceGroup
- modifica: Set-AzResourceGroup con i tag ManagedBy=Autonomo e UD=07
- output: prima lo creo poi lo riutilizzo, tutte e due le volte rg-ud07-auto-ps northeurope Succeeded

## 3. Activity Log

- operazione: Update resource group su rg-ud07-auto
- status: Started e poi Succeeded
- timestamp: 2026-10-21T08:10:46Z

## 4. KQL

1. 2 righe, una per OK e una per WARN, tutte e due con 2 richieste
2. WARN con media 470 ms contro 150 ms di OK
3. perché summarize raggruppa le righe per Status e calcola conteggio e media, quindi da 4 righe una per richiesta passo a 2 righe una per stato e perdo il dettaglio del singolo componente

## 5. Metrics

- metrica: Transactions dello storage account stud0792510358
- unità: Count
- aggregazione: Total che è quella primaria, con intervallo di un'ora sulle ultime 24 ore
- dato presente: sì
- interpretazione: 4 transazioni nell'ora delle 15:51 UTC di ieri quando ho creato e modificato l'account, poi sempre 0. L'account non viene usato

## 6. Alert

- scope: storage account stud0792510358
- condition: Transactions Total GreaterThan con soglia dinamica a sensibilità bassa, non la soglia statica 0 della guida
- severity: 3 Informational
- evaluation frequency: ogni 5 minuti su una finestra di 5 minuti
- Action Group: assente, ag-ud07 esiste ma non è collegato
- Enabled vs Fired: la regola è Enabled cioè attiva e valutata. Fired vuol dire che la condizione si è verificata e qui non succede perché le transazioni sono quasi sempre 0. Una regola configurata bene può non scattare mai

## 7. Guasto amministrativo

- sintomo: az group show su rg-ud07-NON-ESISTE fallisce
- errore: ResourceGroupNotFound, Resource group 'rg-ud07-NON-ESISTE' could not be found
- ipotesi: nome sbagliato oppure sottoscrizione sbagliata
- controllo: az account show per la sottoscrizione e az group list per vedere i nomi veri
- correzione: usare il nome giusto rg-ud07-monitor, senza creare il gruppo che non esiste
- verifica: az group show su rg-ud07-monitor risponde con Succeeded

## 8. Runbook

**RUNBOOK — Risorsa Azure non trovata o contesto errato**

### Sintomo
un comando su un resource group o una risorsa dà ResourceGroupNotFound o ResourceNotFound

### Contesto
Azure CLI con login fatto, serve sapere su quale sottoscrizione si lavora

### Controlli
1. account e sottoscrizione giusti
2. nome del resource group
3. nome o resource ID della risorsa
4. Activity Log per vedere se è stata eliminata o rinominata

### Comandi
- az account show --query name -o tsv
- az group exists --name NOME
- az group list --query "[].name" -o table
- az resource list --resource-group NOME -o table
- az monitor activity-log list --resource-group NOME --offset 24h --query "[].{Time:eventTimestamp,Op:operationName.localizedValue,Status:status.localizedValue}" -o table

### Interpretazione
- sottoscrizione diversa da quella attesa: il problema è il contesto
- exists false e il nome non c'è nella lista: nome sbagliato o gruppo non esistente
- exists true ma la risorsa non c'è: nome o ID della risorsa sbagliato
- nell'Activity Log c'è un Delete: la risorsa è stata eliminata

### Correzione minima
az account set sulla sottoscrizione giusta oppure usare il nome giusto. Non creare la risorsa solo per far sparire l'errore

### Verifica
rieseguire il comando che falliva e controllare che risponda

### Cleanup
eliminare solo i resource group di test creati durante la prova dopo aver controllato tag e contenuto

## 9. Cleanup

- rg-ud07-auto: eliminato con az group delete, az group exists dà false
- rg-ud07-auto-ps: era vuoto con i tag ManagedBy=Autonomo e UD=07, eliminato e az group exists dà false. rg-ud07-monitor resta per la verifica
