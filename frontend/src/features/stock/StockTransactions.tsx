import React, { useEffect, useState } from 'react';
import { DataTable } from '../../components/DataTable';
import type { Column } from '../../components/DataTable';
import { api } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { ArrowUpRight, ArrowDownRight, RefreshCcw } from 'lucide-react';

interface StockTransaction {
  id: number;
  transaction_type: 'IN' | 'OUT' | 'ADJUST';
  asset_id: number;
  quantity: number;
  transaction_date: string;
  reference_no?: string;
}

export const StockTransactions: React.FC = () => {
  const [transactions, setTransactions] = useState<StockTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const { addToast } = useToast();

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await api.get('/stock/transactions');
        setTransactions(response.data.items || response.data);
      } catch (err) {
        addToast('error', 'Failed to fetch stock transactions');
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, [addToast]);

  const columns: Column<StockTransaction>[] = [
    { header: 'ID', accessor: 'id', width: '80px' },
    { header: 'Date', accessor: (row) => new Date(row.transaction_date).toLocaleDateString() },
    { header: 'Reference No', accessor: (row) => row.reference_no || '-' },
    { header: 'Asset ID', accessor: 'asset_id' },
    { 
      header: 'Type', 
      accessor: (row) => (
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          {row.transaction_type === 'IN' && <ArrowDownRight size={16} color="var(--success)" />}
          {row.transaction_type === 'OUT' && <ArrowUpRight size={16} color="var(--danger)" />}
          {row.transaction_type === 'ADJUST' && <RefreshCcw size={16} color="var(--warning)" />}
          {row.transaction_type}
        </span>
      )
    },
    { header: 'Quantity', accessor: (row) => (
        <span style={{ 
          fontWeight: 'bold',
          color: row.transaction_type === 'IN' ? 'var(--success)' : row.transaction_type === 'OUT' ? 'var(--danger)' : 'var(--text-primary)'
        }}>
          {row.transaction_type === 'OUT' ? '-' : '+'}{row.quantity}
        </span>
      ) 
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Stock Ledger</h1>
        <button className="btn btn-primary" onClick={() => addToast('info', 'New transaction modal coming soon')}>Record Transaction</button>
      </div>

      <DataTable 
        columns={columns} 
        data={transactions} 
        loading={loading} 
        emptyMessage="No stock transactions found."
      />
    </div>
  );
};
