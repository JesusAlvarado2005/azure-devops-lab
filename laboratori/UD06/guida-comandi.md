# Guida comandi — UD06

Compute: VM Linux con SSH, Nginx, NSG, Network Watcher, metriche, App Service e backup. Le basi sono in `laboratori/UD02/guida-comandi.md`, le reti in `laboratori/UD05/guida-comandi.md`.

⚠️ **La VM costa finché esiste.** Cleanup lo stesso giorno, oppure `az vm deallocate` la sera.

---

## 1. PREPARO

```bash
cd ~/workspace/azure-devops-k8s-01/UD06
export UD06_DIR="$PWD"
export LAB_RG="rg-ud06-compute"
export LAB_VM="vm-ud06-linux"
export LAB_VNET="vnet-ud06"
export LAB_LOCATION=italynorth
export LAB_VM_SIZE=Standard_F1als_v7
```

Lo script `select-vm-target.sh` non trovava niente perché la serie B è `NotAvailableForSubscription` sulla mia sottoscrizione. Per vedere le size davvero disponibili:

```bash
az vm list-skus --location italynorth --size Standard_B1s --all \
  --query "[].{Name:name,Restr:restrictions[].reasonCode}" --output jsonc   # ci mette qualche minuto
```

⚠️ Nel blocco della guida c'è `exit 1`: in un terminale interattivo **chiude la shell** e perdi le variabili.

---

## 2. CHIAVE SSH

```bash
ls -l ~/.ssh/                         # in zsh ~/.ssh/ud06_azure* dà "no matches found" se non esiste
ssh-keygen -t ed25519 -f ~/.ssh/ud06_azure -C "ud06"
cat ~/.ssh/ud06_azure.pub             # la PUBBLICA va nel portale
```

La chiave **privata** (`ud06_azure` senza `.pub`) non si incolla mai e non va nel repo.

---

## 3. RETE E VM

```bash
az group create --name "$LAB_RG" --location "$LAB_LOCATION" --output table
az network vnet create --resource-group "$LAB_RG" --name "$LAB_VNET" --location "$LAB_LOCATION" \
  --address-prefixes 10.60.0.0/16 --subnet-name snet-vm --subnet-prefixes 10.60.1.0/24
```

Portale: VM con Ubuntu LTS, size `$LAB_VM_SIZE`, chiave SSH pubblica, utente `azureuser`, **Public inbound ports: None**. In Networking controllare VNet e **subnet**: il portale ne può aggiungere una sua.

```bash
az vm show --resource-group "$LAB_RG" --name "$LAB_VM" --show-details \
  --query "{Power:powerState,Private:privateIps,Public:publicIps,Size:hardwareProfile.vmSize}" --output table

export LAB_VM_IP=$(az vm show --resource-group "$LAB_RG" --name "$LAB_VM" --show-details --query publicIps --output tsv)
```

---

## 4. NSG, SSH E NGINX

Portale: `VM → Networking → Create port rule`, Source My IP, porta **22** (controllare che non resti 8080), priorità 300. Poi lo stesso per la **80** con priorità 310.

```bash
export LAB_NSG=vm-ud06-linux-nsg
az network nsg rule update --resource-group "$LAB_RG" --nsg-name "$LAB_NSG" --name Allow-SSH-MyIP --destination-port-ranges 22

ssh -i ~/.ssh/ud06_azure azureuser@"$LAB_VM_IP"
# dentro la VM
sudo apt update && sudo apt install -y nginx
systemctl status nginx --no-pager
curl -I http://localhost
exit

curl -I --max-time 10 "http://$LAB_VM_IP"        # dal PC
```

| Risultato curl | Significato |
|---|---|
| `200 OK` | rete, NSG e servizio a posto |
| timeout | qualcosa **filtra**, di solito l'NSG |
| `Connection refused` | la porta arriva ma nessun servizio ascolta |

---

