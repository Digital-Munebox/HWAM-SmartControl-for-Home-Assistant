# HWAM Smart Control pour Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Cette intégration Home Assistant permet de superviser et de contrôler les poêles à bois HWAM équipés du système Smart Control (IHS).

## Fonctionnalités

### Supervision en temps réel
- 🌡️ Températures
  - Température du poêle
  - Température ambiante
  - Historique sur 24h
- 💨 Niveau d'oxygène
- 🔥 Phase de combustion
- 🚪 État de la porte
- ⚡ Mode de fonctionnement

### Contrôles disponibles
- 🎚️ Niveau de combustion (0-5)
- ⏰ Mode nuit (programmation)
- ▶️ Démarrage de la combustion

### Alertes et notifications
- ⚠️ Alarmes de maintenance
- 🚨 Alarmes de sécurité
- 🪵 Alertes de rechargement
- 🚪 Détection porte ouverte

### Statistiques
- 📊 Historique des températures (24h)
- 📈 Tendances de combustion
- 🔍 Suivi de l'état du système

## Installation

### Via HACS (recommandé)
1. Ouvrir HACS dans Home Assistant
2. Ajouter ce dépôt comme "Dépôt personnalisé"
3. Rechercher "HWAM Smart Control"
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
4. Renseigner :
   - L'adresse IP ou le nom d'hôte du poêle
   - Un nom personnalisé (optionnel)

## Entités créées

### Capteurs (sensor)
| Entité | Description | Unité |
|--------|-------------|-------|
| `sensor.hwam_stove_temperature` | Température du poêle | °C |
| `sensor.hwam_room_temperature` | Température ambiante | °C |
| `sensor.hwam_oxygen_level` | Niveau d'oxygène | % |
| `sensor.hwam_burn_phase` | Phase de combustion | - |
| `sensor.hwam_valve1` | Position valve 1 | % |
| `sensor.hwam_valve2` | Position valve 2 | % |
| `sensor.hwam_valve3` | Position valve 3 | % |

### Capteurs binaires (binary_sensor)
| Entité | Description |
|--------|-------------|
| `binary_sensor.hwam_door` | État de la porte |
| `binary_sensor.hwam_maintenance_needed` | Besoin de maintenance |
| `binary_sensor.hwam_safety_alarm` | Alarme de sécurité |
| `binary_sensor.hwam_refill_needed` | Besoin de rechargement |

### Contrôles
| Entité | Description |
|--------|-------------|
| `number.hwam_burn_level` | Niveau de combustion (0-5) |
| `switch.hwam_night_mode` | Mode nuit |

## Services disponibles

### `hwam_stove.start_combustion`
Démarre le processus de combustion.

### `hwam_stove.set_burn_level`
Définit le niveau de combustion.
```yaml
service: hwam_stove.set_burn_level
data:
  level: 3  # Valeur entre 0 et 5
```

### `hwam_stove.set_night_mode`
Configure les horaires du mode nuit.
```yaml
service: hwam_stove.set_night_mode
data:
  start_time: "22:00"
  end_time: "06:00"
```

## Exemples d'automatisations

### Activation du mode nuit
```yaml
automation:
  - alias: "Mode nuit poêle HWAM"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.hwam_night_mode
```

### Notification de température élevée
```yaml
automation:
  - alias: "Alerte température poêle"
    trigger:
      - platform: numeric_state
        entity_id: sensor.hwam_stove_temperature
        above: 500
    action:
      - service: notify.notify
        data:
          title: "HWAM - Température élevée"
          message: "La température du poêle est très élevée!"
```

## Notes importantes

- Cette intégration respecte le fonctionnement natif du système IHS (Intelligent Heat System)
- L'algorithme interne du poêle gère automatiquement les valves d'air pour une combustion optimale
- Le contrôle du niveau de combustion (0-5) permet d'ajuster la puissance globale souhaitée
- Les données sont mises à jour toutes les 30 secondes par défaut

## Dépannage

### Le poêle n'est pas détecté
1. Vérifier que le poêle est connecté au réseau
2. Vérifier l'adresse IP
3. Tester la connexion avec `ping [adresse_ip]`

### Erreurs de connexion
1. Vérifier que le poêle est allumé
2. Redémarrer le poêle si nécessaire
3. Vérifier les logs Home Assistant

## Support

- Ouvrir une issue sur GitHub
- Documentation HWAM: [lien]

## Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
