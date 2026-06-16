// frontend/src/components/atomic/OrderQuickManualAdd.tsx
import React, { useState } from 'react';

interface OrderQuickManualAddProps {
  onAddItem: (productId: number, quantity: number, price: number) => void;
}

export const OrderQuickManualAdd: React.FC<OrderQuickManualAddProps> = ({ onAddItem }) => {
  const [manualProductId, setManualProductId] = useState('');
  const [manualQuantity, setManualQuantity] = useState('1');
  const [manualPrice, setManualPrice] = useState('100');

  const handleAdd = () => {
    if (!manualProductId || !manualQuantity || !manualPrice) return;
    
    onAddItem(
      parseInt(manualProductId),
      parseInt(manualQuantity) || 1,
      parseFloat(manualPrice) || 0
    );
    
    setManualProductId('');
    setManualQuantity('1');
  };

  return (
    <div style={{ background: '#252525', padding: '10px', borderRadius: '4px', border: '1px solid #333', marginTop: '4px' }}>
      <span style={{ fontSize: '10px', color: '#888', fontWeight: 'bold', display: 'block', marginBottom: '6px' }}>
        ⚡ БЫСТРОЕ ДОБАВЛЕНИЕ ПОЗИЦИИ ВРУЧНУЮ:
      </span>
      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
        <div style={{ flex: 1 }}>
          <input 
            type="number" 
            value={manualProductId} 
            onChange={(e) => setManualProductId(e.target.value)} 
            placeholder="ID товара" 
            style={{ width: '100%', padding: '6px', background: '#1a1a1a', color: '#fff', border: '1px solid #444', borderRadius: '3px', fontSize: '12px', outline: 'none' }} 
          />
        </div>
        <div style={{ width: '60px' }}>
          <input 
            type="number" 
            min="1" 
            value={manualQuantity} 
            onChange={(e) => setManualQuantity(e.target.value)} 
            placeholder="Кол-во" 
            style={{ width: '100%', padding: '6px', background: '#1a1a1a', color: '#fff', border: '1px solid #444', borderRadius: '3px', fontSize: '12px', textAlign: 'center', outline: 'none' }} 
          />
        </div>
        <div style={{ width: '75px' }}>
          <input 
            type="number" 
            min="0" 
            value={manualPrice} 
            onChange={(e) => setManualPrice(e.target.value)} 
            placeholder="Цена" 
            style={{ width: '100%', padding: '6px', background: '#1a1a1a', color: '#fff', border: '1px solid #444', borderRadius: '3px', fontSize: '12px', textAlign: 'right', outline: 'none' }} 
          />
        </div>
        <button 
          type="button" 
          onClick={handleAdd} 
          style={{ background: '#333', color: '#4fa8ff', border: '1px solid #444', padding: '6px 10px', borderRadius: '3px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}
        >
          + Добавить
        </button>
      </div>
    </div>
  );
};
