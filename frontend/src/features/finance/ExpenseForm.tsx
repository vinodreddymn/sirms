import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { expensesApi } from '../../services/expenses';
import { Input, Select } from '../../components/FormControls';
import type { Lookup, Expense } from './types';

const emptyForm = {
  project_id: '',
  expense_date: '',
  expense_category_id: '',
  description: '',
  bill_reference: '',
  amount: '',
  payment_mode_id: '',
  payment_status_id: '',
  remarks: '',
};

export const ExpenseForm: React.FC<{ mode: 'create' | 'edit' }> = ({ mode }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [lookups, setLookups] = useState<{ projects: Lookup[]; categories: Lookup[]; paymentModes: Lookup[]; paymentStatuses: Lookup[] }>({ projects: [], categories: [], paymentModes: [], paymentStatuses: [] });
  const [form, setForm] = useState<any>(emptyForm);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void Promise.all([
      api.get('/common/projects', { params: { page_size: 200 } }),
      api.get('/master/expense-categories', { params: { page_size: 200 } }),
      api.get('/master/payment-modes', { params: { page_size: 200 } }),
      api.get('/master/payment-statuses', { params: { page_size: 200 } }),
    ]).then(([p, c, pm, ps]) => setLookups({ projects: p.data.items, categories: c.data.items, paymentModes: pm.data.items, paymentStatuses: ps.data.items })).catch(() => addToast('error', 'Could not load form options'));
  }, []);

  useEffect(() => {
    if (mode === 'edit' && id) {
      void expensesApi.get(id).then(r => { const e: Expense = r.data; setForm({ ...e, expense_date: e.expense_date.slice(0,10) }); }).catch(() => addToast('error', 'Could not load expense'));
    }
  }, [mode, id]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        // master lookups use UUIDs; keep as strings
        expense_category_id: form.expense_category_id,
        payment_mode_id: form.payment_mode_id,
        payment_status_id: form.payment_status_id,
        amount: Number(form.amount),
      };
      if (mode === 'create') {
        const response = await expensesApi.create(payload);
        addToast('success', 'Expense created');
        navigate(`/expenses/${response.data.id}`);
      } else if (id) {
        await expensesApi.update(id, payload);
        addToast('success', 'Expense updated');
        navigate(`/expenses/${id}`);
      }
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Could not save expense');
    } finally { setSaving(false); }
  };

  return (
    <div style={{ display: 'grid', gap: '1.25rem' }}>
      <div className="page-header">
        <div>
          <h1>{mode === 'create' ? 'Add Expense' : 'Edit Expense'}</h1>
          <p className="page-subtitle">Capture project expense details, payment options, and supporting references.</p>
        </div>
        <button className="btn btn-secondary" onClick={() => navigate('/expenses')}>
          Cancel
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <form onSubmit={submit} style={{ display: 'grid', gap: '1rem' }}>
          <Select
            label="Project"
            required
            value={form.project_id}
            onChange={e => setForm({ ...form, project_id: e.target.value })}
            options={[
              { value: '', label: 'Select project' },
              ...lookups.projects.map(p => ({ value: String(p.id), label: p.project_name || p.project_code || p.name || '' })),
            ]}
          />

          <Input
            label="Expense Date"
            required
            type="date"
            value={form.expense_date}
            onChange={e => setForm({ ...form, expense_date: e.target.value })}
          />

          <Select
            label="Category"
            required
            value={form.expense_category_id}
            onChange={e => setForm({ ...form, expense_category_id: e.target.value })}
            options={[
              { value: '', label: 'Select category' },
              ...lookups.categories.map(c => ({ value: String(c.id), label: c.name || '' })),
            ]}
          />

          <div className="form-field">
            <label>Description</label>
            <textarea
              value={form.description}
              onChange={e => setForm({ ...form, description: e.target.value })}
              style={{
                width: '100%',
                minHeight: '100px',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--border-radius-sm)',
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)',
                padding: '0.75rem',
                fontSize: '0.95rem',
                resize: 'vertical',
              }}
            />
          </div>

          <Input
            label="Bill Reference"
            value={form.bill_reference}
            onChange={e => setForm({ ...form, bill_reference: e.target.value })}
          />

          <Input
            label="Amount"
            required
            type="number"
            step="0.01"
            value={form.amount}
            onChange={e => setForm({ ...form, amount: e.target.value })}
          />

          <Select
            label="Payment Mode"
            required
            value={form.payment_mode_id}
            onChange={e => setForm({ ...form, payment_mode_id: e.target.value })}
            options={[
              { value: '', label: 'Select payment mode' },
              ...lookups.paymentModes.map(pm => ({ value: String(pm.id), label: pm.name || '' })),
            ]}
          />

          <Select
            label="Payment Status"
            required
            value={form.payment_status_id}
            onChange={e => setForm({ ...form, payment_status_id: e.target.value })}
            options={[
              { value: '', label: 'Select payment status' },
              ...lookups.paymentStatuses.map(ps => ({ value: String(ps.id), label: ps.name || '' })),
            ]}
          />

          <div className="form-field">
            <label>Remarks</label>
            <textarea
              value={form.remarks}
              onChange={e => setForm({ ...form, remarks: e.target.value })}
              style={{
                width: '100%',
                minHeight: '100px',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--border-radius-sm)',
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)',
                padding: '0.75rem',
                fontSize: '0.95rem',
                resize: 'vertical',
              }}
            />
          </div>

          <div className="page-actions">
            <button className="btn btn-secondary" type="button" onClick={() => navigate('/expenses')} disabled={saving}>
              Cancel
            </button>
            <button className="btn btn-primary" type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Expense'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ExpenseForm;
