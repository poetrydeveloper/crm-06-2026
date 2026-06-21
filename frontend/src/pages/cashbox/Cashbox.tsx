// frontend/src/pages/cashbox/Cashbox.tsx
import React, { useState, useEffect } from 'react';
import { CategoryTree } from '../../components/atomic/CategoryTree';
import { CashboxSearch } from '../../components/atomic/CashboxSearch';
import { CashboxStatus } from '../../components/atomic/CashboxStatus';
import { CashboxShowcase } from '../../components/atomic/CashboxShowcase';
import { CashboxCart } from '../../components/atomic/CashboxCart';
import { DisassemblyModal } from '../../components/atomic/DisassemblyModal';

interface Category {
  id: number;
  name: string;
  parent_id: number | null;
}

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
  available_qty: number;
}

interface UnitItem {
  unit_id: number;
  unique_serial_number: string;
  purchase_price: number;
  physical_status: string;
}

interface CategoryProduct {
  product_id: number;
  product_name: string;
  product_code: string;
  recommended_retail_price: number;
  in_stock: number;
  units: UnitItem[];
}

interface CartItem {
  product: Product;
  quantity: number;
  price: number;
}

interface SaleRecord {
  time: string;
  product_name: string;
  price: number;
  serial_number: string;
  event_id: number;
}

