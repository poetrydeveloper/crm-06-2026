// frontend/src/components/atomic/ActiveRulesList.tsx
import React from 'react';

interface RuleRecord {
  id: number;
  price_operator: string;
  price_value: number;
  name_contains: string | null;
  stock_threshold: number;
}

interface ActiveRulesListProps {
  rules: RuleRecord[];
}

export const ActiveRulesList: React.FC<ActiveRulesListProps> = ({ rules }) => {
  if (rules.length === 0) {
    return (
      <div className="card mb-3">
        <p className="text-muted" style={{ margin: 0 }}>Правила не заданы. Используется базовый порог дефицита.</p>
      </div>
    );
  }

  return (
    <div className="card mb-3">
      <h3 className="card-title">Активные правила</h3>
      <div className="d-flex gap-8 flex-wrap">
        {rules.map((rule) => (
          <span key={rule.id} className="badge badge-info" style={{ fontSize: '13px', padding: '6px 12px' }}>
            Цена {rule.price_operator} {rule.price_value} ₽
            {rule.name_contains && <> — «{rule.name_contains}»</>}
            {' → '}остаток &lt; {rule.stock_threshold} шт.
          </span>
        ))}
      </div>
    </div>
  );
};