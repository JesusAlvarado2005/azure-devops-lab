# Guida comandi — UD02

Tutti i comandi usati nel laboratorio guidato e in quello autonomo, organizzati per **a cosa servono**, non per numero di passo.

---

## 1. Il metodo: ogni lab segue lo stesso ciclo

```text
 CONTROLLO  →  PREPARO  →  VERIFICO I NOMI  →  CREO  →  VERIFICO  →  INVENTARIO  →  ELIMINO  →  CONFERMO
 sono nel      variabili    sono liberi?       create   show         list          delete      exists
 posto giusto? con i nomi                                                           + wait      = false
```

| Fase | Guidato | Autonomo |
|---|---|---|
| Controllo contesto | `az account show`, `az provider show` | uguale |
| Preparo i nomi | file `01_VARIABILI_LAB.sh` + `source` | variabili `AUTO_` scritte nel terminale |
| Nomi liberi | `az group exists`, `check-name` | uguale |
| **Creo** | **dal portale** | **dalla CLI** (`create`) |
| Verifico | `show` con `--query` | uguale |
| Seconda verifica | CLI dopo il portale | portale dopo la CLI |
| Inventario | `az resource list` | uguale |
| Elimino e confermo | `delete` → `wait` → `exists` | uguale |

**Regola d'oro:** prima di ogni azione che cambia qualcosa c'è un controllo, e dopo c'è una verifica.

---

## 2. Come è fatto un comando Azure CLI

Tutti i comandi `az` hanno la stessa forma:

```text
az   <cosa>             <azione>   --opzione valore   --opzione valore
az   group              create     --name rg-x         --location italynorth
az   network vnet       show       --resource-group …  --name …
az   storage account    delete     …
```

| Azione | Cosa fa | Modifica Azure? |
|---|---|---|
| `show` | mostra **una** risorsa | no |
| `list` | mostra **tutte** le risorse di un tipo | no |
| `exists` | risponde `true` o `false` | no |
| `create` | crea, o **aggiorna** se il nome esiste già | **sì** |
| `delete` | elimina | **sì** |
| `wait` | aspetta che un'operazione finisca | no |

Se non ricordi le opzioni di un comando:

```bash
az group create --help
```

Le opzioni che userai sempre:

| Opzione | A cosa serve |
|---|---|
| `--name` | nome della risorsa |
| `--resource-group` | in quale gruppo si trova la risorsa (non serve per il gruppo stesso) |
| `--location` | località, es. `italynorth` |
| `--tags chiave=valore …` | etichette separate da spazi |
| `--query "…"` | scegli quali campi vedere |
| `--output table/jsonc/tsv` | come vedere il risultato |

---

## 3. Le basi della shell che servono

### Variabili

Una variabile è un nome che contiene un valore.

```bash
AUTO_VNET="vnet-cea-auto"    # SCRIVO: niente $ e niente spazi attorno a =
echo "$AUTO_VNET"            # LEGGO: con $ davanti → stampa vnet-cea-auto
```

| Scrittura | Significato |
|---|---|
| `NOME="valore"` | metto un valore nella variabile |
| `$NOME` o `${NOME}` | leggo il valore. Le graffe servono quando il nome è attaccato ad altro testo: `"stcea${SUFFIX}"` |
| `$(comando)` | eseguo un comando e uso il suo risultato come valore |
| `export NOME=…` | rende la variabile visibile anche ai programmi lanciati dalla shell |

> ⚠️ **Dentro `${ }` va il NOME, mai il valore.** `${LAB_SUFFIX}` è giusto, `${2121b8ad}` dà `bad substitution`.

> ⚠️ **Le variabili vivono solo in quel terminale.** Se lo chiudi spariscono: fai tutto il lab nella stessa finestra, oppure salvale in un file.

### File di variabili e `source`

```bash
source consegne/UD02/01_VARIABILI_LAB.sh
```
Legge il file ed esegue le righe nel terminale attuale, così le variabili restano caricate. Serve quando le variabili sono **salvate in un file**. Se le scrivi direttamente nel terminale, `source` non serve.

> ⚠️ **L'ordine conta.** Prima `source`, poi usi `$LAB_LOCATION`. Al contrario la variabile risulta vuota: è l'errore della "Location vuota" nell'autonomo.

### Il suffisso casuale

