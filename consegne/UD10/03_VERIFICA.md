# UD10 — Verifica

## Parte A

1. B
2. B
3. B
4. B
5. B
6. B
7. B
8. B

## Parte B

9. l'immagine contiene tutto quello che serve per creare il container, il container è il processo vero in esecuzione creato dall'immagine, le porte verso l'host si pubblicano dopo con docker run o nel compose. Il registry è dove si salvano e si scaricano le immagini, come Docker Hub o Azure Container Registry

10. il build context è la cartella che passo a docker build, il punto finale, e viene mandata tutta al daemon. Se è piccola la build è più veloce e non ci finiscono dentro file che non servono o segreti, per questo c'è il .dockerignore

11. il named volume lo crea e lo gestisce Docker, non mi interessa dove sta sul disco e resta anche se tolgo il container, come catalog-runtime per il contatore. Il bind mount invece collega una cartella precisa del mio PC dentro il container, utile per sviluppare ma dipende dal percorso della macchina

12. perché l'immagine è sempre la stessa e cambia solo la configurazione quando creo il container, per esempio LOW_STOCK_THRESHOLD a 5 o 10 senza rifare la build, e così la stessa immagine va bene per ambienti diversi

13. perché il backend deve parlare solo con il frontend sulla rete di Docker, quindi non serve che sia raggiungibile da fuori a differenza del frontend, e meno porte aperte vuol dire più sicurezza

14. docker compose ps -a per vedere lo stato e se è healthy, docker compose logs del servizio che non va, docker compose config per vedere la configurazione vera, e poi curl su /health

## Parte C

15. la variabile LOW_STOCK_THRESHOLD nel compose ha un valore sbagliato, 'abc' non è un numero, quindi il backend va in errore all'avvio e continua a ripartire, e il frontend dà 502 perché dietro non trova il backend. L'immagine è a posto, l'errore è nella configurazione. Modifica minima rimettere un numero, per esempio "5", nel compose.yaml

16. no, non serve ricostruire l'immagine perché si cambia solo il compose, basta docker compose up -d che ricrea il container. Dopo verifico con docker compose ps che il backend sia healthy, i log senza errore e curl su /health e /api/products da 8080 che danno 200

## 17.

il Docker daemon sulla macchina dove gira l'agent, quindi controllo che il servizio docker sia acceso con systemctl status docker e che l'utente che fa girare l'agent possa usarlo, cioè che sia nel gruppo docker. Il self-hosted usa il Docker della mia macchina, se il daemon è spento o l'utente non ha i permessi la build non parte

## 18.

il self-hosted ha solo i tool che ho installato io sulla macchina, come git, python e docker, e li devo tenere aggiornati io. Il Microsoft-hosted ha già un'immagine con tanti tool pronti e la gestisce Microsoft, ma a ogni job la macchina è nuova e non tiene niente tra un job e l'altro

## Cleanup finale

- `docker compose down`: tolti i 2 container e la rete
- volume presente dopo `down`: sì, catalogo-prodotti_catalog-runtime
- `docker compose down -v`: fatto dopo, ha tolto il volume
- volume rimosso: sì, `docker volume ls` non lo mostra più
- immagini UD10 rimosse: sì, catalog-backend:ud10 e catalog-frontend:ud10, `docker ps -a` vuoto
- prune globale usato: NO

