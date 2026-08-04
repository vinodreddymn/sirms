import React, { useEffect, useMemo, useState } from 'react';
import { Download, FileText } from 'lucide-react';

import { Tabs } from '../../components/Tabs';
import { Panel } from '../../components/Panel';
import { useToast } from '../../contexts/ToastContext';
import { api } from '../../services/api';
import { expensesApi } from '../../services/expenses';
import type { Expense, Lookup } from '../finance/types';

const resolveLookupLabel = (items: Lookup[], id: string) => items.find((item) => String(item.id) === id)?.name ?? id;

const exportExpensesCsv = (items: Expense[], categories: Lookup[], paymentStatuses: Lookup[]) => {
  const headers = ['Expense Number', 'Date', 'Category', 'Description', 'Amount', 'Payment Status', 'Bill Reference'];
  const rows = items.map((expense) => [
    expense.expense_number ?? expense.expense_no ?? '',
    expense.expense_date,
    expense.expense_category_name ?? resolveLookupLabel(categories, expense.expense_category_id),
    expense.description ?? '',
    Number(expense.amount).toFixed(2),
    expense.payment_status_name ?? resolveLookupLabel(paymentStatuses, expense.payment_status_id),
    expense.bill_reference ?? '',
  ]);
  const csv = [headers.join(','), ...rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'finance-expenses.csv';
  a.click();
  URL.revokeObjectURL(url);
};

const FinanceReport: React.FC = () => {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [categories, setCategories] = useState<Lookup[]>([]);
  const [paymentStatuses, setPaymentStatuses] = useState<Lookup[]>([]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [categoriesRes, paymentStatusesRes] = await Promise.all([
          api.get<{ items: Lookup[] }>('/master/expense-categories', { params: { page_size: 200 } }),
          api.get<{ items: Lookup[] }>('/master/payment-statuses', { params: { page_size: 200 } }),
        ]);
        setCategories(categoriesRes.data.items);
        setPaymentStatuses(paymentStatusesRes.data.items);
      } catch (err) {
        addToast('error', 'Could not load lookup data.');
      }

      try {
        const pageSize = 200;
        let page = 1;
        let allExpenses: Expense[] = [];
        let total = 0;

        do {
          const response = await expensesApi.list({ page_size: pageSize, page });
          total = response.data.total;
          allExpenses = [...allExpenses, ...response.data.items];
          page += 1;
        } while (allExpenses.length < total);

        setExpenses(allExpenses);
      } catch (err) {
        addToast('error', 'Could not load finance expenses');
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [addToast]);

  const summary = useMemo(() => {
    const totalAmount = expenses.reduce((sum, expense) => sum + Number(expense.amount), 0);
    const categoryGroups = new Map<string, Expense[]>();
    const paymentGroups = new Map<string, Expense[]>();

    expenses.forEach((expense) => {
      const category = resolveLookupLabel(categories, expense.expense_category_id);
      const status = resolveLookupLabel(paymentStatuses, expense.payment_status_id);
      categoryGroups.set(category, [...(categoryGroups.get(category) ?? []), expense]);
      paymentGroups.set(status, [...(paymentGroups.get(status) ?? []), expense]);
    });

    const topCategories = Array.from(categoryGroups.entries())
      .map(([label, items]) => ({ label, amount: items.reduce((sum, item) => sum + Number(item.amount), 0), count: items.length }))
      .sort((a, b) => b.amount - a.amount)
      .slice(0, 5);

    const statusTotals = Array.from(paymentGroups.entries())
      .map(([label, items]) => ({ label, amount: items.reduce((sum, item) => sum + Number(item.amount), 0), count: items.length }))
      .sort((a, b) => b.amount - a.amount);

    return {
      totalAmount,
      count: expenses.length,
      topCategories,
      statusTotals,
    };
  }, [expenses, categories, paymentStatuses]);

  const recentExpenses = useMemo(() =>
    [...expenses]
      .sort((a, b) => new Date(b.expense_date).getTime() - new Date(a.expense_date).getTime())
      .slice(0, 6),
  [expenses]);

  return (
    <div style={{ display: 'grid', gap: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        <div>
          <h2>Finance Reports</h2>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
            Expense reporting, export options and financial summaries.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => exportExpensesCsv(expenses, categories, paymentStatuses)} disabled={!expenses.length || loading}>
            <Download size={16} style={{ marginRight: '0.35rem' }} /> Export expenses
          </button>
          <button className="btn btn-secondary" onClick={() => alert('PDF export not configured yet')}>
            <FileText size={16} style={{ marginRight: '0.35rem' }} /> Export summary
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '1rem' }}>
        <Panel title="Total Expense">
          <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 2 }).format(summary.totalAmount)}</div>
          <div style={{ color: 'var(--text-secondary)' }}>{summary.count} expenses</div>
        </Panel>

        <Panel title="Top Categories">
          {summary.topCategories.length ? summary.topCategories.map((item) => (
            <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
              <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
              <strong>{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(item.amount)}</strong>
            </div>
          )) : <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No category data</p>}
        </Panel>

        <Panel title="Payment Status">
          {summary.statusTotals.length ? summary.statusTotals.map((item) => (
            <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
              <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
              <strong>{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(item.amount)}</strong>
            </div>
          )) : <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No status data</p>}
        </Panel>
      </div>

      <Panel title="Recent Expenses">
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '8px 6px', textAlign: 'left' }}>Date</th>
              <th style={{ padding: '8px 6px', textAlign: 'left' }}>Category</th>
              <th style={{ padding: '8px 6px', textAlign: 'left' }}>Description</th>
              <th style={{ padding: '8px 6px', textAlign: 'right' }}>Amount</th>
              <th style={{ padding: '8px 6px', textAlign: 'left' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {recentExpenses.map((expense) => (
              <tr key={expense.id} style={{ borderBottom: '1px solid var(--bg-secondary)' }}>
                <td style={{ padding: '10px 6px' }}>{new Date(expense.expense_date).toLocaleDateString()}</td>
                <td style={{ padding: '10px 6px' }}>{resolveLookupLabel(categories, expense.expense_category_id)}</td>
                <td style={{ padding: '10px 6px' }}>{expense.description ?? '-'}</td>
                <td style={{ padding: '10px 6px', textAlign: 'right', fontWeight: 600 }}>{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(Number(expense.amount))}</td>
                <td style={{ padding: '10px 6px' }}>{resolveLookupLabel(paymentStatuses, expense.payment_status_id)}</td>
              </tr>
            ))}
            {!recentExpenses.length && (
              <tr>
                <td colSpan={5} style={{ padding: '10px 6px', color: 'var(--text-secondary)' }}>No expenses available.</td>
              </tr>
            )}
          </tbody>
        </table>
      </Panel>
    </div>
  );
};

export const Reports: React.FC = () => {
  const tabs = [
    {
      id: 'overview',
      label: 'Overview',
      content: (
        <div style={{ padding: '1.5rem' }}>
          <h2>Reports</h2>
          <p style={{ color: 'var(--text-muted)' }}>
            This section contains enterprise reporting and export options.
          </p>
        </div>
      ),
    },
    {
      id: 'finance',
      label: 'Finance',
      content: <FinanceReport />,
    },
  ];

  return (
    <div style={{ padding: '1.5rem' }}>
      <Tabs tabs={tabs} defaultTab="finance" />
    </div>
  );
};
