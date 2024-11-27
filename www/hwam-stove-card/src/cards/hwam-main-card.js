import { LitElement, html, css } from 'lit-element';
import { HomeAssistant } from 'custom-card-helpers';

class HWAMMainCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object }
    };
  }

  static get styles() {
    return css`
      :host {
        background: var(--ha-card-background, var(--card-background-color, white));
        border-radius: var(--ha-card-border-radius, 4px);
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px 0 rgba(0, 0, 0, 0.14));
        color: var(--primary-text-color);
        display: block;
        padding: 16px;
      }
      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
      }
      .temperatures {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
      }
      .temp-box {
        background: var(--secondary-background-color);
        padding: 16px;
        border-radius: 4px;
        text-align: center;
      }
      .temp-value {
        font-size: 24px;
        font-weight: bold;
      }
      .slider {
        width: 100%;
        margin: 16px 0;
      }
      .status-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 8px;
      }
      .status-item {
        background: var(--secondary-background-color);
        padding: 8px;
        border-radius: 4px;
        text-align: center;
      }
    `;
  }

  render() {
    if (!this.hass || !this.config) {
      return html``;
    }

    const stoveTemp = this.hass.states[this.config.stove_temperature];
    const roomTemp = this.hass.states[this.config.room_temperature];
    const burnLevel = this.hass.states[this.config.burn_level];
    const oxygenLevel = this.hass.states[this.config.oxygen_level];
    const doorState = this.hass.states[this.config.door_sensor];

    return html`
      <ha-card>
        <div class="header">
          <div>HWAM Smart Control</div>
          <div>Mode: ${burnLevel ? burnLevel.state : 'N/A'}</div>
        </div>

        <div class="temperatures">
          <div class="temp-box">
            <div class="temp-value">${stoveTemp ? stoveTemp.state : 'N/A'}°C</div>
            <div>Température poêle</div>
          </div>
          <div class="temp-box">
            <div class="temp-value">${roomTemp ? roomTemp.state : 'N/A'}°C</div>
            <div>Température pièce</div>
          </div>
        </div>

        <div class="burn-level">
          <div>Niveau de combustion</div>
          <ha-slider
            class="slider"
            min="0"
            max="5"
            step="1"
            value="${burnLevel ? burnLevel.state : 0}"
            @change="${this._setBurnLevel}"
          ></ha-slider>
        </div>

        <div class="status-grid">
          <div class="status-item">
            <div>Oxygène</div>
            <div>${oxygenLevel ? oxygenLevel.state : 'N/A'}%</div>
          </div>
          <div class="status-item">
            <div>Mode</div>
            <div>${this._getPhaseText(burnLevel ? burnLevel.state : null)}</div>
          </div>
          <div class="status-item">
            <div>Porte</div>
            <div>${doorState ? (doorState.state === 'on' ? 'Ouverte' : 'Fermée') : 'N/A'}</div>
          </div>
        </div>
      </ha-card>
    `;
  }

  setConfig(config) {
    if (!config.stove_temperature) {
      throw new Error('You need to define stove_temperature');
    }
    if (!config.room_temperature) {
      throw new Error('You need to define room_temperature');
    }
    if (!config.burn_level) {
      throw new Error('You need to define burn_level');
    }
    this.config = config;
  }

  _setBurnLevel(e) {
    const value = e.target.value;
    this.hass.callService('hwam_stove', 'set_burn_level', {
      entity_id: this.config.burn_level,
      level: value
    });
  }

  _getPhaseText(phase) {
    const phases = {
      1: 'Allumage',
      2: 'Démarrage',
      3: 'Combustion',
      4: 'Braises',
      5: 'Veille'
    };
    return phases[phase] || 'Inconnu';
  }

  // Get card size for Home Assistant
  getCardSize() {
    return 3;
  }
}

customElements.define('hwam-main-card', HWAMMainCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'hwam-main-card',
  name: 'HWAM Smart Control Card',
  description: 'Carte personnalisée pour le poêle HWAM'
});
