// frontend/src/pages/cashbox/Cashbox.tsx
import React, { useState, useEffect } from 'react';
import { CategoryTree } from '../../components/atomic/CategoryTree';
import { CashboxSearch } from '../../components/atomic/CashboxSearch';
import { CashboxStatus } from '../../components/atomic/CashboxStatus';
import { CashboxShowcase } from '../../components/atomic/CashboxShowcase';
import { CashboxCart } from '../../components/atomic/CashboxCart';
import { DisassemblyModal } from '../../components/atomic/DisassemblyModal';
import { ReturnModal } from '../../components/atomic/ReturnModal';

// 🔥 ИСПРАВЛЕНО: Чистый импорт нашего отдельного компонента кнопки Excel
import { CashboxExcelExport } from '../../components/atomic/CashboxExcelExport';

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
  category_id?: number;
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
  type: string;
  description?: string;
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
  const [disassemblyUnit, setDisassemblyUnit] = useState<{
    unique_serial_number: string;
    product_id: number;
  } | null>(null);
  const [showReturnModal, setShowReturnModal] = useState(false);

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
  const loadCategoryUnits = async (id: number) => {
    try {
      const r = await fetch(`/api/v1/warehouse/units/by-category/${id}`);
      if (r.ok) setCategoryUnits(await r.json());
    } catch {}
  };

  useEffect(() => {
    loadCategories();
    loadSaleHistory();
    checkCashDayStatus();
  }, []);
  useEffect(() => {
    if (searchQuery.length < 2) {
      setFoundProducts([]);
      return;
    }
    setCategoryUnits([]);
    const t = setTimeout(async () => {
      try {
        const r = await fetch(`/api/v1/catalog/search?q=${encodeURIComponent(searchQuery)}`);
        if (r.ok) setFoundProducts(await r.json());
      } catch {}
    }, 300);
    return () => clearTimeout(t);
  }, [searchQuery]);

  useEffect(() => {
    if (!selectedCategoryId) {
      setCategoryUnits([]);
      return;
    }
    loadCategoryUnits(selectedCategoryId);
  }, [selectedCategoryId]);

  const handleAddToCart = (product: Product) =>
    setCart((p) => {
      const ex = p.find((i) => i.product.id === product.id);
      return ex
        ? p.map((i) => (i.product.id === product.id ? { ...i, quantity: i.quantity + 1 } : i))
        : [...p, { product, quantity: 1, price: product.recommended_retail_price }];
    });

  const handleRemove = (id: number) => setCart((p) => p.filter((i) => i.product.id !== id));

  const handleQty = (id: number, q: number) => {
    if (q < 1) return;
    setCart((p) => p.map((i) => (i.product.id === id ? { ...i, quantity: q } : i)));
  };

  const handlePrice = (id: number, pr: number) =>
    setCart((p) => p.map((i) => (i.product.id === id ? { ...i, price: pr } : i)));

  const handleAbsorb = async (unitIds: number[]) => {
    const parentId = prompt('ID целевого набора:');
    if (!parentId) return;
    try {
      const r = await fetch('/api/v1/warehouse/sets/absorb', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_product_id: parseInt(parentId),
          satellite_unit_ids: unitIds,
        }),
      });
      if (r.ok) {
        alert('Набор собран');
        if (selectedCategoryId) loadCategoryUnits(selectedCategoryId);
      }
    } catch {}
  };

  const handleCheckout = async () => {
    if (!cart.length) return;
    let ok = true;
    for (const item of cart) {
      try {
        const r = await fetch('/api/v1/cash/sales', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_id: item.product.id,
            sale_price: item.price,
            amount_cash: paymentType === 'cash' ? item.price * item.quantity : 0,
            amount_card: paymentType === 'card' ? item.price * item.quantity : 0,
            amount_credit: paymentType === 'credit' ? item.price * item.quantity : 0,
          }),
        });
        if (!r.ok) ok = false;
      } catch {
        ok = false;
      }
    }
    alert(ok ? 'Чек проведён' : 'Часть позиций не проведена');
    setCart([]);
    setSearchQuery('');
    setFoundProducts([]);
    loadSaleHistory();
  };

  const total = cart.reduce((s, i) => s + i.price * i.quantity, 0);

  return (
    <div className="page-content">
      <div className="card mb-3">
        <div className="d-flex justify-between align-center">
          <CashboxSearch value={searchQuery} onChange={setSearchQuery} />
          <CashboxStatus status={cashDayStatus} />
        </div>
      </div>

      {searchQuery && foundProducts.length > 0 && (
        <div className="mb-3">
          <CashboxShowcase
            products={foundProducts}
            onAddToCart={handleAddToCart}
            onSelectCategory={(categoryId) => {
              setSearchQuery('');
              setSelectedCategoryId(categoryId);
            }}
          />
        </div>
      )}
      {searchQuery && foundProducts.length === 0 && searchQuery.length >= 2 && (
        <div className="card mb-3" style={{ textAlign: 'center', padding: '20px' }}>
          <p className="text-muted">Ничего не найдено</p>
        </div>
      )}

      <div className="d-flex gap-16" style={{ alignItems: 'flex-start' }}>
        <CategoryTree
          categories={categories}
          selectedCategoryId={selectedCategoryId}
          onSelectCategory={(id) => setSelectedCategoryId(id)}
          onCreateCategory={() => {}}
          readonly
        />
        <div style={{ flex: 1 }}>
          {!searchQuery && selectedCategoryId && (
            <CashboxShowcase
              products={[]}
              categoryUnits={categoryUnits}
              onAddToCart={handleAddToCart}
              onSelectCategory={(categoryId) => setSelectedCategoryId(categoryId)}
              onDisassembly={(serial, prodId) =>
                setDisassemblyUnit({ unique_serial_number: serial, product_id: prodId })
              }
              onAbsorb={handleAbsorb}
            />
          )}
          {!searchQuery && !selectedCategoryId && (
            <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
              <p className="text-muted">Выберите категорию или введите запрос</p>
            </div>
          )}
        </div>
        <CashboxCart
          cart={cart}
          paymentType={paymentType}
          onPaymentTypeChange={setPaymentType}
          onRemoveFromCart={handleRemove}
          onUpdateQuantity={handleQty}
          onUpdatePrice={handlePrice}
          onCheckout={handleCheckout}
          totalAmount={total}
        />
      </div>

      {saleHistory.length > 0 && (
        <div className="card mt-3">
          <div className="d-flex justify-between align-center mb-3">
            <h3 className="card-title" style={{ margin: 0 }}>
              Продажи текущей смены
            </h3>
            <div className="d-flex gap-8">
              {/* 🔥 Чистый вызов компонента изолированной кнопки Excel */}
              <CashboxExcelExport />

              <button className="btn btn-sm btn-outline" onClick={loadSaleHistory}>
                Обновить
              </button>
              <button className="btn btn-sm btn-warning" onClick={() => setShowReturnModal(true)}>
                Возврат / Изменение
              </button>
            </div>
          </div>
          <div className="table-wrapper">
            <table
              className="table"
              style={{ fontSize: '13px', width: '100%', borderCollapse: 'collapse' }}
            >
              <thead>
                <tr style={{ background: '#f8f9fa', textAlign: 'left' }}>
                  <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Время</th>
                  <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Тип</th>
                  <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Товар</th>
                  <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>
                    Серийный номер
                  </th>
                  <th
                    style={{
                      padding: '8px',
                      borderBottom: '1px solid #dee2e6',
                      textAlign: 'right',
                    }}
                  >
                    Сумма
                  </th>
                </tr>
              </thead>
              <tbody>
                {saleHistory.map((sale) => (
                  <tr
                    key={sale.event_id}
                    style={{
                      borderBottom: '1px solid #dee2e6',
                      background: sale.type === 'RETURN' ? '#fdf2f2' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '8px' }}>
                      {new Date(sale.time).toLocaleTimeString('ru-RU')}
                    </td>
                    <td
                      style={{
                        padding: '8px',
                        fontWeight: 'bold',
                        color: sale.type === 'RETURN' ? '#dc3545' : '#28a745',
                      }}
                    >
                      {sale.type === 'RETURN' ? 'ВОЗВРАТ' : 'ПРОДАЖА'}
                    </td>
                    <td style={{ padding: '8px' }}>{sale.product_name}</td>
                    <td style={{ padding: '8px', fontFamily: 'monospace' }}>
                      {sale.serial_number}
                    </td>
                    <td style={{ padding: '8px', textAlign: 'right', fontWeight: 'bold' }}>
                      {sale.type === 'RETURN' ? '-' : ''}
                      {sale.price} ₽
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 🔥 ИСПРАВЛЕНО: Передаем точные пропсы, которые ожидает DisassemblyModal */}
      {disassemblyUnit && (
        <DisassemblyModal
          unitSerial={disassemblyUnit.unique_serial_number}
          productId={disassemblyUnit.product_id}
          onClose={() => setDisassemblyUnit(null)}
          onSuccess={() => {
            if (selectedCategoryId) loadCategoryUnits(selectedCategoryId);
          }}
        />
      )}
      {showReturnModal && (
        <ReturnModal onClose={() => setShowReturnModal(false)} onSuccess={loadSaleHistory} />
      )}
    </div>
  );
};
