# Guida comandi — UD05

Reti Azure: VNet, subnet, CIDR, NSG, NIC e diagnosi. Le basi sono in `laboratori/UD02/guida-comandi.md`.

---

## 1. CIDR in un colpo d'occhio

| Prefisso | Indirizzi | Esempio |
|---|---|---|
| /16 | 65.536 | VNet `10.50.0.0/16` |
| /24 | 256 | subnet `10.50.10.0/24` |
| /26 | 64 | |

- più il numero dopo la barra è **piccolo**, più la rete è **grande**
- Azure riserva **5 indirizzi** per subnet: il primo utilizzabile è il `.4`
- le subnet devono stare **dentro** la VNet e **non sovrapporsi**. Due VNet sovrapposte non si possono collegare con il peering

---

## 2. PREPARO E CREO LA RETE

```bash
LAB_SUFFIX="$(openssl rand -hex 3)"
LAB_RG="rg-cea-network-${LAB_SUFFIX}"
LAB_VNET="vnet-cea-${LAB_SUFFIX}"
LAB_NSG="nsg-data-${LAB_SUFFIX}"
LAB_LOCATION="italynorth"

az group create --name "$LAB_RG" --location "$LAB_LOCATION" --tags unit=UD05 environment=lab --output table

az network vnet create --resource-group "$LAB_RG" --name "$LAB_VNET" \
  --address-prefixes 10.50.0.0/16 --subnet-name snet-web --subnet-prefixes 10.50.10.0/24

az network vnet subnet create --resource-group "$LAB_RG" --vnet-name "$LAB_VNET" \
  --name snet-data --address-prefixes 10.50.20.0/24
```

---

## 3. NSG: regole e associazione

```bash
az network nsg create --resource-group "$LAB_RG" --name "$LAB_NSG"

az network nsg rule create --resource-group "$LAB_RG" --nsg-name "$LAB_NSG" \
  --name Allow-Web-Postgres --priority 300 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes 10.50.10.0/24 --destination-port-ranges 5432

az network vnet subnet update --resource-group "$LAB_RG" --vnet-name "$LAB_VNET" \
  --name snet-data --network-security-group "$LAB_NSG"

# leggere le regole nell'ordine in cui Azure le valuta
az network nsg rule list --resource-group "$LAB_RG" --nsg-name "$LAB_NSG" \
  --query "sort_by([], &priority)[].{Nome:name,Prio:priority,Dir:direction,Azione:access,Porta:destinationPortRange,Origine:sourceAddressPrefix}" \
  --output table
```

| Regola NSG | Significato |
|---|---|
| numero più **basso** | valutata **prima** |
| prima regola che corrisponde | decide e l'NSG si ferma |
| nome della regola | **non conta niente** |
| stateful | la risposta di una connessione permessa esce da sola |
| NSG su subnet **e** su NIC | il traffico deve passare **tutti e due** |

---

## 4. NIC e verifica della configurazione

```bash
az network nic create --resource-group "$LAB_RG" --name nic-web-01 --vnet-name "$LAB_VNET" --subnet snet-web

az network nic show --resource-group "$LAB_RG" --name nic-web-01 \
  --query "{IP:ipConfigurations[0].privateIPAddress,Subnet:ipConfigurations[0].subnet.id,NSG:networkSecurityGroup}" \
  --output jsonc | sed -E 's#/subscriptions/[^/]+#/subscriptions/<omitted>#g'

az network vnet subnet show --resource-group "$LAB_RG" --vnet-name "$LAB_VNET" --name snet-data \
  --query "{Prefix:addressPrefix,NSG:networkSecurityGroup.id,RouteTable:routeTable}" --output jsonc
```

⚠️ Dal portale, nella creazione della NIC, il default è "crea una nuova VNet": controllare sempre VNet e subnet prima di Create.

> 💡 Senza una **VM accesa** si legge solo la configurazione. Effective security rules, effective routes e IP Flow Verify servono una NIC collegata a una VM in esecuzione (vedi UD06).

---

## 5. Catena di diagnosi

```text
CIDR → DNS → ROUTE → NSG → firewall del sistema operativo → servizio in ascolto
```

| Errore o sintomo | Livello | Controllo |
|---|---|---|
| `InvalidAddressPrefix` | CIDR | prefisso allineato, dentro la VNet, senza sovrapposizioni |
| `SecurityRuleConflict` | NSG | stessa priorità e stessa direzione di una regola esistente |
| nome che non si risolve | DNS | `nslookup` o `dig`, prova con l'IP diretto |
| porta filtrata | NSG | regole in ordine di priorità, poi IP Flow Verify con la VM |

Correzione minima: togliere o spostare **solo** la regola sbagliata. Mai eliminare l'NSG intero.

---

## 6. ELIMINO E CONFERMO

```bash
az group delete --name "$LAB_RG" --yes --no-wait
az group wait --name "$LAB_RG" --deleted
az group exists --name "$LAB_RG"     # atteso: false
```