```bash
AUTO_SUFFIX="$(date +%s%N | sha256sum | cut -c1-8)"
```

```text
date +%s%N     →  1760432400123456789   (ora attuale in nanosecondi)
| sha256sum    →  b2628df9e1a7c…         (la trasforma in un codice esadecimale)
| cut -c1-8    →  b2628df9               (tiene i primi 8 caratteri)
```

Il `|` (pipe) passa il risultato di un comando al successivo. Il suffisso serve perché il nome dello storage deve essere **unico in tutto Azure**.

### La data per il tag

```bash
AUTO_DELETE_AFTER="$(date -d '+2 days' +%F)"   # → 2026-10-15
```
`-d '+2 days'` vuol dire "fra due giorni", `+%F` il formato `anno-mese-giorno`.

### Stampare per controllare

```bash
printf 'RG: %s\nStorage: %s\n' "$AUTO_RG" "$AUTO_STORAGE"
```
Ogni `%s` viene sostituito dalle variabili in ordine, `\n` va a capo. Prima di creare o eliminare **stampi sempre** i nomi: se una riga è vuota, ti fermi.

### Controllo con espressione regolare

```bash
[[ "$LAB_STORAGE" =~ ^[a-z0-9]{3,24}$ ]] && echo valido
```
`^[a-z0-9]{3,24}$` vuol dire: dall'inizio alla fine, solo minuscole e numeri, da 3 a 24 caratteri. È la regola dei nomi degli storage.

---

## 4. CONTROLLO: sono nel posto giusto?

```bash
pwd
```
Mostra la cartella attuale. Deve essere `~/workspace/azure-devops-lab`.

```bash
az version
```
Mostra la versione della CLI. Se risponde, funziona.

```bash
az login --use-device-code
```
Login con un codice da inserire nel browser, dove fai anche l'MFA. Si rifà quando la sessione scade. Un nuovo login **non** dà più permessi, rinnova solo la sessione.

```bash
az account show --query "{Name:name,State:state,IsDefault:isDefault}" --output table
```
Con quale sottoscrizione sto lavorando? Deve essere `Enabled`. Grazie a `--query` l'ID della sottoscrizione non compare.

```bash
az account list --query "[].{Name:name,State:state,IsDefault:isDefault}" --output table
az account set --subscription "<NOME>"
```
Elenca le sottoscrizioni e cambia quella attiva. Noi ne abbiamo una sola.

```bash
az account list-locations --query "[?name=='italynorth'].{Name:name,DisplayName:displayName}" --output table
```
La località esiste per la mia sottoscrizione?

```bash
az provider show --namespace Microsoft.Network --query "{Namespace:namespace,State:registrationState}" --output table
az provider show --namespace Microsoft.Storage --query "{Namespace:namespace,State:registrationState}" --output table
```
La sottoscrizione può creare reti e storage? Deve essere `Registered`. Solo se è `NotRegistered`:
```bash
az provider register --namespace Microsoft.Storage --wait
```

---

## 5. VERIFICO I NOMI: sono liberi?

```bash
az group exists --name "$AUTO_RG"
```
Atteso **`false`**. Se è `true` il gruppo esiste già, e `create` lo modificherebbe: cambia suffisso.

```bash
az storage account check-name --name "$AUTO_STORAGE" --output table
```
Atteso **`NameAvailable: True`**. Il nome dello storage deve essere libero in tutto il mondo, perché diventa un indirizzo web (`stceaauto….blob.core.windows.net`).

---

## 6. CREO

L'ordine è obbligato, perché ogni cosa sta **dentro** quella precedente:

```text
1. resource group   →   2. VNet (dentro il gruppo)   →   3. storage (dentro il gruppo)
```

### Resource group

```bash
az group create --name "$AUTO_RG" --location "$AUTO_LOCATION" \
  --tags course=cloud-engineer-academy unit=UD02 environment=dev scenario=autonomous deleteAfter="$AUTO_DELETE_AFTER" \
  --output table
```

### VNet con subnet

```bash
az network vnet create --resource-group "$AUTO_RG" --name "$AUTO_VNET" --location "$AUTO_LOCATION" \
  --address-prefixes 10.30.0.0/16 \
  --subnet-name "$AUTO_SUBNET" --subnet-prefixes 10.30.10.0/24 \
  --tags course=cloud-engineer-academy unit=UD02 environment=dev scenario=autonomous deleteAfter="$AUTO_DELETE_AFTER" \
  --output jsonc
```

