// frontend/src/components/atomic/OrderQuickManualAdd.tsx
import React, { useState } from 'react';

interface OrderQuickManualAddProps {
  onAddItem: (productId: number, quantity: number, price: number) => void;
}

export const OrderQuickManualAdd: React.FC<OrderQuickManualAddProps> = ({ onAddItem }) => {
  const [productId, setProductId] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [price, setPrice] = useState('100');

  const handleAdd = () => {
    if (!productId || !quantity || !price) return;
    const parsedPrice = parseFloat(price.replace(',', '.'));
    onAddItem(parseInt(productId), parseInt(quantity) || 1, isNaN(parsedPrice) ? 0 : parsedPrice);
    setProductId('');
    setQuantity('1');
    setPrice('100');
  };

  return (
    <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
      <div className="text-muted" style={{ fontSize: '11px', fontWeight: 600, marginBottom: '6px' }}>Быстрое добавление:</div>
      <div className="d-flex gap-8">
        <input
          type="number"
          className="form-control"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          placeholder="ID товара"
          style={{ flex: 1 }}
        />
        <input
          type="number"
          min="1"
          className="form-control"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="Кол-во"
          style={{ width: '70px' }}
        />
        <input
          type="text"
          inputMode="decimal"
          className="form-control"
          value={price}
          onFocus={(e) => e.target.select()}
          onChange={(e) => {
            const raw = e.target.value.replace(',', '.');
            setPrice(raw);
          }}
          placeholder="Цена"
          style={{ width: '80px', textAlign: 'right' }}
        />
        <button type="button" className="btn btn-primary btn-sm" onClick={handleAdd}>
          +
        </button>
      </div>
    </div>
  );
};