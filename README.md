Bonjour, je viens de finir le projet.
Le projet fonctionne à merveille mais il y a certaines améliorations à faire sur mon travail encore :

-Après l'achat des produits, le panier s'affiche toujours avec les produits, je suis obligé de supprimer le panier avant un nouvel achat. (Je pense que les produits cart ne semblent pas se transformer en ordered donc restent dans le panier.)

-Depuis le chapitre 11 "supprimer une adresse", les adresses ne sont plus sauvegardées automatiquement après de nouveaux achats dans le profil utilisateur. (Je pense que ça vient de la partie Stripe.)

-Problème avec le test "def test_valid_login" avec les 2 dernières lignes que j'ai mises en commentaire.

En dehors de cela, je vais essayer d'intégrer Bootstrap avec le projet pour la partie esthétique et responsive ainsi que de travailler sur l'hébergement en ligne avec Digital Ocean.

pour lancer le projet vous aurez besoin de:

-installer Django
- lancer les migrations pour nourrir la base de donner:
  -python manage.py makemigrations
  -python manege.py migrate

- créer un compte stripe pour les clés identifiant et d'api: https://dashboard.stripe.com/dashboard
