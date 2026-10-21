# UD07 — Verifica

## Parte A

1. A perché --query estrae solo le proprietà che chiedo dal JSON
2. B perché tsv stampa solo il valore senza virgolette
3. B perché i comandi restituiscono oggetti con proprietà
4. A perché registra le operazioni di gestione sulle risorse e sulla sottoscrizione
5. B perché decide quali dati mandare e verso quale destinazione
6. B
7. B perché dice cosa fare quando scatta l'alert
8. B perché viene valutata ma scatta solo se la condizione è vera

## Parte B

9. L'Activity Log registra le operazioni di gestione sulle risorse, cioè chi ha creato modificato o eliminato cosa, quando e con quale esito. Le metriche sono valori numerici nel tempo come CPU o transazioni. I Logs sono record dettagliati di cosa succede dentro una risorsa o un'applicazione e si interrogano con KQL in Log Analytics.

10. Una procedura è idempotente se eseguita una o più volte arriva sempre allo stesso stato. Per esempio il mio script controlla con az group exists se rg-ud07-auto esiste, se no lo crea e se sì lo riusa, poi mette i tag. Eseguito due volte non crea doppioni e non dà errori.

11. table fa una tabella da leggere a occhio. tsv stampa solo i valori senza virgolette né intestazioni ed è comodo per metterli in una variabile, come ho fatto con customerId e ID dello storage account.

12. Il workspace è il posto dove i log vengono salvati e interrogati con KQL. La diagnostic setting è la regola che decide quali dati di una risorsa mandare e dove. Il workspace da solo non riceve l'Activity Log se non c'è una diagnostic setting che ce lo manda.

13. L'alert rule dice cosa osservare e quando la condizione è vera, per esempio Transactions sopra una soglia ogni 5 minuti. L'action group dice cosa fare quando scatta, come mandare una mail o chiamare un webhook, e si può usare per più alert.

14. Perché due eventi vicini nel tempo possono essere solo una coincidenza o avere un'altra causa in comune. Per dire che uno ha causato l'altro servono prove sul collegamento tecnico tra i due.

## Parte C

15. Posso dire solo che alle 10:15 la risorsa è stata modificata, che alle 10:16 l'Activity Log mostra una write riuscita, che alle 10:20 la metrica aumenta e che alle 10:25 l'alert è Fired. So l'ordine degli eventi ma non che la modifica abbia causato l'alert.

16. Devo vedere cosa è stato modificato di preciso nella write, se la metrica dell'alert è collegata tecnicamente a quella modifica e se i log mostrano qualcosa di coerente. Poi controllo se ci sono altre cause nello stesso periodo, come più traffico. Se faccio rollback e la metrica torna normale, o se rifacendo la modifica il problema si ripete, allora ho una prova di causalità.

---

## Cleanup finale della UD07

- diagnostic setting subscription: rimossa, az monitor diagnostic-settings subscription list non restituisce più niente
- `rg-ud07-cli-test`: eliminato dopo aver controllato tag e che fosse vuoto
- `rg-ud07-ps-test`: eliminato, era vuoto con i tag ManagedBy=PowerShell e UD=07
- `rg-ud07-auto`: assente
- `rg-ud07-auto-ps`: assente
- `rg-ud07-monitor`: eliminato con workspace, storage account, action group e alert, az group exists dà false
- controllo finale Resource Group UD07: nessun residuo, resta solo NetworkWatcherRG
