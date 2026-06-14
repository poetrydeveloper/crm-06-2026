// frontend/src/components/atomic/SuppliersTable.tsx
import React from 'react';

interface Supplier {
  supplier_id: number;
  name: string;
}

interface SuppliersTableProps {
  suppliers: Supplier[];
  onCreateSupplier: () => void;
}

export const SuppliersTable: React.FC<SuppliersTableProps> = ({ suppliers, onCreateSupplier }) => {
  return (
    <div style={{ background: '#1a1a1a', padding: '20px', borderRadius: '8px', border: '1px solid #333' }}>
      <div style={{ display: 'flex', justifyContext: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h3 style={{ margin: 0, color: '#fff' }}>🏢 Зарегистрированные поставщики</h3>
        <button
          onClick={onCreateSupplier}
          style={{ background: '#2ea44f', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          + Добавить поставщика
        </button>
      </div>

      {suppliers.length === 0 ? (
        <div style={{ color: '#666', textAlign: 'center', padding: '20px' }}>Список поставщиков пуст. Добавьте первого контрагента.</div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: '#222', color: '#aaa', borderBottom: '2px solid #333' }}>
              <th style={{ padding: '10px' }}>ID Поставщика</th>
              <th style={{ padding: '10px' }}>Наименование компании</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.map(s => (
              <tr key={s.supplier_id} style={{ borderBottom: '1px solid #2d2d2d' }}>
                <td style={{ padding: '10px', color: '#888', fontWeight: 'bold' }}>#{s.supplier_id}</td>
                <td style={{ padding: '10px', color: '#fff' }}>{s.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
