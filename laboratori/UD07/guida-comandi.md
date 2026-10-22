# Guida comandi — UD07

Amministrazione ripetibile e monitoraggio: script idempotenti, PowerShell, Activity Log, Log Analytics con KQL, diagnostic setting, metriche e alert. Le basi sono in `laboratori/UD02/guida-comandi.md`.

---

## 1. PREPARO

```bash
export COURSE_UD07="$HOME/workspace/azure-devops-k8s-01/UD07/partecipanti"   # non il percorso di esempio della guida
export LAB_REPO="$HOME/workspace/azure-devops-lab"
export LAB_RG="rg-ud07-monitor"
export LAB_LOCATION="northeurope"          # westeurope rifiutava il workspace
export LAW="law-ud07-$RANDOM"
export STG="stud07$(date +%s | tail -c 9)"
export ALERT_NAME="alert-ud07-storage-transactions"
export AG_NAME="ag-ud07"
export DIAG_NAME="ud07-activity-to-law"
```

⚠️ Su Fedora `grep` è un alias di **ripgrep**: `grep -E` non funziona, usare `rg 'A|B'` oppure `command grep -E`.

---

## 2. SCRIPT IDEMPOTENTE (bash)

```bash
RG="rg-ud07-auto"
LOCATION="northeurope"

EXISTS=$(az group exists --name "$RG")

if [ "$EXISTS" = "false" ]; then             # spazi dentro [ ] obbligatori
  echo "Il Resource Group non esiste: lo creo."
  az group create --name "$RG" --location "$LOCATION" --output table
else
  echo "Il Resource Group esiste già: lo riutilizzo."
fi

az group update --name "$RG" --set tags.ManagedBy=Autonomo tags.UD=07 --output none
az group show --name "$RG" --query "{Name:name, Location:location, State:properties.provisioningState}" --output table
```

Eseguito due volte arriva allo **stesso stato**: la prima crea, la seconda riusa.

---

## 3. LO STESSO IN POWERSHELL

```powershell
$RgName = "rg-ud07-auto-ps"                  # NON $RG: in PowerShell $RG e $rg sono la stessa variabile
$rg = Get-AzResourceGroup -Name $RgName -ErrorAction SilentlyContinue

if (-not $rg) {
    New-AzResourceGroup -Name $RgName -Location "northeurope"
} else {
    Write-Output "Il Resource Group esiste già: lo riutilizzo."
}

Set-AzResourceGroup -Name $RgName -Tag @{ManagedBy = "Autonomo"; UD = "07"}
```

PowerShell restituisce **oggetti** (`$rg.Location`), la CLI restituisce **JSON** da filtrare con `--query`.

---

## 4. --query E --output

```bash
az group show --name "$LAB_RG" --query "{Name:name,Location:location,State:properties.provisioningState}" --output table
az group show --name "$LAB_RG" --query name --output tsv     # rg-ud07-monitor        → per le variabili
az group show --name "$LAB_RG" --query name --output json    # "rg-ud07-monitor"      → con le virgolette
```

---

## 5. LOG ANALYTICS E KQL

```bash
sudo dnf install -y python3-pip                              # senza pip la CLI non installa estensioni
az extension add --name log-analytics --allow-preview true

az monitor log-analytics workspace create --resource-group "$LAB_RG" --workspace-name "$LAW" --location "$LAB_LOCATION" --output table
export LAW_CUSTOMER_ID=$(az monitor log-analytics workspace show --resource-group "$LAB_RG" --workspace-name "$LAW" --query customerId --output tsv)

az monitor log-analytics query --workspace "$LAW_CUSTOMER_ID" --analytics-query "print Course='AZ-104', UD=7, Status='OK'" --output table
az monitor log-analytics query --workspace "$LAW_CUSTOMER_ID" \
  --analytics-query 'datatable(Component:string,Status:string,DurationMs:int)["WEB","OK",120,"API","OK",180,"DB","WARN",430,"API","WARN",510] | summarize Requests=count(), AvgDuration=avg(DurationMs) by Status | sort by AvgDuration desc' \
  --output table
```

La KQL non si scrive direttamente nel terminale: va dentro `--analytics-query` oppure nel portale in `Workspace → Logs`.

---

## 6. ACTIVITY LOG E DIAGNOSTIC SETTING

```bash
az monitor activity-log list --resource-group "$LAB_RG" --offset 2h --max-events 20 \
  --query "[].{Time:eventTimestamp,Operation:operationName.localizedValue,Status:status.localizedValue}" --output table

# l'Activity Log è della SOTTOSCRIZIONE, quindi anche la diagnostic setting
WS=$(az monitor log-analytics workspace show -g "$LAB_RG" -n "$LAW" --query id -o tsv)
az monitor diagnostic-settings subscription create --name "$DIAG_NAME" --location "$LAB_LOCATION" --workspace "$WS" \
  --logs '[{"category":"Administrative","enabled":true},{"category":"Policy","enabled":true},{"category":"Alert","enabled":true},{"category":"ServiceHealth","enabled":true},{"category":"ResourceHealth","enabled":true}]'
az monitor diagnostic-settings subscription list --query "value[].{name:name,logs:logs[?enabled].category}" -o json
```

> 💡 `AzureActivity` resta vuota per un po': l'ingestion richiede tempo e arrivano solo gli eventi **dopo** la diagnostic setting. Tabella vuota non vuol dire configurazione sbagliata.

---

## 7. METRICHE E ALERT

```bash
export STG_ID=$(az storage account show --resource-group "$LAB_RG" --name "$STG" --query id --output tsv)
az monitor metrics list-definitions --resource "$STG_ID" --query "[].{Metric:name.value,Unit:unit,Primary:primaryAggregationType}" --output table
az monitor metrics list --resource "$STG_ID" --metric Transactions --interval PT1H --aggregation Total --output table

az monitor metrics alert show --name "$ALERT_NAME" --resource-group "$LAB_RG" \
  --query "{Name:name,Enabled:enabled,Severity:severity,Freq:evaluationFrequency,Crit:criteria.allOf[0].criterionType,AG:actions}" --output jsonc
```

- **Enabled** = la regola viene valutata. **Fired** = la condizione si è verificata
- dal portale la soglia di default è **dinamica**: per `Total > 0` scegliere Static
- l'Action Group dice **cosa fare** (mail, webhook), l'alert rule **quando**

---

## 8. ELIMINO E CONFERMO

```bash
az monitor diagnostic-settings subscription delete --name "$DIAG_NAME" --yes   # NON sta nel resource group
az group delete --name rg-ud07-cli-test --yes
az group delete --name rg-ud07-ps-test --yes
az group delete --name "$LAB_RG" --yes
az group list --query "[?contains(name, 'ud07')].name" --output table          # atteso: vuoto
```

---

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `cp: impossibile eseguire stat` | `COURSE_UD07` col percorso di esempio | percorso reale `azure-devops-k8s-01` |
| `RequestDisallowedByAzure` | westeurope non accetta nuovi clienti | `LAB_LOCATION=northeurope` |
| `Pip failed with status code 1` | manca `python3-pip` | `sudo dnf install -y python3-pip` |
| `rg: error parsing flag -E` | `grep` è ripgrep | `rg` oppure `command grep -E` |
| `zsh: parse error near \|` | KQL incollata nel terminale | metterla in `--analytics-query` |
| `ResourceGroupNotFound` | nome sbagliato o sottoscrizione sbagliata | `az account show`, `az group list` |