| Opzione | Cosa fa |
|---|---|
| `--address-prefixes` | lo spazio di indirizzi di tutta la rete |
| `--subnet-name`, `--subnet-prefixes` | crea subito una subnet, cioè un pezzo della rete |

### Storage account

```bash
az storage account create --resource-group "$AUTO_RG" --name "$AUTO_STORAGE" --location "$AUTO_LOCATION" \
  --kind StorageV2 --sku Standard_LRS \
  --https-only true --min-tls-version TLS1_2 --allow-blob-public-access false \
  --tags course=cloud-engineer-academy unit=UD02 environment=dev scenario=autonomous deleteAfter="$AUTO_DELETE_AFTER" \
  --output jsonc
```

| Opzione | Cosa fa |
|---|---|
| `--kind StorageV2` | tipo di account generico e moderno |
| `--sku Standard_LRS` | dischi standard, 3 copie nello stesso datacenter |
| `--https-only true` | 🔒 solo connessioni cifrate |
| `--min-tls-version TLS1_2` | 🔒 rifiuta le versioni di cifratura vecchie |
| `--allow-blob-public-access false` | 🔒 nessuno legge i file senza autorizzazione |

Il `\` a fine riga dice "il comando continua sotto": serve solo a renderlo leggibile.

### Portale e CLI: stesse cose, scritte in modo diverso

| Nel portale | Nella CLI |
|---|---|
| campo Resource group | `--resource-group` |
| campo Name | `--name` |
| campo Region | `--location` |
| scheda Tags | `--tags` |
| scheda IP addresses | `--address-prefixes`, `--subnet-prefixes` |
| Performance / Redundancy | `--sku` |
| scheda Advanced | `--https-only`, `--min-tls-version`, `--allow-blob-public-access` |
| pulsante Create | `create` |

Il portale è comodo per **esplorare** e scoprire le opzioni. La CLI per **ripetere** lo stesso lavoro identico.

> 💡 **I tag non si ereditano.** Quelli del resource group non passano alle risorse: vanno ripetuti in ogni `create`.

---

## 7. VERIFICO: è venuto come volevo?

Dopo ogni creazione leggi le proprietà vere, con comandi che **non modificano niente**.

```bash
az group show --name "$AUTO_RG" \
  --query "{Name:name,Location:location,State:properties.provisioningState,Tags:tags}" --output jsonc
```
Atteso: località giusta, `Succeeded`, tutti i tag.

```bash
az network vnet show --resource-group "$AUTO_RG" --name "$AUTO_VNET" \
  --query "{Address:addressSpace.addressPrefixes,Subnets:subnets[].{Name:name,Prefix:addressPrefix},Tags:tags}" --output jsonc
```
Atteso: spazio `/16`, subnet con il suo `/24`, tag.

```bash
az network vnet subnet show --resource-group "$LAB_RG" --vnet-name "$LAB_VNET" --name "$LAB_SUBNET" --output jsonc
```
Mostra una sola subnet. Ci è servito nel guidato: la subnet creata dal portale aveva il prefisso in `addressPrefixes` (plurale) e la query dava `null`. Quella creata dalla CLI invece lo ha in `addressPrefix`.

```bash
az storage account show --resource-group "$AUTO_RG" --name "$AUTO_STORAGE" \
  --query "{Kind:kind,Sku:sku.name,HttpsOnly:enableHttpsTrafficOnly,MinimumTls:minimumTlsVersion,PublicBlobAccess:allowBlobPublicAccess,State:provisioningState,Tags:tags}" --output jsonc
