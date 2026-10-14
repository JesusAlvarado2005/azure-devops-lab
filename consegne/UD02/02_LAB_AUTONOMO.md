# Consegna UD02 — Laboratorio autonomo

## Requisito e piano

- requisito interpretato: serve un ambiente di sviluppo temporaneo con una rete isolata e uno storage vuoto, separato dagli altri laboratori e da eliminare tutto insieme alla fine
- risorse previste: un resource group dedicato, una VNet con una subnet e uno storage account
- nomi e tag scelti: resource group rg-cea-ud02-auto-b2628df9, VNet vnet-cea-auto con spazio 10.30.0.0/16, subnet snet-workload con 10.30.10.0/24, storage stceaautob2628df9. Tag course cloud-engineer-academy, unit UD02, environment dev, scenario autonomous e deleteAfter 2026-10-15
- verifiche preliminari: sottoscrizione Azure subscription 1 attiva e predefinita, provider Microsoft.Network e Microsoft.Storage registrati, az group exists sul nuovo gruppo false e nome dello storage disponibile

Uso un resource group dedicato perché segna il confine del ciclo di vita dell'ambiente: tutto quello che crea lo scenario sta lì dentro, e alla fine lo elimino con un solo comando senza toccare altro. Come località ho tenuto italynorth, già verificata nel guidato e ripresa dal file delle variabili, così non devo ripetere controlli su una regione nuova. La VNet è una rete logica in cui in futuro potranno stare i componenti da provare. Lo storage account invece è uno spazio per i dati, raggiungibile tramite un endpoint del servizio, e per questo ha bisogno di impostazioni di sicurezza proprie. I tag li metto su ogni risorsa perché il resource group non li passa da solo. Dicono a chiunque guardi la sottoscrizione a che corso appartiene l'ambiente, che è di sviluppo, che è lo scenario autonomo e quando va tolto. Il cleanup lo considero dimostrato solo quando az group exists sul gruppo risponde false.

## Svolgimento

Ho preparato i nomi con variabili AUTO separate da quelle del guidato, così il file 01_VARIABILI_LAB.sh è rimasto invariato. Dal file ho ripreso solo la località.

```bash
AUTO_SUFFIX="$(date +%s%N | sha256sum | cut -c1-8)"
AUTO_RG="rg-cea-ud02-auto-${AUTO_SUFFIX}"
AUTO_VNET="vnet-cea-auto"
AUTO_SUBNET="snet-workload"
AUTO_STORAGE="stceaauto${AUTO_SUFFIX}"
AUTO_DELETE_AFTER="$(date -d '+2 days' +%F)"
source consegne/UD02/01_VARIABILI_LAB.sh
AUTO_LOCATION="$LAB_LOCATION"
```

Questa volta ho creato tutto con la CLI, nell'ordine resource group, VNet e storage, perché la VNet e lo storage devono stare dentro un gruppo che esiste già.

```bash
az group create --name "$AUTO_RG" --location "$AUTO_LOCATION" --tags course=cloud-engineer-academy unit=UD02 environment=dev scenario=autonomous deleteAfter="$AUTO_DELETE_AFTER" --output table
az network vnet create --resource-group "$AUTO_RG" --name "$AUTO_VNET" --location "$AUTO_LOCATION" --address-prefixes 10.30.0.0/16 --subnet-name "$AUTO_SUBNET" --subnet-prefixes 10.30.10.0/24 --tags course=cloud-engineer-academy unit=UD02 environment=dev scenario=autonomous deleteAfter="$AUTO_DELETE_AFTER" --output jsonc
az storage account create --resource-group "$AUTO_RG" --name "$AUTO_STORAGE" --location "$AUTO_LOCATION" --kind StorageV2 --sku Standard_LRS --https-only true --min-tls-version TLS1_2 --allow-blob-public-access false --tags course=cloud-engineer-academy unit=UD02 environment=dev scenario=autonomous deleteAfter="$AUTO_DELETE_AFTER" --output jsonc
```

