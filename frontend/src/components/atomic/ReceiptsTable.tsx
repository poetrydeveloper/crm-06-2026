// frontend/src/components/atomic/ReceiptsTable.tsx
import React, { useState } from 'react';

interface OrderItem {
  product_id: number;
  product_name: string;
  product_code: string;
  qty_in_order: number;
  avg_purchase_price: number;
}

interface UnitItem {
  unit_id: number;
  product_id: number;
  product_name: string;
  product_code: string;
  unique_serial_number: string;
  purchase_price: number;
  physical_status: string;
}

interface SupplierOrder {
  supplier_order_id: number;
  supplier_name: string;
  order_date: string;
  total_financial_load: number;
  status: string;
  items: OrderItem[];
}

interface ReceiptsTableProps {
  orders: SupplierOrder[];
  expandedOrderId: string | null;
  onToggleRow: (id: string) => void;
  onConfirmReceipt: (supplierId: number, unitIds: number[]) => void;
  onOpenModal: () => void;
}

export const ReceiptsTable: React.FC<ReceiptsTableProps> = ({
  orders,
  expandedOrderId,
  onToggleRow,
  onConfirmReceipt,
}) => {
  const [units, setUnits] = useState<Record<string, UnitItem[]>>({});
  const [selectedUnits, setSelectedUnits] = useState<Set<number>>(new Set());
  const [acceptedUnits, setAcceptedUnits] = useState<Set<number>>(new Set());
  const [loadingUnits, setLoadingUnits] = useState<Record<string, boolean>>({});

  const loadUnits = async (supplierId: number, orderKey: string) => {
    if (units[orderKey]) return;
    setLoadingUnits((prev) => ({ ...prev, [orderKey]: true }));
    try {
      const res = await fetch(`/api/v1/warehouse/orders/${supplierId}/items`);
      if (res.ok) {
        const data = await res.json();
        const allUnits = data.items || [];
        setUnits((prev) => ({ ...prev, [orderKey]: allUnits }));
        const alreadyAccepted = allUnits
          .filter((u: UnitItem) => u.physical_status !== 'EXPECTED')
          .map((u: UnitItem) => u.unit_id);
        if (alreadyAccepted.length > 0) {
          setAcceptedUnits((prev) => new Set([...prev, ...alreadyAccepted]));
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingUnits((prev) => ({ ...prev, [orderKey]: false }));
    }
  };

  const handleToggle = (orderKey: string, supplierId: number) => {
    if (expandedOrderId === orderKey) {
      onToggleRow(orderKey);
    } else {
      onToggleRow(orderKey);
      loadUnits(supplierId, orderKey);
    }
  };

  const handleSelectUnit = (unitId: number) => {
    if (acceptedUnits.has(unitId)) return;
    setSelectedUnits((prev) => {
      const next = new Set(prev);
      if (next.has(unitId)) next.delete(unitId);
      else next.add(unitId);
      return next;
    });
  };

  const handleSelectAll = (unitList: UnitItem[]) => {
    const available = unitList.filter((u) => !acceptedUnits.has(u.unit_id));
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

  const handleAcceptSelected = async (supplierId: number, orderKey: string) => {
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

  if (orders.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <p className="text-muted">Нет активных заявок</p>
      </div>
    );
  }

  return (
    <div>
      {orders.map((order, idx) => {
        const orderKey = `${order.order_date}_${order.supplier_order_id}_${idx}`;
        const isExpanded = expandedOrderId === orderKey;
        const unitList = units[orderKey] || [];
        const isLoading = loadingUnits[orderKey];
        const availableUnits = unitList.filter((u) => !acceptedUnits.has(u.unit_id));
        const allAccepted = unitList.length > 0 && unitList.every((u) => acceptedUnits.has(u.unit_id));

        return (
          <div key={orderKey} className="card mb-3">
            <div
              className="d-flex justify-between align-center"
              style={{ cursor: 'pointer', paddingBottom: isExpanded ? '12px' : '0', borderBottom: isExpanded ? '1px solid var(--border)' : 'none' }}
              onClick={() => handleToggle(orderKey, order.supplier_order_id)}
            >
              <div className="d-flex align-center gap-8">
                <span>{isExpanded ? '▼' : '►'}</span>
                <div>
                  <div style={{ fontWeight: 600 }}>{order.supplier_name}</div>
                  <div className="text-muted" style={{ fontSize: '12px' }}>
                    {new Date(order.order_date).toLocaleDateString('ru-RU')} — {order.items.length} поз.
                  </div>
                </div>
              </div>
              <div className="d-flex align-center gap-12">
                <span style={{ fontWeight: 600, color: 'var(--success)' }}>
                  {order.total_financial_load.toFixed(2)} ₽
                </span>
                <span className={`badge ${allAccepted ? 'badge-success' : 'badge-warning'}`}>
                  {allAccepted ? 'Выставлено на полку' : order.status}
                </span>
              </div>
            </div>

            {isExpanded && (
              <div style={{ paddingTop: '12px' }}>
                {isLoading ? (
                  <div className="text-muted text-center" style={{ padding: '16px' }}>Загрузка юнитов...</div>
                ) : unitList.length === 0 ? (
                  <div className="text-muted text-center" style={{ padding: '16px' }}>Нет юнитов</div>
                ) : (
                  <>
                    <div className="d-flex justify-between align-center mb-2">
                      <label className="d-flex align-center gap-8" style={{ cursor: 'pointer', fontSize: '13px' }}>
                        <input
                          type="checkbox"
                          checked={availableUnits.length > 0 && availableUnits.every((u) => selectedUnits.has(u.unit_id))}
                          onChange={() => handleSelectAll(unitList)}
                        />
                        Выбрать всё ({availableUnits.length} шт.)
                      </label>
                      <button
                        className="btn btn-success btn-sm"
                        disabled={selectedUnits.size === 0}
                        onClick={() => handleAcceptSelected(order.supplier_order_id, orderKey)}
                      >
                        Принять выбранное ({selectedUnits.size})
                      </button>
                    </div>
                    <div className="table-wrapper">
                      <table className="table" style={{ fontSize: '13px' }}>
                        <thead>
                          <tr>
                            <th style={{ width: '30px' }}></th>
                            <th>Серийный номер</th>
                            <th>Товар</th>
                            <th style={{ textAlign: 'right' }}>Цена</th>
                            <th>Статус</th>
                          </tr>
                        </thead>
                        <tbody>
                          {unitList.map((unit) => (
                            <tr
                              key={unit.unit_id}
                              style={{
                                background: acceptedUnits.has(unit.unit_id) ? 'var(--bg-tertiary)' : undefined,
                                opacity: acceptedUnits.has(unit.unit_id) ? 0.7 : 1,
                              }}
                            >
                              <td>
                                {!acceptedUnits.has(unit.unit_id) && (
                                  <input
                                    type="checkbox"
                                    checked={selectedUnits.has(unit.unit_id)}
                                    onChange={() => handleSelectUnit(unit.unit_id)}
                                  />
                                )}
                              </td>
                              <td className="text-mono" style={{ fontSize: '12px' }}>{unit.unique_serial_number}</td>
                              <td style={{ textTransform: 'capitalize' }}>{unit.product_name.replace(/_/g, ' ')}</td>
                              <td style={{ textAlign: 'right', color: 'var(--success)' }}>
                                {unit.purchase_price.toFixed(2)} ₽
                              </td>
                              <td>
                                {acceptedUnits.has(unit.unit_id) ? (
                                  <span className="badge badge-success">✔ Принят</span>
                                ) : (
                                  <span className="badge badge-warning">Ожидает</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
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