```
Atteso: `StorageV2`, `Standard_LRS`, `true`, `TLS1_2`, `false`, `Succeeded`, tag.

> 🚫 **Mai** `az storage account keys list`: mostra le chiavi segrete.

### `--query`: scegliere i campi (JMESPath)

| Scrittura | Significato | Esempio SQL simile |
|---|---|---|
| `name` | un campo | `SELECT name` |
| `{Nome:name,Stato:state}` | più campi, con il nome che voglio | `SELECT name AS Nome, state AS Stato` |
| `tags.unit` | campo dentro un altro campo | — |
| `[]` | per ogni elemento della lista | ogni riga |
| `[].{Name:name}` | per ogni elemento, prendi questi campi | `SELECT name FROM …` |
| `[?name=='x']` | filtra | `WHERE name = 'x'` |

**`show` restituisce un oggetto** `{…}` → query senza `[]`.
**`list` restituisce una lista** `[{…},{…}]` → query con `[]`.

### `--output`: come vedere il risultato

| Formato | Quando |
|---|---|
| `table` | leggere a occhio |
| `jsonc` | vedere la struttura completa, colorata |
| `tsv` | solo i valori, per script o pipe |

---

## 8. INVENTARIO: cosa c'è nel gruppo?

```bash
az resource list --resource-group "$AUTO_RG" \
  --query "[].{Name:name,Type:type,Location:location,Unit:tags.unit,Scenario:tags.scenario}" --output table
```
Elenca **tutte** le risorse del gruppo. La subnet non compare perché fa parte della VNet (è una risorsa "figlia"). Così dimostri anche che VNet e storage **stanno nello stesso gruppo**.

```bash
az resource list --resource-group "$AUTO_RG" --query "[].id" --output tsv \
  | sed -E 's#/subscriptions/[^/]+#/subscriptions/<omitted>#'
```
Prende gli ID e con `sed` nasconde l'ID della sottoscrizione. Così si legge l'ID di una risorsa:

```text
/subscriptions/<omitted>/resourceGroups/rg-cea-ud02-auto-b2628df9/providers/Microsoft.Network/virtualNetworks/vnet-cea-auto
 └ sottoscrizione        └ resource group                         └ provider        └ tipo          └ nome
```

---

## 9. ELIMINO E CONFERMO

```bash
# 1. CONTROLLO: il nome non è vuoto ed è il mio
printf 'Da eliminare: %s\n' "$AUTO_RG"
az group show --name "$AUTO_RG" --query "{Name:name,Unit:tags.unit,Scenario:tags.scenario}" --output table
az resource list --resource-group "$AUTO_RG" --query "[].{Name:name,Type:type}" --output table

# 2. ELIMINO tutto il gruppo e quello che contiene
az group delete --name "$AUTO_RG" --yes --no-wait

