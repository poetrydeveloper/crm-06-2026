// frontend/src/components/atomic/CashboxCart.tsx
import React from 'react';

interface PhysicalUnit {
  id: number;
  name: string;
  code: string;
  unique_serial_number: string;
  recommended_retail_price: number;
  physical_status: 'IN_STORE' | 'SOLD' | 'LOST' | 'IN_DISASSEMBLED' | 'ABSORBED';
}

interface CartItem {
  unit: PhysicalUnit;
  quantity: number;
}

interface CashboxCartProps {
  cart: CartItem[];
  paymentType: 'cash' | 'card' | 'credit';
  onPaymentTypeChange: (type: 'cash' | 'card' | 'credit') => void;
  onRemoveFromBag: (serial: string) => void;
  onCheckout: () => void;
}

export const CashboxCart: React.FC<CashboxCartProps> = ({
  cart,
  paymentType,
  onPaymentTypeChange,
  onRemoveFromBag,
  onCheckout,
}) => {
  const totalAmount = cart.reduce((sum, item) => sum + (item.unit.recommended_retail_price * item.quantity), 0);

  return (
    <div style={{ width: '320px', background: '#1a1a1a', borderLeft: '1px solid #333', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '15px', borderBottom: '1px solid #333', background: '#222' }}>
        <h3 style={{ margin: 0, color: '#fff' }}>🛒 Текущий чек</h3>
      </div>

      {/* Список позиций в чеке */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '15px' }}>
        {cart.length === 0 ? (
          <div style={{ padding: '40px 0', textAlign: 'center', color: '#555' }}>Чек пуст. Добавьте товар с витрины.</div>
        ) : (
          cart.map(item => (
            <div key={item.unit.unique_serial_number} style={{ background: '#252525', borderRadius: '4px', padding: '10px', marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ maxWidth: '200px' }}>
                <div style={{ fontSize: '14px', color: '#fff', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{item.unit.name}</div>
                <div style={{ fontSize: '11px', color: '#666' }}>{item.unit.unique_serial_number}</div>
                <div style={{ fontSize: '13px', color: '#2ea44f', fontWeight: 'bold', marginTop: '4px' }}>{item.unit.recommended_retail_price.toFixed(2)} ₽</div>
              </div>
              <button 
                onClick={() => onRemoveFromBag(item.unit.unique_serial_number)}
                style={{ background: 'none', border: 'none', color: '#ff4d4d', fontSize: '16px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>

      {/* Выбор типа оплаты */}
      <div style={{ padding: '15px', borderTop: '1px solid #333', background: '#1e1e1e' }}>
        <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '6px' }}>💰 Способ оплаты:</label>
        <div style={{ display: 'flex', gap: '5px' }}>
          {(['cash', 'card', 'credit'] as const).map((type) => (
            <button
              key={type}
              onClick={() => onPaymentTypeChange(type)}
              style={{
                flex: 1,
                padding: '6px 0',
                borderRadius: '4px',
                border: '1px solid #444',
                background: paymentType === type ? '#4fa8ff' : '#2d2d2d',
                color: paymentType === type ? '#000' : '#fff',
                fontWeight: 'bold',
                fontSize: '12px',
                cursor: 'pointer',
              }}
            >
              {type === 'cash' ? 'Наличные' : type === 'card' ? 'Карта' : 'Кредит'}
            </button>
          ))}
        </div>
      </div>

      {/* Итоги чека и кнопка оплаты */}
      <div style={{ padding: '15px', borderTop: '1px solid #333', background: '#222', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: '#aaa' }}>Итого к оплате:</span>
          <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#2ea44f' }}>{totalAmount.toFixed(2)} ₽</span>
        </div>
        <button 
          disabled={cart.length === 0}
          onClick={onCheckout}
          style={{ 
            width: '100%', 
            background: cart.length === 0 ? '#444' : '#2ea44f', 
            color: cart.length === 0 ? '#888' : '#fff', 
            border: 'none', 
            padding: '12px', 
            borderRadius: '4px', 
            fontWeight: 'bold', 
            fontSize: '15px', 
            cursor: cart.length === 0 ? 'not-allowed' : 'pointer' 
          }}
        >
          Оформить продажу
        </button>
      </div>

    </div>
  );
};
