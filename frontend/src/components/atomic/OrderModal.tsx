// frontend/src/components/atomic/OrderModal.tsx
import React, { useState, useEffect } from 'react';
import { OrderModalItemsTable } from './OrderModalItemsTable';
import type { PurchaseItem } from './OrderModalItemsTable';

interface Supplier {
  supplier_id: number;
  name: string;
}

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
}

interface OrderModalProps {
  onClose: () => void;
  onOrderCreated: () => void;
}

export const OrderModal: React.FC<OrderModalProps> = ({ onClose, onOrderCreated }) => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [selectedSupplierId, setSelectedSupplierId] = useState<number | string>('');
  const [items, setItems] = useState<PurchaseItem[]>([]);
  const [newSupplierName, setNewSupplierName] = useState('');
  const [showSupplierInput, setShowSupplierInput] = useState(false);
  const [supplierError, setSupplierError] = useState<string | null>(null);

  // Умный поиск товаров
  const [productSearch, setProductSearch] = useState('');
  const [foundProducts, setFoundProducts] = useState<Product[]>([]);
  const [selectedProductIds, setSelectedProductIds] = useState<Set<number>>(new Set());

  const loadSuppliers = async () => {
    try {
      const response = await fetch('/api/v1/warehouse/suppliers');
      if (response.ok) {
        const data = await response.json();
        setSuppliers(Array.isArray(data) ? data : data.suppliers || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadSuppliers();

    try {
      const cartRaw = localStorage.getItem('purchase_cart');
      if (cartRaw) {
        const cartList = JSON.parse(cartRaw);
        if (cartList.length > 0) setItems(cartList);
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  // Умный поиск с дебаунсом
  useEffect(() => {
    if (productSearch.length < 2) {
      setFoundProducts([]);
      return;
    }
    const delay = setTimeout(async () => {
      try {
        const response = await fetch(`/api/v1/catalog/search?q=${encodeURIComponent(productSearch)}`);
        if (response.ok) {
          const data = await response.json();
          setFoundProducts(Array.isArray(data) ? data : []);
        }
      } catch (e) {
        console.error(e);
      }
    }, 300);
    return () => clearTimeout(delay);
  }, [productSearch]);

  const handleCreateSupplier = async () => {
    const name = newSupplierName.trim();
    if (!name) {
      setSupplierError('Введите название');
      return;
    }

    try {
      const response = await fetch('/api/v1/warehouse/suppliers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });

      const data = await response.json();

      if (response.ok) {
        await loadSuppliers();
        setSelectedSupplierId(String(data.supplier_id));
        setNewSupplierName('');
        setShowSupplierInput(false);
        setSupplierError(null);
      } else {
        setSupplierError(data.detail || 'Ошибка при создании');
      }
    } catch (e) {
      console.error(e);
      setSupplierError('Ошибка сети');
    }
  };

  const handleToggleProduct = (productId: number) => {
    setSelectedProductIds((prev) => {
      const next = new Set(prev);
      if (next.has(productId)) {
        next.delete(productId);
      } else {
        next.add(productId);
      }
      return next;
    });
  };

  const handleAddSelectedToOrder = () => {
    const toAdd = foundProducts.filter((p) => selectedProductIds.has(p.id));
    if (toAdd.length === 0) return;

    setItems((prev) => {
      const updated = [...prev];
      for (const product of toAdd) {
        const existingIdx = updated.findIndex((i) => i.product_id === product.id);
        if (existingIdx > -1) {
          updated[existingIdx] = {
            ...updated[existingIdx],
            quantity: updated[existingIdx].quantity + 1,
          };
        } else {
          updated.push({
            product_id: product.id,
            product_name: product.name.replace(/_/g, ' '),
            product_code: product.code,
            quantity: 1,
            estimated_purchase_price: product.recommended_retail_price * 0.6,
          });
        }
      }
      return updated;
    });

    setSelectedProductIds(new Set());
    setProductSearch('');
    setFoundProducts([]);
  };

  const handleItemChange = (index: number, field: keyof PurchaseItem, value: any) => {
    const updated = [...items];
    updated[index] = { ...updated[index], [field]: value };
    setItems(updated);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplierId) {
      alert('Выберите или создайте поставщика');
      return;
    }
    if (items.length === 0) {
      alert('Добавьте хотя бы один товар');
      return;
    }

    try {
      const response = await fetch('/api/v1/warehouse/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          supplier_id: Number(selectedSupplierId),
          items: items.map((i) => ({
            product_id: i.product_id,
            quantity: i.quantity,
            estimated_purchase_price: i.estimated_purchase_price,
          })),
        }),
      });

      if (response.ok) {
        alert('Заявка создана');
        localStorage.removeItem('purchase_cart');
        onOrderCreated();
        onClose();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <form
        onSubmit={handleSubmit}
        className="card"
        style={{ width: '560px', maxWidth: '90vw', maxHeight: '90vh', overflowY: 'auto', zIndex: 1001 }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="card-title">Новая заявка</h3>

        {/* Поставщик */}
        <div className="form-group">
          <label className="form-label">Поставщик</label>
          {!showSupplierInput ? (
            <div className="d-flex gap-8">
              <select
                className="form-control"
                value={selectedSupplierId}
                onChange={(e) => setSelectedSupplierId(e.target.value)}
                style={{ flex: 1 }}
              >
                <option value="">-- Выберите --</option>
                {suppliers.map((s) => (
                  <option key={s.supplier_id} value={s.supplier_id}>{s.name}</option>
                ))}
              </select>
              <button type="button" className="btn btn-outline btn-sm" onClick={() => setShowSupplierInput(true)}>
                +
              </button>
            </div>
          ) : (
            <div>
              <div className="d-flex gap-8 mb-2">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Название нового поставщика"
                  value={newSupplierName}
                  onChange={(e) => setNewSupplierName(e.target.value)}
                  autoFocus
                />
                <button type="button" className="btn btn-success btn-sm" onClick={handleCreateSupplier}>
                  OK
                </button>
                <button type="button" className="btn btn-outline btn-sm" onClick={() => {
                  setShowSupplierInput(false); setNewSupplierName(''); setSupplierError(null);
                }}>
                  ✕
                </button>
              </div>
              {supplierError && (
                <div className="alert alert-danger" style={{ padding: '6px 10px', fontSize: '12px', margin: 0 }}>
                  {supplierError}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Умный поиск товаров */}
        <div className="form-group">
          <label className="form-label">Поиск товаров для заявки</label>
          <div className="d-flex gap-8">
            <input
              type="text"
              className="form-control"
              placeholder="Название или артикул..."
              value={productSearch}
              onChange={(e) => setProductSearch(e.target.value)}
            />
            <button
              type="button"
              className="btn btn-primary btn-sm"
              disabled={selectedProductIds.size === 0}
              onClick={handleAddSelectedToOrder}
            >
              Добавить ({selectedProductIds.size})
            </button>
          </div>

          {foundProducts.length > 0 && (
            <div
              className="mt-2"
              style={{
                maxHeight: '200px',
                overflowY: 'auto',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              {foundProducts.map((product) => (
                <label
                  key={product.id}
                  className="d-flex align-center gap-8"
                  style={{
                    padding: '8px 12px',
                    cursor: 'pointer',
                    borderBottom: '1px solid var(--border)',
                    background: selectedProductIds.has(product.id) ? 'var(--bg-secondary)' : 'var(--bg)',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedProductIds.has(product.id)}
                    onChange={() => handleToggleProduct(product.id)}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 500, textTransform: 'capitalize' }}>
                      {product.name.replace(/_/g, ' ')}
                    </div>
                    <div className="text-muted" style={{ fontSize: '12px' }}>
                      {product.code} — {product.recommended_retail_price.toFixed(2)} ₽
                    </div>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Таблица позиций */}
        <OrderModalItemsTable items={items} onItemChange={handleItemChange} onRemoveItem={handleRemoveItem} />

        <div className="d-flex gap-8 mt-3">
          <button type="button" className="btn btn-outline" onClick={onClose}>Отмена</button>
          <button type="submit" className="btn btn-success">Отправить заказ</button>
        </div>
      </form>
    </div>
  );
};