# UD15 — Inventario aggiornato

Partecipante: Jesus Alvarado  
Data/ora e fuso: 2026-11-04, Europe/Rome (CET, UTC+01:00)  
Repository operativo e commit prima della prova: `/home/jj/Documenti/sviluppo/lab repo remoto/azure-devops-lab`, commit `34000d8`

| Elemento | Versione / stato osservato | Intervento necessario ed esito |
|---|---|---|
| WSL/architettura, memoria e spazio | Fedora 44, `x86_64`, 22 GiB RAM, 292 GB liberi su `/home` | Nessun intervento: risorse sufficienti per un nodo Minikube da 2 CPU e 4 GiB |
| Docker Client/Server e context | Client e Server `29.9.3`, context `default`, driver `overlayfs` | Nessun intervento: motore già attivo e raggiungibile |
| kubectl Client/Server | Client `v1.36.5` (Kustomize `v5.8.1`), Server `v1.37.0` | Client già presente; differenza entro una minor, nessun aggiornamento necessario |
| Minikube e profilo | `v1.39.0`, profilo `minikube` creato con driver Docker e runtime containerd | Installato l'eseguibile in `~/.local/bin/minikube` (sudo richiedeva password), avviato il cluster |
| Context e nodo | Context `minikube`, nodo `minikube` `Ready` con IP interno `192.168.49.2`, Kubernetes `v1.37.0` | Creato dal `minikube start`; nessun altro nodo |
| Porte 8081/8082 | Libere prima dei test | Usate solo con `port-forward` temporanei e chiuse a fine prova |

Tempo setup effettivo, con download/attese: circa 8 minuti, quasi tutti per il download dell'immagine base `kicbase` (507 MiB) e del preload Kubernetes.  
Controllo funzionale cluster, output essenziale: nodo `Ready`, Pod di `kube-system` (etcd, API server, controller manager, scheduler, CoreDNS, kindnet, kube-proxy, storage-provisioner) `1/1 Running`, `web-intro` `1/1 Running` e `HTTP/1.1 200 OK` su `127.0.0.1:8081`.  
Modifiche Git preesistenti conservate: `consegne/UD14/00_DOMANDE_CONCETTI.md` modificato prima della UD15, non toccato da questo lavoro.

Non inserire kubeconfig, certificati o token. Se un controllo non è stato possibile, scriverlo.

### Ambiente iniziale

```text
2026-11-04T09:14:49+01:00
/home/jj/Documenti/sviluppo/lab repo remoto/azure-devops-lab
34000d8 Aggiunge Terraform e pipeline di delivery della UD14
x86_64
               total        used        free      shared  buff/cache   available
Mem:            22Gi        10Gi       1,3Gi       366Mi        12Gi        12Gi
Swap:          8,0Gi          0B       8,0Gi
File system                                            Dim. Usati Dispon. Uso% Montato su
/dev/mapper/luks-1cd54a68-1087-497d-aed8-d61e260be5c9  322G   29G    292G   9% /home
Client: Docker Engine - Community
 Version:           29.9.3
 API version:       1.56
 Go version:        go1.26.10
 Git commit:        5457199
 Built:             Tue Nov  3 21:44:34 2026
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          29.9.3
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.10
  Git commit:       70efc0e
  Built:            Tue Nov  3 21:39:45 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.4.2
  GitCommit:        b7a25261e029d68978bbf290df0a62fc819b3c51
 runc:
  Version:          1.5.2
  GitCommit:        v1.5.2-0-g29dd3dc2
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
Client Version: v1.36.5
Kustomize Version: v5.8.1
minikube version: v1.39.0
commit: 7a9f6a841470a207de8cf4bafcccee0969d8ba10
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured

CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         minikube   minikube   minikube   default
NAME       STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION                   CONTAINER-RUNTIME
minikube   Ready    control-plane   38s   v1.37.0   192.168.49.2   <none>        Debian GNU/Linux 12 (bookworm)   7.2.15-200.fc44.x86_64 (amd64)   containerd://2.3.4
```
