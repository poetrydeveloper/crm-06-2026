// frontend/src/pages/warehouse/SupplyReport.tsx
import React, { useState, useEffect } from 'react';

interface PreOrder {
  product_id: number;
  deficit_quantity: number;
  reason: string;
}

// Интерфейс для локального словаря продуктов
interface ProductCatalogItem {
  id: number;
  name: string;
  code: string;
}

export const SupplyReport: React.FC = () => {
  const [preOrders, setPreOrders] = useState<PreOrder[]>([]);
  const [productsMap, setProductsMap] = useState<Record<number, { name: string; code: string }>>(
    {},
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFallback, setIsFallback] = useState(false);

  // Функция загрузки аналитического отчета и каталога товаров
  const fetchReport = async () => {
    try {
      setLoading(true);

      // Параллельно запрашиваем отчет о дефиците и справочник номенклатуры
      const [reportRes, catalogRes] = await Promise.all([
        fetch('/api/v1/warehouse/pre-orders'),
        fetch('/api/v1/catalog/products/all'),
      ]);

      if (!reportRes.ok) throw new Error('Не удалось получить аналитический отчет');

      // Если каталог успешно загрузился, строим карту для мгновенного поиска по ID
      if (catalogRes.ok) {
        const catalogData: ProductCatalogItem[] = await catalogRes.json();
        const catalogMap: Record<number, { name: string; code: string }> = {};
        catalogData.forEach((p) => {
          catalogMap[p.id] = { name: p.name, code: p.code };
        });
        setProductsMap(catalogMap);
      }

      const result = await reportRes.json();
      if (result.status === 'success') {
        setPreOrders(result.data || []);
        setIsFallback(!!result.fallback_active);
      }
      setError(null);
    } catch (err: unknown) {
      // 🔥 ИСПРАВЛЕНО: Безопасное приведение типов вместо any
      const errorMessage = err instanceof Error ? err.message : 'Ошибка получения кэша снабжения';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // 🔥 ИСПРАВЛЕНО: Чистый вызов эффекта без предупреждений линтера
  useEffect(() => {
    fetchReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Функция исключения товара (кнопка Скрыть навсегда)
  const handleExclude = async (productId: number) => {
    const productInfo = productsMap[productId];
    const displayName = productInfo
      ? `"${productInfo.name}" [арт. ${productInfo.code}]`
      : `Товар #${productId}`;

    if (!window.confirm(`Исключить ${displayName} из будущих расчетов автозаказа?`)) return;

    try {
      const res = await fetch('/api/v1/warehouse/pre-orders/exclude', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId }),
      });
      if (!res.ok) throw new Error('Не удалось занести товар в черный список');

      // Удаляем товар локально из таблицы интерфейса
      setPreOrders((prev) => prev.filter((item) => item.product_id !== productId));
    } catch (err: unknown) {
      // 🔥 ИСПРАВЛЕНО: Заменен any на строгую обработку ошибок TypeScript
      const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка';
      alert(errorMessage);
    }
  };

  // Вспомогательная функция для парсинга остатка из строки обоснования бэкенда
  const parseInStock = (reasonText: string): string => {
    // Ищем число, которое идет после "На полке: "
    const match = reasonText.match(/На полке:\s*(\d+)/);
    return match ? `${match[1]} шт.` : reasonText;
  };

  return (
    <div className="page-content" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>📊 Живой анализ дефицита сети</h2>
          <p style={{ color: '#666' }}>
            Автоматический расчет объема необходимых закупок на основе действующих правил.
          </p>
        </div>
        <button
          className="btn btn-secondary"
          onClick={fetchReport}
          disabled={loading}
          style={{
            padding: '10px 15px',
            background: '#6c757d',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          {loading ? 'Обсчет...' : '🔄 Пересчитать СУБД'}
        </button>
      </div>

      {isFallback && (
        <div
          style={{
            background: '#fff3cd',
            color: '#856404',
            padding: '12px',
            borderRadius: '6px',
            marginBottom: '15px',
            border: '1px solid #ffeeba',
          }}
        >
          ⚠️ <strong>Внимание:</strong> Кэш анализатора пуст. Показана базовая пустая матрица.
          Нажмите кнопку «Пересчитать СУБД» для принудительного прогрева ядра.
        </div>
      )}

      {loading ? (
        <div>Интеллектуальный анализ складских юнитов...</div>
      ) : error ? (
        <div style={{ color: 'red', padding: '10px', background: '#fff0f0', borderRadius: '4px' }}>
          ⚠️ Ошибка шлюза аналитики: {error}
        </div>
      ) : preOrders.length === 0 ? (
        <div
          style={{
            padding: '30px',
            textAlign: 'center',
            background: '#f8f9fa',
            borderRadius: '8px',
            border: '1px dashed #ccc',
            marginTop: '20px',
          }}
        >
          🎉 <strong>Склад в идеальном состоянии!</strong> Ни по одному правилу дефицит товаров не
          обнаружен.
        </div>
      ) : (
        <table
          className="table"
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            marginTop: '20px',
            background: '#fff',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          }}
        >
          <thead>
            <tr style={{ background: '#343a40', color: '#fff', textAlign: 'left' }}>
              <th style={{ padding: '12px' }}>Наименование товара</th>
              <th style={{ padding: '12px' }}>Рекомендуемый объем закупки</th>
              {/* 🔥 ИСПРАВЛЕНО: Изменено название колонки на Остаток */}
              <th style={{ padding: '12px' }}>Остаток</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Действие</th>
            </tr>
          </thead>
          <tbody>
            {preOrders.map((item) => {
              const productInfo = productsMap[item.product_id];
              return (
                <tr key={item.product_id} style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: '12px' }}>
                    {productInfo ? (
                      <div>
                        <div style={{ fontWeight: 'bold', color: '#212529' }}>
                          {productInfo.name.replace(/_/g, ' ')}
                        </div>
                        <div
                          style={{
                            fontSize: '0.85em',
                            color: '#6c757d',
                            marginTop: '4px',
                            fontFamily: 'monospace',
                          }}
                        >
                          Арт: {productInfo.code}
                        </div>
                      </div>
                    ) : (
                      <span style={{ fontWeight: 'bold', color: '#dc3545' }}>
                        Товар #{item.product_id}
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ color: '#28a745', fontWeight: 'bold', fontSize: '1.1em' }}>
                      + {item.deficit_quantity}
                    </span>{' '}
                    шт.
                  </td>
                  {/* 🔥 ИСПРАВЛЕНО: Теперь выводим только чистый остаток цифрой */}
                  <td style={{ padding: '12px', color: '#212529', fontWeight: '500' }}>
                    {parseInStock(item.reason)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    <button
                      onClick={() => handleExclude(item.product_id)}
                      style={{
                        padding: '5px 10px',
                        background: '#dc3545',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.9em',
                      }}
                    >
                      🚫 Скрыть навсегда
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
};
