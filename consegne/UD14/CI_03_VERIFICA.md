# UD14 — Verifica (blocco CI)

## 1.

Perché se il codice non passa i test non ha senso costruire e pubblicare un'immagine: sprecherei tempo e lascerei in ACR un artefatto rotto. Lo stage `BuildPush` ha `dependsOn: Test` e `condition: succeeded()`, quindi con il test rosso non parte nemmeno.

## 2.

Che tutti gli stage, job e step previsti sono terminati con successo e l'immagine è stata pubblicata. Non vuol dire che l'applicazione sia perfetta in produzione, ma che quel commit ha superato i controlli definiti dalla pipeline.

## 3.

Perché `Build.BuildId` è univoco per ogni run e collega in modo diretto run → tag immagine → immagine in ACR → deployment. Così quando vedo il tag `10` so quale build lo ha prodotto e posso risalire ai log e al commit.

## 4.

`sc-acr-ud14`, una Docker Registry service connection con autenticazione Workload Identity Federation verso `acrud1315iwmnnz3ek6q7o.azurecr.io`. Non uso admin user né password nel YAML.

## 5.

Perché l'admin user è un account con password condivisa e statica: se resta attivo è una credenziale in più da proteggere e non serve alla pipeline, che si autentica con la service connection e il ruolo `AcrPush`. Disabilitato, l'accesso avviene solo con identità e ruoli.

## 6.

No, se fallisce `Test` non ha senso partire dai permessi ACR: `BuildPush` non viene eseguito, quindi il problema è nel codice o nel test, non nel registry. I permessi ACR diventano rilevanti solo se la build arriva al push e riceve `401` o `403`.

## 7.

Il push o il merge su `main`, perché il YAML ha `trigger: main`. La CI non parte per una PR da sola, a meno che una branch policy non la richieda. Nel nostro flusso il merge su `main` attiva `ud13-ci`.

## 8.

Perché ACR, immagini, service connection, agent e pipeline servono al blocco CD e alle verifiche successive. Cancellare adesso significherebbe rifare tutto e perdere le evidenze; il cleanup si fa solo alla fine della UD14.

## 9.

Perché non devo tenere acceso il mio PC, ogni job parte su una VM pulita gestita da Microsoft e il risultato è più riproducibile. Il self-hosted resta un fallback per quando Microsoft-hosted non è disponibile.

## 10.

Perché due job Microsoft-hosted possono girare su VM diverse e nuove, quindi non condividono il workspace. Se un job produce un file che serve all'altro, va pubblicato come artifact e scaricato, oppure il secondo job deve rifare checkout e build.

## 11.

Quando Microsoft-hosted non è disponibile, per esempio per quota, parallel jobs o stato ancora pendente come nel mio caso. Uso il pool `pool-ud09-wsl` e l'agent `wsl-ud09-jesusalvaradojeanfra`, che deve essere `Online` prima della run.

## 12.

Perché sul self-hosted i file restano tra una run e l'altra: senza `clean: all` potrei usare per errore file vecchi, risultati di test precedenti o un checkout sporco. La pulizia rende la run ripetibile e non dipendente da ciò che è rimasto sulla macchina.

## 13.

L'agent è la macchina che esegue i job, individuata dal pool. La Docker Registry service connection è la credenziale con cui il task `Docker@2` si autentica all'ACR. Sono due cose separate: l'agent può essere online e la service connection comunque non autorizzata o senza il ruolo giusto.

## 14.

Per verificare che l'ambiente scelto abbia davvero Python e Docker e per lasciare nei log la versione usata. Se manca il tool o la versione è diversa, lo capisco subito e distinguo un problema di ambiente da un test o una build falliti.

## Gate

- `UD14_AGENT_MODE`: `SELF_HOSTED_FALLBACK`
- pipeline CI riuscita: build 14 (numero `20261102.3`) dopo il merge della PR #5; `Test` e `BuildPush` riusciti, tag `14` pubblicato
- ACR/tag: ACR `acrud1315iwmnnz3ek6q7o` presente, repository `catalog-backend` presente, tag osservati `14`, `11`, `10`, `7`; il tag della run del merge è `14`
- agent usato: `linux-ud14-jj` (AgentId 18), OS `Linux`, macchina `jj-host`
- `sc-azure-ud13-15`: presente (ARM/WIF, usata dal blocco CD)
- `sc-acr-ud14`: presente (`isReady: true`, `isShared: false`, WIF)
- cleanup eseguito: NO
