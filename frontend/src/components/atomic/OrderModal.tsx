// frontend/src/components/atomic/OrderModal.tsx
import React, { useState, useEffect } from 'react';
import { OrderModalItemsTable } from './OrderModalItemsTable';
import type { PurchaseItem } from './OrderModalItemsTable';
import { OrderQuickManualAdd } from './OrderQuickManualAdd';

interface Supplier { supplier_id: number; name: string; }
interface OrderModalProps { onClose: () => void; onOrderCreated: () => void; }

export const OrderModal: React.FC<OrderModalProps> = ({ onClose, onOrderCreated }) => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [selectedSupplierId, setSelectedSupplierId] = useState<number | string>('');
  const [items, setItems] = useState<PurchaseItem[]>([]);

  // 📥 1. Автоподхват накопительной корзины и загрузка контрагентов
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

    try {
      const cartRaw = localStorage.getItem('purchase_cart');
      if (cartRaw) {
        const cartList = JSON.parse(cartRaw);
        if (cartList.length > 0) {
          setItems(cartList.map((c: any) => ({
            product_id: c.product_id, product_name: c.product_name, product_code: c.product_code,
            quantity: c.quantity, estimated_purchase_price: c.estimated_purchase_price
          })));
        }
      }
    } catch (e) { console.error(e); }
  }, []);

  // ➕ 2. Коллбэк добавления ручной позиции из атомного компонента ввода
  const handleAddManualItem = (productId: number, quantity: number, price: number) => {
    const existingIdx = items.findIndex(i => i.product_id === productId);
    if (existingIdx > -1) {
      const updated = [...items];
      updated[existingIdx].quantity += quantity;
      setItems(updated);
    } else {
      setItems([...items, { product_id: productId, quantity, estimated_purchase_price: price }]);
    }
  };

  const handleItemChange = (index: number, field: keyof PurchaseItem, value: any) => {
    const updated = [...items];
    updated[index] = { ...updated[index], [field]: value };
    setItems(updated);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  // 🚀 3. Отправка комплексного заказа
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplierId) { alert('Выберите поставщика!'); return; }
    if (items.length === 0) { alert('Добавьте хотя бы один товар!'); return; }

    try {
      const response = await fetch('/api/v1/warehouse/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplier_id: Number(selectedSupplierId),
          items: items.map(i => ({ product_id: i.product_id, quantity: i.quantity, estimated_purchase_price: i.estimated_purchase_price }))
        })
      });

      if (response.ok) {
        alert('🎉 Комплексная заявка успешно создана!');
        localStorage.removeItem('purchase_cart'); // Стираем буфер за собой
        onOrderCreated();
        onClose();
      }
    } catch (err) { console.error(err); }
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
      <form onSubmit={handleSubmit} style={{ background: '#1e1e1e', padding: '20px', borderRadius: '8px', border: '1px solid #333', width: '100%', maxWidth: '440px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <h3 style={{ margin: 0, color: '#4fa8ff' }}>📝 Формирование комплексной заявки</h3>
        
        <div>
          <label style={{ display: 'block', fontSize: '11px', color: '#aaa', marginBottom: '4px' }}>Контрагент-Поставщик:</label>
          <select required value={selectedSupplierId} onChange={(e) => setSelectedSupplierId(e.target.value)} style={{ width: '100%', padding: '8px', background: '#2d2d2d', color: '#fff', border: '1px solid #444', borderRadius: '4px', outline: 'none' }}>
            <option value="">-- Выберите поставщика из списка --</option>
            {suppliers.map(s => <option key={s.supplier_id} value={s.supplier_id}>{s.name}</option>)}
          </select>
        </div>

        {/* Таблица спецификаций */}
        <OrderModalItemsTable items={items} onItemChange={handleItemChange} onRemoveItem={handleRemoveItem} />

        {/* Атомарный блок быстрого ручного ввода */}
        <OrderQuickManualAdd onAddItem={handleAddManualItem} />

        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
          <button type="button" onClick={onClose} style={{ flex: 1, padding: '10px', background: '#333', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '14px' }}>Отмена</button>
          <button type="submit" style={{ flex: 1, padding: '10px', background: '#2ea44f', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px' }}>Отправить заказ</button>
        </div>
      </form>
    </div>
  );
};
