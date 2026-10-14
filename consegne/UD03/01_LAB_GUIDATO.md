# Consegna UD03 — Laboratorio guidato

## Contesto anonimizzato

- sottoscrizione e tenant verificati: Azure CLI 2.83.0, az account show mostra Azure subscription 1 attiva con il mio account. ID di sottoscrizione e tenant non riportati
- percorso Entra eseguito: A, perché dal mio account potevo creare utenti e gruppi di sicurezza
- resource group temporaneo: rg-cea-identity-c3f11a in italynorth, creato da CLI con i tag course cloud-engineer-academy, unit UD03, environment lab e deleteAfter 2026-10-15

## Identità e assegnazione RBAC

| Principal anonimizzato | Ruolo | Scope | Diretta/ereditata | Motivo |
|---|---|---|---|---|
| gruppo grp-cea-readers-c3f11a (Group) | Reader | /subscriptions/<omitted>/resourceGroups/rg-cea-identity-c3f11a | diretta | assegnazione creata nel laboratorio per dare sola lettura sul gruppo di risorse |
| il mio account (User) | Owner | /subscriptions/<omitted> | ereditata dalla sottoscrizione | ruolo già presente come proprietario della sottoscrizione, non creato dal laboratorio |

In Entra ID ho creato l'utente cloud cea-lab-c3f11a e il gruppo di sicurezza grp-cea-readers-c3f11a con membership Assigned, poi ho aggiunto l'utente come membro. Per creare utenti e gruppi serve un ruolo amministrativo nella directory, almeno User Administrator, e il mio account lo aveva. La password temporanea dell'utente non l'ho salvata da nessuna parte.

Nel resource group, da Access control (IAM), ho assegnato il ruolo Reader al gruppo e non al singolo utente, così l'accesso si gestisce aggiungendo o togliendo membri dal gruppo. Lo scope è solo il resource group, non tutta la sottoscrizione. Ho verificato da CLI con:

```bash
RG_SCOPE="$(az group show --name "$LAB_RG" --query id --output tsv)"
az role assignment list --scope "$RG_SCOPE" --include-inherited --query "[].{Role:roleDefinitionName,PrincipalType:principalType,Scope:scope}" --output jsonc | sed -E 's#/subscriptions/[^/]+#/subscriptions/<omitted>#g'
```

Il primo tentativo è fallito con "--scope can't be an empty string" perché non avevo ancora valorizzato RG_SCOPE. Dopo averla assegnata il comando ha mostrato due righe: Reader per il gruppo sullo scope del resource group e Owner per il mio account ereditato dalla sottoscrizione.

L'accesso effettivo dipende da tutte le assegnazioni insieme. L'utente cea-lab-c3f11a ha solo Reader tramite il gruppo, quindi può leggere il resource group ma non modificarlo. Il mio account invece resta Owner per ereditarietà: anche se fossi nel gruppo, Reader non toglierebbe nulla, perché in RBAC i permessi si sommano. Per questo una singola riga di role assignment non basta a capire cosa può fare davvero un principal.

## Governance e costi

- tag e significato: course e unit dicono a quale corso e unità appartiene il gruppo, environment lab che è un ambiente di prova, deleteAfter entro quando va eliminato. Servono a riconoscere e ripulire l'ambiente, ma non eliminano niente da soli
- lock e operazione impedita: lock-cea-delete di tipo CanNotDelete sul resource group. Con az group delete --name "$LAB_RG" --yes l'eliminazione è stata rifiutata con errore ScopeLocked, che dice che lo scope è bloccato e che va prima rimosso il lock. Subito dopo az group exists ha restituito true, quindi il gruppo è rimasto
- stato di Cost Analysis: nel mese corrente il costo del resource group è 0 euro. È normale, perché il gruppo non contiene risorse a consumo e i dati di costo arrivano comunque con un po' di ritardo
- budget creato o limitazione documentata: budget-cea-c3f11a sul resource group, mensile, importo 40, con avviso sul costo effettivo all'80%
- motivo per cui il budget non blocca la spesa: il budget serve solo a misurare e avvisare. Quando si supera la soglia arriva una notifica, ma le risorse continuano a funzionare e a costare. Per fermare la spesa serve un intervento manuale o un'automazione separata

## Cleanup

Ho fatto il cleanup dopo il laboratorio autonomo e la verifica. Per prima cosa ho rimosso il lock, perché provando a eliminare il budget ho ricevuto l'errore di scope bloccato: il lock sul resource group vale anche per tutto quello che contiene.

```bash
LOCK_ID="$(az lock list --resource-group "$LAB_RG" --query "[?name=='lock-cea-delete'].id | [0]" --output tsv)"
test -n "$LOCK_ID" && az lock delete --ids "$LOCK_ID"
az lock list --resource-group "$LAB_RG" --output table
```

