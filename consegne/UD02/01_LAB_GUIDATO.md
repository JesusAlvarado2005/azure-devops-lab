# Consegna UD02 — Laboratorio guidato

## Contesto verificato

- Azure Portal accessibile: sì, ho creato dal portale il resource group, la VNet e lo storage account
- Azure CLI autenticata: sì, uso Azure CLI 2.83.0 in Ubuntu WSL e az account show mostra Azure subscription 1 attiva e predefinita
- sottoscrizione corretta verificata senza pubblicarne l'ID: az account list mostra una sola sottoscrizione, quindi non ho dovuto usare az account set
- località scelta e motivo: italynorth, perché compare tra le località disponibili, i provider Microsoft.Network e Microsoft.Storage sono già registrati e il portale ha accettato tutte le creazioni

## Ambiente creato

| Elemento | Nome tecnico | Tipo | Località | Scopo |
|---|---|---|---|---|
| Resource group | rg-cea-ud02-2121b8ad | Resource group | italynorth | contiene tutto il laboratorio e viene eliminato alla fine |
| Rete virtuale | vnet-cea-ud02 con subnet snet-app | Virtual network | italynorth | rete 10.20.0.0/16 con subnet 10.20.1.0/24 |
| Storage account | stcea2121b8ad | StorageV2 Standard_LRS | italynorth | account vuoto per vedere le impostazioni di sicurezza, senza container e senza dati |

Su tutte e tre le risorse ho messo gli stessi tag: course cloud-engineer-academy, unit UD02, environment lab e deleteAfter 2026-10-15.

## Decisioni e verifiche

Ho messo VNet e storage nello stesso resource group perché vengono create e eliminate insieme. Così con un solo az group delete tolgo tutto e con un solo az group exists controllo che non sia rimasto niente. Il resource group non passa i suoi tag alle risorse, per questo li ho aggiunti a mano su ognuna e li ho ritrovati con az resource list.

Azure si occupa dell'infrastruttura fisica e del funzionamento del servizio. A me restano la scelta di sottoscrizione e località, gli indirizzi della rete, le impostazioni di sicurezza dello storage e il cleanup. Sullo storage ho controllato con la CLI che ci fossero HTTPS obbligatorio, TLS minimo 1.2 e accesso pubblico ai blob disattivato. Le chiavi non le ho mai lette.

Il suffisso 2121b8ad l'ho generato con date, sha256sum e cut. Serve soprattutto per lo storage, che deve avere un nome unico in tutto Azure, e non contiene dati personali. I tag servono a capire di chi è l'ambiente e quando va tolto, ma da soli non cancellano niente.

Quando ho caricato il file delle variabili con source ho avuto l'errore bad substitution. Avevo scritto il suffisso anche al posto di LAB_SUFFIX dentro le parentesi graffe e avevo lasciato i simboli minore e maggiore. Ho capito che il valore va scritto solo nella riga di LAB_SUFFIX e che le altre righe lo richiamano da sole. Dopo la correzione tutte le variabili si sono caricate.

Nel portale, nella pagina Resources del resource group, ho visto le stesse due risorse che mi dava az resource list, con località, tag e stato uguali. Nella JSON View c'è tutta la risorsa con l'ID completo, che ha la stessa struttura dell'output jsonc della CLI. La differenza più chiara l'ho vista sulla subnet. Nel portale l'indirizzo 10.20.1.0/24 si vede subito, mentre con la query del lab la CLI mi dava null. Interrogando direttamente la subnet ho scoperto che il valore si trova nel campo addressPrefixes. Per me il portale è più comodo per esplorare una risorsa nuova, la CLI è meglio quando so già cosa cercare e voglio ripetere lo stesso controllo.

In Cloud Shell, aperto senza storage, la CLI vede la stessa sottoscrizione di WSL ma ha una versione più nuova, la 2.90.0. È un ambiente separato, gestito da Azure. In PowerShell il modulo Az.Resources è alla versione 10.2.0 e Get-AzContext mostra già Azure subscription 1. Con Get-AzResourceGroup ho letto il gruppo del laboratorio e ho controllato che nome, località e stato fossero uguali a quelli della CLI.

Comandi principali che ho usato per le verifiche:

```bash
az group show --name "$LAB_RG" --query "{Name:name,Location:location,State:properties.provisioningState,Tags:tags}" --output jsonc
az network vnet show --resource-group "$LAB_RG" --name "$LAB_VNET" --query "{Name:name,Location:location,Address:addressSpace.addressPrefixes,Subnets:subnets[].{Name:name,Prefix:addressPrefix},Tags:tags}" --output jsonc
az storage account show --resource-group "$LAB_RG" --name "$LAB_STORAGE" --query "{Name:name,Location:location,Kind:kind,Sku:sku.name,HttpsOnly:enableHttpsTrafficOnly,MinimumTls:minimumTlsVersion,PublicBlobAccess:allowBlobPublicAccess,State:provisioningState,Tags:tags}" --output jsonc
az resource list --resource-group "$LAB_RG" --query "[].id" --output tsv | sed -E 's#/subscriptions/[^/]+#/subscriptions/<omitted>#'
```

## Cleanup

- operazione di eliminazione: az group delete con --yes e --no-wait alle 14:25, dopo aver ricontrollato nome, tag e risorse del gruppo
- controllo utilizzato: az group wait --deleted e poi az group exists
- risultato finale: alle 14:38 az group exists ha restituito false, quindi il gruppo con VNet e storage non esiste più
- eventuale anomalia e soluzione: nessuna, prima dei controlli finali ho rifatto az login --use-device-code

