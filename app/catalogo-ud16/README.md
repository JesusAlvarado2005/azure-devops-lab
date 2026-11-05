# Catalogo prodotti containerizzato

## Architettura

```text
Browser / curl
   |
127.0.0.1:8080
   |
frontend (Nginx)
   |
   | /api/* e /health
   v
backend:8000
   |
named volume /runtime
```

## Servizi

### frontend

- immagine base Nginx;
- serve `frontend/index.html`;
- reverse proxy verso `backend:8000`;
- pubblicato solo su `127.0.0.1:8080`.

### backend

- Python standard library;
- API prodotti;
- health endpoint;
- contatore persistente;
- non pubblicato sull'host nel Compose.

## Endpoint dall'host

```text
http://127.0.0.1:8080/
http://127.0.0.1:8080/health
http://127.0.0.1:8080/api/products
http://127.0.0.1:8080/api/products/P001
http://127.0.0.1:8080/api/counter
```

## Avvio

```bash
docker compose up -d --build
```

## Stato

```bash
docker compose ps
```

## Log

```bash
docker compose logs
```

## Stop

```bash
docker compose down
```

## Reset completo dei dati

Solo quando richiesto:

```bash
docker compose down -v
```
