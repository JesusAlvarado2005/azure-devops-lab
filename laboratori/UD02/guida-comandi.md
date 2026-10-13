# Guida comandi — UD02

Riassunto dei comandi usati nel laboratorio guidato, nell'ordine in cui li abbiamo usati.
Per ognuno: cosa fa e a cosa serve.

## Lo schema del laboratorio

```text
 1. Controllo dove sono         pwd, git status
 2. Controllo Azure CLI         az version, az account show
 3. Controllo località/provider az account list-locations, az provider show
 4. Preparo i nomi              file variabili + source
 5. Creo il resource group      portale  → verifico con az group show
 6. Creo la VNet                portale  → verifico con az network vnet show
 7. Creo lo storage             portale  → verifico con az storage account show
 8. Faccio l'inventario         az resource list
 9. Confronto portale/CLI       portale + Cloud Shell (Bash e PowerShell)
10. Controllo cosa pubblico     git status, git diff
12. Elimino e verifico          az group delete → wait → exists = false
```

L'idea di fondo: **creo dal portale, verifico dalla CLI, prima di eliminare faccio l'inventario, dopo l'eliminazione controllo che non sia rimasto niente.**

```text
Sottoscrizione  (Azure subscription 1)          → chi paga, confine amministrativo
└── Resource group  rg-cea-ud02-2121b8ad        → contenitore, si elimina tutto insieme
    ├── VNet  vnet-cea-ud02   10.20.0.0/16      → la rete
    │   └── Subnet  snet-app  10.20.1.0/24      → un pezzo della rete (risorsa "figlia")
    └── Storage  stcea2121b8ad                  → nome unico in tutto Azure
```

---

## 1. Terminale e Git

```bash
pwd
```
Mostra la cartella in cui ti trovi. Serve a essere sicuri di lavorare nel repository giusto.

```bash
git status
git status --short
```
Mostra quali file sono modificati (`M`) o nuovi e non ancora tracciati (`??`). Va lanciato sempre prima di un commit.

```bash
git diff -- consegne/UD02/01_LAB_GUIDATO.md
```
Mostra riga per riga cosa è cambiato in un file. Non mostra i file nuovi (`??`): quelli vanno aperti e letti.

```bash
mkdir -p consegne/UD02
```
Crea la cartella e anche quelle intermedie se mancano. Con `-p` non dà errore se la cartella esiste già.

```bash
ls -1 consegne/UD02/*.md
```
Elenca i file `.md` della cartella, uno per riga.

---

## 2. Azure CLI: controllo iniziale

```bash
az version
```
Mostra la versione di Azure CLI. Se risponde, la CLI è installata e funziona.

```bash
command -v az
type -a az
```
Servono solo se `az` dà problemi: indicano quale programma `az` viene eseguito e se ne esistono più copie.

```bash
az login --use-device-code
```
Fa il login ad Azure. Ti dà un codice da inserire in una pagina web, dove completi anche l'MFA. Si rifà quando la sessione scade. Il codice non va salvato da nessuna parte.

```bash
az account show --query "{Name:name,State:state,IsDefault:isDefault}" --output table
```
Mostra con quale sottoscrizione sta lavorando la CLI. Con `--query` scegli solo i campi che ti interessano, così l'ID della sottoscrizione non compare.

```bash
az account list --query "[].{Name:name,State:state,IsDefault:isDefault}" --output table
```
Elenca tutte le sottoscrizioni a cui hai accesso.

```bash
az account set --subscription "<NOME_O_ID>"
```
Cambia la sottoscrizione attiva. A noi non è servito perché ce n'è una sola.

---

## 3. Località e provider

```bash
az account list-locations --query "[?name=='italynorth'].{Name:name,DisplayName:displayName}" --output table
```
Controlla che la località `italynorth` esista per la tua sottoscrizione. `[?name=='italynorth']` è un filtro: tiene solo la riga con quel nome.