## 5. DIAGNOSI CON LA VM ACCESA

```bash
# simula un pacchetto e dice quale regola decide (non manda pacchetti veri)
az network watcher test-ip-flow --resource-group "$LAB_RG" --vm "$LAB_VM" \
  --direction Inbound --protocol TCP --local 10.60.0.4:80 --remote <IP_PUBBLICO_MIO>:60000 --output table

az network nic list-effective-nsg --resource-group "$LAB_RG" --name <NIC>            # regole effettive
az network nic show-effective-route-table --resource-group "$LAB_RG" --name <NIC> -o table

ssh -i ~/.ssh/ud06_azure azureuser@"$LAB_VM_IP" "systemctl is-active nginx; curl -sI http://localhost | head -1"
```

- **local** = la VM, **remote** = chi chiama. La remote port è quella casuale del client, un numero alto qualsiasi
- correzione minima: `az network nsg rule delete` **solo** della regola sbagliata

---

## 6. METRICHE

```bash
ID=$(az vm show -g "$LAB_RG" -n "$LAB_VM" --query id -o tsv)
az monitor metrics list --resource "$ID" --metric "Percentage CPU" --interval PT5M --offset 4h \
  --aggregation Average Maximum --output table
```

La CPU dice quanto lavora la VM, **non** se gli utenti la raggiungono: durante un blocco NSG il grafico sembra normale.

---

## 7. APP SERVICE (solo piano Free F1)

Lo script `prepare-appservice.sh` cerca `PHP|` ma la CLI nuova restituisce `PHP:8.4`, quindi si fa a mano:

```bash
az webapp list-runtimes --os linux --output json
export WEB_RUNTIME="PHP:8.4"
export WEB_PLAN="plan-ud06-$RANDOM"
export WEB_APP="ud06-web-$(date +%s)-$RANDOM"      # il nome diventa <nome>.azurewebsites.net

az appservice plan create --resource-group "$LAB_RG" --name "$WEB_PLAN" --location "$LAB_LOCATION" --sku F1 --is-linux --output table
az webapp create --resource-group "$LAB_RG" --plan "$WEB_PLAN" --name "$WEB_APP" --runtime "$WEB_RUNTIME" --output table
az webapp deploy --resource-group "$LAB_RG" --name "$WEB_APP" --src-path ~/ud06-web/index.html --type static --target-path index.html
export WEB_HOST=$(az webapp show --resource-group "$LAB_RG" --name "$WEB_APP" --query defaultHostName -o tsv)
curl -fsS "https://$WEB_HOST/" | grep -F "Deployment riuscito."
```

Al primo uso la CLI registra da sola il provider `Microsoft.Web`: può metterci qualche minuto. Scale up e scale out si **guardano** soltanto, nessun upgrade.

---

## 8. ELIMINO E CONFERMO

```bash
az resource list --resource-group "$LAB_RG" --output table    # solo roba UD06?
az group delete --name "$LAB_RG"
az group exists --name "$LAB_RG"                              # atteso: false
```

`NetworkWatcherRG` lo crea Azure da solo, è gratis e si lascia.

---

## Errori incontrati

| Errore | Causa | Soluzione |
|---|---|---|
| terminale chiuso dopo lo script | `exit 1` della guida in shell interattiva | toglierlo, rifare gli export |
| `Could not resolve hostname :` | `LAB_VM_IP` vuota | fare l'export con `--query publicIps -o tsv` |
| ssh fermo poi timeout | regola SSH sulla porta 8080 | `nsg rule update --destination-port-ranges 22` |
| `option requires an argument -- f` | comando ssh-keygen tagliato nell'incolla | scriverlo su una riga |
| `LIVE=no` dallo script App Service | formato runtime `PHP:` invece di `PHP\|` | piano F1 e Web App a mano |
| regola "Deny" che non blocca | Action rimasta Allow nel portale | `nsg rule update --access Deny` |
