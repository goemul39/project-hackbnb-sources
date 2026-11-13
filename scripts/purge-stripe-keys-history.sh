#!/usr/bin/env bash
#
# D6 : enlève les clés Stripe de l'historique Git.
# À lancer après avoir révoqué la clé dans Stripe. Ça réécrit l'historique,
# donc prévenir l'équipe et faire un push --force après.
#
# Usage : ./scripts/purge-stripe-keys-history.sh
#
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "git-filter-repo est requis : pip install git-filter-repo" >&2
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "Il y a des modifications non commitées, commit ou stash avant." >&2
  exit 1
fi

cat <<'WARNING'
/!\ Cette opération réécrit TOUT l'historique du dépôt.
    - faites une sauvegarde (git clone --mirror) avant ;
    - prévenez l'équipe : les hashs de commits vont changer ;
    - le remote "origin" sera retiré par git-filter-repo, il faudra le remettre ;
    - un push --force sera nécessaire.
WARNING

read -r -p "Tapez PURGE pour confirmer : " answer
if [ "$answer" != "PURGE" ]; then
  echo "Annulé."
  exit 1
fi

rules_file="$(mktemp)"
trap 'rm -f "$rules_file"' EXIT

# On ne met jamais les vraies clés dans ce script : on filtre par motif.
cat > "$rules_file" <<'RULES'
regex:sk_(test|live)_[A-Za-z0-9]{20,}==>***REMOVED***
regex:rk_(test|live)_[A-Za-z0-9]{20,}==>***REMOVED***
RULES

git filter-repo --force --replace-text "$rules_file"

echo
echo "Vérification :"
if git log --all -G '(sk|rk)_(test|live)_[A-Za-z0-9]{20,}' --oneline | grep -q .; then
  echo "  ATTENTION : il reste des clés Stripe dans l'historique." >&2
  exit 1
fi

echo "  OK : plus aucune clé Stripe dans l'historique."
echo
echo "Prochaines étapes :"
echo "  git remote add origin <url-du-depot>"
echo "  git push --force --all origin"
echo "  git push --force --tags origin"