Poi ho verificato ogni risorsa con comandi di sola lettura.

```bash
az group show --name "$AUTO_RG" --query "{Name:name,Location:location,State:properties.provisioningState,Tags:tags}" --output jsonc
```
Il gruppo è in italynorth, Succeeded, con i cinque tag.

```bash
az network vnet show --resource-group "$AUTO_RG" --name "$AUTO_VNET" --query "{Address:addressSpace.addressPrefixes,Subnets:subnets[].{Name:name,Prefix:addressPrefix},Tags:tags}" --output jsonc
```
La VNet ha spazio 10.30.0.0/16 e contiene snet-workload con 10.30.10.0/24, quindi la subnet sta dentro la rete. Ci sono tutti e cinque i tag. Qui il prefisso compare nel campo addressPrefix, mentre nel guidato la subnet creata dal portale lo aveva in addressPrefixes.

```bash
az storage account show --resource-group "$AUTO_RG" --name "$AUTO_STORAGE" --query "{Kind:kind,Sku:sku.name,HttpsOnly:enableHttpsTrafficOnly,MinimumTls:minimumTlsVersion,PublicBlobAccess:allowBlobPublicAccess,State:provisioningState,Tags:tags}" --output jsonc
```
Lo storage è StorageV2, Standard_LRS, HttpsOnly true, MinimumTls TLS1_2, PublicBlobAccess false, Succeeded, con i cinque tag. Le chiavi non le ho lette.

```bash
az resource list --resource-group "$AUTO_RG" --query "[].{Name:name,Type:type,Location:location,Unit:tags.unit,Scenario:tags.scenario}" --output table
```
```text
Name               Type                               Location    Unit    Scenario
vnet-cea-auto      Microsoft.Network/virtualNetworks  italynorth  UD02    autonomous
stceaautob2628df9  Microsoft.Storage/storageAccounts  italynorth  UD02    autonomous
```

```bash
az resource list --resource-group "$AUTO_RG" --query "[].id" --output tsv | sed -E 's#/subscriptions/[^/]+#/subscriptions/<omitted>#'
```
```text
/subscriptions/<omitted>/resourceGroups/rg-cea-ud02-auto-b2628df9/providers/Microsoft.Network/virtualNetworks/vnet-cea-auto
/subscriptions/<omitted>/resourceGroups/rg-cea-ud02-auto-b2628df9/providers/Microsoft.Storage/storageAccounts/stceaautob2628df9
```

## Diagnosi

- errore o anomalia analizzata: al primo printf di controllo la riga Location era vuota, mentre gli altri nomi erano corretti
- ipotesi: AUTO_LOCATION prende il valore da LAB_LOCATION, che però in quel terminale non era ancora caricata
- controllo: ho ripercorso i comandi e ho visto che avevo assegnato AUTO_LOCATION prima di fare source del file delle variabili
- correzione: ho lanciato source consegne/UD02/01_VARIABILI_LAB.sh e poi di nuovo AUTO_LOCATION="$LAB_LOCATION"
- verifica successiva: il printf ha mostrato Location italynorth. Ho controllato i nomi prima di qualsiasi creazione, quindi su Azure non è stato creato niente con una variabile vuota

## Cleanup e consegna

- risorse eliminate: il resource group rg-cea-ud02-auto-b2628df9 con dentro vnet-cea-auto e stceaautob2628df9. Prima di eliminarlo ho ricontrollato nome, tag UD02 e autonomous e inventario
- controllo finale: subito dopo il delete az group exists dava ancora true perché l'eliminazione era in corso. Dopo az group wait --deleted, terminato in circa 30 secondi, az group exists ha restituito false
- hash abbreviato e messaggio del commit: 4b45d90 Completa lo scenario Azure autonomo


## Registro cronologico delle evidenze

Gli orari sono in ora italiana. Quelli delle creazioni li ho ricontrollati nell'Activity Log del resource group.

