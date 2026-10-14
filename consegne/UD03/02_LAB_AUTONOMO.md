# Consegna UD03 — Laboratorio autonomo

## Analisi dell'accesso

Per il team FinOps userei un gruppo di sicurezza come principal, il ruolo Reader e come scope il solo resource group dell'ambiente applicativo. Il gruppo permette di gestire l'accesso aggiungendo o togliendo persone senza toccare i permessi su Azure. Reader basta perché il team deve solo consultare costi e risorse. Contributor non va bene perché permetterebbe di modificare le risorse, Owner ancora meno perché oltre a modificare permetterebbe anche di gestire gli accessi. Come scope scelgo il resource group perché è il livello più piccolo che copre tutto l'ambiente. Sulla sottoscrizione il team vedrebbe anche tutti gli altri resource group, mentre su una singola risorsa vedrebbe solo un pezzo dell'ambiente.

| Principal | Ruolo | Scope |
|---|---|---|
| gruppo del team FinOps (Group) | Reader | resource group dell'ambiente applicativo |

Nel mio laboratorio questa assegnazione corrisponde a quella creata nel guidato. Ho ricostruito tutte le assegnazioni che valgono sul resource group rg-cea-identity-c3f11a, comprese quelle ereditate, con la CLI e poi nel portale da Access control (IAM) → Role assignments, dove compaiono le stesse due righe.

```bash
az role assignment list --scope "$RG_SCOPE" --include-inherited --query "[].{Role:roleDefinitionName,PrincipalType:principalType,Scope:scope}" --output table | sed -E 's#/subscriptions/[^/ ]+#/subscriptions/<omitted>#g'
```

| Principal anonimizzato | Ruolo | Scope | Origine | Accesso effettivo |
|---|---|---|---|---|
| grp-cea-readers-c3f11a (Group) | Reader | /subscriptions/<omitted>/resourceGroups/rg-cea-identity-c3f11a | diretta, lo scope è esattamente il resource group | i membri del gruppo possono leggere il resource group ma non modificarlo |
| il mio account (User) | Owner | /subscriptions/<omitted> | ereditata, lo scope è la sottoscrizione che sta sopra il resource group | controllo completo sul resource group, compresa la gestione degli accessi |

Per capire se un'assegnazione è diretta o ereditata ho confrontato il suo scope con quello del resource group: se è uguale è diretta, se è più in alto è ereditata. L'assegnazione Reader non riduce i privilegi più ampi che uno ha già. In RBAC i permessi si sommano, quindi se il mio account fosse anche nel gruppo dei lettori resterebbe comunque Owner per l'eredità dalla sottoscrizione.

## Diagnosi dei casi

**Caso A**, Please run 'az login' to setup account.
- sintomo: qualsiasi comando az viene rifiutato e chiede di fare il login
- causa probabile: la CLI non ha una sessione attiva, perché è scaduta, ho fatto logout oppure non ho mai fatto il login in quel terminale. È un problema di autenticazione, Azure non sa chi sono
- verifica: az account show
- correzione: az login --use-device-code, completando l'MFA nel browser
- risultato atteso: az account show mostra di nuovo Azure subscription 1 Enabled, e controllo che sia la sottoscrizione giusta prima di continuare

**Caso B**, AuthorizationFailed ... Microsoft.Authorization/roleAssignments/write
- sintomo: il tentativo di creare un'assegnazione di ruolo viene rifiutato
- causa probabile: il mio account è autenticato ma non ha il permesso di scrivere assegnazioni di ruolo su quello scope. È un problema di autorizzazione RBAC. Questo permesso ce l'hanno ruoli come Owner o User Access Administrator, non Reader o Contributor
- verifica: az role assignment list sullo scope per vedere quali ruoli ho davvero lì
- correzione: chiedere a chi è Owner di creare l'assegnazione o di darmi il ruolo necessario. Rifare il login non serve perché rinnova la sessione ma non aggiunge permessi, e non bisogna cercare di aggirare il blocco
- risultato atteso: con il ruolo giusto l'assegnazione viene creata e compare in az role assignment list

**Caso C**, ScopeLocked: The scope is locked and can't be deleted.
- sintomo: l'eliminazione viene rifiutata anche se ho i permessi. L'ho visto anche io nel guidato, essendo Owner non sono riuscito a eliminare il resource group
- causa probabile: sullo scope c'è un lock CanNotDelete. Il lock è un blocco di governance e vale per tutti, anche per gli Owner, quindi usare un altro utente non risolve
- verifica: az lock list --resource-group "$LAB_RG" per vedere quale lock c'è e perché è stato messo
- correzione: prima capire se l'eliminazione deve davvero avvenire. Se è prevista e autorizzata, chi ha il permesso di gestire i lock lo rimuove e poi si ripete l'eliminazione. Se non è prevista, il lock ha fatto il suo lavoro e non va tolto
- risultato atteso: dopo la rimozione del lock l'eliminazione va a buon fine e az group exists restituisce false

I tre casi sono su livelli diversi. Il caso A riguarda l'autenticazione, cioè chi sono. Il caso B riguarda l'autorizzazione, cioè cosa posso fare. Il caso C riguarda la governance, cioè un blocco messo apposta che vale per tutti.

## Budget, lock e cleanup

Il budget budget-cea-c3f11a è sul resource group, mensile, con importo 40 e avviso sul costo effettivo impostato all'80%. Quando la spesa supera la soglia arriva una notifica, ma il budget non blocca né le risorse né la spesa, quindi non limita l'utilizzo. In Cost Analysis il costo del mese è 0 euro perché il resource group non contiene risorse a consumo.

Il lock lock-cea-delete di tipo CanNotDelete impedisce di eliminare il resource group ma non di consultarlo. Nel guidato az group delete è stato rifiutato con ScopeLocked, mentre anche con il lock attivo az group show ha letto il gruppo senza problemi.

Il cleanup va fatto in quest'ordine, perché alcuni oggetti bloccano o dipendono da altri:

1. rimuovere per primo il lock lock-cea-delete, perché vale anche per tutto quello che sta dentro il resource group e blocca l'eliminazione del budget e del gruppo stesso. L'ho scoperto provando a cancellare il budget prima del lock e ricevendo l'errore di scope bloccato
2. eliminare il budget budget-cea-c3f11a dal portale
3. rimuovere dal resource group solo l'assegnazione Reader di grp-cea-readers-c3f11a, senza toccare l'Owner ereditato
4. togliere l'utente cea-lab-c3f11a dal gruppo, poi eliminare il gruppo grp-cea-readers-c3f11a e l'utente cea-lab-c3f11a da Entra ID, controllando bene nomi e suffisso
5. eliminare il resource group con az group delete, aspettare con az group wait --deleted e verificare con az group exists, che deve dare false
6. controllare che non siano rimasti budget, assegnazioni, lock, utente o gruppo del laboratorio

## Risultato finale

- output anonimizzati utilizzati: az account show con query su Name, State e IsDefault, az group show, az role assignment list con query su ruolo, tipo di principal e scope e sed per nascondere l'ID della sottoscrizione, az lock list
- cleanup verificato: ho seguito la checklist partendo dal lock. Il lock è stato rimosso, il resource group eliminato con az group exists che restituisce false, e gruppo e utente del laboratorio non risultano più in Entra ID
- hash abbreviato e messaggio del commit: 02b41be Completa laboratorio identita accessi e governance
