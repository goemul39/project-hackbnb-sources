<img src="./front/public/img/logo.png" alt="logo" width="200"/>

HackBNB est une plateforme en ligne permettant à des professionnels de la cybersécurité de trouver des lieux de séjour adaptés à leurs activités, dans un cadre légal et communautaire.

Pour démarrer le projet en local, copiez d'abord le fichier d'exemple puis renseignez vos secrets :

```bash
cp .env.example .env
# éditez .env (STRIPE_API_KEY, ...)
docker compose up
```

Le fichier `.env` est ignoré par Git : ne commitez jamais de clé API dans le dépôt.

## Sécurité — clé Stripe

Une clé Stripe a été trouvée dans l'historique Git (voir le rapport P3 / D6).
Après avoir révoqué et roulé la clé dans le dashboard Stripe, purgez l'historique :

```bash
./scripts/purge-stripe-keys-history.sh
git remote add origin <url-du-depot>
git push --force --all origin
```

Le script filtre les motifs `sk_test_`, `sk_live_`, `rk_test_`, `rk_live_` de tous
les commits. Il réécrit l'historique : prévenez l'équipe et forcez le push.

puis accéder à la plateforme : http://localhost:9001