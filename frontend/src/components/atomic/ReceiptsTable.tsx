// frontend/src/components/atomic/ReceiptsTable.tsx
import React, { useState } from 'react';

interface UnitItem {
  unit_id: number;
  unique_serial_number: string;
  purchase_price: number;
  physical_status: string;
}

interface ProductItem {
  product_id: number;
  product_name: string;
  product_code: string;
  units: UnitItem[];
  expected_count: number;
  total_count: number;
}

interface SupplierOrder {
  order_key: string;
  order_date: string;
  supplier_id: number;
  supplier_name: string;
  total_financial_load: number;
  products: ProductItem[];
}

interface ReceiptsTableProps {
  orders: SupplierOrder[];
  expandedOrderKey: string | null;
  onToggleRow: (key: string) => void;
  onConfirmReceipt: (supplierId: number, unitIds: number[]) => void;
  onOpenModal: () => void;
}

export const ReceiptsTable: React.FC<ReceiptsTableProps> = ({
  orders,
  expandedOrderKey,
  onToggleRow,
  onConfirmReceipt,
}) => {
  const [selectedUnits, setSelectedUnits] = useState<Set<number>>(new Set());
  const [acceptedUnits, setAcceptedUnits] = useState<Set<number>>(new Set());

  const handleSelectUnit = (unitId: number, isAccepted: boolean) => {
    if (isAccepted) return;
    setSelectedUnits((prev) => {
      const next = new Set(prev);
      if (next.has(unitId)) next.delete(unitId);
      else next.add(unitId);
      return next;
    });
  };

  const handleSelectAll = (units: UnitItem[]) => {
    const available = units.filter((u) => u.physical_status === 'EXPECTED');
    if (available.length === 0) return;
    const allSelected = available.every((u) => selectedUnits.has(u.unit_id));
    setSelectedUnits((prev) => {
      const next = new Set(prev);
      for (const u of available) {
        if (allSelected) next.delete(u.unit_id);
        else next.add(u.unit_id);
      }
      return next;
    });
  };

  const handleAcceptSelected = async (supplierId: number, key: string, units: UnitItem[]) => {
    const ids = Array.from(selectedUnits);
    if (ids.length === 0) return;

    await onConfirmReceipt(supplierId, ids);
    setAcceptedUnits((prev) => {
      const next = new Set(prev);
      for (const id of ids) next.add(id);
      return next;
    });
    setSelectedUnits(new Set());
  };

  // Сбрасываем accepted при новых данных
  React.useEffect(() => {
    setAcceptedUnits(new Set());
    setSelectedUnits(new Set());
  }, [orders]);

  if (orders.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <p className="text-muted">Нет активных заявок за выбранный период</p>
      </div>
    );
  }

  return (
    <div>
      {orders.map((order) => {
        const isExpanded = expandedOrderKey === order.order_key;
        const allUnits = order.products.flatMap((p) => p.units);
        const expectedUnits = allUnits.filter((u) => u.physical_status === 'EXPECTED');
        const allAccepted = expectedUnits.length === 0 || expectedUnits.every((u) => acceptedUnits.has(u.unit_id));

        return (
          <div key={order.order_key} className="card mb-3">
            <div
              className="d-flex justify-between align-center"
              style={{
                cursor: 'pointer',
                paddingBottom: isExpanded ? '12px' : '0',
                borderBottom: isExpanded ? '1px solid var(--border)' : 'none',
              }}
              onClick={() => onToggleRow(order.order_key)}
            >
              <div className="d-flex align-center gap-8">
                <span>{isExpanded ? '▼' : '►'}</span>
                <div>
                  <div style={{ fontWeight: 600 }}>{order.supplier_name}</div>
                  <div className="text-muted" style={{ fontSize: '12px' }}>
                    {new Date(order.order_date).toLocaleDateString('ru-RU')} — {order.products.length} поз. ({expectedUnits.length} ожидает)
                  </div>
                </div>
              </div>
              <div className="d-flex align-center gap-12">
                <span style={{ fontWeight: 600, color: 'var(--success)' }}>
                  {order.total_financial_load.toFixed(2)} ₽
                </span>
                <span className={`badge ${allAccepted ? 'badge-success' : 'badge-warning'}`}>
                  {allAccepted ? 'Выставлено на полку' : 'В ПУТИ'}
                </span>
              </div>
            </div>

            {isExpanded && (
              <div style={{ paddingTop: '12px' }}>
                {allUnits.length === 0 ? (
                  <div className="text-muted text-center" style={{ padding: '16px' }}>Нет юнитов</div>
                ) : (
                  <>
                    <div className="d-flex justify-between align-center mb-2">
                      <label className="d-flex align-center gap-8" style={{ cursor: 'pointer', fontSize: '13px' }}>
                        <input
                          type="checkbox"
                          checked={expectedUnits.length > 0 && expectedUnits.every((u) => selectedUnits.has(u.unit_id))}
                          onChange={() => handleSelectAll(allUnits)}
                        />
                        Выбрать всё ({expectedUnits.length} шт.)
                      </label>
                      <button
                        className="btn btn-success btn-sm"
                        disabled={selectedUnits.size === 0}
                        onClick={() => handleAcceptSelected(order.supplier_id, order.order_key, allUnits)}
                      >
                        Принять выбранное ({selectedUnits.size})
                      </button>
                    </div>

                    {order.products.map((product) => (
                      <div key={product.product_id} className="mb-3">
                        <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px', textTransform: 'capitalize' }}>
                          {product.product_name.replace(/_/g, ' ')}
                        </div>
                        <div className="text-muted text-mono" style={{ fontSize: '11px', marginBottom: '6px' }}>
                          {product.product_code} — {product.expected_count}/{product.total_count} ожидает
                        </div>
                        <div className="table-wrapper">
                          <table className="table" style={{ fontSize: '13px' }}>
                            <thead>
                              <tr>
                                <th style={{ width: '30px' }}></th>
                                <th>Серийный номер</th>
                                <th style={{ textAlign: 'right' }}>Цена</th>
                                <th>Статус</th>
                              </tr>
                            </thead>
                            <tbody>
                              {product.units.map((unit) => {
                                const isAccepted = unit.physical_status !== 'EXPECTED' || acceptedUnits.has(unit.unit_id);
                                return (
                                  <tr
                                    key={unit.unit_id}
                                    style={{
                                      background: isAccepted ? 'var(--bg-tertiary)' : undefined,
                                      opacity: isAccepted ? 0.7 : 1,
                                    }}
                                  >
                                    <td>
                                      {!isAccepted && (
                                        <input
                                          type="checkbox"
                                          checked={selectedUnits.has(unit.unit_id)}
                                          onChange={() => handleSelectUnit(unit.unit_id, isAccepted)}
                                        />
                                      )}
                                    </td>
                                    <td className="text-mono" style={{ fontSize: '12px' }}>{unit.unique_serial_number}</td>
                                    <td style={{ textAlign: 'right', color: 'var(--success)' }}>
                                      {unit.purchase_price.toFixed(2)} ₽
                                    </td>
                                    <td>
                                      {isAccepted ? (
                                        <span className="badge badge-success">✔ Принят</span>
                                      ) : (
                                        <span className="badge badge-warning">Ожидает</span>
                                      )}
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ))}
                  </>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};