# Cartes personnalisées HWAM Smart Control

## Installation

1. Copier le dossier `hwam-stove-card` dans le dossier `www` de votre installation Home Assistant
2. Ajouter le code suivant à votre configuration Lovelace (via l'interface ou `configuration.yaml`) :

```yaml
resources:
  - url: /local/hwam-stove-card/dist/hwam-card.js
    type: module
```

## Utilisation

### Carte principale
```yaml
type: 'custom:hwam-main-card'
stove_temperature: sensor.hwam_stove_temperature
room_temperature: sensor.hwam_room_temperature
burn_level: number.hwam_burn_level
oxygen_level: sensor.hwam_oxygen_level
door_sensor: binary_sensor.hwam_door
```

## Développement

1. Installation des dépendances
```bash
npm install
```

2. Construction
```bash
npm run build
```

3. Mode développement (reconstruction automatique)
```bash
npm run watch
```

## Personnalisation

Les styles peuvent être personnalisés via les variables CSS de Home Assistant ou en modifiant directement le fichier source.
