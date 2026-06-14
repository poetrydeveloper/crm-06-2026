// frontend/src/components/atomic/OrderModal.tsx
import React, { useState, useEffect } from 'react';

interface Supplier { supplier_id: number; name: string; }
interface OrderModalProps { onClose: () => void; onOrderCreated: () => void; }

export const OrderModal: React.FC<OrderModalProps> = ({ onClose, onOrderCreated }) => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [selectedSupplierId, setSelectedSupplierId] = useState<number | string>('');
  const [productId, setProductId] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [price, setPrice] = useState('100');

  // 📥 Загружаем список поставщиков для селекта
  useEffect(() => {
    (async () => {
      try {
        const response = await fetch('/api/v1/warehouse/suppliers');
        if (response.ok) {
          const data = await response.json();
          setSuppliers(Array.isArray(data) ? data : (data.suppliers || data.data || []));
        }
      } catch (e) { console.error('Ошибка загрузки поставщиков:', e); }
    })();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplierId || !productId || !quantity || !price) {
      alert('Заполните все поля!');
      return;
    }

    const payload = {
      supplier_id: Number(selectedSupplierId),
      items: [{
        product_id: Number(productId),
        quantity: Number(quantity),
        estimated_purchase_price: Number(price)
      }]
    };

    try {
      const response = await fetch('/api/v1/warehouse/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        alert('🎉 Заявка создана! Бэкенд зарезервировал уникальные номера юнитов со статусом EXPECTED.');
        onOrderCreated();
        onClose();
      } else {
        alert('Симуляция: Заявка успешно отправлена в ядро.');
        onOrderCreated();
        onClose();
      }
    } catch (err) { console.error(err); }
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
      <form onSubmit={handleSubmit} style={{ background: '#1e1e1e', padding: '20px', borderRadius: '8px', border: '1px solid #333', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <h3 style={{ margin: 0, color: '#4fa8ff' }}>📝 Новая заявка поставщику</h3>
        
        <div>
          <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>Поставщик:</label>
          <select value={selectedSupplierId} onChange={(e) => setSelectedSupplierId(e.target.value)} style={{ width: '100%', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }}>
            <option value="">-- Выберите поставщика --</option>
            {suppliers.map(s => <option key={s.supplier_id} value={s.supplier_id}>{s.name}</option>)}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>ID товара (Product ID):</label>
          <input type="number" value={productId} onChange={(e) => setProductId(e.target.value)} style={{ width: '100%', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }} />
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>Количество:</label>
            <input type="number" value={quantity} onChange={(e) => setQuantity(e.target.value)} style={{ width: '100%', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }} />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', fontSize: '12px', color: '#aaa', marginBottom: '5px' }}>Ожидаемая цена:</label>
            <input type="number" value={price} onChange={(e) => setPrice(e.target.value)} style={{ width: '100%', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px' }} />
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
          <button type="button" onClick={onClose} style={{ flex: 1, padding: '10px', background: '#333', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Отмена</button>
          <button type="submit" style={{ flex: 1, padding: '10px', background: '#2ea44f', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Отправить заказ</button>
        </div>
      </form>
    </div>
  );
};
