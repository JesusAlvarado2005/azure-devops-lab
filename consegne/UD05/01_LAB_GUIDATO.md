# Consegna UD05 — Laboratorio guidato

## Piano di indirizzamento

| Elemento | CIDR | Scopo | Sovrapposizioni |
|---|---|---|---|
| VNet | 10.50.0.0/16 | spazio privato del laboratorio da 10.50.0.0 a 10.50.255.255 | nessuna, contiene le due subnet |
| subnet web | 10.50.10.0/24 | parte web da 10.50.10.0 a 10.50.10.255 | nessuna, finisce prima di 10.50.20.0 |
| subnet data | 10.50.20.0/24 | parte dati con il database da 10.50.20.0 a 10.50.20.255 | nessuna, inizia dopo 10.50.10.255 |

Le subnet web e data sono interamente contenute in 10.50.0.0/16 e non condividono indirizzi IP. Questo controllo l'ho fatto prima di creare le risorse.

## NSG e associazioni

| NSG | Scope associato | Regola | Priorità | Origine | Porta | Esito |
|---|---|---|---:|---|---|---|
| nsg-data-4756a8 | subnet snet-data | Allow-Web-Postgres Inbound TCP | 300 | 10.50.10.0/24 | 5432 | permette solo il traffico dalla subnet web al database |
| nsg-data-4756a8 | subnet snet-data | Deny-Web-Postgres Inbound TCP, guasto didattico | 200 | 10.50.10.0/24 | 5432 | veniva valutata prima della 300 e bloccava il flusso, l'ho eliminata |

Il resource group rg-cea-network-4756a8 e la VNet vnet-cea-4756a8 li ho creati da CLI. L'NSG l'ho creato dal portale con i tag unit UD05 ed environment lab, poi ho aggiunto la regola e l'ho associato alla subnet snet-data.

## Verifica della configurazione

- NIC create e subnet: nic-data-01 creata dal portale in snet-data con IP privato dinamico 10.50.20.4 e nessun IP pubblico, nic-web-01 creata da CLI in snet-web con IP 10.50.10.4 e nessun IP pubblico. La prima volta dal portale avevo messo come nome della NIC quello del resource group e avevo lasciato la scelta di creare una nuova VNet, così era finita in una rete 172.16.0.0/16. Ho eliminato la NIC e quella VNet e l'ho ricreata nella subnet giusta
- NSG associato alla subnet e regole osservate: snet-data ha associato nsg-data-4756a8 e sulla NIC non c'è un NSG. Con az network nsg rule list ordinato per priorità ho visto prima solo la 300, poi la 200 di Deny sopra la 300 e dopo averla eliminata è rimasta solo Allow-Web-Postgres
- Route table associata alla subnet (o assente): RouteTable è null, quindi non c'è una route table personalizzata ma restano le route di sistema di Azure
- ciò che è stato verificato: configurazione NSG e associazioni verificate con la CLI. La NIC dati non ha una VM collegata e Vm risulta null
- report effettivi e test di flusso rinviati alla UD06: il flusso da provare è 10.50.10.0/24:any → 10.50.20.0/24:5432 TCP. Effective security rules, effective routes e IP Flow Verify li farò quando ci sarà una VM in esecuzione

## Costi e cleanup

Ho creato un resource group con una VNet, due subnet, un NSG e due NIC. Queste risorse da sole non hanno un costo significativo come una VM, ma vanno eliminate comunque per non lasciare ambienti abbandonati. Dopo il laboratorio autonomo e la verifica ho eliminato il resource group rg-cea-network-4756a8 con tutto quello che conteneva. az group exists ha restituito false e non risultano più resource group rg-cea nella sottoscrizione.

## Rilevanza professionale

Gli indirizzi vanno decisi prima perché quando le reti sono collegate e ci sono i servizi sopra cambiarli vuol dire migrare tutto. Se due reti hanno spazi sovrapposti non si possono nemmeno collegare con il peering. Anche le regole vanno controllate prima, perché una regola con priorità sbagliata come il Deny 200 blocca un flusso giusto e il problema si vede solo quando l'applicazione non funziona. Nel laboratorio poi ho visto che sul portale basta un valore lasciato di default per creare una rete in più e mettere la NIC nel posto sbagliato.
