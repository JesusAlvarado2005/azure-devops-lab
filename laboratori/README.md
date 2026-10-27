# Manuale comandi

Una guida per ogni unità con i comandi usati davvero nei laboratori, organizzati per fase e con gli errori incontrati.

| UD | Argomento | Guida |
|---|---|---|
| UD01 | ambiente di lavoro, Git e GitHub | [nota operativa](UD01/nota-operativa.md), [verifica](UD01/verifica.md), [verifica autonoma](UD01/verifica-autonoma.md) |
| UD02 | Azure CLI, resource group, VNet, storage, basi della shell | [guida-comandi](UD02/guida-comandi.md) |
| UD03 | Entra ID, RBAC, tag, lock, costi e budget | [guida-comandi](UD03/guida-comandi.md) |
| UD04 | Storage account, blob, ruoli dati, SAS, lifecycle | [guida-comandi](UD04/guida-comandi.md) |
| UD05 | VNet, subnet, CIDR, NSG, NIC, diagnosi di rete | [guida-comandi](UD05/guida-comandi.md) |
| UD06 | VM Linux, SSH, Nginx, IP Flow Verify, metriche, App Service | [guida-comandi](UD06/guida-comandi.md) |
| UD07 | script idempotenti, PowerShell, Activity Log, KQL, alert | [guida-comandi](UD07/guida-comandi.md) |
| UD08 | branch, Pull Request, review, conflitti, Catalogo prodotti | [guida-comandi](UD08/guida-comandi.md) |
| UD09 | Azure DevOps, Agent Pool, self-hosted agent, PAT | [guida-comandi](UD09/guida-comandi.md) |

## Il ciclo di ogni laboratorio

```text
CONTROLLO → PREPARO → CREO → VERIFICO → DIAGNOSTICO → ELIMINO E CONFERMO → CONSEGNO
```

## Regole che valgono sempre

- un comando alla volta, mai incollare blocchi con le righe ``` della guida
- nelle consegne niente ID di sottoscrizione o tenant, email, chiavi, token, SAS o password
- prima di eliminare controllo nome, tag e contenuto, poi verifico con `az group exists` → `false`
- correzione minima: tocco solo quello che serve e poi riprovo
