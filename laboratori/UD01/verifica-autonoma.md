# Verifica autonoma — UD01

Il sistema è Fedora Linux nativo, non Windows con WSL: il controllo `wsl --list --verbose` non
è applicabile e non esiste una distribuzione WSL da verificare. Il repository si trova in
`/home/jj_yts/workspace/azure-devops-lab`, nel filesystem Linux nativo, e `git remote -v`
conferma che `origin` punta a `https://github.com/JesusAlvarado2005/azure-devops-lab.git`,
lo stesso repository visibile su GitHub. Il working tree è la copia dei file così come si
trovano ora sul disco; `git add` sposta le modifiche scelte nella staging area, un'area
intermedia che prepara il prossimo commit; `git commit` registra quella selezione nella storia
locale; `git push` invia i commit locali al repository remoto, dove diventano visibili. Azure
CLI è stata verificata con `az version` (2.83.0 installata); `az login` non è ancora stato
eseguito perché l'account/subscription Azure del corso non è stato ancora comunicato dal
docente. L'invito al docente (username `EttorePannain`) risulta come invito pendente in
Settings → Collaborators, non ancora accettato. Un possibile errore di contesto è lavorare per
errore dentro `~/workspace/azure-devops-k8s-01` (il repository pubblico del corso) invece che
in `azure-devops-lab`: lo si riconosce con `git remote -v`, che in quel caso mostrerebbe l'URL
del repository del corso invece del proprio.
