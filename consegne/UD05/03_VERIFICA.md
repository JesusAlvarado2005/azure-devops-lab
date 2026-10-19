# Consegna UD05 — Verifica

## Parte A — Scelta singola

Per le domande 1–8 riporta risposta e motivazione.

1. B perché /24 lascia 8 bit agli indirizzi cioè 256, mentre /26 ne lascia 6 cioè 64.
2. B perché con lo stesso spazio 10.0.0.0/16 un indirizzo esiste in tutte e due le reti e non si sa dove mandare il pacchetto, quindi il peering non si può fare.
3. B perché vince il numero più basso e la 200 viene letta prima della 300.
4. A perché un NSG si associa a una subnet, a una scheda di rete o a tutte e due.
5. A perché il traffico deve passare tutti e due i filtri e un Allow in uno non annulla un Deny nell'altro.
6. A perché il DNS traduce un nome in un indirizzo IP e non filtra né decide il percorso.
7. B perché IP Flow Verify prova un flusso sulla NIC di una VM e dice quale regola lo permette o lo blocca.
8. B perché l'IP pubblico è solo un indirizzo e senza un servizio in ascolto e regole che permettono il traffico la connessione non arriva.

## Parte B — Risposte brevi

9. Perché col tempo si aggiungono macchine o servizi, per esempio altre VM per dividere il traffico, e ognuno prende un indirizzo. In più Azure si riserva 5 indirizzi in ogni subnet. Se la subnet è piena allargarla quando ci sono già le risorse sopra è complicato e può voler dire spostare tutto, quindi conviene dimensionarla da subito con margine.

10. L'NSG è un filtro che permette o blocca il traffico in base a origine, destinazione, porta e protocollo e si applica a subnet o NIC. La route decide il percorso del pacchetto cioè il next hop, per esempio per far passare tutto il traffico da un firewall. Il DNS traduce il nome di un servizio in un indirizzo IP. Sono tre controlli diversi e la connessione funziona solo se sono a posto tutti e tre.

11. Vuol dire che l'NSG si ricorda delle connessioni che ha permesso. Se una richiesta entra con una regola Allow la risposta può uscire da sola senza bisogno di una regola outbound uguale. Questo vale solo per la risposta di quella connessione e non permette di aprire una connessione nuova nel verso opposto.

12. Perché con un solo NSG sulla subnet le stesse regole valgono per tutte le NIC collegate, anche quelle che arriveranno dopo. Le regole stanno in un posto solo e sono uguali per tutti. Con un NSG diverso su ogni NIC invece è facile avere configurazioni diverse, e quando ci sono sia subnet sia NIC il traffico deve passare tutti e due i filtri e un problema è più difficile da trovare.

13. Senza VM posso leggere la configurazione della NIC cioè subnet, IP privato e assenza di IP pubblico, poi l'NSG associato alla subnet o alla NIC, le regole ordinate per priorità e se c'è una route table associata. Manca la prova reale, cioè effective security rules, effective routes e IP Flow Verify, che servono a una NIC collegata a una VM in esecuzione. Quindi so cosa dice la configurazione ma non ho ancora provato un flusso vero.

## Parte C — Caso situazionale

14. Perché l'NSG non guarda il nome delle regole ma solo la priorità. La Deny-Web 150 ha un numero più basso della 400, quindi viene letta prima, corrisponde al traffico TCP 443 da 10.60.10.0/24 e l'NSG si ferma lì. AAA-Allow-Web resta alla 400 e non viene mai raggiunta, qualunque nome abbia.

15. Se la Deny-Web non serve la tolgo, altrimenti sposto la regola Allow a un numero più basso di 150, per esempio 140, lasciando la stessa origine 10.60.10.0/24, TCP e porta 443. In alternativa porto la Deny a un numero più alto di 400. Non uso Internet o Any come origine e non apro altre porte. Dopo controllo con az network nsg rule list ordinato per priorità che l'Allow venga prima del Deny.

16. Controllo che la modifica sia salvata e l'ordine delle regole sia quello giusto, poi se c'è un NSG anche sulla NIC che blocca. Con la VM accesa guardo effective security rules e provo il flusso con IP Flow Verify. Poi guardo le route, cioè se c'è una route table che manda il traffico verso un next hop sbagliato, e le effective routes. Controllo che il nome DNS si risolva nell'IP giusto. Alla fine guardo la VM, cioè se il firewall del sistema operativo blocca la 443 e se il servizio è davvero in ascolto su quella porta.