```bash
az provider show --namespace Microsoft.Network --query "{Namespace:namespace,State:registrationState}" --output table
```
Controlla se la sottoscrizione è abilitata a creare risorse di rete. Deve risultare `Registered`. Per lo storage si usa `Microsoft.Storage`.

```bash
az provider register --namespace Microsoft.Storage --wait
```
Abilita un provider. Si usa solo se risulta `NotRegistered`. Non installa niente sul PC.

---

## 4. Variabili e nomi

```bash
LAB_SUFFIX="$(date +%s%N | sha256sum | cut -c1-8)"
```
Genera un suffisso casuale di 8 caratteri. `date` dà l'ora attuale in nanosecondi, `sha256sum` la trasforma in un codice, `cut -c1-8` tiene i primi 8 caratteri. Il simbolo `|` (pipe) passa l'output di un comando a quello successivo.

```bash
export LAB_RG="rg-cea-ud02-${LAB_SUFFIX}"
```
Crea una variabile e la rende visibile ai comandi lanciati dalla shell. `${LAB_SUFFIX}` viene sostituito con il valore della variabile.

> ⚠️ L'errore `bad substitution` dipendeva da questo: dentro `${...}` va il **nome** della variabile, non il suo valore. `${2121b8ad}` è sbagliato, `${LAB_SUFFIX}` è giusto. E nella consegna `<SUFFISSO>` va sostituito tutto, comprese `< >`.

```bash
source consegne/UD02/01_VARIABILI_LAB.sh
```
Esegue il file nella shell attuale, così le variabili restano caricate. Va rifatto ogni volta che apri un terminale nuovo. Prima di farlo leggi il file, perché `source` esegue qualsiasi cosa ci sia scritta dentro.

```bash
printf 'RG: %s\nStorage: %s\n' "$LAB_RG" "$LAB_STORAGE"
```
Stampa testo formattato: ogni `%s` viene sostituito con le variabili in ordine, `\n` va a capo. Serve per controllare i valori caricati.

```bash
[[ "$LAB_STORAGE" =~ ^[a-z0-9]{3,24}$ ]] && echo valido
```
Controlla che il nome dello storage abbia solo minuscole e numeri, da 3 a 24 caratteri. `=~` confronta con un'espressione regolare.

---

## 5–7. Verificare le risorse create

```bash
az group exists --name "$LAB_RG"
```
Risponde `true` o `false`. Si usa **prima** di creare (deve essere `false`) e **dopo** aver eliminato (deve tornare `false`).

```bash
az group show --name "$LAB_RG" --query "{Name:name,Location:location,State:properties.provisioningState,Tags:tags}" --output jsonc
```
Mostra le proprietà del resource group. `provisioningState` deve essere `Succeeded`.

```bash
az network vnet show --resource-group "$LAB_RG" --name "$LAB_VNET" --query "{Address:addressSpace.addressPrefixes,Subnets:subnets[].name}" --output jsonc
```
Mostra la VNet, il suo spazio di indirizzi e le subnet.

```bash
az network vnet subnet show --resource-group "$LAB_RG" --vnet-name "$LAB_VNET" --name "$LAB_SUBNET" --query "{ps:addressPrefixes,state:provisioningState}" --output json
```
Mostra una singola subnet. L'abbiamo usato perché nella query della VNet il prefisso risultava `null`: il valore stava in `addressPrefixes` (plurale).

```bash
az storage account check-name --name "$LAB_STORAGE" --query "{Available:nameAvailable,Reason:reason}" --output jsonc
```
Controlla se il nome dello storage è libero in tutto Azure. Va fatto prima di crearlo.

```bash
az storage account show --resource-group "$LAB_RG" --name "$LAB_STORAGE" --query "{Sku:sku.name,HttpsOnly:enableHttpsTrafficOnly,MinimumTls:minimumTlsVersion,PublicBlobAccess:allowBlobPublicAccess}" --output jsonc
```
Mostra le impostazioni dello storage, senza le chiavi. Abbiamo controllato HTTPS `true`, TLS `TLS1_2` e blob pubblici `false`.

> 🚫 Non usare mai `az storage account keys list`: mostra le chiavi segrete dello storage.