# 3. ASPETTO e CONFERMO
az group wait --name "$AUTO_RG" --deleted
az group exists --name "$AUTO_RG"          # atteso: false
```

| Opzione | Cosa fa |
|---|---|
| `--yes` | non chiede conferma |
| `--no-wait` | restituisce subito il prompt, mentre Azure continua a eliminare |
| `wait --deleted` | blocca finché il gruppo non è sparito |

Nell'autonomo, subito dopo il delete, `exists` dava ancora **`true`**: l'eliminazione era in corso. Dopo `wait` (33 secondi) ha dato **`false`**. Per questo il prompt che torna **non è una prova**.

> ⚠️ Se `exists` dà ancora `true`, aspetta e ripeti **solo** `exists`. Non rilanciare il delete.

---

## 10. Cloud Shell e Azure PowerShell

Cloud Shell è un terminale dentro Azure, già loggato. Va aperto **senza storage** e **senza rete privata**, altrimenti crea risorse in più. È un ambiente separato dal tuo PC: noi avevamo CLI 2.90.0 lì e 2.83.0 sul PC.

| Cosa voglio fare | Azure CLI | Azure PowerShell |
|---|---|---|
| vedere il contesto | `az account show` | `Get-AzContext` |
| cambiare sottoscrizione | `az account set` | `Set-AzContext` |
| leggere un resource group | `az group show` | `Get-AzResourceGroup` |
| scegliere i campi | `--query` | `Select-Object` |

```powershell
Get-Module -ListAvailable Az.Resources | Select-Object Name,Version
Get-AzResourceGroup -Name 'rg-…' | Select-Object ResourceGroupName,Location,ProvisioningState
```
In PowerShell `Get-` legge e `|` passa l'oggetto a `Select-Object`, che sceglie le colonne.

---

## 11. Git: salvare e pubblicare

```bash
git status --short                   # cosa è cambiato:  M = modificato,  ?? = nuovo
git diff -- <file>                   # cosa è cambiato, riga per riga (non mostra i file nuovi)
git add <file>                       # metto il file nella staging area
git diff --cached --name-only        # cosa entrerà nel commit
git commit -m "messaggio"            # salvo una versione in locale
git push                             # la pubblico su GitHub
git log --oneline -3                 # ultimi commit con il loro hash
```

`git status -sb` mostra `[avanti 1]` se hai commit locali non ancora pubblicati.

**L'hash** (es. `4b45d90`) è la "targa" unica di un commit. Nella consegna si cita un commit **già pubblicato**: un file non può contenere l'hash del commit che lo contiene, perché l'hash dipende dal contenuto.

---

## 12. Indirizzi IP e CIDR, in breve

Il numero dopo `/` dice quanti bit dell'indirizzo sono **fissi**. Più è grande, più l'intervallo è piccolo.

```text
10.30.0.0/16   →  10.30.???.???  →  da 10.30.0.0  a 10.30.255.255  →  65.536 indirizzi   (la VNet)
10.30.10.0/24  →  10.30.10.???   →  da 10.30.10.0 a 10.30.10.255   →     256 indirizzi   (la subnet)
```

La subnet deve stare **dentro** lo spazio della VNet. In ogni subnet Azure si riserva 5 indirizzi.

---

## 13. Errori incontrati e come li abbiamo risolti

| Cosa hai visto | Perché | Soluzione |
|---|---|---|
| `bad substitution` | valore messo dentro `${ }` al posto del nome | `${LAB_SUFFIX}`, il valore solo nella riga `LAB_SUFFIX=` |
| righe `∙ ∙ ∙` e il comando non parte | incollati i backtick ` ``` ` o un comando a metà, la shell aspetta il resto | `Ctrl+C` e incollare solo la riga del comando |
| `^[[200~` / `bad pattern` | caratteri spuri del copia-incolla | riscrivere il comando pulito |
| `Location:` vuota | `AUTO_LOCATION` assegnata prima di `source` | prima `source`, poi la variabile |
| sessione scaduta, richiesta di login | il token è scaduto, serve di nuovo l'MFA | `az login --use-device-code`, poi solo il comando fallito |
| prefisso subnet `null` | campo `addressPrefixes` invece di `addressPrefix` | `az network vnet subnet show` |
| `exists` ancora `true` dopo delete | eliminazione in corso | `az group wait --deleted`, poi `exists` |

---

## 14. Ricetta completa (laboratorio autonomo)

```bash
cd ~/workspace/azure-devops-lab

# CONTROLLO
az account show --query "{Name:name,State:state,IsDefault:isDefault}" --output table
az provider show --namespace Microsoft.Network --query "{Namespace:namespace,State:registrationState}" --output table
az provider show --namespace Microsoft.Storage --query "{Namespace:namespace,State:registrationState}" --output table

# PREPARO
AUTO_SUFFIX="$(date +%s%N | sha256sum | cut -c1-8)"
AUTO_RG="rg-cea-ud02-auto-${AUTO_SUFFIX}"
AUTO_VNET="vnet-cea-auto"
AUTO_SUBNET="snet-workload"
AUTO_STORAGE="stceaauto${AUTO_SUFFIX}"
AUTO_DELETE_AFTER="$(date -d '+2 days' +%F)"
source consegne/UD02/01_VARIABILI_LAB.sh
AUTO_LOCATION="$LAB_LOCATION"
printf 'Location: %s\nRG: %s\nVNet: %s\nSubnet: %s\nStorage: %s\n' "$AUTO_LOCATION" "$AUTO_RG" "$AUTO_VNET" "$AUTO_SUBNET" "$AUTO_STORAGE"

# NOMI LIBERI
az group exists --name "$AUTO_RG"                                   # false
az storage account check-name --name "$AUTO_STORAGE" --output table # True

# CREO  →  sezione 6
# VERIFICO  →  sezione 7
# INVENTARIO  →  sezione 8
# ELIMINO E CONFERMO  →  sezione 9
```

## Regole da ricordare

- Prima **controllo**, poi agisco, poi **verifico**.
- Stampo i nomi prima di creare o eliminare.
- I tag vanno su **ogni** risorsa.
- Nel repository non metto mai ID della sottoscrizione o del tenant, email, token, codici di login e chiavi.
- Se un comando è già partito **non lo ripeto**: ne controllo lo stato.
