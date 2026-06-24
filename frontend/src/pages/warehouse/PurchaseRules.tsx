import React, { useState, useEffect } from 'react';

interface PurchaseRule {
  id: number;
  price_operator: string;
  price_value: number;
  name_contains: string | null;
  stock_threshold: number;
}

export const PurchaseRules: React.FC = () => {
  const [rules, setRules] = useState<PurchaseRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Состояние формы
  const [priceOperator, setPriceOperator] = useState('ge');
  const [priceValue, setPriceValue] = useState('500');
  const [nameContains, setNameContains] = useState('');
  const [stockThreshold, setStockThreshold] = useState('2');
  const [submitLoading, setSubmitLoading] = useState(false);

  const fetchRules = async () => {
    try {
      setLoading(true);
      // 🔥 ИСПРАВЛЕНО: Добавлен обязательный префикс /warehouse
      const res = await fetch('/api/v1/warehouse/purchase-rules');
      if (!res.ok) throw new Error('Не удалось загрузить правила');
      const data = await res.json();
      setRules(Array.isArray(data) ? data : data.rules || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Ошибка сети');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitLoading(true);
    try {
      const res = await fetch('/api/v1/warehouse/purchase-rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price_operator: priceOperator, // отправляет 'ge' или 'le'
          price_value: Number(priceValue) || 0, // 🔥 Гарантирует float для бэкенда
          // 🔥 Строгая проверка: если инпут пустой, отправляем строго null, а не пустую строку ""
          name_contains: nameContains.trim() === '' ? null : nameContains.trim(), 
          stock_threshold: Number(stockThreshold) || 0, // 🔥 Гарантирует чистый int
        }),
      });

      // Если бэкенд выплюнул ошибку (например, ту самую 422), 
      // мы распарсим ответ сервера и покажем точную причину в alert
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        const detail = errData.detail ? JSON.stringify(errData.detail) : 'Ошибка сервера';
        throw new Error(`Ошибка сохранения правила: ${detail}`);
      }
      
      // Сброс формы и обновление списка
      setNameContains('');
      await fetchRules(); // Перезапрашивает обновленный список из базы
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <div className="page-content" style={{ padding: '20px' }}>
      <h2>⚙️ Матрица управления автоснабжением</h2>
      <p style={{ color: '#666' }}>Задайте условия, по которым система будет находить дефицит товаров и формировать закупки.</p>

      {/* Форма создания правила */}
      <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '3px', border: '1px solid #dee2e6' }}>
        <h4>🌱 Добавить новое правило снабжения</h4>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', alignItems: 'flex-end', marginTop: '15px' }}>
          <div style={{ flex: '1', minWidth: '150px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Оператор цены</label>
            <select className="form-control" value={priceOperator} onChange={(e) => setPriceOperator(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}>
              <option value="ge">Больше или равно (&gt;=)</option>
              <option value="le">Меньше или равно (&lt;=)</option>
            </select>
          </div>

          <div style={{ flex: '1', minWidth: '120px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Цена товара (₽)</label>
            <input type="number" className="form-control" value={priceValue} onChange={(e) => setPriceValue(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }} />
          </div>

          <div style={{ flex: '2', minWidth: '200px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Название содержит (необязательно)</label>
            <input type="text" className="form-control" placeholder="Например: iphone, кабель, бита" value={nameContains} onChange={(e) => setNameContains(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }} />
          </div>

          <div style={{ flex: '1', minWidth: '120px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Порог на полке (шт)</label>
            <input type="number" className="form-control" value={stockThreshold} onChange={(e) => setStockThreshold(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }} />
          </div>

          <button type="submit" className="btn btn-primary" disabled={submitLoading} style={{ padding: '9px 20px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
            {submitLoading ? 'Сохранение...' : '➕ Создать правило'}
          </button>
        </form>
      </div>

      {/* Таблица текущих правил */}
      <h4>📋 Действующие правила сканирования склада</h4>
      {loading ? (
        <div>Загрузка матрицы правил...</div>
      ) : error ? (
        <div style={{ color: 'red', padding: '10px', background: '#fff0f0', borderRadius: '4px' }}>⚠️ Ошибка: {error}</div>
      ) : (
        <table className="table" style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', background: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <thead>
            <tr style={{ background: '#e9ecef', textAlign: 'left' }}>
              <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6' }}>ID</th>
              <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6' }}>Условие по цене</th>
              <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6' }}>Фильтр по имени</th>
              <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6' }}>Критический остаток</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                <td style={{ padding: '12px' }}>#{rule.id}</td>
                <td style={{ padding: '12px' }}>
                  <span style={{ background: '#e2f0d9', padding: '3px 8px', borderRadius: '4px', fontWeight: 'bold', marginRight: '5px' }}>
                    {rule.price_operator === 'ge' ? '≥' : '≤'}
                  </span>
                  {rule.price_value} ₽
                </td>
                <td style={{ padding: '12px', color: rule.name_contains ? '#000' : '#888' }}>
                  {rule.name_contains ? `"${rule.name_contains}"` : '📌 Любой товар'}
                </td>
                <td style={{ padding: '12px', fontWeight: 'bold', color: '#dc3545' }}>
                  меньше {rule.stock_threshold} шт.
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};