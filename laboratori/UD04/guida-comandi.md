# Guida comandi — UD04

Comandi del laboratorio guidato su Azure Storage, organizzati per **a cosa servono**. Le basi (forma dei comandi `az`, variabili, `--query`, `--output`, git) sono in `laboratori/UD02/guida-comandi.md`.

---

## 1. Il ciclo, con una novità: i due piani

```text
 CONTROLLO → PREPARO → NOME LIBERO → CREO ACCOUNT → CONTAINER E BLOB → RUOLO DATI → USO I DATI → LIFECYCLE → ELIMINO
             variabili  check-name    management       portale           IAM          data plane    portale      cleanup
                                      plane
```

| Piano | Cosa fa | Dove passa | Ruoli |
|---|---|---|---|
| **management plane** | crea e configura la risorsa | Azure Resource Manager | Reader, Contributor, Owner |
| **data plane** | legge e scrive i dati dentro | `https://<account>.blob.core.windows.net` | Storage Blob Data Reader / Contributor / Owner |

> 💡 Essere **Owner** della sottoscrizione non basta per leggere i blob con la tua identità: serve un ruolo **Storage Blob Data**.

---

## 2. PREPARO: variabili e file

```bash
LAB_SUFFIX="$(openssl rand -hex 4)"              # 4 byte casuali → 8 caratteri esadecimali, es. 3105028c
LAB_RG="rg-cea-storage-${LAB_SUFFIX}"
LAB_STORAGE="stcea${LAB_SUFFIX}"
LAB_CONTAINER="documents"
LAB_LOCATION="italynorth"
LAB_DELETE_AFTER="$(date -u -d '+1 day' +%F)"   # -u = ora UTC, domani in formato anno-mese-giorno

printf 'Documento didattico UD04 - nessun dato personale\n' > consegne/UD04/01_DOCUMENTO_LAB.txt
```

`>` scrive l'output di un comando dentro un file, sostituendo quello che c'era.

```bash
az storage account check-name --name "$LAB_STORAGE" --output table   # atteso: True
```

---

## 3. CREO E VERIFICO L'ACCOUNT (management plane)

```bash
az group create --name "$LAB_RG" --location "$LAB_LOCATION" \
  --tags course=cloud-engineer-academy unit=UD04 environment=lab deleteAfter="$LAB_DELETE_AFTER" \
  --output table

az storage account create --resource-group "$LAB_RG" --name "$LAB_STORAGE" --location "$LAB_LOCATION" \
  --sku Standard_LRS --kind StorageV2 \
  --https-only true --min-tls-version TLS1_2 --allow-blob-public-access false \
  --tags course=cloud-engineer-academy unit=UD04 environment=lab deleteAfter="$LAB_DELETE_AFTER" \
  --output table

az storage account show --resource-group "$LAB_RG" --name "$LAB_STORAGE" \
  --query "{Sku:sku.name,Kind:kind,Https:enableHttpsTrafficOnly,Tls:minimumTlsVersion,PublicBlob:allowBlobPublicAccess,BlobEndpoint:primaryEndpoints.blob}" \
  --output jsonc
```

Atteso: `Standard_LRS`, `StorageV2`, `true`, `TLS1_2`, `false`.

L'avviso su `TLS1_0` e `TLS1_1` dismessi è solo informativo: noi usiamo `TLS1_2`.

---

## 4. CONTAINER E PRIMO BLOB (portale)

- **Data storage → Containers → + Container**: `documents`, accesso **Private**.
- Nel container **Upload**: il blob prende **il nome del file** (`01_DOCUMENTO_LAB.txt`).

```text
https://stcea3105028c.blob.core.windows.net/documents/temporary/temporaneo.txt
                                             └container └nome del blob (la / fa parte del nome)
```

> ⚠️ Nei comandi successivi usa il **nome vero** del blob. La guida scriveva `documento-lab.txt`, ma il blob caricato si chiama `01_DOCUMENTO_LAB.txt`: con il nome sbagliato ricevi `BlobNotFound`.

