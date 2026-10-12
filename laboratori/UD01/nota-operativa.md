# Nota operativa — UD01

La cartella di lavoro si trova nel filesystem nativo di Fedora Linux 44 (non Windows/WSL) ed è
stata aperta con Visual Studio Code nativo per Linux, senza passare da alcuna estensione WSL
(non applicabile su questo sistema, dove non è presente un host Windows).

Il controllo che ha dimostrato il corretto contesto di esecuzione è:

```bash
pwd
```

L'output ha mostrato un percorso nella home Linux (`~/workspace/azure-devops-lab`), coerente
con l'assenza di qualunque mount di tipo `/mnt/c`, che su questo sistema non esiste perché il
sistema operativo è Linux nativo e non Windows con WSL.
