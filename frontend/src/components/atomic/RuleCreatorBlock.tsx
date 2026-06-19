// frontend/src/components/atomic/RuleCreatorBlock.tsx
import React, { useState } from 'react';

interface RuleCreatorBlockProps {
  onRuleCreated: () => void;
}

export const RuleCreatorBlock: React.FC<RuleCreatorBlockProps> = ({ onRuleCreated }) => {
  const [operator, setOperator] = useState('>');
  const [price, setPrice] = useState('');
  const [keyword, setKeyword] = useState('');
  const [threshold, setThreshold] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!price || !threshold) return;

    try {
      await fetch('/api/v1/warehouse/purchase-rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price_operator: operator,
          price_value: parseFloat(price),
          name_contains: keyword.trim() || null,
          stock_threshold: parseInt(threshold),
        }),
      });
      alert('Правило создано');
      setPrice('');
      setKeyword('');
      setThreshold('');
      onRuleCreated();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card mb-3">
      <h3 className="card-title">Конструктор правил</h3>
      <div className="form-inline">
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">Цена</label>
          <select className="form-control" value={operator} onChange={(e) => setOperator(e.target.value)} style={{ width: '80px' }}>
            <option value=">">&gt;</option>
            <option value="<">&lt;</option>
          </select>
        </div>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">Порог (₽)</label>
          <input type="number" className="form-control" value={price} onChange={(e) => setPrice(e.target.value)} style={{ width: '100px' }} />
        </div>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">Ключевое слово</label>
          <input type="text" className="form-control" value={keyword} onChange={(e) => setKeyword(e.target.value)} style={{ width: '140px' }} />
        </div>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">Остаток &lt;</label>
          <input type="number" className="form-control" value={threshold} onChange={(e) => setThreshold(e.target.value)} style={{ width: '80px' }} />
        </div>
        <button type="submit" className="btn btn-success btn-sm">Создать</button>
      </div>
    </form>
  );
};