# Guida comandi — UD10

Docker locale: image, container, porte, environment, Compose con frontend e backend, DNS interno, named volume e diagnosi di una variabile sbagliata.

Su Fedora Docker gira direttamente sul sistema: le parti della guida su Docker Desktop e WSL Integration non servono.

---

## 1. PREPARO

```bash
export COURSE_UD10="$HOME/workspace/azure-devops-k8s-01/UD10/partecipanti"   # i materiali, NON consegne/UD10
export LAB_REPO="$HOME/workspace/azure-devops-lab"
export LAB_SUBMISSION="$LAB_REPO/consegne/UD10"

docker version
docker compose version
docker info                 # se fallisce il daemon è spento: systemctl status docker
```

---

## 2. IMAGE E CONTAINER SINGOLO

```bash
cd "$LAB_REPO/app/catalogo-prodotti"
docker build --tag catalog-backend:ud10 --file docker/backend.Dockerfile .    # il punto = build context
docker history catalog-backend:ud10

docker run --detach --name catalog-backend-ud10 --publish 127.0.0.1:8000:8000 --env LOW_STOCK_THRESHOLD=5 catalog-backend:ud10
docker ps --filter name=catalog-backend-ud10
docker logs catalog-backend-ud10
curl -i http://127.0.0.1:8000/health
docker inspect catalog-backend-ud10 --format '{{range .Config.Env}}{{println .}}{{end}}' | command grep -E 'APP_PORT|LOW_STOCK|RUNTIME_DIR'

docker stop catalog-backend-ud10 && docker rm catalog-backend-ud10
```

| Dockerfile | Cosa fa |
|---|---|
| `FROM python:3.13-slim` | immagine base leggera |
| `WORKDIR /app` + `COPY` | copia server.py |
| `RUN useradd ...` + `USER appuser` | non gira come root |
| `ENV` | valori di default, il compose li può sostituire |
| `EXPOSE 8000` | documenta la porta, **non** la pubblica |
| `CMD` | il comando che parte quando avvii il container |

---

## 3. COMPOSE (sempre dalla cartella di compose.yaml)

```bash
cd "$LAB_REPO/app/catalogo-prodotti"
docker compose config          # configurazione reale
docker compose build
docker compose up -d
docker compose ps              # backend (healthy), frontend su 127.0.0.1:8080
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/api/products/XXX     # 404 corretto

docker compose exec frontend getent hosts backend                    # DNS di Docker
docker compose exec frontend sh -c 'wget -qO- http://backend:8000/health'
docker compose exec frontend sh -c 'wget -qO- http://localhost:8000/health'   # refused: localhost = frontend stesso
```

- il backend ha solo `expose`, non è raggiungibile da fuori: ci passa Nginx
- `depends_on: service_healthy` → il frontend parte solo quando il backend è healthy
- running non vuol dire healthy

---

## 4. CONFIGURAZIONE E VOLUME

| Cambio | Comando |
|---|---|
| environment, porte, volumi nel compose | `docker compose up -d` (ricrea il container) |
| codice o Dockerfile | `docker compose up -d --build` |

```bash
curl -s http://127.0.0.1:8080/api/counter     # 1, 2, 3
docker compose down                            # toglie container e rete, il volume RESTA
docker compose up -d
curl -s http://127.0.0.1:8080/api/counter     # 4: il dato è nel named volume
```

---

## 5. DIAGNOSI

```text
docker compose ps -a → docker compose logs backend → docker compose config → causa → fix minimo → up -d → test
```

`LOW_STOCK_THRESHOLD: "not-a-number"` → il backend fa `int()` all'avvio e va in `ValueError`, non diventa healthy e il frontend non parte. Fix: rimettere `"5"`, **niente rebuild**.

---

## 6. ELIMINO E CONFERMO

```bash
docker compose down
docker volume ls                       # il volume c'è ancora
docker compose down -v                 # ora anche il volume
docker image rm catalog-backend:ud10 catalog-frontend:ud10
docker ps -a
```

⚠️ Mai `docker system prune -a --volumes`: cancella anche roba di altri progetti.

---

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| test "Materiali UD10" non stampa niente | `COURSE_UD10` messo su `consegne/UD10` | percorso dei materiali del corso |
| `rg: error parsing flag -E` | `grep` è ripgrep | `command grep -E` |
| `no configuration file provided` | `docker compose` dalla root del repo | `cd app/catalogo-prodotti` |
| `Fast forward non possibile` dopo il merge | commit del guidato non pushato e poi finito nello squash | controllato che origin/main avesse tutto e riallineato main |
| VS Code propone di installare Task | suggerimento di un'estensione | non serve per il corso |
