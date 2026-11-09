#!/usr/bin/env bash
#
# D6 — garde-fou : échoue si une clé Stripe ressemble à un secret réel dans
# les fichiers suivis par Git. À brancher en pre-commit ou en CI.
#
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

pattern='(sk|rk)_(test|live)_[A-Za-z0-9]{16,}'
if git grep -nE "$pattern" -- . ':!*.md' ':!.env.example' >/tmp/stripe-secret-hits.txt 2>/dev/null; then
  echo "Clé Stripe potentielle détectée dans des fichiers suivis :" >&2
  cat /tmp/stripe-secret-hits.txt >&2
  rm -f /tmp/stripe-secret-hits.txt
  exit 1
fi

rm -f /tmp/stripe-secret-hits.txt
echo "OK : aucune clé Stripe dans les fichiers suivis."
