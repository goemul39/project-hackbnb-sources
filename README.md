<img src="./front/public/img/logo.png" alt="logo" width="200"/>

HackBNB est une plateforme en ligne qui permet à des professionnels de la cybersécurité de trouver des lieux de séjour adaptés à leurs activités, dans un cadre légal et communautaire.

## Lancer le projet

Il faut d'abord créer un fichier `.env` à partir de l'exemple, puis mettre la clé Stripe dedans :

```bash
cp .env.example .env
# éditer .env pour mettre STRIPE_API_KEY
docker compose up
```

La plateforme est ensuite accessible sur http://localhost:9000.
Le fichier `.env` n'est pas versionné, donc pas de clé dans le dépôt.

## Clé Stripe dans l'historique Git

Une clé Stripe a été trouvée dans le dépôt et dans l'historique (voir D6).
Après l'avoir révoquée et remplacée dans le dashboard Stripe, on peut nettoyer l'historique :

```bash
./scripts/purge-stripe-keys-history.sh
git remote add origin <url-du-depot>
git push --force --all origin
```

Le script enlève les clés des anciens commits. Ça réécrit l'historique, donc il faut prévenir l'équipe avant de force push.
