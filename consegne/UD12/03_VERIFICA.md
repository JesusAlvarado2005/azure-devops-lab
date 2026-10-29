# UD12 — Verifica individuale

## Parte A

1. B
2. A
3. B
4. B
5. B
6. B
7. B
8. B

## Parte B

9. imperativo dico i comandi uno dopo l'altro, come az group create e poi az storage account create, dichiarativo descrivo come deve essere alla fine e lo strumento decide cosa fare

10. così lo stesso codice lo uso con valori diversi, per esempio nome dello storage o regione, senza toccare la definizione delle risorse

11. tutti e due fanno vedere cosa cambierà prima di applicare, what-if confronta il template Bicep con quello che c'è in Azure, plan confronta il codice Terraform con lo state e con Azure

12. perché non lo scrivo io, cambia a ogni apply e può contenere dati sensibili delle risorse, se lo metto in git rischio segreti e conflitti

13. validate controlla che il codice sia scritto giusto senza toccare Azure, plan fa vedere cosa cambierebbe, apply lo fa davvero

14. perché le risorse costano e si possono ricreare quando servono, il codice invece serve alle pipeline di UD13 e UD14

## Parte C

15. no, il piano dice che distrugge 2 risorse e ne crea 1 mentre lui voleva solo aggiungere un tag, quindi c'è qualcosa di sbagliato e con apply perderebbe le risorse

16. leggere il piano per capire quali risorse e quale proprietà fanno la ricreazione, guardare il git diff di main.tf, controllare che non sia cambiato un nome o una location, e rifare il plan finché mostra solo 1 to change

## Gate 2

- agent Online: sì
- Terraform disponibile: sì, 1.17.0
- Azure CLI/Bicep disponibile: sì, 2.83.0 e 0.48.1
- Git/Python/Docker disponibili: sì

## 17.

perché il self-hosted è il mio PC quindi usa il Terraform che ho installato, il Microsoft-hosted è un'altra macchina gestita da Microsoft e quello che ho sul mio PC lì non c'è

## 18.

perché ogni job Microsoft-hosted parte da una macchina nuova e alla fine viene buttata, i file del job prima non ci sono più

## 19.

perché così nel log vedo che versioni ha davvero l'agent, se una cosa cambia o manca me ne accorgo subito e non dopo con errori strani

## 20.

il vantaggio è che ha sempre i tool aggiornati senza fare niente, il rischio è che cambia da solo e una pipeline che andava può rompersi senza che io abbia toccato niente, con un'immagine versionata sai sempre cosa usi


## Gate 2A — self-hosted

- Agent Online: sì, `./run.sh` in ascolto senza rifare config e senza nuovo PAT
- Terraform: 1.17.0
- Azure CLI: 2.83.0
- Bicep: 0.48.1
- Git: 2.56.0
- Python: 3.14.8
- Docker: 29.9.2

## Gate 2B — Microsoft-hosted

- stato: MICROSOFT_HOSTED_PENDING come in UD09, UD13 usa il self-hosted
