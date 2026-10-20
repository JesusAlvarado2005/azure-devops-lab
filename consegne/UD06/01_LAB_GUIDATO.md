# UD06 — Consegna laboratorio guidato

## VM

- regione selezionata: italynorth
- size selezionata: Standard_F1als_v7
- image: Ubuntu Server 24.04 LTS di Canonical
- size: Standard_F1als_v7 con 1 vCPU e 2 GB di RAM
- private IP: 10.60.0.4
- public IP: vm-ud06-linux-ip Standard statico
- NIC: vm-ud06-linux670 con l'NSG vm-ud06-linux-nsg
- subnet: snet-italynorth-2 10.60.0.0/24 nella VNet vnet-ud06 10.60.0.0/16
- OS disk: disco gestito da 30 GB Premium SSD LRS

Lo script select-vm-target.sh non ha trovato nessuna combinazione perché la serie B risultava NotAvailableForSubscription in westeurope, northeurope e anche in italynorth. Quando la selezione fallisce il blocco della guida fa exit 1 e mi ha chiuso il terminale con tutte le variabili. Ho cercato da CLI le size senza restrizioni in italynorth e ho preso la più piccola disponibile cioè Standard_F1als_v7, senza scegliere una VM più grande del necessario.

La VNet l'avevo creata da CLI con la subnet snet-vm 10.60.1.0/24, ma dal portale nella creazione della VM è stata aggiunta e usata la subnet snet-italynorth-2 10.60.0.0/24. La subnet snet-vm è rimasta vuota.

## Accesso e workload

- SSH: chiave ed25519 creata con ssh-keygen in ~/.ssh/ud06_azure, sulla VM ho caricato solo la chiave pubblica e mi collego come azureuser. La prima volta ssh restava fermo perché la regola Allow-SSH-MyIP era sulla porta 8080 rimasta di default nel portale invece che sulla 22. L'ho cambiata con az network nsg rule update e il collegamento ha funzionato
- Nginx: installato con apt e systemctl lo dà active
- test localhost: dentro la VM curl su localhost dà HTTP/1.1 200 OK
- test esterno: dal mio PC curl -I sull'IP pubblico dà HTTP/1.1 200 OK con Server nginx/1.24.0 (Ubuntu)
- IP Flow Verify: Inbound TCP dal mio IP pubblico porta 60000 verso 10.60.0.4 porta 80 dà Allow
- regola responsabile: Allow-HTTP-MyIP con priorità 310, che apre la porta 80 solo dal mio IP

Il public IP da solo non bastava. La VM era creata con Public inbound ports None e finché l'NSG non ha avuto le regole giuste per la 22 e la 80 dal mio IP non era raggiungibile.

## Azure Monitor

- metrica VM: Percentage CPU
- intervallo: ultime 4 ore con un punto ogni 5 minuti
- aggregazione: Average e Maximum
- osservazione: la CPU media resta intorno allo 0,2% e c'è un picco massimo del 20% intorno alle 12:47 ora italiana durante l'installazione di Nginx. È una metrica numerica nel tempo e non un log, quindi mi dice quanto lavora la VM ma non cosa è successo dentro

## VMSS / Autoscale

- min: 1
- default: 1
- max: 3
- metrica: Percentage CPU media delle istanze
- soglia: maggiore del 70% per 5 minuti
- azione: aggiungere 1 istanza
- perché serve un max: per mettere un tetto ai costi e alla quota di vCPU. Senza massimo un picco anomalo o un bug che tiene la CPU alta farebbe creare VM senza limite e ognuna si paga

Il VM Scale Set non è stato creato, i parametri vengono dai comandi di esempio della guida.

## App Service

- App Service Plan: plan-ud06-2113 Linux in italynorth
- tier: Free F1 con 1 istanza
- Web App: ud06-web-1792498300-10955 con runtime PHP 8.4
- hostname: ud06-web-1792498300-10955.azurewebsites.net
- test HTTPS: curl in https dà 200 e nella pagina compare Deployment riuscito., quindi risponde la pagina che ho pubblicato e non quella predefinita

Lo script prepare-appservice.sh ha dato LIVE=no perché cerca i runtime nel formato PHP| con la barra mentre la mia Azure CLI 2.83 li restituisce come PHP:8.4 con i due punti. I runtime c'erano quindi ho creato a mano il piano F1 e la Web App seguendo le stesse regole dello script, cioè runtime PHP e solo piano Free senza tier a pagamento. Alla prima creazione la CLI ha registrato da sola il resource provider Microsoft.Web che non era mai stato usato nella sottoscrizione.

## Scaling App Service

| Modalità | Basata su |
|---|---|
| Manual | numero di istanze scelto e cambiato a mano da me |
| Azure Monitor Autoscale | regole che scrivo io su metriche come la CPU con soglie e orari, più minimo e massimo |
| Automatic Scaling | gestito dalla piattaforma in base al traffico HTTP, imposto solo istanze sempre pronte e limite massimo, solo su alcuni tier |

Scale up cambia il tier del piano e scale out il numero di istanze, tutte e due si fanno sul piano e non sulla Web App. Sul piano Free F1 lo scale out non è disponibile e non ho fatto nessun upgrade.

## Azure Monitor App Service

- metrica: Requests e Http2xx nelle ultime 4 ore
- osservazione: 3 richieste totali tutte con risposta 2xx, cioè i miei test con curl. Rispetto alla VM qui vedo direttamente le richieste HTTP e le risposte, invece sulla VM vedo solo CPU e rete e non so se il sito ha risposto

## Backup

- Recovery Services vault: è la risorsa che conserva i recovery point e gestisce la protezione. L'ho visto dal portale nella VM in Backup + disaster recovery senza abilitarlo
- frequenza ipotizzata: una volta al giorno alle 02:00 di notte quando il servizio è poco usato
- retention: 7 giorni
- recovery point: è lo stato della VM salvato da ogni backup a cui posso tornare. Con un backup al giorno nel caso peggiore perdo un giorno di modifiche, ma per una pagina statica che cambia poco va bene
- backup reale avviato?: no — non previsto nella UD

## HA / Backup / DR

- Scenario A: High Availability perché voglio ridurre l'impatto del guasto di una sola istanza e il servizio continua sulle altre
- Scenario B: Backup perché voglio riportare il contenuto della VM a uno stato precedente con un recovery point
- Scenario C: Disaster Recovery perché dopo un grave outage il workload deve ripartire in un'altra region. Con Azure Site Recovery la VM viene replicata dalla region A alla region B, con il failover il servizio riparte in B e con il failback torna in A quando A è di nuovo disponibile

## Cleanup

- Resource Group eliminato: rg-ud06-compute con VM, disco, NIC, IP pubblico, NSG, VNet, piano F1 e Web App, dopo aver controllato con az resource list che ci fossero solo risorse della UD06
- `az group exists`: false

Nella sottoscrizione resta solo NetworkWatcherRG che Azure crea da solo per Network Watcher e non contiene risorse a pagamento del laboratorio.
