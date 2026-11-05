#!/usr/bin/env bash
# Legge cluster/Docker e scrive soltanto .env locale; non avvia container.
set -euo pipefail
if [ "$#" -ne 4 ]; then
  echo 'Uso: bash configura.sh NAMESPACE SERVICE PORTA_LOCALE PROGETTO_COMPOSE' >&2
  exit 2
fi
NS="$1"; SVC="$2"; ENTRY_PORT="$3"; PROJECT="$4"
[[ "$NS" =~ ^[a-z0-9-]+$ && "$SVC" =~ ^[a-z0-9-]+$ && "$PROJECT" =~ ^ft152-entry-ud(16|18)$ ]] || exit 2
[[ "$ENTRY_PORT" =~ ^[0-9]+$ ]] && (( ENTRY_PORT >= 1024 && ENTRY_PORT <= 65535 )) || exit 2
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v python3 >/dev/null
docker compose version
kubectl --context=minikube get node minikube >/dev/null
# Il corso usa il profilo Docker singolo chiamato minikube.
NODE_NAME=minikube
NETWORK=$(docker inspect "$NODE_NAME" | python3 -c 'import json,sys; d=json.load(sys.stdin)[0]; assert d["State"]["Running"], "Nodo Docker fermo"; n=list(d["NetworkSettings"]["Networks"]); assert len(n)==1, "Reti multiple: leggere e adattare prima di procedere"; print(n[0])')
[[ "$NETWORK" =~ ^[a-zA-Z0-9_.-]+$ ]] || exit 2
NODEPORT=$(kubectl --context=minikube -n "$NS" get service "$SVC" -o json | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["spec"]["type"]=="NodePort", "Atteso Service NodePort"; p=[p for p in d["spec"]["ports"] if p["port"]==80 and p.get("protocol","TCP")=="TCP"]; assert len(p)==1; print(p[0]["nodePort"])')
[[ "$NODEPORT" =~ ^[0-9]+$ ]] || exit 2
TARGET=$(mktemp)
trap 'rm -f "$TARGET"' EXIT
printf 'COMPOSE_PROJECT_NAME=%s\nENTRY_PORT=%s\nNODE_NAME=%s\nGATEWAY_NODEPORT=%s\nK8S_DOCKER_NETWORK=%s\n' "$PROJECT" "$ENTRY_PORT" "$NODE_NAME" "$NODEPORT" "$NETWORK" > "$TARGET"
if [ -e .env ] && ! cmp -s .env "$TARGET"; then
  echo '.env esistente diverso: confronto richiesto; nessuna sovrascrittura.' >&2
  diff -u .env "$TARGET" || true
  echo 'Conserva la configurazione precedente, poi riesegui soltanto dopo aver deciso il cambio.' >&2
  exit 1
fi
cp "$TARGET" .env
docker compose config --quiet
printf 'Configurazione verificata: localhost:%s -> %s:%s (%s)\n' "$ENTRY_PORT" "$NODE_NAME" "$NODEPORT" "$NETWORK"
echo 'Nessun container avviato. Leggi compose.yaml e usa docker compose up -d nel guidato.'
