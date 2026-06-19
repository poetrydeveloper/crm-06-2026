// frontend/src/components/atomic/CashboxCart.tsx
import React from 'react';

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
}

interface CartItem {
  product: Product;
  quantity: number;
  price: number;
}

interface CashboxCartProps {
  cart: CartItem[];
  paymentType: 'cash' | 'card' | 'credit';
  onPaymentTypeChange: (type: 'cash' | 'card' | 'credit') => void;
  onRemoveFromCart: (productId: number) => void;
  onUpdateQuantity: (productId: number, quantity: number) => void;
  onUpdatePrice: (productId: number, price: number) => void;
  onCheckout: () => void;
  totalAmount: number;
}

export const CashboxCart: React.FC<CashboxCartProps> = ({
  cart,
  paymentType,
  onPaymentTypeChange,
  onRemoveFromCart,
  onUpdateQuantity,
  onUpdatePrice,
  onCheckout,
  totalAmount,
}) => {
  return (
    <div className="card" style={{ width: '360px', flexShrink: 0 }}>
      <div className="card-header">
        <h3 className="card-title">Текущий чек</h3>
      </div>

      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {cart.length === 0 ? (
          <p className="text-muted text-center" style={{ padding: '40px 0', margin: 0 }}>
            Чек пуст
          </p>
        ) : (
          cart.map((item) => (
            <div
              key={item.product.id}
              style={{
                padding: '12px',
                borderBottom: '1px solid var(--border)',
              }}
            >
              <div style={{ fontWeight: 600, marginBottom: '8px', textTransform: 'capitalize', fontSize: '14px' }}>
                {item.product.name.replace(/_/g, ' ')}
              </div>
              <div className="d-flex gap-8 align-center mb-2">
                <label className="text-muted" style={{ fontSize: '11px', whiteSpace: 'nowrap' }}>Кол-во:</label>
                <input
                  type="number"
                  min="1"
                  className="form-control"
                  value={item.quantity}
                  onChange={(e) => onUpdateQuantity(item.product.id, parseInt(e.target.value) || 1)}
                  style={{ width: '60px', padding: '4px', textAlign: 'center', fontSize: '13px' }}
                />
                <label className="text-muted" style={{ fontSize: '11px', whiteSpace: 'nowrap', marginLeft: '8px' }}>Цена:</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  className="form-control"
                  value={item.price}
                  onChange={(e) => onUpdatePrice(item.product.id, parseFloat(e.target.value) || 0)}
                  style={{ width: '90px', padding: '4px', textAlign: 'right', fontSize: '13px' }}
                />
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => onRemoveFromCart(item.product.id)}
                  style={{ border: 'none', color: 'var(--danger)', padding: '2px 6px', marginLeft: 'auto' }}
                >
                  ✕
                </button>
              </div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--success)' }}>
                { (item.price * item.quantity).toFixed(2)} ₽
              </div>
            </div>
          ))
        )}
      </div>

      <div style={{ borderTop: '1px solid var(--border)', padding: '16px 0' }}>
        <div className="form-label">Способ оплаты:</div>
        <div className="d-flex gap-8">
          {(['cash', 'card', 'credit'] as const).map((type) => (
            <button
              key={type}
              className={`btn btn-sm ${paymentType === type ? 'btn-primary' : 'btn-outline'}`}
              style={{ flex: 1 }}
              onClick={() => onPaymentTypeChange(type)}
            >
              {type === 'cash' ? 'Нал' : type === 'card' ? 'Карта' : 'Долг'}
            </button>
          ))}
        </div>
      </div>

      <div style={{ borderTop: '1px solid var(--border)', padding: '16px 0' }}>
        <div className="d-flex justify-between align-center mb-3">
          <span style={{ fontSize: '16px', fontWeight: 600 }}>Итого:</span>
          <span style={{ fontSize: '20px', fontWeight: 700, color: 'var(--success)' }}>
            {totalAmount.toFixed(2)} ₽
          </span>
        </div>
        <button
          className="btn btn-success btn-lg"
          style={{ width: '100%' }}
          disabled={cart.length === 0}
          onClick={onCheckout}
        >
          Оформить продажу
        </button>
      </div>
    </div>
  );
};