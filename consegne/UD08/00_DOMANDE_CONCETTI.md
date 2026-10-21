# UD08 — Risposte domande concetti

## 1.
**Risposta:** DevOps è un modo di lavorare che unisce sviluppo e operations, cioè chi scrive il codice e chi lo mette in produzione e lo gestisce, con modifiche piccole testate e rilasciate spesso. Azure DevOps invece è un prodotto di Microsoft con repo, board e pipeline che aiuta a lavorare così, ma si può fare DevOps anche con altri strumenti come GitHub.

## 2.
**Risposta:** La Continuous Integration vuol dire integrare spesso nel branch principale piccole modifiche, e ogni volta build e test automatici controllano che non si rompa niente. Con la Continuous Delivery il codice è sempre pronto per il rilascio ma il deploy in produzione parte dopo un'approvazione. Con il Continuous Deployment se passa tutti i controlli va in produzione da solo senza approvazione.

## 3.
**Risposta:** La working tree sono i file su cui sto lavorando in locale. La staging area contiene le modifiche che ho scelto con git add per il prossimo commit. Il commit registra queste modifiche nella cronologia locale con un messaggio. Niente va su GitHub finché non faccio git push.

## 4.
**Risposta:** Perché parto dall'ultima versione e riduco i conflitti. Lavoro isolato senza toccare main né il lavoro degli altri, e se qualcosa va storto main resta pulita. La modifica entra in main solo dopo la Pull Request e la review.

## 5.
**Risposta:** La base branch è quella che riceve la modifica, di solito main. La head branch è quella che contiene la proposta, per esempio feature/catalog-ui. La Pull Request mostra le differenze dalla head verso la base.

## 6.
**Risposta:** Perché un codice che funziona può comunque essere scritto male o essere insicuro. Nella review si controlla anche se la modifica fa quello che serve, se è leggibile e coerente con il resto, se ci sono rischi di sicurezza come segreti nel codice e se è stata testata.

## 7.
**Risposta:** La Pull Request si aggiorna da sola perché segue il branch e non una copia. Il nuovo commit compare nella PR con il diff aggiornato, ed è così che si risponde a una richiesta di modifica della review senza aprire una nuova PR.

## 8.
**Risposta:** Succede quando due branch modificano in modo diverso la stessa riga dello stesso file, oppure uno modifica un file che l'altro ha eliminato. Git non sa quale versione tenere e mette i marker nel file. La decisione la deve prendere una persona.

## 9.
**Risposta:** Per il principio del privilegio minimo. Se l'accesso resta il collaboratore può ancora leggere e scrivere nella mia repo anche quando non serve più, e se il suo account viene compromesso lo è anche la mia repo.

## 10.
**Risposta:** Il frontend è static/index.html, la pagina con il JavaScript che il browser mostra. Il backend è server.py che riceve le richieste HTTP e risponde in JSON. La configurazione è config.json con host, porta, api_prefix e soglia delle scorte. I dati sono data/products.json con i prodotti.

## 11.
**Risposta:** GET /health per lo stato del servizio, GET /api/products per l'elenco dei prodotti, GET /api/products/<id> per un prodotto come P001 che dà 404 se non esiste, e GET / per la pagina HTML. Il prefisso /api viene da api_prefix in config.json.

## 12.
**Risposta:** Perché mostra le righe che ho cambiato prima di registrarle. Così controllo di committare solo quello che volevo, senza file di prova, modifiche per sbaglio o segreti come password e chiavi.

---

# Approfondimento API REST e microservizi

## 1.
**Risposta:** Perché tutti e due sono client HTTP e fanno la stessa richiesta alla stessa API. Il server risponde con lo stesso JSON senza sapere chi lo chiama. Cambia solo cosa ne fanno, il browser con il JavaScript lo trasforma in una tabella mentre curl mostra la risposta così com'è.

## 2.
**Risposta:** La risorsa è il prodotto in sé, cioè il dato del prodotto P001 salvato in products.json. L'endpoint /api/products/P001 è l'indirizzo con il metodo GET che uso per chiederlo. La rappresentazione JSON è la forma in cui il server me lo manda nella risposta, con in più campi calcolati come stock_status.

## 3.
**Risposta:** So solo che server.py è acceso e risponde a quella richiesta. Non so se /api/products funziona, se il JavaScript chiama il percorso giusto, se config.json è coerente o se products.json si legge bene. Devo provare con curl /api/products e guardare nel browser quale richiesta parte e che codice riceve.

## 4.
**Risposta:** Perché il JavaScript chiama sempre /api/products, scritto fisso nel codice. Il backend costruisce i percorsi dal prefisso di config.json e dopo la modifica risponde su /api-v2/products. Il browser chiede un indirizzo che non esiste più e riceve un errore, anche se /health dà ancora 200. Frontend e backend non rispettano più lo stesso contratto API.

## 5.
**Risposta:** Perché sono tre file della stessa applicazione e non tre servizi autonomi. Gira un solo programma, server.py, che serve la pagina, legge config e dati e risponde alle API, e si avvia e si aggiorna tutto insieme. Un microservizio invece è un processo separato con il suo deploy e i suoi dati, che sta su da solo e parla con gli altri via rete.
