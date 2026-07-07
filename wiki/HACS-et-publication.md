# HACS et publication

## Depot personnalise HACS

CrueVeille peut deja etre installe comme depot personnalise HACS:

`https://github.com/vico34/crueveille`

Categorie:

`Integration`

## Release GitHub

HACS s'appuie sur les tags/releases pour proposer proprement les versions.

Version actuelle:

- tag: `v0.1.1`;
- manifest: `"version": "0.1.1"`.

Pour finaliser une release GitHub:

1. Aller sur https://github.com/vico34/crueveille/releases.
2. Cliquer sur `Draft a new release`.
3. Selectionner le tag `v0.1.1`.
4. Titre: `v0.1.1`.
5. Publier la release.

## Inclusion dans les depots HACS par defaut

Pour demander l'inclusion dans `hacs/default`, il faut generalement:

- un depot public;
- un `hacs.json` valide;
- un `manifest.json` avec `issue_tracker`;
- une release GitHub;
- des GitHub Actions HACS/Hassfest au vert;
- une documentation d'installation claire;
- une demande d'ajout via PR dans https://github.com/hacs/default.

Le depot contient deja un workflow de validation dans `.github/workflows/validate.yml`.
