# Verifica — UD01

## Parte A — Scelte operative

1. **B** — Windows e Ubuntu possono possedere installazioni distinte di Git, con versioni
   diverse perché vivono in file system e gestori di pacchetti separati.
2. **C** — `wsl --list --verbose` mostra la colonna `VERSION`, che indica se ogni
   distribuzione usa l'architettura WSL 1 o WSL 2.
3. **C** — Il file system Linux nativo è più adatto al workflow successivo con Docker e
   bind mount rispetto a un percorso Windows montato (`/mnt/c`).
4. **C** — Se lo strumento è presente e compatibile, va solo verificato il funzionamento;
   reinstallarlo senza motivo rischia di alterare una configurazione già funzionante.
5. **A** — Il commit esiste nella storia locale ma non è ancora stato inviato al remote con
   `git push`; GitHub mostra solo ciò che ha effettivamente ricevuto.
6. **A** — `git status` dopo `git add` mostra con precisione quali file sono in staging e
   quindi entreranno nel prossimo commit.
7. **C** — Il codice temporaneo va inserito nella pagina di autenticazione del browser e non
   deve mai essere conservato, condiviso o pubblicato nel repository.
8. **B** — L'indicatore `WSL: Ubuntu` insieme a un terminale integrato con percorso Linux
   dimostra che VS Code opera davvero dentro l'ambiente Linux (su questo sistema, essendo
   Fedora nativo, l'equivalente è un terminale con percorso Linux nativo, senza indicatore
   WSL perché non applicabile).
9. **C** — L'invito serve a dare al docente un ruolo attivo di scrittura, revisione e
   collaborazione sul percorso, non solo a permettergli di leggere un repository già pubblico.

## Parte B — Risposte brevi

### 10. Differenza fra Git e GitHub

Git è il sistema di versionamento installato localmente, che registra la storia del
progetto in una cartella `.git`. GitHub è un servizio remoto che ospita repository Git e
aggiunge collaborazione, revisione e accesso via web. Si può usare Git senza GitHub, e
viceversa modificare file su GitHub senza avere Git installato in locale.

### 11. Sequenza minima di comandi

```bash
git status
git diff
git add <file>
git commit -m "<messaggio descrittivo>"
git push
```

### 12. Controlli prima di un `wsl --update` generalizzato

Prima di aggiornare tutte le postazioni andrebbero verificati: 1) se qualche distribuzione
usa ancora WSL 1 con dati importanti, che richiederebbero un backup/esportazione prima di
qualsiasi conversione; 2) la versione attuale del componente WSL (`wsl --version` o
`wsl --status`), per capire se l'aggiornamento è realmente necessario o se la versione è già
sufficiente per i laboratori successivi.

### 13. `code .` apre un percorso `C:\Users\...`

Si sospetta che la cartella sia stata aperta come cartella Windows e non attraverso
l'estensione Remote-WSL. La verifica è controllare l'indicatore in basso a sinistra della
finestra (deve mostrare `WSL: Ubuntu`) e, se assente, richiudere e rilanciare `code .` dal
terminale Ubuntu invece che da PowerShell o da Esplora file.

### 14. Token pubblicato e poi "rimosso" con un commit successivo

Il problema non è risolto perché Git conserva ogni versione precedente nella cronologia: il
token resta recuperabile nei commit passati da chiunque clona il repository o ne consulta la
history, anche se nell'ultima versione dei file non compare più. L'unica azione corretta è
revocare o ruotare il token alla fonte (es. GitHub, Azure), non semplicemente coprirlo.
