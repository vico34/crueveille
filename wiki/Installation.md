# Installation

## Installation avec HACS

Le depot est compatible HACS comme depot personnalise.

1. Ouvrir HACS dans Home Assistant.
2. Aller dans `Integrations`.
3. Ouvrir le menu puis `Depots personnalises`.
4. Ajouter le depot:

   `https://github.com/vico34/crueveille`

5. Choisir la categorie `Integration`.
6. Installer `CrueVeille`.
7. Redemarrer completement Home Assistant.
8. Aller dans `Parametres > Appareils et services > Ajouter une integration`.
9. Chercher `CrueVeille`.

Lien direct:

https://my.home-assistant.io/redirect/hacs_repository/?owner=vico34&repository=crueveille&category=integration

## Installation manuelle

1. Telecharger le depot GitHub.
2. Copier le dossier `custom_components/vigicrues_alert` dans le dossier `custom_components` de Home Assistant.
3. Redemarrer Home Assistant.
4. Ajouter l'integration depuis `Parametres > Appareils et services`.

## Mise a jour

Apres une mise a jour HACS, redemarrer Home Assistant. Un simple rechargement YAML ne suffit pas pour recharger correctement un `config_flow.py` ou un `manifest.json`.

La version `0.1.1` corrige un probleme de serialisation du formulaire de configuration Home Assistant.
