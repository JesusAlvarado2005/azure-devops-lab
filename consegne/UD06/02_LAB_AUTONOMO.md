# UD06 — Consegna laboratorio autonomo

## 1. Baseline

- VM: vm-ud06-linux in esecuzione in italynorth con size Standard_F1als_v7 e IP privato 10.60.0.4
- Nginx: active, dentro la VM curl su localhost dà HTTP/1.1 200 OK
- HTTP: dal mio PC curl -I sull'IP pubblico dà HTTP/1.1 200 OK con Server nginx/1.24.0 (Ubuntu)
- regola NSG: Allow-HTTP-MyIP con priorità 310 Inbound TCP porta 80 solo dal mio IP pubblico, oltre a Allow-SSH-MyIP 300 sulla porta 22

Il curl con 200 OK l'ho registrato dopo il ripristino perché la prima volta la regola del guasto era rimasta Allow e non avevo salvato il test prima. Lo stato è lo stesso della baseline cioè solo le regole 300 e 310.

## 2–4. Guasto, diagnosi, ripristino

- regola introdotta: Deny-HTTP-Auto con priorità 200 Inbound TCP dal mio IP sulla porta 80 con azione Deny. Dal portale all'inizio era rimasta l'azione Allow quindi la regola non bloccava niente anche se si chiamava Deny. L'ho corretta con az network nsg rule update --access Deny
- sintomo: curl -I verso l'IP pubblico della VM va in timeout dopo 10 secondi, cioè i pacchetti vengono scartati senza risposta
- ipotesi: il servizio funziona ma qualcosa sul percorso blocca la porta 80, probabilmente una regola NSG con priorità più bassa della Allow 310
- controllo: con ssh dentro la VM Nginx risulta active e curl su localhost dà HTTP/1.1 200 OK quindi il servizio è a posto. Le route effettive sono solo quelle di sistema con 0.0.0.0/0 verso Internet quindi non è il routing. Nel rule list ordinato per priorità la 200 Deny sta sopra la 310 Allow sulla stessa porta e la stessa origine. IP Flow Verify Inbound TCP dal mio IP verso 10.60.0.4:80 ha dato Deny con la regola Deny-HTTP-Auto
- causa: la regola Deny 200 corrisponde al traffico HTTP dal mio IP e viene valutata prima della Allow-HTTP-MyIP 310, quindi l'NSG si ferma lì
- correzione minima: ho eliminato solo Deny-HTTP-Auto senza toccare la regola Allow 310 né l'NSG
- verifica: curl -I dal mio PC dà di nuovo HTTP/1.1 200 OK, IP Flow Verify dà Allow con la regola Allow-HTTP-MyIP e nel rule list restano solo Allow-SSH-MyIP 300 e Allow-HTTP-MyIP 310

## 5. Monitoring

- metrica: Percentage CPU della VM
- intervallo: ultime 4 ore con un punto ogni 5 minuti
- aggregazione: Average e per confronto Maximum
- deduzione: la VM è quasi ferma, la CPU media resta intorno allo 0,2% per quasi tutto il tempo. C'è un picco con massimo del 20% intorno alle 12:47 ora italiana che coincide con l'installazione di Nginx, e qualche piccolo picco sotto il 5%. Prima delle 12:37 non ci sono dati perché la VM non esisteva ancora. Quindi la size è più che sufficiente per questo carico e non c'è nessun motivo per fare scale up
- cosa non posso dedurre: la CPU non mi dice se Nginx risponde né se gli utenti riescono a raggiungerlo. Durante il guasto NSG la CPU era bassa come sempre perché i pacchetti venivano scartati prima di arrivare alla VM, quindi il grafico sembrava normale mentre il sito non era raggiungibile. Non vedo nemmeno la RAM o lo spazio su disco, che questa metrica non misura, né gli errori dentro l'applicazione. Per quelli servono log o test come curl

## 6. VMSS Autoscale

- min: 1
- default: 1
- max: 4
- metrica: Percentage CPU media di tutte le istanze del Scale Set
- condizione: CPU media maggiore del 70% per 5 minuti
- azione: aggiungere 1 istanza fino al massimo di 4
- perché max=4: il massimo mette un tetto al numero di VM e quindi ai costi. Se arriva un picco di traffico anomalo, un attacco o un bug che tiene la CPU sempre alta, senza un massimo l'autoscale continuerebbe ad aggiungere istanze e la spesa crescerebbe senza controllo. Serve anche a restare dentro la quota di vCPU della sottoscrizione

## 7. App Service scaling

- A: Scale up perché serve una sola istanza più potente quindi cambio tier e non numero di istanze
- B: Azure Monitor Autoscale perché sono io a definire una regola su una metrica con una soglia di CPU
- C: Automatic Scaling perché è la piattaforma a reagire al traffico HTTP senza regole scritte da me, ma solo sui tier che lo supportano
- D: Scale out manuale perché decido io il numero di istanze e lo cambio a mano da 1 a 2

## 8. Backup policy

- frequenza: una volta al giorno
- orario: all'1 di notte
- retention: copie giornaliere per 30 giorni, una copia settimanale per 12 settimane e una mensile per 6 mesi
- motivazione: l'azienda ha molti dati importanti e anche sensibili, quindi devo poter tornare indietro anche di mesi se un problema viene scoperto tardi. Faccio il backup di notte perché l'azienda è chiusa e i servizi sono poco usati, così non rallento il lavoro. Non tengo tutte le copie giornaliere per 6 mesi perché costerebbe troppo, quindi tengo le giornaliere per un mese e le più vecchie solo una a settimana o una al mese. Con un backup al giorno nel caso peggiore perdo le modifiche di un giorno, se serve meno bisogna fare backup più frequenti o usare la replica

## 9. HA / Backup / DR

- A: HA perché si guasta una sola istanza e il servizio deve continuare sulle altre
- B: Backup perché i dati sono stati cancellati e devo tornare a uno stato precedente con un recovery point
- C: DR perché la region intera non è disponibile e il workload deve ripartire in un'altra region con il failover

## 10. RPO / RTO

- RPO: 15 minuti, cioè al massimo posso perdere gli ultimi 15 minuti di dati. Un backup al giorno non basta e serve una replica o un backup almeno ogni 15 minuti
- RTO: 60 minuti, cioè entro un'ora dal guasto il servizio deve tornare a funzionare
