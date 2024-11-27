#!/bin/bash

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installation des cartes HWAM Smart Control...${NC}"

# Vérification de l'environnement Home Assistant
if [ ! -d "/config" ]; then
    echo -e "${RED}Erreur: Ce script doit être exécuté dans l'environnement Home Assistant${NC}"
    exit 1
fi

# Création du dossier www s'il n'existe pas
if [ ! -d "/config/www" ]; then
    echo "Création du dossier www..."
    mkdir -p /config/www
fi

# Création du dossier pour les cartes
CARD_DIR="/config/www/hwam-stove-card"
if [ ! -d "$CARD_DIR" ]; then
    echo "Création du dossier hwam-stove-card..."
    mkdir -p "$CARD_DIR"
fi

# Installation des dépendances Node.js
echo "Installation des dépendances..."
cd "$CARD_DIR"
npm install

# Construction des cartes
echo "Construction des cartes..."
npm run build

# Vérification de la configuration Lovelace
CONFIG_FILE="/config/ui-lovelace.yaml"
if [ -f "$CONFIG_FILE" ]; then
    if ! grep -q "hwam-card.js" "$CONFIG_FILE"; then
        echo "Ajout de la ressource dans la configuration Lovelace..."
        echo "
resources:
  - url: /local/hwam-stove-card/dist/hwam-card.js
    type: module" >> "$CONFIG_FILE"
    fi
else
    echo -e "${BLUE}Note: Configuration Lovelace non trouvée. Ajoutez manuellement la ressource:${NC}"
    echo "
resources:
  - url: /local/hwam-stove-card/dist/hwam-card.js
    type: module"
fi

# Message de fin
echo -e "${GREEN}Installation terminée!${NC}"
echo -e "Pour utiliser les cartes, ajoutez dans votre tableau de bord:"
echo -e "${BLUE}
type: 'custom:hwam-main-card'
stove_temperature: sensor.hwam_stove_temperature
room_temperature: sensor.hwam_room_temperature
burn_level: number.hwam_burn_level
oxygen_level: sensor.hwam_oxygen_level
door_sensor: binary_sensor.hwam_door

type: 'custom:hwam-stats-card'
stove_temperature: sensor.hwam_stove_temperature
room_temperature: sensor.hwam_room_temperature
efficiency_score: sensor.hwam_efficiency_score
burn_time: sensor.hwam_burn_time
door_count: sensor.hwam_door_count${NC}"

# Redémarrage de Home Assistant
echo -e "${BLUE}Voulez-vous redémarrer Home Assistant maintenant? (o/n)${NC}"
read -r response
if [[ "$response" =~ ^([oO])$ ]]; then
    echo "Redémarrage de Home Assistant..."
    ha core restart
fi
