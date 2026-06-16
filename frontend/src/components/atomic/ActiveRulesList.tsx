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
  return (
    <div style={{ 
      background: '#1a1a1a', padding: '20px', borderRadius: '6px', 
      border: '1px solid #333', marginBottom: '25px' 
    }}>
      <h3 style={{ margin: '0 0 12px 0', color: '#aaa', fontSize: '13px', fontWeight: 'bold', textTransform: 'uppercase' }}>
        📋 Текущие активные матрицы автозаказа (Теги СУБД)
      </h3>
      
      {rules.length === 0 ? (
        <div style={{ color: '#555', fontSize: '13px' }}>Динамические правила в конструкторе отсутствуют. Система использует базовый порог дефицита.</div>
      ) : (
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {rules.map(rule => (
            <div key={rule.id} style={{ 
              background: '#2d2d2d', 
              border: '1px solid #444', 
              padding: '6px 12px', 
              borderRadius: '20px',
              fontSize: '13px',
              color: '#4fa8ff',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span style={{ fontWeight: 'bold', color: '#888' }}>#{rule.id}</span>
              <span>Цена {rule.price_operator} {rule.price_value} ₽</span>
              {rule.name_contains && (
                <span style={{ background: '#1b3a4b', color: '#81c784', padding: '1px 6px', borderRadius: '3px', fontSize: '11px' }}>
                  текст: "{rule.name_contains}"
                </span>
              )}
              <span style={{ color: '#ffb74d' }}>➡️ порог &lt; {rule.stock_threshold} шт</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
