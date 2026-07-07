# Configuration

CrueVeille peut surveiller une station de deux facons.

## Par position

Renseigner:

- latitude;
- longitude;
- rayon de recherche en kilometres.

L'integration recherche la station hydrometrique la plus proche dans le rayon configure.

## Par code station

Renseigner directement le code station Vigicrues/Hub'Eau dans le champ `Code station Vigicrues`.

Quand un code station est fourni, il est prioritaire sur la recherche par position.

## Seuils

Les seuils de hauteur sont propres a chaque station et a son repere local. Il n'existe pas de seuil universel fiable.

Champs utiles:

- `Seuil hauteur vigilance (m)`;
- `Seuil hauteur critique (m)`;
- `Hausse vigilance (cm/h)`;
- `Hausse critique (cm/h)`;
- `Projection (heures)`;
- `Niveau qui declenche l'alerte`.

Sans seuil de hauteur, CrueVeille peut quand meme signaler une hausse rapide via la vitesse de montee.

## Conseils de reglage

- Commencer avec des seuils conservateurs.
- Comparer pendant quelques jours les valeurs CrueVeille avec les courbes Vigicrues officielles.
- Ajuster les seuils selon le comportement local de la riviere et la distance entre la station et le lieu surveille.