L'ultimo comando non ha mostrato nessun lock. Poi ho eliminato il resource group, che conteneva anche il budget e l'assegnazione Reader, e ho tolto da Entra ID il gruppo grp-cea-readers-c3f11a e l'utente cea-lab-c3f11a. L'assegnazione Owner ereditata dalla sottoscrizione non l'ho toccata.

```bash
az group delete --name "$LAB_RG" --yes --no-wait
az group wait --name "$LAB_RG" --deleted
az group exists --name "$LAB_RG"
```

az group exists ha restituito false. Nel controllo finale non risultano più resource group rg-cea, gruppi grp-cea né utenti cea-lab.

## Rilevanza professionale

L'autenticazione dice chi sei: è il login con az login o nel portale, gestito da Entra ID. L'autorizzazione RBAC dice cosa puoi fare e dove: per esempio il gruppo ha Reader solo su rg-cea-identity-c3f11a, mentre il mio account ha Owner su tutta la sottoscrizione. Il lock invece è un blocco di governance che vale per tutti, anche per chi è Owner. Infatti io, pur avendo tutti i permessi, non sono riuscito a eliminare il gruppo finché c'era il lock. Tenere separati questi tre livelli aiuta a capire da dove nasce un errore: un problema di login, un permesso mancante o un blocco messo apposta.


## Registro cronologico delle evidenze

| Data/ora | Fase e contesto | Comando o pagina | Risultato reale ripulito | Interpretazione / passo successivo |
|---|---|---|---|---|
| 14/10 11:11 | 1, terminale Fedora | mkdir -p consegne/UD03, az version, az account show | CLI 2.83.0, Azure subscription 1 Enabled | contesto corretto |
| 14/10 11:13 | 1, terminale Fedora | LAB_SUFFIX con openssl rand -hex 3, az group create | rg-cea-identity-c3f11a in italynorth con 4 tag | scope isolato per il laboratorio |
| 14/10 11:21 | 1, terminale Fedora | az group show -n "$LAB_SUFFIX" | ResourceGroupNotFound per c3f11a | avevo usato il suffisso al posto del nome completo, il nome giusto è in LAB_RG |
| 14/10 mattina | 2, Portal | Entra ID, Users e Groups | New user e New group disponibili e creazione riuscita | percorso A |
| 14/10 mattina | 3A, Portal | Users, New user | utente cloud cea-lab-c3f11a | alias non personale, password non conservata |
| 14/10 mattina | 3A, Portal | Groups, New group | gruppo Security grp-cea-readers-c3f11a, Assigned, con membro cea-lab-c3f11a | corretti in seguito uno spazio iniziale nel nome del gruppo e il membro mancante |
| 14/10 11:44 | 4, Portal | IAM, Add role assignment | Reader al gruppo sullo scope del resource group | assegnazione creata |
| 14/10 11:59 | 4, terminale Fedora | az role assignment list con --include-inherited | errore --scope can't be an empty string | RG_SCOPE non ancora valorizzata |
| 14/10 12:04 | 4 e 5, terminale Fedora | RG_SCOPE da az group show, az role assignment list con sed | Reader Group sul resource group, Owner User ereditato dalla sottoscrizione | accesso effettivo dato dalla somma dei ruoli |
| 14/10 mattina | 6, Portal | Cost Management, Cost analysis | costo del mese corrente 0 euro | nessuna risorsa a consumo nel gruppo |
| 14/10 mattina | 6, Portal | Cost Management, Budgets, Add | budget-cea-c3f11a mensile, 40, avviso all'80% | il budget avvisa ma non blocca |
| 14/10 11:58 | 7, Portal e terminale Fedora | Locks Add, az lock list | lock-cea-delete CanNotDelete | lock attivo |
| 14/10 11:58 | 7, terminale Fedora | az group delete --name "$LAB_RG" --yes | ScopeLocked, eliminazione rifiutata | il lock funziona |
| 14/10 11:59 | 7, terminale Fedora | az group exists | true | il gruppo è ancora presente |
| 14/10 16:30 | 9, terminale Fedora | az lock delete con LOCK_ID, az lock list | nessun lock nel resource group | ora il gruppo si può eliminare |
| 14/10 16:38 | 9, terminale Fedora | az group delete --no-wait, az group wait --deleted | wait terminato senza errori | eliminazione completata |
| 14/10 16:40 | 9, terminale Fedora | az group exists | false | resource group eliminato |
| 14/10 17:13 | 9, Portal e terminale Fedora | Entra ID Groups e Users, az ad group list, az ad user list | gruppo grp-cea-readers-c3f11a e utente cea-lab-c3f11a non più presenti | cleanup completo |
