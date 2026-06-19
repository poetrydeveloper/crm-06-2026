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
    <div className="card">
      <div className="d-flex justify-between align-center mb-3">
        <h3 className="card-title" style={{ margin: 0 }}>Поставщики</h3>
        <button className="btn btn-success btn-sm" onClick={onCreateSupplier}>
          Добавить
        </button>
      </div>

      {suppliers.length === 0 ? (
        <p className="text-muted text-center" style={{ padding: '20px 0' }}>Список пуст</p>
      ) : (
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Наименование</th>
              </tr>
            </thead>
            <tbody>
              {suppliers.map((s) => (
                <tr key={s.supplier_id}>
                  <td className="text-muted">#{s.supplier_id}</td>
                  <td style={{ fontWeight: 500 }}>{s.name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};