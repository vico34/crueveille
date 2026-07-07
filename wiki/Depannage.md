# Depannage

## Le flux de configuration affiche une erreur 500

Mettre a jour vers `v0.1.1` ou plus recent, puis redemarrer completement Home Assistant.

La version `0.1.1` corrige l'erreur suivante:

```text
ValueError: Unable to convert schema: Any('', Coerce(float, msg=None), msg=None)
```

Cette erreur venait d'un schema de formulaire que Home Assistant ne pouvait pas serialiser.

## Home Assistant semble encore utiliser l'ancien fichier

Si les logs contiennent encore `Any('', Coerce(float))`, l'ancienne version est toujours chargee.

Actions recommandees:

1. Mettre a jour CrueVeille dans HACS.
2. Redemarrer Home Assistant.
3. Si le probleme continue, supprimer puis reinstaller l'integration HACS.
4. Verifier que `custom_components/vigicrues_alert/manifest.json` contient `"version": "0.1.1"` ou plus recent.

## Impossible de contacter l'API Hub'Eau

Verifier:

- l'acces Internet de Home Assistant;
- la disponibilite de https://hubeau.eaufrance.fr/;
- le code station renseigne;
- le rayon de recherche si la configuration se fait par position.

## Aucun capteur ne remonte de valeur

Certaines stations n'ont pas toujours hauteur et debit en temps reel. Essayer une station proche ou verifier directement la station sur Vigicrues/Hub'Eau.
