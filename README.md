# HWAM Smart Control Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release][releases-shield]][releases]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

_Intégration Home Assistant pour les poêles à bois HWAM équipés du système Smart Control™._

## À propos

Cette intégration permet de contrôler et surveiller votre poêle HWAM directement depuis Home Assistant. Elle inclut :

- 🌡️ Surveillance des températures (poêle et pièce)
- 💨 Contrôle et surveillance des niveaux d'oxygène
- 🔥 Gestion du niveau de combustion
- ⚠️ Notifications et alertes
- 📊 Statistiques et historiques
- 🎨 Cartes personnalisées pour l'interface

## Installation

### HACS (Recommandé)

1. Ouvrir HACS
2. Cliquer sur "Intégrations"
3. Cliquer sur le bouton "+"
4. Chercher "HWAM"
5. Cliquer sur "Télécharger"
6. Redémarrer Home Assistant

### Manuel

1. Utiliser ce dépôt comme template ou télécharger les sources
2. Copier le dossier `custom_components/hwam_stove` dans votre dossier `custom_components`
3. Redémarrer Home Assistant
4. Ajouter l'intégration via l'interface

## Configuration

1. Aller dans Configuration > Intégrations
2. Cliquer sur "Ajouter une intégration"
3. Chercher "HWAM Smart Control"
4. Suivre les étapes de configuration

## Interface personnalisée

Des cartes personnalisées sont disponibles pour une meilleure expérience utilisateur :

- Carte principale avec contrôles
- Carte statistiques avec graphiques
- Historique et analyses

[Voir la documentation des cartes](www/hwam-stove-card/README.md)

## Contributions

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

## Licence

MIT - Voir [LICENSE](LICENSE)

[releases-shield]: https://img.shields.io/github/release/Digital-Munebox/hwam_stove.svg
[releases]: https://github.com/Digital-Munebox/hwam_stove/releases
[maintenance-shield]: https://img.shields.io/maintenance/yes/2024.svg
[license-shield]: https://img.shields.io/github/license/Digital-Munebox/hwam_stove.svg
