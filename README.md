# StudyOnline

Le but de ce projet est de développer une plateforme éducative interactive avec des fonctionnalités basiques à l’aide de Redis, une base de données en mémoire, et Django, un framework de développement web en Python.

## Installation

### Avec nix

```bash
nix-shell
```

### Sans nix

#### Dépendences

- redis
- python3 (avec pip)

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
redis-server &
python manage.py runserver
```


## Spécifications de l’application

1. La plateforme éducative doit proposer des cours, des professeurs et des étudiants. Chaque cours a un ID, un titre, un enseignant et une liste d’étudiants inscrits. Les cours peuvent également avoir d’autres propriétés, telles que le résumé du cours, le niveau du cours (débutant, intermédiaire, avancé), et le nombre de places disponibles.

2. Les professeurs et les étudiants ont des profils contenant des informations telles que le nom, l’ID, les cours auxquels ils sont inscrits (pour les étudiants) ou les cours qu’ils enseignent (pour les professeurs). Les profils doivent également inclure des fonctionnalités pour mettre à jour ces informations.

3. Implémentez un système de nouvelles de type publish-subscribe qui :  
N'a pas été fait du à un maque de compréhension du système de notifications en temps réel de django, et cela malgrès le fait que j'ai compris le système pub/sub de redis (cf. TP2).
   1. Du côté de l’éditeur, permet à l’enseignant de publier des mises à jour de cours, de créer de nouveaux cours et d’émettre un message de nouvelles contenant l’ID du cours mis à jour ou nouvellement créé.
   2. Du côté de l’abonné, permet aux étudiants de s’abonner aux mises à jour du cours, de récupérer les détails du cours à partir d’une nouvelle par l’ID et d’afficher l’entrée complète du cours à partir de la base de données. Les étudiants doivent également pouvoir s’inscrire à des cours via la plateforme.

4. Fait expirer les cours après un certain temps (si le cours n’est pas mis à jour ou si personne ne s’y inscrit) : ces cours ne sont plus disponibles pour l’inscription.

5. Si un étudiant s’inscrit à un cours (par exemple, en définissant un certain champ dans la base de données), fait rafraîchir la date d’expiration du cours.

6. La plateforme doit également inclure une fonction de recherche qui permet aux utilisateurs de chercher des cours par titre, enseignant, niveau, ou d’autres critères pertinents.

## Livrable du Projet

- Code source de l’application, y compris tous les fichiers et les dépendances nécessaires pour exécuter l’application.
- Documentation détaillée expliquant comment exécuter l’application, y compris l’installation de Redis, Django et de toute autre dépendance nécessaire.

