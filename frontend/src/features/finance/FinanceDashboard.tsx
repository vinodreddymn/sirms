import React, { useEffect, useMemo, useState } from 'react';
import { PieChart, TrendingUp, Clock3 } from 'lucide-react';

import { api } from '../../services/api';
import { expensesApi } from '../../services/expenses';
import { useToast } from '../../contexts/ToastContext';
import { Panel } from '../../components/Panel';
import type { Expense, Lookup } from './types';

const formatCurrency = (value: number) => new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
}).format(value);

const resolveLookupLabel = (items: Lookup[], id: string) => {
  return items.find((item) => String(item.id) === id)?.name ?? id;
};

const groupBy = <T, K extends string | number>(items: T[], keyFn: (item: T) => K) => {
  const groups = new Map<K, T[]>();
  items.forEach((item) => {
    const key = keyFn(item);
    const list = groups.get(key) ?? [];
    list.push(item);
    groups.set(key, list);
  });
  return groups;
};

export const FinanceDashboard: React.FC = () => {
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
        addToast('error', 'Could not load finance lookups');
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
        addToast('error', 'Could not load expenses for dashboard');
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [addToast]);

  const summary = useMemo(() => {
    const total = expenses.reduce((sum, expense) => sum + Number(expense.amount), 0);
    const count = expenses.length;
    const currentDate = new Date();
    const currentFinancialYearStart = new Date(currentDate.getFullYear(), 3, 1); // April 1
    const currentFinancialYearEnd = new Date(currentDate.getFullYear() + 1, 3, 0); // March 31

    if (currentDate.getMonth() < 3) {
      currentFinancialYearStart.setFullYear(currentDate.getFullYear() - 1);
      currentFinancialYearEnd.setFullYear(currentDate.getFullYear());
    }

    const currentFinancialYearTotal = expenses
      .filter((expense) => {
        const expenseDate = new Date(expense.expense_date);
        return expenseDate >= currentFinancialYearStart && expenseDate <= currentFinancialYearEnd;
      })
      .reduce((sum, expense) => sum + Number(expense.amount), 0);

    const paymentGroups = groupBy(expenses, (expense) => resolveLookupLabel(paymentStatuses, expense.payment_status_id));
    const categoryGroups = groupBy(expenses, (expense) => resolveLookupLabel(categories, expense.expense_category_id));
    const monthlyGroups = groupBy(expenses, (expense) => {
      const date = new Date(expense.expense_date);
      return date.toLocaleString('en-US', { year: 'numeric', month: 'long' });
    });

    const topCategories = Array.from(categoryGroups.entries())
      .map(([label, items]) => ({ label, amount: items.reduce((acc, item) => acc + Number(item.amount), 0), count: items.length }))
      .sort((a, b) => b.amount - a.amount)
      .slice(0, 5);

    const statusTotals = Array.from(paymentGroups.entries())
      .map(([label, items]) => ({ label, amount: items.reduce((acc, item) => acc + Number(item.amount), 0), count: items.length }))
      .sort((a, b) => b.amount - a.amount);

    const trend = Array.from(monthlyGroups.entries())
      .map(([month, items]) => ({
        month,
        amount: items.reduce((acc, item) => acc + Number(item.amount), 0),
      }))
      .sort((a, b) => a.month.localeCompare(b.month));

    return {
      total,
      count,
      currentFinancialYearTotal,
      topCategories,
      statusTotals,
      trend,
    };
  }, [expenses, categories, paymentStatuses]);

  const recentExpenses = useMemo(
    () => [...expenses].sort((a, b) => new Date(b.expense_date).getTime() - new Date(a.expense_date).getTime()).slice(0, 8),
    [expenses],
  );

  return (
    <div style={{ display: 'grid', gap: '1.25rem' }}>
      <div>
        <h1>Finance Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          Summary of expense activity, payment status, category performance, and recent transactions.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '1rem' }}>
        <Panel title="Total Expense">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <TrendingUp size={18} />
            <div>
              <div style={{ fontSize: '1.6rem', fontWeight: 700 }}>{formatCurrency(summary.total)}</div>
              <div style={{ color: 'var(--text-secondary)' }}>{summary.count} expenses</div>
              <div style={{ marginTop: '0.4rem', fontSize: '0.95rem', color: 'var(--text-secondary)' }}>
                FY Total Payment: <strong style={{ color: 'var(--text-primary)' }}>{formatCurrency(summary.currentFinancialYearTotal)}</strong>
              </div>
            </div>
          </div>
        </Panel>

        <Panel title="Top Category">
          {summary.topCategories.length ? (
            <div style={{ display: 'grid', gap: '0.6rem' }}>
              {summary.topCategories.slice(0, 3).map((item) => (
                <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                  <strong>{formatCurrency(item.amount)}</strong>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No category data</p>
          )}
        </Panel>

        <Panel title="Payment Status">
          {summary.statusTotals.length ? (
            <div style={{ display: 'grid', gap: '0.6rem' }}>
              {summary.statusTotals.slice(0, 3).map((item) => (
                <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                  <strong>{formatCurrency(item.amount)}</strong>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No status data</p>
          )}
        </Panel>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }}>
        <Panel title="Monthly Spend Trend" actions={<PieChart size={16} />}> 
          {loading ? (
            <p>Loading...</p>
          ) : summary.trend.length ? (
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              {summary.trend.map((item) => (
                <div key={item.month} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>{item.month}</span>
                  <strong>{formatCurrency(item.amount)}</strong>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No trend data available</p>
          )}
        </Panel>

        <Panel title="Category Breakdown" actions={<PieChart size={16} />}>
          {summary.topCategories.length ? (
            <div style={{ display: 'grid', gap: '0.6rem' }}>
              {summary.topCategories.map((item) => (
                <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                  <strong>{formatCurrency(item.amount)}</strong>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No category breakdown</p>
          )}
        </Panel>
      </div>

      <Panel title="Recent Expenses">
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
              <th style={{ padding: '8px 6px' }}>Date</th>
              <th style={{ padding: '8px 6px' }}>Category</th>
              <th style={{ padding: '8px 6px' }}>Description</th>
              <th style={{ padding: '8px 6px' }}>Amount</th>
              <th style={{ padding: '8px 6px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {recentExpenses.map((expense) => (
              <tr key={expense.id} style={{ borderBottom: '1px solid var(--bg-secondary)' }}>
                <td style={{ padding: '10px 6px' }}>{new Date(expense.expense_date).toLocaleDateString()}</td>
                <td style={{ padding: '10px 6px' }}>{resolveLookupLabel(categories, expense.expense_category_id)}</td>
                <td style={{ padding: '10px 6px' }}>{expense.description || '-'}</td>
                <td style={{ padding: '10px 6px', fontWeight: 600 }}>{formatCurrency(Number(expense.amount))}</td>
                <td style={{ padding: '10px 6px' }}>{resolveLookupLabel(paymentStatuses, expense.payment_status_id)}</td>
              </tr>
            ))}
            {!recentExpenses.length && (
              <tr>
                <td colSpan={5} style={{ padding: '10px 6px', color: 'var(--text-secondary)' }}>
                  No expenses available for the dashboard.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </Panel>
    </div>
  );
};

export default FinanceDashboard;
