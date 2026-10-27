# Guida comandi — UD09

Fondamenti DevOps e Azure DevOps: Organization, Project, Agent Pool e self-hosted agent registrato con PAT.

---

## 1. PREPARO

```bash
export COURSE_UD09="$HOME/workspace/azure-devops-k8s-01/UD09/partecipanti"
export LAB_REPO="$HOME/workspace/azure-devops-lab"
export LAB_SUBMISSION="$LAB_REPO/consegne/UD09"
export AGENT_DIR="$HOME/azdo-agent"
```

⚠️ `read -r -p "..." VAR` è sintassi bash: in zsh dà `no coprocess`. In zsh si scrive `read -r "VAR?Domanda: "` oppure si fa l'export diretto.

---

## 2. AZURE DEVOPS (portale)

```text
dev.azure.com → Organization (collegata alla subscription) → Project privato, Git, Agile
Project settings → Agent pools → Add pool → Self-hosted → pool-ud09-wsl   (accesso a tutte le pipeline: NO)
Organization settings → Pipelines → Parallel jobs                         (self-hosted 1, hosted da documentare)
User settings → Personal access tokens → New Token → Custom defined → Agent Pools: Read & manage
```

Il nome dell'organization è la parte dopo `dev.azure.com/` nell'URL del browser.

---

## 3. INSTALLO L'AGENT (fuori dal repo)

```bash
mkdir -p "$AGENT_DIR" && cd "$AGENT_DIR"           # PRIMA entro nella cartella
curl -fL 'https://download.agent.dev.azure.com/agent/5.281.0/vsts-agent-linux-x64-5.281.0.tar.gz' -o agent.tar.gz
tar xzf agent.tar.gz
sudo ./bin/installdependencies.sh
./config.sh
```

| Domanda di config.sh | Risposta |
|---|---|
| licenza Team Explorer | N, serve solo per TFVC |
| URL server | `https://dev.azure.com/NOMEORG` **senza progetto** |
| autenticazione | INVIO = PAT, incollato una volta sola |
| pool | `pool-ud09-wsl` |
| agent name, work folder | default |

---

## 4. AVVIO E VERIFICO

```bash
cd "$AGENT_DIR"
./run.sh                    # "Listening for Jobs" = Online, il terminale resta occupato
```

- Ctrl+C → Offline nel portale, `./run.sh` di nuovo → Online. **Non** si rifà `config.sh`
- dopo la registrazione il PAT si **revoca**: l'agent resta Online con le sue credenziali in `.credentials`
- `gh` e `git fetch` vanno lanciati da `$LAB_REPO`, non dalla cartella dell'agent

---

## 5. DIAGNOSI AGENT OFFLINE

```text
run.sh acceso? → rete HTTPS → URL organization → pool → cartella agent (.agent, .credentials) → ./run.sh --diagnostics e _diag/
```

Rimuovere e registrare di nuovo è l'ultima cosa, non la prima.

---

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `read: -p: no coprocess` | sintassi bash in zsh | export diretto |
| agent estratto nel repo | `tar` lanciato dalla cartella sbagliata | spostare tutto in `$AGENT_DIR` prima di `config.sh` |
| `VS30063: You are not authorized` | URL con anche il progetto, PAT incollato a metà | solo `https://dev.azure.com/NOMEORG`, PAT intero |
| `./run.sh~cd: file non esistente` | due comandi incollati attaccati | un comando per riga |
| `non è un repository Git` | `git fetch` da `~/azdo-agent` | `cd "$LAB_REPO"` |
| PAT incollato in chat | | revocarlo subito e crearne uno nuovo |
