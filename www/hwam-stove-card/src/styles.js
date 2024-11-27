import { css } from 'lit-element';

export const styles = css`
  :host {
    --hwam-primary: var(--primary-color, #03a9f4);
    --hwam-secondary: var(--secondary-color, #2196f3);
    --hwam-background: var(--card-background-color, var(--ha-card-background, white));
    --hwam-text-primary: var(--primary-text-color, #212121);
    --hwam-text-secondary: var(--secondary-text-color, #727272);
    --hwam-divider: var(--divider-color, #dbdbdb);
    --hwam-warning: var(--warning-color, #ffa726);
    --hwam-error: var(--error-color, #db4437);
    --hwam-success: var(--success-color, #66bb6a);
  }

  ha-card {
    background: var(--hwam-background);
    color: var(--hwam-text-primary);
    padding: 16px;
    border-radius: var(--ha-card-border-radius, 4px);
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .temp-box {
    background: var(--ha-card-background, var(--card-background-color));
    border: 1px solid var(--hwam-divider);
    border-radius: 8px;
    padding: 16px;
  }

  .temp-value {
    font-size: 24px;
    font-weight: bold;
    color: var(--hwam-text-primary);
  }

  .temp-label {
    color: var(--hwam-text-secondary);
    font-size: 14px;
  }

  .slider {
    --paper-slider-active-color: var(--hwam-primary);
    --paper-slider-secondary-color: var(--hwam-secondary);
    --paper-slider-knob-color: var(--hwam-primary);
    --paper-slider-pin-color: var(--hwam-primary);
    width: 100%;
    margin: 8px 0;
  }

  .stat-box {
    background: var(--ha-card-background, var(--card-background-color));
    border: 1px solid var(--hwam-divider);
    border-radius: 4px;
    padding: 12px;
  }

  .chart-container {
    margin: 16px 0;
    border: 1px solid var(--hwam-divider);
    border-radius: 4px;
    padding: 8px;
    background: var(--hwam-background);
  }

  /* Dark theme optimizations */
  @media (prefers-color-scheme: dark) {
    .temp-box, .stat-box {
      border-color: var(--hwam-divider);
      background: rgba(255, 255, 255, 0.05);
    }
  }
`;
