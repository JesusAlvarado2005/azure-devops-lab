# UD06 — Verifica

## Parte A

1. A perché la NIC è la scheda di rete della VM ed è lei a stare in una subnet con il suo IP privato.
2. B perché il VM Scale Set gestisce un gruppo di VM uguali e può aumentarle o diminuirle con l'autoscaling.
3. B perché aumento il numero di istanze e non la potenza di una sola.
4. A perché è il piano a decidere tier e capacità e la Web App gira sopra il piano.
5. B perché Autoscale lavora con regole su metriche come la CPU media sopra una soglia.
6. B perché le metriche sono numeri nel tempo mentre i log sono record con più dettaglio che si interrogano con KQL.
7. A perché nel Recovery Services vault vengono gestite la protezione e le policy e vengono conservati i recovery point.
8. B perché Site Recovery replica le VM in un'altra region e permette failover e failback, quindi serve al Disaster Recovery.

## Parte B

9. Le Availability Zone sono datacenter fisicamente separati dentro la stessa region, ognuno con alimentazione e rete proprie. Se metto le VM in zone diverse il guasto di una zona non le ferma tutte. L'Availability Set lavora dentro un solo datacenter e distribuisce le VM su fault domain diversi, cioè rack con alimentazione e switch diversi, e su update domain diversi così la manutenzione non riavvia tutte le VM insieme. Il VM Scale Set gestisce un gruppo di VM uguali create dalla stessa configurazione e può cambiarne il numero a mano o con l'autoscaling in base al carico.

10. Scale up vuol dire rendere più potente la stessa VM cambiando size, per esempio da 2 a 4 vCPU. Di solito serve un riavvio e c'è comunque un limite alla size più grande. Scale out vuol dire aggiungere altre istanze uguali che rispondono allo stesso servizio. Così non dipendo da una sola macchina, ma serve qualcosa che divida il traffico e l'applicazione non deve tenere dati di sessione su una sola istanza.

11. Tutti e due aumentano o diminuiscono le istanze. Con Azure Monitor Autoscale sono io a scrivere le regole su metriche come la CPU o su orari e a decidere minimo e massimo. Con Automatic Scaling invece è la piattaforma a reagire da sola al traffico HTTP e io imposto solo cose come le istanze sempre pronte e il limite massimo. Automatic Scaling è disponibile solo su alcuni tier.

12. L'High Availability tiene attivo il servizio quando si guasta un componente, grazie a più istanze per esempio in zone diverse, quindi riduce il downtime. Il backup è una copia per tornare a uno stato precedente se i dati vengono cancellati o rovinati, ma non evita che il servizio si fermi durante un guasto. Il Disaster Recovery serve a far ripartire l'intero servizio in un'altra region quando quella principale non è disponibile, per esempio replicando le VM e facendo il failover.

13. Il Recovery Services vault è la risorsa dove si gestisce la protezione delle VM e dove sono conservati i backup. La backup policy decide ogni quanto fare il backup, a che ora e per quanto tempo tenere le copie cioè la retention. Il recovery point è la singola copia prodotta da un backup, cioè uno stato della VM in un certo momento a cui posso tornare.

14. L'RPO dice quanti dati posso permettermi di perdere, misurato in tempo. Se l'RPO è 15 minuti posso perdere al massimo gli ultimi 15 minuti di dati, quindi devo copiare i dati almeno ogni 15 minuti. L'RTO dice in quanto tempo il servizio deve tornare a funzionare dopo il guasto, cioè quanto può restare fermo prima che diventi un problema serio.

## Parte C

15. La causa è l'ordine di priorità. Le due regole sono sulla stessa porta 80 e dalla stessa origine, ma Deny-HTTP ha priorità 100 e viene valutata prima di Allow-HTTP 300. La richiesta corrisponde alla 100 e l'NSG si ferma lì, quindi la 300 non viene mai letta. Il servizio non c'entra perché Nginx risponde a curl localhost e la VM è running. Non è un conflitto di regole, che ci sarebbe solo con la stessa priorità.

16. La correzione minima è eliminare solo Deny-HTTP se non serve, oppure dare alla regola Allow un numero più basso di 100, senza cambiare porta, aprire ad Any o togliere l'NSG. Poi verifico con il rule list ordinato per priorità che la Allow venga prima, con IP Flow Verify Inbound TCP dal mio IP verso l'IP privato della VM sulla porta 80 che deve dare Allow con Allow-HTTP, e alla fine con curl dall'esterno sull'IP pubblico che deve dare HTTP 200 da Nginx. Quest'ultimo è il test end-to-end perché prova tutto il percorso fino al servizio.
