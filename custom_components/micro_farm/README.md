# Micro Ferme pour Home Assistant

Integration locale pour suivre la production et l'autonomie d'une petite ferme:
poulailler, potager, reserve d'eau, stock de nourriture et batterie.

## Entites creees

Champs modifiables:

- `Oeufs aujourd'hui`
- `Recolte aujourd'hui`
- `Stock nourriture`
- `Stock eau`
- `Batterie`
- `Humidite du sol`

Capteurs calcules:

- `Autonomie nourriture`
- `Autonomie eau`
- `Autonomie minimale`
- `Etat de production`
- `Oeufs produits`
- `Recolte produite`

Alertes:

- `Nourriture basse`
- `Eau basse`
- `Batterie basse`
- `Sol sec`

Boutons:

- `Ajouter un oeuf`
- `Remettre la production du jour a zero`

## Installation

1. Copier le dossier `custom_components/micro_farm` dans le dossier
   `custom_components` de Home Assistant.
2. Redemarrer Home Assistant.
3. Aller dans `Parametres > Appareils et services > Ajouter une integration`.
4. Chercher `Micro Ferme`.

## Configuration

Les seuils configurables servent aux calculs d'autonomie et aux alertes:

- consommation quotidienne de nourriture;
- consommation quotidienne d'eau;
- seuil de stock nourriture bas en jours;
- seuil de stock eau bas en jours;
- seuil batterie basse;
- seuil humidite de sol sec.

Les valeurs de production et de stock sont conservees par Home Assistant et peuvent
etre modifiees depuis le tableau de bord, une automatisation ou les boutons fournis.
