# Consegna UD03 — Domande sui concetti

Per ciascuna domanda 1–8 riporta una risposta motivata.

1. L'autenticazione verifica l'identità della persona, cioè chi sei, mentre l'autorizzazione stabilisce quali azioni puoi fare e dove. Sono due controlli separati: posso fare login correttamente ma non avere nessun ruolo su una risorsa, e in quel caso entro ma ricevo AuthorizationFailed quando provo a fare qualcosa.

2. I ruoli Microsoft Entra danno permessi sulla directory, cioè su utenti, gruppi e applicazioni. Per esempio per creare l'utente del laboratorio serve un ruolo come User Administrator. I ruoli Azure invece danno permessi sulle risorse e sulle operazioni dentro uno scope, come Reader, Contributor e Owner. Per assegnare Reader al gruppo sul resource group serviva un ruolo Azure come Owner, non un ruolo Entra.

3. Principal, role definition e scope, cioè chi riceve il permesso, cosa può fare e dove vale.

4. Perché serve solo consultare quel progetto. Contributor sulla sottoscrizione darebbe due cose in più del necessario: la possibilità di modificare le risorse e l'accesso a tutti i resource group della sottoscrizione. Reader sul resource group dà solo la lettura e solo su quel progetto, quindi rispetta il minimo privilegio sia nel ruolo sia nello scope.

5. Perché il ruolo ereditato non è assegnato sulla risorsa figlia ma sullo scope padre, per esempio la sottoscrizione, e da lì vale anche sotto. Nella risorsa figlia si vede come ereditato ma non si può rimuovere lì. Per toglierlo bisogna intervenire sullo scope dove è stato assegnato, e così cambia l'accesso anche su tutto il resto che sta sotto.

6. No. Il tag è solo un'informazione, un'etichetta che indica entro quando l'ambiente andrebbe eliminato. Non attiva funzioni e non blocca operazioni, quindi non impedisce l'eliminazione e non la fa nemmeno in automatico. Per impedire l'eliminazione serve un lock.

7. Il ruolo Reader è un permesso dato a un principal e limita solo quello che può fare lui, cioè leggere senza modificare. Il lock CanNotDelete invece si mette su uno scope e vale per tutti, anche per chi è Owner. Nel laboratorio io ero Owner ma non sono riuscito a eliminare il resource group finché c'era il lock.

8. Perché il budget confronta i costi con una soglia e manda una notifica quando viene superata, ma non blocca la spesa e non spegne le risorse. In più i dati di costo arrivano con un po' di ritardo, quindi l'avviso può partire quando la spesa è già avvenuta. Per fermare davvero la spesa serve un intervento manuale o un'automazione separata.
