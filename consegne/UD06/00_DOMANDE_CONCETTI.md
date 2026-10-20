# UD06 — Risposte alle domande sui concetti

## 1.
**Risposta:** Una VM è fatta di più risorse. L'immagine decide il sistema operativo di partenza e la size decide quante vCPU e quanta RAM ha. Poi c'è il disco del sistema operativo e se serve uno o più dischi dati. Infine la NIC che collega la VM a una subnet e porta l'IP privato, l'eventuale IP pubblico e l'eventuale NSG.

## 2.
**Risposta:** Perché l'IP pubblico è solo un indirizzo e non garantisce che il servizio risponda. Il traffico deve essere permesso dagli NSG su subnet e NIC, non deve essere bloccato dal firewall del sistema operativo e sulla porta ci deve essere un servizio in ascolto come Nginx sulla 80. Se manca uno di questi l'IP c'è ma la connessione non arriva.

## 3.
**Risposta:** Le Availability Zone sono datacenter fisicamente separati dentro la stessa region, con alimentazione e rete proprie. Se metto le VM in zone diverse il guasto di una zona non le ferma tutte. L'Availability Set invece distribuisce le VM dentro lo stesso datacenter su fault domain diversi, cioè rack con alimentazione e rete diverse, e su update domain diversi così la manutenzione non riavvia tutte le VM insieme. Il VM Scale Set gestisce un gruppo di VM uguali create dalla stessa configurazione e può aumentare o diminuire il numero di istanze, anche in automatico con l'autoscaling.

## 4.
**Risposta:** Scale up è la scalabilità verticale e vuol dire rendere più potente la stessa istanza, per esempio passare da 2 a 4 vCPU. Scale out è la scalabilità orizzontale e vuol dire aggiungere altre istanze uguali, per esempio passare da 1 a 3 VM.

## 5.
**Risposta:** Azure Monitor Autoscale cambia il numero di istanze del Scale Set in base a regole su metriche e soglie o in base a orari. Per esempio se la CPU media resta sopra il 70% per 5 minuti aggiunge istanze e quando scende le toglie. Si fissano un minimo, un default e un massimo, e il massimo serve anche a tenere sotto controllo i costi.

## 6.
**Risposta:** L'App Service Plan è la parte che fornisce le risorse e che si paga. Decide region, sistema operativo, tier e capacità cioè quante istanze e quanto potenti. La Web App è l'applicazione vera che gira sopra il piano e sullo stesso piano possono girare più Web App che ne condividono le risorse.

## 7.
**Risposta:** Tutti e due fanno scale out ma in modo diverso. Con Azure Monitor Autoscale sono io a scrivere le regole su metriche o orari e a decidere minimo e massimo delle istanze. Automatic Scaling invece è gestito dalla piattaforma in base al traffico HTTP e io imposto solo cose come le istanze sempre pronte e il limite massimo. È disponibile solo su alcuni tier.

## 8.
**Risposta:** Le metriche sono valori numerici raccolti nel tempo, come percentuale di CPU, traffico di rete o numero di richieste, e servono a vedere subito come sta andando una risorsa e a creare grafici e allarmi. I log sono record con più dettaglio su cosa è successo e quando, che vengono salvati in un Log Analytics workspace e si interrogano con il linguaggio KQL. Con i log si ricostruisce cosa è successo un po' come una scatola nera.

## 9.
**Risposta:** Il Recovery Services vault è la risorsa dove si gestisce la protezione delle VM e dove sono conservati i recovery point. La backup policy decide ogni quanto fare il backup, a che ora e per quanto tempo tenerlo. Il recovery point è la copia prodotta da un backup, cioè uno stato della VM a cui posso tornare se qualcosa si rompe o viene cancellato.

## 10.
**Risposta:** L'High Availability serve a far continuare il servizio quando si rompe un componente, per esempio con più VM in zone diverse, quindi riduce il downtime. Il backup serve a recuperare dati o uno stato precedente ma non evita che il servizio si fermi durante un guasto. Il Disaster Recovery serve a far ripartire tutto il servizio dopo un evento grave come la perdita di una region, per esempio replicando le VM in un'altra region e facendo il failover.

## 11.
**Risposta:** L'RPO dice quanti dati posso permettermi di perdere, misurato in tempo. Con RPO di 1 ora posso perdere al massimo l'ultima ora di dati, quindi i backup o le repliche devono essere almeno ogni ora. L'RTO dice in quanto tempo il servizio deve tornare a funzionare dopo il problema, per esempio 30 minuti.

## 12.
**Risposta:** Perché deallocate libera solo la parte di calcolo, cioè CPU e RAM, e quella non si paga più. Restano però i dischi che continuano a occupare spazio, l'IP pubblico se è statico o Standard, i backup nel vault e gli altri servizi collegati. Per non pagare niente bisogna eliminare le risorse.
