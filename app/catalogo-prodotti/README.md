# Catalogo prodotti locale

Applicazione didattica senza dipendenze Python esterne.

## Avvio

Dalla directory `catalogo-prodotti`:

```bash
python3 server.py
```

Output atteso:

```text
Catalogo prodotti in ascolto su http://127.0.0.1:8000
```

## Test

In un secondo terminale:

```bash
curl -i http://127.0.0.1:8000/health
```

```bash
curl -s http://127.0.0.1:8000/api/products | python3 -m json.tool
```

```bash
curl -s http://127.0.0.1:8000/api/products/P001 | python3 -m json.tool
```

Aprire nel browser:

```text
http://127.0.0.1:8000/
```

## Stop

Nel terminale del server:

```text
Ctrl+C
```

## Architettura

```text
Browser/curl
   |
server.py
   |
   +--> config.json
   +--> data/products.json
   +--> static/index.html
```
