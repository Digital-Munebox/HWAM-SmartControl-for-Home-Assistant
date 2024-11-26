# HWAM Smart Control pour Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Cette intégration permet de contrôler et surveiller les poêles à bois HWAM équipés du système Smart Control via Home Assistant.

## Fonctionnalités

- 🌡️ Surveillance des températures (poêle et pièce)
- 🔥 Contrôle du niveau de combustion (0-5)
- ⏰ Programmation du mode nuit
- ⚠️ Gestion des alarmes et notifications
- 📊 Historique des températures et niveaux d'oxygène
- 🚪 Détection d'ouverture de porte
- 🌬️ Contrôle des valves d'air

## Installation

### Via HACS (recommandé)

1. Ouvrir HACS dans Home Assistant
2. Cliquer sur les trois points en haut à droite et sélectionner "Dépôts personnalisés"
3. Ajouter ce dépôt : `https://github.com/Digital-Munebox/hwam_stove`
4. Cliquer sur "Télécharger"
5. Redémarrer Home Assistant

### Installation manuelle

1. Copier le dossier `custom_components/hwam_stove` dans votre dossier `custom_components`
2. Redémarrer Home Assistant
3. Ajouter l'intégration via l'interface

## Configuration

1. Dans Home Assistant, aller dans Configuration > Intégrations
2. Cliquer sur le bouton "+" pour ajouter une intégration
3. Rechercher "HWAM Smart Control"
4. Suivre les étapes de configuration :
   - Entrer l'adresse IP ou le nom d'hôte de votre poêle
   - Donner un nom à votre poêle

## Entités créées

### Capteurs
- Température du poêle (°C)
- Température ambiante (°C)
- Niveau d'oxygène (%)
- Phase de combustion
- Mode de fonctionnement
- Positions des valves (%)

### Capteurs binaires
- État de la porte (ouvert/fermé)
- Alarme de maintenance
- Alarme de sécurité
- Besoin de rechargement

### Contrôles
- Niveau de combustion (0-5)
- Mode nuit (on/off)
- Programmation des horaires

## Services disponibles

### `hwam_stove.start_combustion`
Démarre le processus de combustion.

### `hwam_stove.set_burn_level`
Définit le niveau de combustion.
- `level`: Niveau de combustion (0-5)

### `hwam_stove.set_night_mode`
Configure les horaires du mode nuit.
- `start_time`: Heure de début
- `end_time`: Heure de fin

## Exemples d'automatisations

```yaml
# Démarrage automatique le matin
automation:
  - alias: "Démarrage poêle matin"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: hwam_stove.start_combustion
      - service: hwam_stove.set_burn_level
        data:
          level: 3

# Activation mode nuit
automation:
  - alias: "Mode nuit poêle"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: hwam_stove.set_night_mode
        data:
          start_time: "22:00"
          end_time: "06:00"
```

## Dépannage

### Le poêle n'est pas détecté

1. Vérifier que le poêle est bien connecté au réseau
2. Vérifier que l'adresse IP est correcte
3. Vérifier que le port n'est pas bloqué

### Les données ne se mettent pas à jour

1. Vérifier la connexion réseau
2. Augmenter l'intervalle de mise à jour dans les options
3. Redémarrer l'intégration

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
