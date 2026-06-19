// frontend/src/components/atomic/CashboxSearch.tsx
import React from 'react';

interface CashboxSearchProps {
  value: string;
  onChange: (text: string) => void;
}

export const CashboxSearch: React.FC<CashboxSearchProps> = ({ value, onChange }) => {
  return (
    <input
      type="text"
      placeholder="Поиск по названию, артикулу или серийному номеру..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="form-control"
      style={{ maxWidth: '500px' }}
    />
  );
};