// frontend/src/components/atomic/CashDaysLoader.tsx
import { useState, useEffect } from 'react';

interface CashDayRecord {
  id: number;
  created_at: string;
  status: 'ОТКРЫТА' | 'ЗАКРЫТА';
  total_sales: number;
}

interface CashDaysLoaderProps {
  children: (data: {
    records: CashDayRecord[];
    loading: boolean;
    error: string | null;
    reload: () => void;
  }) => React.ReactNode;
}

export const CashDaysLoader: React.FC<CashDaysLoaderProps> = ({ children }) => {
  const [records, setRecords] = useState<CashDayRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCashDays = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/cash/days');
      if (response.ok) {
        const data = await response.json();
        setRecords(Array.isArray(data.days) ? data.days : []);
      } else {
        setError(`Ошибка ${response.status}: ${response.statusText}`);
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка сети');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCashDays();
  }, []);

  return <>{children({ records, loading, error, reload: loadCashDays })}</>;
};