| Data/ora | Fase e contesto | Comando o pagina | Risultato reale ripulito | Interpretazione / passo successivo |
|---|---|---|---|---|
| 13/10 17:07 | contesto, terminale Fedora | az version, az account show, az account list | CLI 2.83.0, Azure subscription 1 Enabled e predefinita, una sola sottoscrizione | posso procedere sulla sottoscrizione prevista |
| 13/10 17:09 | contesto, terminale Fedora | az account list-locations su italynorth | italynorth Italy North presente | località confermata |
| 13/10 17:12 | contesto, terminale Fedora | az provider show Microsoft.Network | non eseguito, avevo incollato anche i backtick del blocco di codice e zsh restava in attesa | annullato e ripetuto pulito |
| 13/10 17:30 | contesto, terminale Fedora | az provider show Network e Storage | Microsoft.Network Registered, Microsoft.Storage Registered | nessuna registrazione necessaria |
| 13/10 17:47 | nomi, terminale Fedora | variabili AUTO e printf | Location vuota, gli altri nomi corretti | variabile caricata nell'ordine sbagliato, vedi Diagnosi |
| 13/10 17:48 | nomi, terminale Fedora | source del file guidato, AUTO_LOCATION, printf | italynorth, rg-cea-ud02-auto-b2628df9, vnet-cea-auto, snet-workload, stceaautob2628df9 | nomi pronti |
| 13/10 17:49 | controlli preliminari, terminale Fedora | az group exists, az storage account check-name | false, NameAvailable True | gruppo assente e nome storage libero |
| 13/10 17:52 | creazione, terminale Fedora | az group create | gruppo creato in italynorth con 5 tag | posso creare le risorse dentro il gruppo |
| 14/10 09:12 | creazione, terminale Fedora | az network vnet create | VNet 10.30.0.0/16 con snet-workload 10.30.10.0/24, Succeeded | rete creata |
| 14/10 09:15 | creazione, terminale Fedora | az storage account create | terminato senza errori | storage creato, da verificare |
| 14/10 09:18 | verifica, terminale Fedora | az group show, az network vnet show | italynorth, Succeeded, prefissi giusti, 5 tag | gruppo e rete conformi |
| 14/10 09:19 | verifica, terminale Fedora | az storage account show | StorageV2, Standard_LRS, HTTPS true, TLS1_2, blob pubblici false, 5 tag | storage conforme |
| 14/10 09:19 | inventario, terminale Fedora | az resource list in tabella | vnet-cea-auto e stceaautob2628df9, italynorth, UD02, autonomous | solo le due risorse dello scenario |
| 14/10 09:23 | inventario, terminale Fedora | az resource list degli ID con sed | ID con /subscriptions/<omitted>/ | ID pronti per la relazione |
| 14/10 09:26 | cleanup, terminale Fedora | printf di AUTO_RG, az group show, az resource list | rg-cea-ud02-auto-b2628df9 con UD02 e autonomous, solo vnet-cea-auto e stceaautob2628df9 | variabile non vuota e gruppo giusto, posso eliminare |
| 14/10 09:27 | cleanup, terminale Fedora | az group delete --yes --no-wait | prompt tornato senza errori | richiesta inviata |
| 14/10 09:27 | cleanup, terminale Fedora | az group exists | true | eliminazione ancora in corso, aspetto |
| 14/10 09:28 | cleanup, terminale Fedora | az group wait --deleted | terminato dopo circa 33 secondi | eliminazione finita |
| 14/10 09:28 | cleanup, terminale Fedora | az group exists | false | il gruppo non esiste più, cleanup completato |

Riporta le proprietà e l'inventario prima dell'eliminazione, poi richiesta, attesa e assenza finale. Per il guidato includi il confronto CLI/Azure PowerShell; per l'autonomo motivazioni e requisiti. Nella conferma finale cita un commit già pubblicato, non l'hash del documento che stai ancora modificando.
