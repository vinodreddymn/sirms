import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Trash2 } from 'lucide-react';

import { api } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import type { Expense, Paginated, Lookup } from './types';
import { expensesApi } from '../../services/expenses';
import { DataTable } from '../../components/DataTable';
import type { Column } from '../../components/DataTable';

export const ExpenseList: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [data, setData] = useState<Paginated<Expense> | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<Lookup[]>([]);
  const [categories, setCategories] = useState<Lookup[]>([]);
  const [paymentModes, setPaymentModes] = useState<Lookup[]>([]);
  const [paymentStatuses, setPaymentStatuses] = useState<Lookup[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedMonth, setSelectedMonth] = useState('');
  const [selectedFinancialYear, setSelectedFinancialYear] = useState('');
  const [selectedPaymentStatus, setSelectedPaymentStatus] = useState('');

  const financialYearOptions = Array.from({ length: 5 }, (_, index) => {
    const year = new Date().getFullYear() - index;
    return { label: `${year}-${year + 1}`, value: String(year) };
  });

  const load = async (pageNumber = 1) => {
    try {
      setLoading(true);
      const params: Record<string, unknown> = { page_size: 100, page: pageNumber };
      if (selectedCategory) params.category_id = selectedCategory;
      if (selectedPaymentStatus) params.payment_status_id = selectedPaymentStatus;
      if (selectedFinancialYear || selectedMonth) {
        const baseYear = Number(selectedFinancialYear || new Date().getFullYear());
        const monthIndex = selectedMonth ? Number(selectedMonth) - 1 : null;
        const startDate = monthIndex === null ? new Date(baseYear, 0, 1) : new Date(baseYear, monthIndex, 1);
        const endDate = monthIndex === null ? new Date(baseYear + 1, 0, 0) : new Date(baseYear, monthIndex + 1, 0);
        params.date_from = startDate.toISOString().slice(0, 10);
        params.date_to = endDate.toISOString().slice(0, 10);
      }
      const res = await expensesApi.list(params);
      setData(res.data);
      setPage(pageNumber);
    } catch (err) {
      addToast('error', 'Could not load expenses');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(1); }, [selectedCategory, selectedPaymentStatus, selectedMonth, selectedFinancialYear]);

  useEffect(() => {
    void api.get('/common/projects', { params: { page_size: 200 } }).then(r => setProjects(r.data.items)).catch(() => setProjects([]));
    void api.get('/master/expense-categories', { params: { page_size: 200 } }).then(r => setCategories(r.data.items)).catch(() => setCategories([]));
    void api.get('/master/payment-modes', { params: { page_size: 200 } }).then(r => setPaymentModes(r.data.items)).catch(() => setPaymentModes([]));
    void api.get('/master/payment-statuses', { params: { page_size: 200 } }).then(r => setPaymentStatuses(r.data.items)).catch(() => setPaymentStatuses([]));
  }, []);

  const remove = async (id: string) => {
    if (!confirm('Delete this expense?')) return;
    try {
      await expensesApi.delete(id);
      addToast('success', 'Expense deleted');
      await load();
    } catch (err: any) { addToast('error', err.response?.data?.detail || 'Could not delete expense'); }
  };

  const resolveLookupLabel = (item?: Lookup) => item?.name ?? item?.project_name ?? item?.project_code ?? '';

  const exportCsv = () => {
    if (!data) return;
    const rows = data.items;
    const headers = ['Expense No','Expense Date','Project','Category','Description','Bill Reference','Amount','Payment Mode','Payment Status','Created At'];
    const csv = [headers.join(','), ...rows.map(r => {
      const expenseNumber = r.expense_number ?? r.expense_no ?? '';
      const project = resolveLookupLabel(projects.find(p => String(p.id) === r.project_id)) || r.project_id;
      const category = resolveLookupLabel(categories.find(c => String(c.id) === r.expense_category_id)) || r.expense_category_id;
      const mode = resolveLookupLabel(paymentModes.find(m => String(m.id) === r.payment_mode_id)) || r.payment_mode_id;
      const status = resolveLookupLabel(paymentStatuses.find(s => String(s.id) === r.payment_status_id)) || r.payment_status_id;
      const amount = Number.isFinite(Number(r.amount)) ? Number(r.amount).toFixed(2) : r.amount;
      return [
        expenseNumber,
        r.expense_date,
        project,
        category,
        '"' + (r.description || '') + '"',
        r.bill_reference || '',
        amount,
        mode,
        status,
        r.created_at,
      ].join(',');
    })].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'expenses.csv'; a.click(); URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: 'grid', gap: '1.25rem' }}>
      <div className="page-header">
        <div>
          <h1>Expense Register</h1>
          <p className="page-subtitle">Manage project expenses, attachments and payments.</p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button className="btn" onClick={exportCsv}>Export CSV</button>
          <button className="btn btn-primary" onClick={() => navigate('/expenses/new')}><Plus size={14} /> Add Expense</button>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1rem', display: 'grid', gap: '0.75rem', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <label style={{ display: 'grid', gap: '0.35rem', fontSize: '0.9rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Category</span>
          <select value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)} style={{ padding: '0.6rem 0.75rem', borderRadius: 'var(--border-radius-sm)', border: '1px solid var(--border-color)', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
            <option value="">All categories</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>{resolveLookupLabel(category)}</option>
            ))}
          </select>
        </label>

        <label style={{ display: 'grid', gap: '0.35rem', fontSize: '0.9rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Month</span>
          <select value={selectedMonth} onChange={e => setSelectedMonth(e.target.value)} style={{ padding: '0.6rem 0.75rem', borderRadius: 'var(--border-radius-sm)', border: '1px solid var(--border-color)', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
            <option value="">All months</option>
            {Array.from({ length: 12 }, (_, index) => (
              <option key={index + 1} value={String(index + 1)}>{new Date(2020, index).toLocaleString('en-US', { month: 'long' })}</option>
            ))}
          </select>
        </label>

        <label style={{ display: 'grid', gap: '0.35rem', fontSize: '0.9rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Financial Year</span>
          <select value={selectedFinancialYear} onChange={e => setSelectedFinancialYear(e.target.value)} style={{ padding: '0.6rem 0.75rem', borderRadius: 'var(--border-radius-sm)', border: '1px solid var(--border-color)', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
            <option value="">All years</option>
            {financialYearOptions.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>

        <label style={{ display: 'grid', gap: '0.35rem', fontSize: '0.9rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Payment Status</span>
          <select value={selectedPaymentStatus} onChange={e => setSelectedPaymentStatus(e.target.value)} style={{ padding: '0.6rem 0.75rem', borderRadius: 'var(--border-radius-sm)', border: '1px solid var(--border-color)', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
            <option value="">All statuses</option>
            {paymentStatuses.map(status => (
              <option key={status.id} value={status.id}>{resolveLookupLabel(status)}</option>
            ))}
          </select>
        </label>

        <div style={{ display: 'flex', alignItems: 'end' }}>
          <button className="btn" onClick={() => { setSelectedCategory(''); setSelectedMonth(''); setSelectedFinancialYear(''); setSelectedPaymentStatus(''); }} style={{ width: '100%' }}>Clear Filters</button>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1rem' }}>
        <DataTable
          loading={loading}
          columns={([
            { header: 'Expense No', accessor: (r: Expense) => <strong>{r.expense_number ?? r.expense_no ?? ''}</strong>, width: '13%' },
            { header: 'Date', accessor: (r: Expense) => new Date(r.expense_date).toLocaleDateString(), width: '10%', sortKey: 'expense_date' },
            { header: 'Project', accessor: (r: Expense) => resolveLookupLabel(projects.find(p => String(p.id) === r.project_id)) || r.project_id, width: '12%' },
            { header: 'Category', accessor: (r: Expense) => categories.find(c => String(c.id) === r.expense_category_id)?.name ?? r.expense_category_id, width: '12%' },
            { header: 'Description', accessor: (r: Expense) => r.description ?? '', width: '18%' },
            { header: 'Bill Ref', accessor: (r: Expense) => r.bill_reference ?? '', width: '10%' },
            { header: 'Amount', accessor: (r: Expense) => { const n = Number(r.amount); return Number.isFinite(n) ? n.toFixed(2) : r.amount; }, width: '8%', sortKey: 'amount' },
            { header: 'Payment Mode', accessor: (r: Expense) => paymentModes.find(m => String(m.id) === r.payment_mode_id)?.name ?? r.payment_mode_id, width: '10%' },
            { header: 'Payment Status', accessor: (r: Expense) => paymentStatuses.find(s => String(s.id) === r.payment_status_id)?.name ?? r.payment_status_id, width: '10%' },
            { header: 'Created At', accessor: (r: Expense) => new Date(r.created_at).toLocaleString(), width: '12%', sortKey: 'created_at' },
            { header: 'Actions', accessor: (r: Expense) => (
                <div style={{ display: 'flex', gap: '0.4rem' }}>
                  <button className="btn btn-secondary" onClick={(e) => { e.stopPropagation(); navigate(`/expenses/${r.id}`); }}>View</button>
                  <button className="btn" onClick={(e) => { e.stopPropagation(); navigate(`/expenses/${r.id}/edit`); }}>Edit</button>
                  <button className="btn btn-ghost" onClick={(e) => { e.stopPropagation(); remove(r.id); }} title="Delete"><Trash2 size={14} /></button>
                </div>
              ), width: '12%' },
          ]) as Column<Expense>[]}
          data={data?.items ?? []}
          page={data?.page ?? 1}
          totalPages={data?.pages ?? 1}
          totalCount={data?.total}
          onPageChange={(p) => void load(p)}
          onRowClick={(r) => navigate(`/expenses/${r.id}`)}
          emptyMessage="No expenses found."
        />
      </div>
    </div>
  );
};

export default ExpenseList;
