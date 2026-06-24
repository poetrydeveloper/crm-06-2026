import React, { useState, useEffect } from 'react';

interface PreOrder {
  product_id: number;
  deficit_quantity: number;
  reason: string;
}

export const SupplyReport: React.FC = () => {
  const [preOrders, setPreOrders] = useState<PreOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFallback, setIsFallback] = useState(false);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/warehouse/pre-orders');
      if (!res.ok) throw new Error('Не удалось получить аналитический отчет');
      const result = await res.json();
      
      if (result.status === 'success') {
        setPreOrders(result.data || []);
        setIsFallback(!!result.fallback_active);
      }
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Ошибка получения кэша снабжения');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const handleExclude = async (productId: number) => {
    if (!window.confirm(`Исключить товар #${productId} из будущих расчетов автозаказа?`)) return;
    
    try {
      const res = await fetch('/api/v1/warehouse/pre-orders/exclude', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId }),
      });
      if (!res.ok) throw new Error('Не удалось занести товар в черный список');
      
      // Удаляем товар локально из таблицы интерфейса
      setPreOrders(prev => prev.filter(item => item.product_id !== productId));
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="page-content" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>📊 Живой анализ дефицита сети</h2>
          <p style={{ color: '#666' }}>Автоматический расчет объема необходимых закупок на основе действующих правил.</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchReport} disabled={loading} style={{ padding: '10px 15px', background: '#6c757d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          {loading ? 'Обсчет...' : '🔄 Пересчитать СУБД'}
        </button>
      </div>

      {isFallback && (
        <div style={{ background: '#fff3cd', color: '#856404', padding: '12px', borderRadius: '6px', marginBottom: '15px', border: '1px solid #ffeeba' }}>
          ⚠️ <strong>Внимание:</strong> Кэш анализатора пуст. Показана базовая пустая матрица. Нажмите кнопку «Пересчитать СУБД» для принудительного прогрева ядра.
        </div>
      )}

      {loading ? (
        <div>Интеллектуальный анализ складских юнитов...</div>
      ) : error ? (
        <div style={{ color: 'red', padding: '10px', background: '#fff0f0', borderRadius: '4px' }}>⚠️ Ошибка шлюза аналитики: {error}</div>
      ) : preOrders.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', background: '#f8f9fa', borderRadius: '8px', border: '1px dashed #ccc', marginTop: '20px' }}>
          🎉 <strong>Склад в идеальном состоянии!</strong> Ни по одному правилу дефицит товаров не обнаружен.
        </div>
      ) : (
        <table className="table" style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px', background: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <thead>
            <tr style={{ background: '#343a40', color: '#fff', textAlign: 'left' }}>
              <th style={{ padding: '12px' }}>ID Товара</th>
              <th style={{ padding: '12px' }}>Рекомендуемый объем закупки</th>
              <th style={{ padding: '12px' }}>Автоматическое обоснование</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Действие</th>
            </tr>
          </thead>
          <tbody>
            {preOrders.map((item) => (
              <tr key={item.product_id} style={{ borderBottom: '1px solid #dee2e6' }}>
                <td style={{ padding: '12px', fontWeight: 'bold' }}>Товар #{item.product_id}</td>
                <td style={{ padding: '12px' }}>
                  <span style={{ color: '#28a745', fontWeight: 'bold', fontSize: '1.1em' }}>+ {item.deficit_quantity}</span> шт.
                </td>
                <td style={{ padding: '12px', color: '#555', fontStyle: 'italic' }}>{item.reason}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  <button onClick={() => handleExclude(item.product_id)} style={{ padding: '5px 10px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.9em' }}>
                    🚫 Скрыть навсегда
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