---

## 8. Inventario

```bash
az resource list --resource-group "$LAB_RG" --query "[].{Name:name,Type:type,Location:location}" --output table
```
Elenca tutte le risorse del gruppo. La subnet non compare perché fa parte della VNet.

```bash
az resource list --resource-group "$LAB_RG" --query "[].id" --output tsv | sed -E 's#/subscriptions/[^/]+#/subscriptions/<omitted>#'
```
Prende gli ID delle risorse e con `sed` sostituisce l'ID della sottoscrizione con `<omitted>`. Così puoi copiarli nella consegna senza dati riservati.

**I formati di output:**

| `--output` | Quando usarlo |
|---|---|
| `table` | da leggere a occhio |
| `jsonc` | JSON colorato, mostra la struttura completa |
| `tsv` | solo valori, utile negli script o con una pipe |

**`--query` in breve** (si chiama JMESPath):

| Scrittura | Significato |
|---|---|
| `name` | un campo |
| `{Nome:name,Stato:state}` | scelgo i campi e gli do un nome |
| `[]` | per ogni elemento della lista |
| `[?name=='x']` | filtra gli elementi |
| `tags.unit` | campo dentro un altro campo |

---

## 9A. Cloud Shell e Azure PowerShell

Cloud Shell è un terminale che gira dentro Azure: si apre dal portale ed è già loggato. Va aperto **senza storage** e **senza rete privata**.

```powershell
Get-Module -ListAvailable Az.Resources | Select-Object Name,Version
```
Controlla che il modulo Az di PowerShell sia installato. `Get-` legge, `Select-Object` sceglie le colonne da mostrare.

```powershell
Get-AzContext
```
È l'equivalente PowerShell di `az account show`: dice su quale sottoscrizione stai lavorando.

```powershell
Get-AzResourceGroup -Name 'rg-cea-ud02-2121b8ad' | Select-Object ResourceGroupName,Location,ProvisioningState
```
È l'equivalente PowerShell di `az group show`.

| Cosa voglio fare | Azure CLI (Bash) | Azure PowerShell |
|---|---|---|
| vedere il contesto | `az account show` | `Get-AzContext` |
| cambiare sottoscrizione | `az account set` | `Set-AzContext` |
| leggere un resource group | `az group show` | `Get-AzResourceGroup` |
| scegliere i campi | `--query` | `Select-Object` |

---

## 12. Cleanup

```bash
az group delete --name "$LAB_RG" --yes --no-wait
```
Elimina il resource group **e tutto quello che contiene**. `--yes` salta la conferma, `--no-wait` restituisce subito il prompt. Il prompt che torna **non** significa che sia già tutto eliminato. Prima di lanciarlo controlla sempre nome, tag e risorse del gruppo.

```bash
az group wait --name "$LAB_RG" --deleted
```
Aspetta che l'eliminazione sia finita.

```bash
az group exists --name "$LAB_RG"
```
Prova finale: deve rispondere `false`. Se risponde ancora `true`, aspetta e ripeti solo questo controllo, senza lanciare di nuovo il delete.

---

## Errori che abbiamo incontrato

| Errore | Causa | Soluzione |
|---|---|---|
| `bad substitution` | valore messo dentro `${...}` al posto del nome della variabile | scrivere il valore solo in `LAB_SUFFIX`, le altre righe usano `${LAB_SUFFIX}` |
| sessione CLI scaduta, richiesta di nuovo login | il token è scaduto e serve rifare l'MFA | `az login --use-device-code`, poi ripetere solo il comando fallito |
| subnet con prefisso `null` | il campo si chiama `addressPrefixes` (plurale) | interrogare la subnet con `az network vnet subnet show` |

## Regole da ricordare

- Prima **verifico**, poi agisco.
- Dopo ogni creazione nel portale **controllo con la CLI**.
- Nel repository non metto mai ID della sottoscrizione o del tenant, email, token, codici di login e chiavi.
- Se un comando è già partito, **non lo ripeto**: controllo lo stato.
