# Guida comandi — UD08

Git collaborativo e Catalogo prodotti: branch, Pull Request, review, merge, conflitti e test HTTP. Le basi di git sono in `laboratori/UD02/guida-comandi.md`.

---

## 1. Le tre aree di git

```text
working tree --git add--> staging area --git commit--> repo locale --git push--> GitHub
```

```bash
git status --short
git diff                 # cosa ho cambiato e NON è ancora in staging
git diff --cached        # cosa entrerà nel prossimo commit
git add <file>           # mai "git add ." alla cieca
git commit -m "..."
git push
```

---

## 2. BRANCH

```bash
git switch main
git pull --ff-only                       # parto da main aggiornata
git switch -c fix/ud08-api-prefix        # crea ED entra
git switch fix/ud08-api-prefix           # entra in uno che esiste già (senza -c)
git branch --show-current
git push -u origin HEAD                  # HEAD = il branch dove sono
```

⚠️ I `<valore>` della guida sono segnaposto: in zsh `<` e `>` sono redirezioni e danno `parse error`.

---

## 3. PULL REQUEST E REVIEW

```bash
gh pr create --base main --head fix/ud08-api-prefix --title "..." --body "..."
gh pr diff 2                             # controllare file, contenuto, segreti
gh pr merge 2 --squash --delete-branch
git switch main && git pull --ff-only && git log --oneline -5
```

| Termine | Significato |
|---|---|
| **base** | branch che riceve, di solito `main` |
| **head** | branch con la proposta |
| Request changes | il merge aspetta le correzioni |
| nuovo commit sul branch | compare **da solo** nella stessa PR |

Collaboratore: `Settings → Collaborators` per invitare e poi **rimuovere** a fine lavoro. Branch remoto finito: `git push origin --delete <branch>`.

Per lavorare sul repo di un altro:

```bash
git clone https://github.com/<utente>/<repo>.git repo-a      # senza nome finale la cartella si chiama come il repo
cd repo-a
git remote -v                                                 # controllo di essere nel repo giusto
```

---

## 4. CONFLITTO

```bash
git switch -c lab/conflict-base && echo "PORT=8000" > ud08-conflict.txt && git add ud08-conflict.txt && git commit -m "base"
git switch -c lab/conflict-a    && echo "PORT=9000" > ud08-conflict.txt && git commit -am "9000"
git switch lab/conflict-base && git switch -c lab/conflict-b && echo "PORT=7000" > ud08-conflict.txt && git commit -am "7000"
git merge lab/conflict-a        # CONFLITTO
cat ud08-conflict.txt           # <<<<<<< HEAD ... ======= ... >>>>>>> lab/conflict-a
nano ud08-conflict.txt          # togliere TUTTI i marker e lasciare il contenuto giusto
grep -c '<<<<<<<' ud08-conflict.txt   # deve dare 0
git add ud08-conflict.txt && git commit -m "lab: resolve port conflict"
```

⚠️ `git add` subito dopo il conflitto committa il file **con i marker dentro**: prima si modifica il file.

---

## 5. CATALOGO PRODOTTI

```text
app/catalogo-prodotti/
├── server.py           backend/API, un solo programma Python
├── config.json         host, port, api_prefix, low_stock_threshold
├── data/products.json  i dati, non c'è un database
└── static/index.html   frontend, fetch("/api/products")
```

```bash
cd ~/workspace/azure-devops-lab/app/catalogo-prodotti
python3 server.py                                     # Ctrl+C per fermarlo

# da un secondo terminale
curl -i http://127.0.0.1:8000/health                  # 200
curl -i http://127.0.0.1:8000/api/products            # 200
curl -i http://127.0.0.1:8000/api/products/P001       # 200
curl -i http://127.0.0.1:8000/api/products/XXX        # 404, corretto
curl -i -X POST http://127.0.0.1:8000/api/products    # 501, c'è solo do_GET
```

Gli endpoint stanno in `do_GET` dentro `server.py`: ogni `if path == ...` è un endpoint, e il prefisso arriva da `api_prefix` in `config.json`.

---

## 6. Il guasto del contratto API

| Test | Con `api_prefix: /api-v2` |
|---|---|
| `/health` | 200, il server è acceso |
| `/api-v2/products` | 200 |
| `/api/products` | 404 |
| frontend | vuoto, perché chiama ancora `/api/products` |

Fix minimo: rimettere `/api`. Dopo il fix `git diff` è **vuoto** perché il file è tornato uguale a main.

---

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| `cd: repo-a non esistente` | clone senza nome cartella | entrare nella cartella col nome del repo |
| `parse error near \n` | `<valore>` scritto davvero | togliere `<` e `>` |
| `a branch named ... already exists` | branch già creato | `git switch` senza `-c` |
| `can't open file .../app/server.py` | cartella sbagliata | `cd app/catalogo-prodotti` |
| test -d `.git` falso | `LAB_REPO="$PWD"` dalla cartella del corso | percorso completo del repo personale |
| marker nel commit | `git add` senza risolvere | modificare il file prima di `git add` |
