// frontend/src/pages/admin/UnitMapStyles.tsx
import React from 'react';

export const UnitMapStyles: React.FC = () => (
  <style>{`
    .category-row {
      display: flex; align-items: center; gap: 8px; padding: 8px 12px;
      cursor: pointer; border-radius: var(--radius-sm); transition: background 0.1s;
      user-select: none;
    }
    .category-row:hover { background: var(--bg-secondary); }
    .category-arrow { width: 16px; font-size: 11px; color: var(--text-muted); flex-shrink: 0; }
    .category-name { font-weight: 600; font-size: 14px; flex: 1; }
    .products-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 12px; padding: 12px 0 16px 24px;
    }
    .unitmap-card {
      background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius);
      padding: 14px; display: flex; flex-direction: column; gap: 12px; box-shadow: var(--shadow-sm);
    }
    .unitmap-header { text-align: center; }
    .unitmap-code { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }
    .unitmap-brand { font-size: 11px; color: var(--primary); font-weight: 500; margin-top: 2px; }
    .unitmap-name { font-size: 13px; font-weight: 600; text-transform: capitalize; margin-top: 4px; }
    .unitmap-circle-wrap { display: flex; flex-direction: column; align-items: center; gap: 4px; }
    .unitmap-circle {
      width: 80px; height: 80px; border-radius: 50%; border: 3px solid var(--border);
      display: flex; flex-direction: column; overflow: hidden;
    }
    .circle-part { flex: 1; display: flex; align-items: center; justify-content: center; }
    .circle-top { background: #e8f0fe; color: #084298; }
    .circle-bottom { background: #e6f4ea; color: #155724; }
    .circle-divider { height: 2px; background: var(--border); }
    .circle-divider.hidden { display: none; }
    .circle-num { font-size: 18px; font-weight: 700; }
    .circle-labels { display: flex; gap: 8px; font-size: 10px; color: var(--text-muted); }
    .unitmap-footer {
      text-align: center; font-size: 11px; font-weight: 600;
      color: #856404; background: #fff3cd; padding: 4px 8px; border-radius: var(--radius-sm);
    }
  `}</style>
);
