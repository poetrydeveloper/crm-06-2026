// frontend/src/pages/cashbox/Cashbox.tsx
import React, { useState, useEffect } from 'react';
import { CashboxSearch } from '../../components/atomic/CashboxSearch';
import { CashboxStatus } from '../../components/atomic/CashboxStatus';
import { CashboxShowcase } from '../../components/atomic/CashboxShowcase';
import { CashboxCart } from '../../components/atomic/CashboxCart';

interface Product {
  id: number;
  name: string;
  code: string;
  recommended_retail_price: number;
  available_qty: number;
}

interface CartItem {
  product: Product;
  quantity: number;
  price: number;
}

export const Cashbox: React.FC = () => {
  const [serialSearchQuery, setSerialSearchQuery] = useState('');
  const [cashDayStatus] = useState<'ЗАКРЫТА' | 'ОТКРЫТА'>('ОТКРЫТА');
  const [foundProducts, setFoundProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [paymentType, setPaymentType] = useState<'cash' | 'card' | 'credit'>('cash');
  const [saleHistory, setSaleHistory] = useState<Array<{ name: string; price: number; time: string }>>([]);

  // Умный поиск товаров
  useEffect(() => {
    if (serialSearchQuery.length < 2) {
      setFoundProducts([]);
      return;
    }
    const delay = setTimeout(async () => {
      try {
        const response = await fetch(`/api/v1/catalog/search?q=${encodeURIComponent(serialSearchQuery)}`);
        if (response.ok) {
          const data = await response.json();
          setFoundProducts(Array.isArray(data) ? data : []);
        }
      } catch (e) {
        console.error('Ошибка поиска:', e);
      }
    }, 300);
    return () => clearTimeout(delay);
  }, [serialSearchQuery]);

  const handleAddToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.product.id === product.id);
      if (existing) {
        return prev.map((i) =>
          i.product.id === product.id ? { ...i, quantity: i.quantity + 1 } : i
        );
      }
      return [...prev, { product, quantity: 1, price: product.recommended_retail_price }];
    });
  };

  const handleRemoveFromCart = (productId: number) => {
    setCart((prev) => prev.filter((i) => i.product.id !== productId));
  };

  const handleUpdateQuantity = (productId: number, quantity: number) => {
    if (quantity < 1) return;
    setCart((prev) =>
      prev.map((i) => (i.product.id === productId ? { ...i, quantity } : i))
    );
  };

  const handleUpdatePrice = (productId: number, price: number) => {
    setCart((prev) =>
      prev.map((i) => (i.product.id === productId ? { ...i, price } : i))
    );
  };

  const handleCheckout = async () => {
    if (cart.length === 0) return;

    const totalAmount = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const amountCash = paymentType === 'cash' ? totalAmount : 0;
    const amountCard = paymentType === 'card' ? totalAmount : 0;
    const amountCredit = paymentType === 'credit' ? totalAmount : 0;

    // Продаём каждый товар отдельным запросом
    let allSuccess = true;
    for (const item of cart) {
      try {
        const response = await fetch('/api/v1/cash/sales', {
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

        if (response.ok) {
          setSaleHistory((prev) => [
            ...prev,
            {
              name: item.product.name.replace(/_/g, ' '),
              price: item.price * item.quantity,
              time: new Date().toLocaleTimeString('ru-RU'),
            },
          ]);
        } else {
          const err = await response.json();
          console.error('Ошибка продажи:', err);
          allSuccess = false;
        }
      } catch (e) {
        console.error('Сетевая ошибка:', e);
        allSuccess = false;
      }
    }

    if (allSuccess) {
      alert('Чек успешно проведён');
    } else {
      alert('Некоторые позиции не удалось провести. Проверьте остатки.');
    }

    setCart([]);
    setSerialSearchQuery('');
    setFoundProducts([]);
  };

  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return (
    <div className="page-content">
      <div className="card mb-3">
        <div className="d-flex justify-between align-center">
          <CashboxSearch value={serialSearchQuery} onChange={setSerialSearchQuery} />
          <CashboxStatus status={cashDayStatus} />
        </div>
      </div>

      <div className="d-flex gap-16" style={{ alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <CashboxShowcase products={foundProducts} onAddToCart={handleAddToCart} />

          {/* История продаж текущей смены */}
          {saleHistory.length > 0 && (
            <div className="card mt-3">
              <h3 className="card-title">Продажи текущей смены</h3>
              <div className="table-wrapper">
                <table className="table" style={{ fontSize: '13px' }}>
                  <thead>
                    <tr>
                      <th>Время</th>
                      <th>Товар</th>
                      <th style={{ textAlign: 'right' }}>Сумма</th>
                    </tr>
                  </thead>
                  <tbody>
                    {saleHistory.map((sale, idx) => (
                      <tr key={idx}>
                        <td className="text-muted">{sale.time}</td>
                        <td style={{ textTransform: 'capitalize' }}>{sale.name}</td>
                        <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--success)' }}>
                          {sale.price.toFixed(2)} ₽
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
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
          totalAmount={totalAmount}
        />
      </div>
    </div>
  );
};