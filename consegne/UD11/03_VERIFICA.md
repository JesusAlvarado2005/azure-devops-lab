# UD11 — Verifica

## Parte A

1. B
2. B
3. A
4. B
5. A
6. A
7. B
8. B

## Parte B

9. il tag è un'etichetta leggibile come v2 ma si può spostare su un'altra immagine, il digest è lo sha256 che identifica proprio quel contenuto e non cambia

10. l'Environment è l'ambiente dove vivono le app, la Container App è l'applicazione con immagine e configurazione, la revision è una versione fissa di quella configurazione e la replica è l'istanza che gira davvero

11. perché con la managed identity non ci sono username e password da salvare, l'app ha la sua identità e le do solo AcrPull con RBAC, l'admin user è un segreto statico che dà accesso a tutto il registry

12. perché l'immagine fa parte della configurazione della revision, se la cambio Azure crea una nuova versione, come da v1 a v2

13. la porta dove ascolta il backend e il target port dell'ingress, se il backend è sulla 8000 anche il target port deve essere 8000

14. ingress external, target port uguale alla porta dell'app, revision attiva e Healthy, ci sono repliche, log dell'app con la porta di ascolto, immagine e tag presenti in ACR, identità con AcrPull e variabili d'ambiente

15. perché prima devo capire cosa fa ogni passaggio, chi fa push, chi fa pull, con che identità e su che porta, poi la pipeline automatizza una cosa che ho già capito

16. perché in RBAC+ABAC AcrPull non vale per i repository e servono i ruoli nuovi come Container Registry Repository Reader, il ruolo giusto dipende da come è configurato il registry

17. i passaggi che ho fatto a mano sono gli stessi che farà la pipeline, in UD13 si prepara infrastruttura e CI e in UD14 l'agent farà test, build, push in ACR, update della Container App e smoke test

18. la system-assigned nasce e muore con la risorsa, se elimino la Container App sparisce anche lei, la user-assigned è una risorsa a parte che si crea prima e si può usare su più risorse

## Parte C

19. il target port è 9000 ma il backend ascolta sulla 8000, quindi l'ingress manda il traffico dove non c'è nessuno. L'immagine e la revision sono a posto, la correzione minima è rimettere il target port a 8000 con `az containerapp ingress update`

20. ricontrollo l'ingress che dica 8000, la revision attiva e Healthy, curl su /health con 200 e version v2 e anche /api/products, e guardo i log che non ci siano errori

## Cleanup finale

- resource list verificata: sì, solo ACR, Log Analytics, Environment e Container App di UD11, tag Course=AZ104 e UD=11
- Resource Group eliminato: sì, rg-ud11-containers
- `az group exists` = false: sì
- immagini Docker locali UD11 rimosse: sì, ud11-v1, ud11-v2 e i tag con il login server dell'ACR
- prune globale usato: NO
