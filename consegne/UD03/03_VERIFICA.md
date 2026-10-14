# Consegna UD03 — Verifica

## Parte A — Scelta singola

Per le domande 1–8 riporta risposta e motivazione.

1. B, perché se accede al portale il login è riuscito, quindi manca un ruolo che gli permetta di leggere quel resource group.
2. D, perché una role assignment è fatta da principal, role definition e scope. La password riguarda l'autenticazione.
3. C, perché Reader permette solo di leggere e il resource group è lo scope più piccolo che copre quello che serve.
4. B, perché i ruoli assegnati a uno scope valgono anche per tutto quello che sta sotto.
5. B, perché Contributor può creare e modificare risorse ma non ha il permesso di scrivere role assignment.
6. C, perché il lock blocca l'eliminazione per tutti finché resta applicato, ma la lettura continua a funzionare.
7. B, perché il budget manda una notifica quando si raggiunge la soglia, ma non ferma né le risorse né la spesa.
8. B, perché gli utenti stanno nella directory di Microsoft Entra ID e per crearli serve un ruolo Entra come User Administrator.

## Parte B — Risposte brevi

9. Perché assegnando il ruolo a un gruppo non serve impostare i permessi per ogni singolo utente. Basta dare i permessi al gruppo e poi aggiungere o togliere le persone. Così è più ordinato, si fanno meno errori e si capisce subito chi ha accesso e perché, quindi aumenta anche la tracciabilità.

10. Un ruolo Microsoft Entra dà permessi sulla directory, cioè su utenti, gruppi e applicazioni. Per esempio User Administrator può creare ed eliminare utenti. Un ruolo Azure invece dà permessi sulle risorse dentro uno scope. Per esempio Reader su un resource group permette di consultare le risorse che contiene senza modificarle.

11. L'accesso effettivo è quello di Contributor sul resource group, quindi può leggere e anche modificare le risorse. Questo perché in RBAC i ruoli si sommano: Reader non riduce i permessi che arrivano da Contributor ereditato dalla sottoscrizione.

12. Prima leggo bene l'errore per capire quale azione è stata negata e su quale scope. Poi controllo con az account show di essere con l'account, la sottoscrizione e il tenant giusti. Dopo guardo quali ruoli ho davvero su quello scope con az role assignment list --scope e --include-inherited, così vedo sia quelli diretti sia quelli ereditati. Poi verifico se quei ruoli contengono l'azione negata, per esempio Contributor non può scrivere role assignment. Se il ruolo è stato assegnato da poco aspetto qualche minuto e rifaccio il login. Se il permesso manca davvero lo chiedo a chi è Owner, senza cercare di aggirare il blocco.

13. Il tag deleteAfter è solo un'etichetta che indica entro quando l'ambiente andrebbe eliminato. Non elimina niente da solo e non blocca niente, serve a chi fa il cleanup o a un'automazione. Il lock CanNotDelete invece impedisce davvero l'eliminazione a tutti, anche agli Owner, finché non viene rimosso. Il budget controlla la spesa rispetto a una soglia e manda un avviso quando la supera, ma non blocca né le risorse né i costi.

## Parte C — Caso situazionale

14. La prima scelta sbagliata è dare Contributor per consultare una VNet, perché Contributor permette di modificare mentre serviva solo leggere. La seconda è assegnarlo su tutta la sottoscrizione, che è uno scope molto più ampio del necessario visto che serviva una sola VNet. La terza è un errore di interpretazione: ScopeLocked non è un problema di permessi del tecnico ma un lock sullo scope, che blocca l'eliminazione per chiunque.

15. Reader sulla VNet in rg-network-prod, perché permette di consultarla senza modificarla ed è lo scope più piccolo possibile. Se deve vedere anche le risorse collegate alla rete, Reader sul resource group rg-network-prod.

16. Non riesce ad assegnare Reader al collega per un limite di RBAC: Contributor non ha il permesso Microsoft.Authorization/roleAssignments/write, che hanno invece ruoli come Owner o User Access Administrator. Non riesce a eliminare per un motivo diverso: sullo scope c'è un lock CanNotDelete. Contributor normalmente potrebbe eliminare, ma il lock vale per tutti, anche per gli Owner, e va prima rimosso da chi è autorizzato e solo se l'eliminazione è davvero prevista.