export const Cashbox: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [foundProducts, setFoundProducts] = useState<Product[]>([]);
  const [categoryUnits, setCategoryUnits] = useState<CategoryProduct[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [paymentType, setPaymentType] = useState<'cash' | 'card' | 'credit'>('cash');
  const [saleHistory, setSaleHistory] = useState<SaleRecord[]>([]);
  const [cashDayStatus, setCashDayStatus] = useState<'ЗАКРЫТА' | 'ОТКРЫТА'>('ОТКРЫТА');
  const [disassemblyUnit, setDisassemblyUnit] = useState<{ unique_serial_number: string; product_id: number } | null>(null);

  const loadCategories = async () => {
    try {
      const r = await fetch('/api/v1/catalog/categories');
      if (r.ok) setCategories(await r.json());
    } catch {}
  };

  const loadSaleHistory = async () => {
    try {
      const r = await fetch('/api/v1/cash/days/current/sales');
      if (r.ok) setSaleHistory((await r.json()).sales || []);
    } catch {}
  };

  const checkCashDayStatus = async () => {
    try {
      const r = await fetch('/api/v1/cash/days');
      if (r.ok) {
        const d = await r.json();
        if (d.days?.length) setCashDayStatus(d.days[0].status);
      }
    } catch {}
  };

  const loadCategoryUnits = async (categoryId: number) => {
    try {
      const r = await fetch(`/api/v1/warehouse/units/by-category/${categoryId}`);
      if (r.ok) setCategoryUnits(await r.json());
    } catch {}
  };

  useEffect(() => { loadCategories(); loadSaleHistory(); checkCashDayStatus(); }, []);

  // Поиск
  useEffect(() => {
    if (searchQuery.length < 2) { setFoundProducts([]); return; }
    setCategoryUnits([]);
    const t = setTimeout(async () => {
      try {
        const r = await fetch(`/api/v1/catalog/search?q=${encodeURIComponent(searchQuery)}`);
        if (r.ok) setFoundProducts(await r.json());
      } catch {}
    }, 300);
    return () => clearTimeout(t);
  }, [searchQuery]);

  // Юниты категории
  useEffect(() => {
    if (!selectedCategoryId) { setCategoryUnits([]); return; }
    loadCategoryUnits(selectedCategoryId);
  }, [selectedCategoryId]);

  const handleAddToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.product.id === product.id);
      if (existing) return prev.map((i) => i.product.id === product.id ? { ...i, quantity: i.quantity + 1 } : i);
      return [...prev, { product, quantity: 1, price: product.recommended_retail_price }];
    });
  };

  const handleRemoveFromCart = (productId: number) => setCart((p) => p.filter((i) => i.product.id !== productId));
  const handleUpdateQuantity = (productId: number, q: number) => { if (q < 1) return; setCart((p) => p.map((i) => i.product.id === productId ? { ...i, quantity: q } : i)); };
  const handleUpdatePrice = (productId: number, pr: number) => setCart((p) => p.map((i) => i.product.id === productId ? { ...i, price: pr } : i));

  const handleAbsorb = async (unitIds: number[]) => {
    const parentProductId = prompt('Введите ID целевого набора инструментов:');
    if (!parentProductId) return;
    try {
      const r = await fetch('/api/v1/warehouse/sets/absorb', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parent_product_id: parseInt(parentProductId), satellite_unit_ids: unitIds }),
      });
      if (r.ok) {
        alert('Набор успешно собран');
        if (selectedCategoryId) loadCategoryUnits(selectedCategoryId);
      } else {
        const err = await r.json();
        alert(err.detail || 'Ошибка сборки набора');
      }
    } catch (e) { console.error(e); }
  };

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    let ok = true;
    for (const item of cart) {
      try {
        const r = await fetch('/api/v1/cash/sales', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_id: item.product.id,
            sale_price: item.price,
            amount_cash: paymentType === 'cash' ? item.price * item.quantity : 0,
            amount_card: paymentType === 'card' ? item.price * item.quantity : 0,
            amount_credit: paymentType === 'credit' ? item.price * item.quantity : 0,
          }),
        });
        if (!r.ok) ok = false;
      } catch { ok = false; }
    }
    alert(ok ? 'Чек проведён' : 'Часть позиций не проведена');
    setCart([]); setSearchQuery(''); setFoundProducts([]); loadSaleHistory();
  };

  const total = cart.reduce((s, i) => s + i.price * i.quantity, 0);

  return (
    <div className="page-content">
      {/* Поиск + статус */}
      <div className="card mb-3">
        <div className="d-flex justify-between align-center">
          <CashboxSearch value={searchQuery} onChange={setSearchQuery} />
          <CashboxStatus status={cashDayStatus} />
        </div>
      </div>

      {/* Результаты поиска */}
      {searchQuery && foundProducts.length > 0 && (
        <div className="mb-3">
          <CashboxShowcase products={foundProducts} onAddToCart={handleAddToCart} />
        </div>
      )}
      {searchQuery && foundProducts.length === 0 && searchQuery.length >= 2 && (
        <div className="card mb-3" style={{ textAlign: 'center', padding: '20px' }}>
          <p className="text-muted">Ничего не найдено</p>
        </div>
      )}

      {/* Дерево + товары категории | Корзина */}
      <div className="d-flex gap-16" style={{ alignItems: 'flex-start' }}>
        <CategoryTree
          categories={categories}
          selectedCategoryId={selectedCategoryId}
          onSelectCategory={(id) => setSelectedCategoryId(id)}
          onCreateCategory={() => {}}
          readonly={true}
        />

        <div style={{ flex: 1 }}>
          {!searchQuery && selectedCategoryId && (
            <CashboxShowcase
              products={[]}
              categoryUnits={categoryUnits}
              onAddToCart={handleAddToCart}
              onDisassembly={(serial, prodId) => setDisassemblyUnit({ unique_serial_number: serial, product_id: prodId })}
              onAbsorb={handleAbsorb}
            />
          )}
          {!searchQuery && !selectedCategoryId && (
            <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
              <p className="text-muted">Выберите категорию слева или введите запрос в поиск</p>
            </div>
          )}
        </div>

        <CashboxCart
          cart={cart}
          paymentType={paymentType}
          onPaymentTypeChange={setPaymentType}
          onRemoveFromCart={handleRemoveFromCart}
          onUpdateQuantity={handleUpdateQuantity}
          onUpdatePrice={handleUpdatePrice}
          onCheckout={handleCheckout}
          totalAmount={total}
        />
      </div>

      {/* История продаж */}
      {saleHistory.length > 0 && (
        <div className="card mt-3">
          <div className="d-flex justify-between align-center mb-3">
            <h3 className="card-title" style={{ margin: 0 }}>Продажи текущей смены</h3>
            <button className="btn btn-sm btn-outline" onClick={loadSaleHistory}>Обновить</button>
          </div>
          <div className="table-wrapper">
            <table className="table" style={{ fontSize: '13px' }}>
              <thead>
                <tr><th>Время</th><th>Товар</th><th>Серийный номер</th><th style={{ textAlign: 'right' }}>Сумма</th></tr>
              </thead>
              <tbody>
                {saleHistory.map((s, i) => (
                  <tr key={i}>
                    <td className="text-muted">{new Date(s.time).toLocaleTimeString('ru-RU')}</td>
                    <td style={{ textTransform: 'capitalize' }}>{s.product_name.replace(/_/g, ' ')}</td>
                    <td className="text-mono" style={{ fontSize: '12px' }}>{s.serial_number}</td>
                    <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--success)' }}>{s.price.toFixed(2)} ₽</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Модалка разукомплектации */}
      {disassemblyUnit && (
        <DisassemblyModal
          unitSerial={disassemblyUnit.unique_serial_number}
          productId={disassemblyUnit.product_id}
          onClose={() => setDisassemblyUnit(null)}
          onSuccess={() => {
            setDisassemblyUnit(null);
            if (selectedCategoryId) loadCategoryUnits(selectedCategoryId);
          }}
        />
      )}
    </div>
  );
};