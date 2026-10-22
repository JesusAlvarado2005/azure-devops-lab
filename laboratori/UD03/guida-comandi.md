# Guida comandi — UD03

Identità, accessi e governance: Entra ID, RBAC, tag, lock, costi e budget. Le basi (variabili, `--query`, `--output`, git) sono in `laboratori/UD02/guida-comandi.md`.

---

## 1. Tre livelli da non confondere

| Livello | Domanda | Dove si vede |
|---|---|---|
| **autenticazione** | chi sei? | `az login`, Entra ID |
| **autorizzazione RBAC** | cosa puoi fare e dove? | role assignment = principal + ruolo + scope |
| **governance** | cosa è bloccato o tracciato per tutti? | tag, lock, budget, policy |

> 💡 In RBAC i permessi **si sommano**: un Reader in più non toglie niente a chi è già Owner. Il lock invece vale anche per l'Owner.

---

## 2. CONTROLLO E PREPARO

```bash
az version --output table
az account show --query "{Sub:name,State:state}" --output table   # niente ID nelle consegne

LAB_SUFFIX="$(openssl rand -hex 3)"            # es. c3f11a
LAB_RG="rg-cea-identity-${LAB_SUFFIX}"
LAB_LOCATION="italynorth"

az group create --name "$LAB_RG" --location "$LAB_LOCATION" \
  --tags course=cloud-engineer-academy unit=UD03 environment=lab deleteAfter="$(date -u -d '+1 day' +%F)" \
  --output table
```

⚠️ `az group show -n "$LAB_SUFFIX"` dà `ResourceGroupNotFound`: il nome completo è in `$LAB_RG`, non nel suffisso.

---

## 3. IDENTITÀ (portale Entra ID)

```text
Entra ID → Users  → New user  → utente cloud cea-lab-<suffisso>     (password temporanea: non salvarla)
Entra ID → Groups → New group → Security, Assigned, grp-cea-readers-<suffisso> → Members: aggiungi l'utente
```

Per creare utenti e gruppi serve almeno **User Administrator** nella directory.

---

## 4. RBAC: assegnare e leggere

Portale: `Resource group → Access control (IAM) → Add role assignment → Reader → al gruppo`.

```bash
RG_SCOPE="$(az group show --name "$LAB_RG" --query id --output tsv)"   # prima valorizzo, poi uso

az role assignment list --scope "$RG_SCOPE" --include-inherited \
  --query "[].{Role:roleDefinitionName,PrincipalType:principalType,Scope:scope}" \
  --output jsonc | sed -E 's#/subscriptions/[^/]+#/subscriptions/<omitted>#g'
```

- `--include-inherited` mostra anche i ruoli che arrivano dalla sottoscrizione, come Owner
- `sed` toglie l'ID della sottoscrizione prima di copiare l'output in una consegna
- ruolo al **gruppo** e non al singolo utente, scope **minimo** (il resource group, non tutta la sottoscrizione)

---

## 5. GOVERNANCE: lock, costi, budget

```bash
az lock create --name lock-cea-delete --resource-group "$LAB_RG" --lock-type CanNotDelete
az lock list --resource-group "$LAB_RG" --output table

az group delete --name "$LAB_RG" --yes      # atteso: ScopeLocked
az group exists --name "$LAB_RG"            # atteso: true, il gruppo è rimasto
```

Portale: `Cost Management → Cost analysis` per il costo e `Budgets → Add` per il budget (es. mensile 40 con avviso all'80%).

> 💡 Il budget **avvisa e basta**: non ferma le risorse e non blocca la spesa.

---

## 6. ELIMINO E CONFERMO

Il lock blocca anche l'eliminazione di quello che c'è dentro il gruppo, budget compreso. Prima si toglie il lock.

```bash
LOCK_ID="$(az lock list --resource-group "$LAB_RG" --query "[?name=='lock-cea-delete'].id | [0]" --output tsv)"
test -n "$LOCK_ID" && az lock delete --ids "$LOCK_ID"
az lock list --resource-group "$LAB_RG" --output table    # deve essere vuoto

az group delete --name "$LAB_RG" --yes --no-wait
az group wait --name "$LAB_RG" --deleted
az group exists --name "$LAB_RG"                          # atteso: false
```

Poi da Entra ID elimina il gruppo e l'utente di prova. L'Owner ereditato non si tocca.

---

## 7. Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `ResourceGroupNotFound` | usato `$LAB_SUFFIX` al posto di `$LAB_RG` | usare il nome completo |
| `--scope can't be an empty string` | `RG_SCOPE` non ancora valorizzata | prima `RG_SCOPE=$(az group show ...)` |
| `ScopeLocked` su delete | c'è un lock CanNotDelete | è il comportamento atteso, togliere il lock prima del cleanup |
| `AuthorizationFailed` | manca il ruolo sullo scope | `az role assignment list --include-inherited` e ruolo minimo sullo scope giusto |

## Regole da ricordare

- ruoli ai **gruppi**, scope **minimo**
- autenticazione ≠ autorizzazione ≠ lock
- il budget avvisa, non blocca
- ID di sottoscrizione e tenant mai nelle consegne