---

## 5. RUOLO DATI (portale, IAM)

Storage account → **Access control (IAM)** → Add role assignment → **Storage Blob Data Contributor** al tuo account.

| Scope | Vale per |
|---|---|
| storage account | solo quell'account (**minimo**, quello della guida) |
| resource group | tutti gli storage del gruppo |

Il ruolo può impiegare qualche minuto ad attivarsi. Se compare `AuthorizationPermissionMismatch`, aspetta e riprova **senza** assegnare ruoli più ampi.

---

## 6. USO I DATI (data plane)

### Con la mia identità: `--auth-mode login`

```bash
az storage container list --account-name "$LAB_STORAGE" --auth-mode login \
  --query "[].{Container:name,PublicAccess:properties.publicAccess}" --output table

az storage blob list --account-name "$LAB_STORAGE" --container-name "$LAB_CONTAINER" --auth-mode login \
  --query "[].{Blob:name,Tier:properties.blobTier,Bytes:properties.contentLength}" --output table
```

```bash
az storage blob upload --account-name "$LAB_STORAGE" --container-name "$LAB_CONTAINER" \
  --name temporary/temporaneo.txt --file /tmp/ud04-temporaneo.txt \
  --auth-mode login --overwrite --output table

az storage blob download --account-name "$LAB_STORAGE" --container-name "$LAB_CONTAINER" \
  --name 01_DOCUMENTO_LAB.txt --file /tmp/documento-lab-scaricato.txt \
  --auth-mode login --overwrite --output table
```

| Opzione | Cosa fa |
|---|---|
| `--name` | nome del blob in Azure |
| `--file` | file sul tuo PC (da leggere in upload, da scrivere in download) |
| `--overwrite` | sostituisce se esiste già |
| `--auth-mode login` | usa la tua identità Entra e i tuoi ruoli dati |

```bash
cmp consegne/UD04/01_DOCUMENTO_LAB.txt /tmp/documento-lab-scaricato.txt
```
`cmp` confronta due file byte per byte. **Nessun output = identici.** Se sono diversi stampa dove.

### Con la chiave dell'account: `--auth-mode key` (solo per confronto)

```bash
AZURE_STORAGE_KEY="$(az storage account keys list --resource-group "$LAB_RG" --account-name "$LAB_STORAGE" \
  --query '[0].value' --output tsv)"
export AZURE_STORAGE_KEY

az storage blob list --account-name "$LAB_STORAGE" --container-name "$LAB_CONTAINER" \
  --auth-mode key --query "[].name" --output table

unset AZURE_STORAGE_KEY
```

- `export` rende la variabile visibile ad `az`, che la cerca proprio con quel nome.
- `unset` cancella la variabile dalla memoria del terminale.

> 🚫 Mai `echo` della chiave, mai copiarla. La chiave **scavalca RBAC**: apre tutto l'account, non scade e non dice chi la usa. Fuori da questo passo, **mai** `keys list`.

### Con una user delegation SAS

```bash
SAS_EXPIRY="$(date -u -d '+30 minutes' +%Y-%m-%dT%H:%MZ)"   # es. 2026-10-15T10:55Z
SAS_URL="$(az storage blob generate-sas --account-name "$LAB_STORAGE" --container-name "$LAB_CONTAINER" \
  --name 01_DOCUMENTO_LAB.txt --permissions r --expiry "$SAS_EXPIRY" \
  --auth-mode login --as-user --full-uri --output tsv)"

curl --fail --silent --show-error "$SAS_URL" --output /tmp/documento-sas.txt
cmp consegne/UD04/01_DOCUMENTO_LAB.txt /tmp/documento-sas.txt
unset SAS_URL
```

