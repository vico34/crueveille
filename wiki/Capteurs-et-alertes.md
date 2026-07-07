# Capteurs et alertes

CrueVeille expose des capteurs Home Assistant et un capteur binaire d'alerte.

## Capteurs

- `Hauteur d'eau`: hauteur d'eau en metres.
- `Debit`: debit en m3/s.
- `Vitesse de montee`: tendance recente en cm/h.
- `Hauteur projetee`: extrapolation simple de la tendance sur la duree configuree.
- `Risque local`: niveau calcule par l'integration.
- `Distance station`: distance entre la position configuree et la station retenue.

## Capteur binaire

`Alerte inondation` passe a `on` quand le niveau de risque local atteint le niveau choisi dans la configuration.

## Niveaux de risque

- `clear`: pas de signal local.
- `watch`: niveau en hausse ou donnees partielles.
- `warning`: seuil de vigilance atteint ou hausse rapide.
- `critical`: seuil critique atteint ou montee tres rapide.

## Logique de projection

La hauteur projetee est une extrapolation lineaire simple de la vitesse de montee recente. Ce n'est pas une prevision officielle Vigicrues.

Exemple:

- hauteur actuelle: `1.20 m`;
- vitesse de montee: `10 cm/h`;
- projection: `3 h`;
- hauteur projetee: `1.50 m`.