## Rilevanza professionale

Fare l'inventario prima del cleanup mi permette di sapere esattamente cosa sto per eliminare. Se nel gruppo ci fosse qualcosa che non ho creato io me ne accorgerei prima di cancellarlo. I tag uguali su ogni risorsa fanno capire a chiunque a cosa serve l'ambiente e quando va tolto. Il file delle variabili tiene tutti i nomi in un posto solo, così gli stessi comandi si possono rifare uguali. Infine il cleanup lo considero finito solo quando az group exists risponde false, non quando torna il prompt. In questo modo anche un'altra persona può ripetere la procedura e controllare che sia andata bene.


## Registro cronologico delle evidenze

Gli orari sono in ora italiana. Quelli delle creazioni nel portale li ho presi dall'Activity Log del resource group.

| Data/ora | Fase e contesto | Comando o pagina | Risultato reale ripulito | Interpretazione / passo successivo |
|---|---|---|---|---|
| 13/10 mattina | 1, WSL Bash | pwd, git status, ls dei modelli | percorso /home/jj_yts/workspace/azure-devops-lab, quattro modelli presenti | sono nel repository personale giusto. I materiali del corso sono in azure-devops-k8s-01 e non in corso-azure-devops |
| 13/10 mattina | 2, WSL Bash | az version, az account show, az account list | CLI 2.83.0, Azure subscription 1 Enabled e predefinita, una sola sottoscrizione | CLI funzionante e già autenticata |
| 13/10 mattina | 3, WSL Bash | az account list-locations, az provider show | italynorth presente, Microsoft.Network e Microsoft.Storage Registered | posso usare italynorth, nessun provider da registrare |
| 13/10 mattina | 4, WSL Bash e VS Code | source del file variabili | bad substitution alla riga 3 | suffisso scritto nel posto sbagliato, corretto il file |
| 13/10 mattina | 4, WSL Bash | source, printf delle variabili, controllo nome storage | nomi corretti, cleanup entro 2026-10-15, nome storage valido | variabili caricate dal file |
| 13/10 12:35 | 5, Portal | Resource groups, Create con 4 tag | gruppo creato, az group show dà italynorth, Succeeded e 4 tag | resource group pronto |
| 13/10 12:39 | 6, Portal | Virtual networks, Create | prima validazione senza creazione | ho ricontrollato i campi e ripreso |
| 13/10 12:48 | 6, Portal e WSL Bash | Review + create, az network vnet show | VNet 10.20.0.0/16 e subnet snet-app create. Nella query la subnet risulta null, con az network vnet subnet show trovo 10.20.1.0/24 | VNet e subnet corrette |
| 13/10 12:57 | 7, Portal e WSL Bash | Storage accounts Create, az storage account show | StorageV2, Standard_LRS, HTTPS obbligatorio, TLS 1.2, blob pubblici disattivati, Succeeded, 4 tag | storage creato con le impostazioni richieste, nessun dato caricato |
| 13/10 13:03 | 8, WSL Bash | az resource list in tabella e jsonc | vnet-cea-ud02 e stcea2121b8ad, italynorth, UD02, 2026-10-15 | due risorse, la subnet non compare perché è dentro la VNet |
| 13/10 13:03 | 8, WSL Bash | az resource list degli ID con sed | /subscriptions/<omitted>/resourceGroups/rg-cea-ud02-2121b8ad/providers/Microsoft.Network/virtualNetworks/vnet-cea-ud02 e lo stesso per lo storage | ID salvati senza l'ID della sottoscrizione |
| 13/10 pomeriggio | 9, Portal | Resources e JSON View del gruppo | 2 risorse, italynorth, 4 tag, Succeeded | uguale a quanto visto con la CLI |
| 13/10 pomeriggio | 9A, Cloud Shell Bash | az version, az account show | CLI 2.90.0, Azure subscription 1 Enabled | stessa sottoscrizione, ambiente diverso da WSL |
| 13/10 pomeriggio | 9A, Cloud Shell PowerShell | Get-Module Az.Resources, Get-AzContext, Get-AzResourceGroup | Az.Resources 10.2.0, Azure subscription 1, gruppo letto correttamente | contesto giusto, Set-AzContext non necessario |
| 13/10 pomeriggio | 10, WSL Bash | git status --short, git diff | modificati solo i due file della consegna, nessun dato sensibile | file pronti per il commit |
| 13/10 pomeriggio | 11 | nessun comando | non eseguito perché non ci sono stati errori | la parte 11A serve per l'autonomo |
| 13/10 14:25 | 12, WSL Bash | az group show, az resource list | rg-cea-ud02-2121b8ad con UD02 e lab, solo VNet e storage | niente di sconosciuto, posso eliminare |
| 13/10 14:25 | 12, WSL Bash | az group delete --yes --no-wait | comando terminato senza errori | richiesta inviata, da verificare |
| 13/10 14:38 | 12, WSL Bash | az login --use-device-code | login completato su Azure subscription 1 | sessione rinnovata |
| 13/10 14:38 | 12, WSL Bash | az group wait --deleted, az group exists | wait terminato, exists false | cleanup completato |

Riporta le proprietà e l'inventario prima dell'eliminazione, poi richiesta, attesa e assenza finale. Per il guidato includi il confronto CLI/Azure PowerShell; per l'autonomo motivazioni e requisiti. Nella conferma finale cita un commit già pubblicato, non l'hash del documento che stai ancora modificando.
