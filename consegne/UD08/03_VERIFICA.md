# UD08 — Verifica

## Parte A

1. B perché DevOps è un modo di lavorare con cultura, pratiche, automazione e feedback e non un singolo strumento
2. A perché si integrano spesso piccole modifiche controllate da build e test
3. B perché git add sposta le modifiche nella staging area per il prossimo commit, non pubblica niente
4. B perché la head è il branch con la proposta e main è la base che la riceve
5. B perché chi revisiona chiede correzioni e il merge aspetta finché non vengono fatte
6. B perché Git non sa quale versione tenere e serve una decisione di una persona
7. B perché è un endpoint esposto da server.py
8. A perché mostra solo quello che è in staging e quindi entrerà nel commit

## Parte B

9. Con la Continuous Delivery il codice è sempre pronto per il rilascio ma il deploy in produzione parte solo dopo un'approvazione. Con il Continuous Deployment se passa tutti i controlli automatici va in produzione da solo senza approvazione.

10. Perché lavoro isolato senza toccare main né il lavoro degli altri. Se qualcosa va storto main resta pulita e la modifica entra solo dopo Pull Request, review e test.

11. La PR si aggiorna da sola perché segue il branch. I nuovi commit compaiono nella stessa PR con il diff aggiornato, come è successo con il commit docs: address UD08 review dopo la Request changes.

12. Che la modifica faccia quello che chiede la PR, che tocchi solo i file che servono, che non ci siano segreti come token o password, che ci siano i test e siano passati, e che il codice sia leggibile e coerente con il resto.

13. Per il principio del privilegio minimo. Finito il lavoro il collaboratore non ha più motivo di scrivere nella mia repo, e se l'accesso resta lui o chi gli ruba l'account può ancora modificarla.

14. Il frontend è static/index.html con il JavaScript che chiama /api/products. Il backend è server.py che risponde alle richieste HTTP in JSON. La configurazione è config.json con porta, api_prefix e soglia delle scorte. I dati sono data/products.json con i prodotti.

## Parte C

15. La PR mischia cose diverse. config.json e server.py possono andare insieme se fanno parte della stessa modifica, ma il file di consegna di un'altra UD non c'entra e va tolto. token.txt è il problema più grave perché probabilmente contiene un segreto e non deve mai finire nella repo, e se è già stato pushato il token va considerato compromesso. In più senza test HTTP documentati non so se la modifica funziona davvero.

16. Chiederei con Request changes di togliere token.txt e il file dell'altra UD dalla PR, e se il token è vero di revocarlo e crearne uno nuovo fuori dalla repo, magari aggiungendo token.txt al .gitignore. Poi di lasciare solo config.json e server.py, eseguire e documentare i test su /health, /api/products, /api/products/P001 e /api/products/XXX, e verificare il frontend. Alla fine ricontrollo con gh pr diff che ci siano solo i file previsti e nessun segreto, e solo allora approvo.