| Opzione | Cosa fa |
|---|---|
| `--permissions r` | solo lettura |
| `--expiry` | quando scade (in UTC) |
| `--as-user` | **user delegation**: firmata con la tua identità, non con la chiave |
| `--full-uri` | restituisce l'URL completo con il token |
| `curl --fail` | se il server risponde con un errore, curl fallisce invece di salvare la pagina di errore |
| `--silent --show-error` | niente barra di avanzamento, ma mostra gli errori |

> 🚫 L'URL della SAS **è** l'accesso: non stamparlo, non salvarlo, non metterlo nel repo.

### Riassunto dei tre metodi

| | Entra ID (`login`) | Account key (`key`) | SAS |
|---|---|---|---|
| chi sei | la tua identità | nessuno, solo "la chiave" | chi ha l'URL |
| cosa può fare | quello che dice il ruolo | tutto | i permessi del token |
| scadenza | finché hai il ruolo | mai | quella scelta |
| come si revoca | togli il ruolo | ruoti la chiave (rompe tutti) | scade, o revochi la chiave usata per firmarla |

---

## 7. LIFECYCLE (portale + verifica CLI)

**Data management → Lifecycle management → Add a rule**: `delete-temporary`, block blob, **filtro prefisso `documents/temporary/`**, eliminazione dopo 1 giorno dall'ultima modifica.

```bash
az storage account management-policy show --account-name "$LAB_STORAGE" --resource-group "$LAB_RG" \
  --query "policy.rules[].{Name:name,Enabled:enabled,Prefixes:definition.filters.prefixMatch,DeleteAfter:definition.actions.baseBlob.delete.daysAfterModificationGreaterThan}" \
  --output jsonc
```

Atteso: `"Prefixes": ["documents/temporary/"]`.

> ⚠️ **`"Prefixes": null` = nessun filtro**: la regola vale per **tutti** i blob dell'account. Il prefisso comprende anche il nome del container.

La regola non parte subito: Azure la esegue una volta al giorno circa, e solo sui blob abbastanza vecchi. Si verifica la **configurazione**, non l'eliminazione.

---

## 8. ELIMINO (dopo autonomo e verifica)

1. Dal portale togli la role assignment **Storage Blob Data Contributor**.
2. Pulisci i file temporanei e le variabili:

```bash
rm -f /tmp/ud04-temporaneo.txt /tmp/documento-lab-scaricato.txt /tmp/documento-sas.txt
unset AZURE_STORAGE_KEY SAS_URL
```

3. Controlla nome e tag, poi elimina e conferma:

```bash
echo "Gruppo da eliminare: $LAB_RG"
az group show --name "$LAB_RG" --query "{Name:name,Tags:tags}" --output jsonc   # unit deve essere UD04

az group delete --name "$LAB_RG" --yes --no-wait
az group wait --name "$LAB_RG" --deleted
az group exists --name "$LAB_RG"                                              # atteso: false
```

---

## 9. Errori incontrati e come li abbiamo risolti

| Cosa hai visto | Perché | Soluzione |
|---|---|---|
| `^[[200~cd` / `bad pattern` | caratteri invisibili del copia-incolla | riscrivere il comando a mano |
| `~` → `permesso negato` | zsh prova a **eseguire** la cartella home | niente, per entrarci si usa `cd ~` |
| prompt `>....` e il comando non parte | incollati anche i ` ``` ` della guida, la shell aspetta la fine | `Ctrl+C`, incollare solo i comandi. **Mai** incollare il blocco con `git push` |
| `"Prefixes": null` | la regola lifecycle è stata salvata senza filtro | aggiungere `documents/temporary/` nel Filter set |
| nome blob diverso dalla guida | dal portale il blob prende il nome del file | usare il nome vero, `01_DOCUMENTO_LAB.txt` |

## Regole da ricordare

- Ruoli di gestione e ruoli dati sono **diversi**.
- Prima l'identità (`login`), poi la SAS limitata, la chiave **mai** nell'uso normale.
- `cmp` senza output = file identici.
- Chiavi, URL SAS e token non finiscono mai in file, screenshot o repo.
- Leggi ogni output di verifica e chiediti: "è quello che mi aspettavo?".
