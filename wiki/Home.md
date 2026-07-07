# CrueVeille

CrueVeille est une integration personnalisee Home Assistant pour surveiller une station hydrometrique Vigicrues/Hub'Eau proche d'une position et generer des alertes locales de risque d'inondation.

## Pages

- [Installation](Installation)
- [Configuration](Configuration)
- [Capteurs et alertes](Capteurs-et-alertes)
- [Depannage](Depannage)
- [HACS et publication](HACS-et-publication)

## Version actuelle

- Version integration: `0.1.1`
- Depot: https://github.com/vico34/crueveille
- Release/tag: `v0.1.1`

## Sources de donnees

CrueVeille utilise l'API Hydrometrie Hub'Eau, alimentee par les donnees hydrometriques publiees par les services Vigicrues.

- API Hub'Eau Hydrometrie: https://hubeau.eaufrance.fr/page/api-hydrometrie
- Vigicrues: https://www.vigicrues.gouv.fr/

## Avertissement

CrueVeille ne remplace pas les bulletins officiels Vigicrues, les consignes prefectorales, FR-Alert ou les dispositifs communaux. L'integration produit un signal domotique local base sur les mesures disponibles et les seuils configures par l'utilisateur.
