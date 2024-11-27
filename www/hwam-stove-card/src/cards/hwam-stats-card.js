import { LitElement, html, css } from 'lit-element';
import { HomeAssistant } from 'custom-card-helpers';
import Chart from 'chart.js/auto';

class HWAMStatsCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _chart: { type: Object }
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
      }
      .stats-card {
        background: var(--ha-card-background, var(--card-background-color, white));
        border-radius: var(--ha-card-border-radius, 4px);
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px 0 rgba(0, 0, 0, 0.14));
      }
      .header {
        padding: 16px;
        font-size: 18px;
        font-weight: bold;
      }
      .chart-container {
        height: 200px;
        position: relative;
        margin-bottom: 16px;
      }
      .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        padding: 16px;
      }
      .stat-box {
        background: var(--secondary-background-color);
        padding: 12px;
        border-radius: 4px;
        text-align: center;
      }
      .stat-value {
        font-size: 20px;
        font-weight: bold;
        margin: 8px 0;
      }
      .stat-label {
        font-size: 14px;
        color: var(--secondary-text-color);
      }
      .details {
        padding: 16px;
        border-top: 1px solid var(--divider-color);
      }
      .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
      }
    `;
  }

  firstUpdated() {
    this._createChart();
  }

  updated(changedProps) {
    if (changedProps.has('hass')) {
      this._updateChart();
    }
  }

  _createChart() {
    const ctx = this.shadowRoot.querySelector('canvas').getContext('2d');
    
    this._chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Température poêle',
            borderColor: 'rgb(255, 99, 132)',
            data: []
          },
          {
            label: 'Température pièce',
            borderColor: 'rgb(54, 162, 235)',
            data: []
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }

  _updateChart() {
    if (!this._chart || !this.hass || !this.config) return;

    const stoveHistory = this.hass.states[this.config.stove_temperature].attributes.history || [];
    const roomHistory = this.hass.states[this.config.room_temperature].attributes.history || [];

    this._chart.data.labels = stoveHistory.map(h => new Date(h.time).toLocaleTimeString());
    this._chart.data.datasets[0].data = stoveHistory.map(h => h.value);
    this._chart.data.datasets[1].data = roomHistory.map(h => h.value);
    this._chart.update();
  }

  render() {
    if (!this.hass || !this.config) return html``;

    const stoveTemp = this.hass.states[this.config.stove_temperature];
    const roomTemp = this.hass.states[this.config.room_temperature];
    const efficiency = this.hass.states[this.config.efficiency_score];
    const burnTime = this.hass.states[this.config.burn_time];
    const doorCount = this.hass.states[this.config.door_count];

    return html`
      <ha-card class="stats-card">
        <div class="header">
          Statistiques HWAM
        </div>
        
        <div class="chart-container">
          <canvas></canvas>
        </div>

        <div class="stats-grid">
          <div class="stat-box">
            <div class="stat-label">Efficacité</div>
            <div class="stat-value">${efficiency ? efficiency.state : 'N/A'}%</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Temps de chauffe</div>
            <div class="stat-value">${burnTime ? burnTime.state : 'N/A'}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Ouvertures porte</div>
            <div class="stat-value">${doorCount ? doorCount.state : '0'}</div>
          </div>
        </div>

        <div class="details">
          <div class="detail-row">
            <span>Température max (24h)</span>
            <span>${stoveTemp ? stoveTemp.attributes.max_24h : 'N/A'}°C</span>
          </div>
          <div class="detail-row">
            <span>Température min (24h)</span>
            <span>${stoveTemp ? stoveTemp.attributes.min_24h : 'N/A'}°C</span>
          </div>
          <div class="detail-row">
            <span>Température moyenne pièce</span>
            <span>${roomTemp ? roomTemp.attributes.average : 'N/A'}°C</span>
          </div>
        </div>
      </ha-card>
    `;
  }

  setConfig(config) {
    if (!config.stove_temperature) throw new Error('Définir stove_temperature');
    if (!config.room_temperature) throw new Error('Définir room_temperature');
    if (!config.efficiency_score) throw new Error('Définir efficiency_score');
    this.config = config;
  }

  getCardSize() {
    return 4;
  }
}

customElements.define('hwam-stats-card', HWAMStatsCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'hwam-stats-card',
  name: 'HWAM Statistics Card',
  description: 'Carte de statistiques pour le poêle HWAM'
});
