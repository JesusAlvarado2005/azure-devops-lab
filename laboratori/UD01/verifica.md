# Verifica — UD01

## Parte A

1. B
2. C
3. C
4. C
5. A
6. A
7. C
8. B
9. C

## Parte B

Git e GitHub sono due cose diverse. Git è il programma installato sul computer che tiene la storia delle modifiche in locale, dentro la cartella .git. GitHub invece è un sito che ospita i repository Git online e permette di collaborare con altri. Si può usare Git senza GitHub e si può anche modificare un file su GitHub senza avere Git installato.

La sequenza minima di comandi per vedere le modifiche, preparare un file, fare un commit e inviarlo è: prima git status o git diff per guardare cosa è cambiato, poi git add con il nome del file, poi git commit con un messaggio, e infine git push per inviarlo al repository remoto.

Prima di aggiornare WSL su tutte le postazioni con wsl --update bisognerebbe controllare due cose: se qualche distribuzione usa ancora WSL 1 con dati importanti dentro, perché in quel caso andrebbe fatto un backup prima di toccare qualcosa, e qual è la versione attuale del componente WSL, per capire se serve davvero aggiornare o se va già bene così.

Se code . apre VS Code ma il terminale mostra un percorso C:\Users\... invece di un percorso Linux, probabilmente la cartella è stata aperta come cartella Windows e non tramite WSL. Per controllare basta guardare in basso a sinistra se c'è scritto WSL: Ubuntu, e se non c'è si richiude tutto e si rilancia code . dal terminale Ubuntu.

Se un token viene pubblicato per errore in un commit e poi tolto con un commit successivo il problema non è risolto perché Git si ricorda tutta la storia, quindi quel token resta visibile e recuperabile guardando i commit precedenti. L'unica cosa giusta da fare è revocare o cambiare quel token alla fonte, non basta nasconderlo.
