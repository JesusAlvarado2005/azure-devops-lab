# Consegna UD05 — Domande sui concetti

Per ciascuna domanda 1–8 riporta una risposta motivata.

1. Perché una volta collegate le due reti devono sapere dove mandare ogni pacchetto. Se i CIDR si sovrappongono lo stesso indirizzo esiste in tutte e due le VNet e non si capisce se il pacchetto va da una parte o dall'altra. Per questo Azure non permette nemmeno di creare il peering tra VNet con spazi sovrapposti.

2. È più grande la /24. Il numero dopo la barra dice quanti bit sono fissi per la rete e quelli che restano sono per gli indirizzi. Con /24 restano 8 bit cioè 256 indirizzi, con /26 ne restano 6 cioè 64. Più il numero è piccolo più la rete è grande.

3. Perché l'IP pubblico è solo un indirizzo. Per essere raggiungibile deve essere associato a una risorsa con un servizio in ascolto sulla porta giusta e il traffico deve essere permesso da NSG, route e firewall del sistema operativo. Se uno di questi manca l'IP c'è ma la connessione non arriva.

4. Le regole vengono valutate in ordine di priorità partendo dal numero più basso. Alla prima regola che corrisponde al traffico Azure applica Allow o Deny e si ferma, quindi le regole dopo non vengono più guardate. Le regole predefinite hanno numeri alti e vengono valutate per ultime.

5. Vuol dire che l'NSG si ricorda delle connessioni che ha permesso. Se una richiesta è consentita in entrata la risposta può uscire senza bisogno di una regola anche nell'altra direzione. Questo vale solo per la risposta di quella connessione e non permette di aprire una connessione nuova nel verso opposto.

6. Perché quando ci sono un NSG sulla subnet e uno sulla NIC il traffico deve passare tutti e due, come due porte una dopo l'altra. Se la porta della subnet è chiusa non serve a niente che quella della NIC sia aperta. Un Allow in un NSG non annulla un Deny nell'altro.

7. Il DNS traduce un nome in un indirizzo IP ma non decide se il traffico può passare. Il routing decide il percorso del pacchetto cioè verso quale next hop mandarlo, per esempio facendo passare tutto da un firewall. L'NSG è un filtro che permette o blocca il traffico in base a origine, destinazione, porta e protocollo. Sono tre controlli diversi e il traffico funziona solo se sono a posto tutti e tre.

8. Perché IP Flow Verify simula un pacchetto da o verso la scheda di rete di una VM e dice quale regola NSG lo permette o lo blocca. Senza una VM con la sua NIC accesa non c'è niente su cui fare il test. In questa UD non creiamo VM, quindi il test lo faremo in UD06.
