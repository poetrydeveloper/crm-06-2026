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
      const response = await fetch('/api/v1/warehouse/purchase-rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price_operator: operator,
          price_value: parseFloat(price),
          name_contains: keyword.trim() || null,
          stock_threshold: parseInt(threshold)
        })
      });

      if (response.ok) {
        alert('🎉 Аналитическое правило успешно внесено в матрицу автозаказа!');
        setPrice('');
        setKeyword('');
        setThreshold('');
        onRuleCreated(); // Оповещаем родительскую страницу о необходимости обновить списки
      }
    } catch (err) {
      console.error('Сетевой сбой при сохранении правила:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ 
      background: '#1a1a1a', padding: '20px', borderRadius: '6px', 
      border: '1px solid #333', marginBottom: '25px'
    }}>
      <h3 style={{ margin: '0 0 15px 0', color: '#4fa8ff', fontSize: '15px' }}>
        ⚙️ Собрать новое правило снабжения (Конструктор тегов)
      </h3>
      <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
        
        <div>
          <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>Если розничная цена:</label>
          <select value={operator} onChange={(e) => setOperator(e.target.value)} style={{ padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px', outline: 'none' }}>
            <option value=">">&gt; (Больше)</option>
            <option value="<">&lt; (Меньше)</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>Порог стоимости (₽):</label>
          <input type="number" required value={price} onChange={(e) => setPrice(e.target.value)} placeholder="80" style={{ width: '90px', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px', outline: 'none' }} />
        </div>

        <div style={{ flex: 1, minWidth: '150px' }}>
          <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>В названии содержится слово (Тег):</label>
          <input type="text" value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="например: бита" style={{ width: '100%', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px', outline: 'none' }} />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>Остаток &lt; :</label>
          <input type="number" required value={threshold} onChange={(e) => setThreshold(e.target.value)} placeholder="3" style={{ width: '70px', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px', outline: 'none' }} />
        </div>

        <button type="submit" style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '9px 20px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px' }}>
          + Внедрить в СУБД
        </button>
      </div>
    </form>
  );
};
