// frontend/src/components/atomic/CashboxExcelExport.tsx
import React, { useState } from 'react';

export const CashboxExcelExport: React.FC = () => {
  const [exporting, setExporting] = useState(false);

  const handleExportExcel = async () => {
    try {
      setExporting(true);
      const response = await fetch('/api/v1/cash/days/current/export-excel');

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Не удалось сформировать файл смены');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      const dateStr = new Date().toLocaleDateString('ru-RU').replace(/\./g, '-');
      a.download = `Отчет_Смены_${dateStr}.xlsx`;

      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (error: any) {
      alert(`⚠️ Ошибка экспорта Excel: ${error.message}`);
    } finally {
      setExporting(false);
    }
  };

  return (
    <button
      className="btn btn-sm btn-success"
      onClick={handleExportExcel}
      disabled={exporting}
      style={{ background: '#28a745', color: '#fff', border: 'none' }}
    >
      {exporting ? '⏳ Формирование...' : '📥 Выгрузить в Excel'}
    </button>
  );
};
