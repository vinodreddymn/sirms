import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { useToast } from '../../contexts/ToastContext';
import { api } from '../../services/api';
import { expensesApi } from '../../services/expenses';
import type { Expense, Lookup } from './types';

const DetailRow: React.FC<{
  label: string;
  value?: React.ReactNode;
}> = ({ label, value }) => (
  <div className="detail-row">
    <div className="detail-label">{label}</div>
    <div className="detail-value">{value || '-'}</div>
  </div>
);

const formatDate = (value?: string | null) => {
  if (!value) return '-';

  return new Date(value).toLocaleDateString(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
};

const formatCurrency = (value?: string | number | null) => {
  const amount = Number(value);

  if (!Number.isFinite(amount)) return '-';

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
  }).format(amount);
};

export const ExpenseDetails: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [expense, setExpense] = useState<Expense | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [projectName, setProjectName] = useState<string | null>(null);
  const [categoryName, setCategoryName] = useState<string | null>(null);
  const [paymentModeName, setPaymentModeName] = useState<string | null>(null);
  const [paymentStatusName, setPaymentStatusName] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<Array<{ id: string; name: string; url: string }>>([]);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [viewerBlobUrl, setViewerBlobUrl] = useState<string | null>(null);
  const [viewerIsImage, setViewerIsImage] = useState(false);
  const [viewerLoading, setViewerLoading] = useState(false);

  const resolveLookupLabel = (lookup?: Lookup) =>
    lookup?.name ?? lookup?.project_name ?? lookup?.project_code ?? undefined;

  const handleUploadDocument = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !id) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const uploadResponse = await api.post<{ id: string; filename: string; url: string }>('/uploads', formData);
      await expensesApi.uploadAttachment(id, { attachment_id: uploadResponse.data.id });

      setAttachments((current) => [
        ...current,
        {
          id: uploadResponse.data.id,
          name: uploadResponse.data.filename,
          url: resolveBackendUrl(uploadResponse.data.url),
        },
      ]);
      addToast('success', 'Document attached to expense');
    } catch {
      addToast('error', 'Could not upload document');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const parseJwt = (token: string | null) => {
    if (!token) return null;
    try {
      const parts = token.split('.');
      if (parts.length < 2) return null;
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const decoded = atob(payload.padEnd(payload.length + (4 - (payload.length % 4)) % 4, '='));
      return JSON.parse(decoded);
    } catch {
      return null;
    }
  };

  const isAdmin = () => {
    const token = localStorage.getItem('access_token');
    const payload = parseJwt(token);
    return !!(payload && payload.is_admin);
  };

  const getBackendOrigin = () => {
    const base = api.defaults.baseURL ?? window.location.origin;
    try {
      return new URL(base).origin;
    } catch {
      return window.location.origin;
    }
  };

  const resolveBackendUrl = (url: string) => {
    if (!url) return url;
    const normalized = url.trim();
    if (normalized.startsWith('blob:')) return normalized;
    if (normalized.startsWith('http://') || normalized.startsWith('https://')) {
      return normalized;
    }
    const origin = getBackendOrigin();
    if (normalized.startsWith('//')) {
      return `${window.location.protocol}${normalized}`;
    }
    if (normalized.startsWith('/')) {
      return `${origin}${normalized}`;
    }
    if (normalized.startsWith('api/v1')) {
      return `${origin}/${normalized}`;
    }
    return `${origin}/${normalized}`;
  };

  const handleView = async (attachment: { id: string; name: string; url: string }) => {
    const isImage = /\.(png|jpe?g|gif|bmp|webp)(\?|$)/i.test(attachment.name) || /^image\//i.test(attachment.name);
    setViewerIsImage(isImage);
    setViewerOpen(true);
    setViewerLoading(true);
    try {
      if (viewerBlobUrl) {
        try {
          URL.revokeObjectURL(viewerBlobUrl);
        } catch {
          // ignore
        }
        setViewerBlobUrl(null);
      }

      const fileUrl = resolveBackendUrl(attachment.url);
      const token = localStorage.getItem('access_token');
      const headers: Record<string, string> = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      const resp = await fetch(fileUrl, {
        method: 'GET',
        headers,
      });
      if (!resp.ok) {
        const message = await resp.text();
        throw new Error(message || 'Could not load document');
      }
      const blob = await resp.blob();
      const blobUrl = URL.createObjectURL(blob);
      setViewerUrl(blobUrl);
      setViewerBlobUrl(blobUrl);
    } catch (err: any) {
      addToast('error', err.message || 'Could not load document');
      setViewerOpen(false);
    } finally {
      setViewerLoading(false);
    }
  };

  const handleCloseViewer = () => {
    setViewerOpen(false);
    setViewerUrl(null);
    if (viewerBlobUrl) {
      try {
        URL.revokeObjectURL(viewerBlobUrl);
      } catch {
        // ignore
      }
      setViewerBlobUrl(null);
    }
  };

  const handleDeleteAttachment = async (attachmentId: string) => {
    if (!attachmentId) return;
    if (!window.confirm('Delete this document? This action cannot be undone.')) return;
    try {
      await expensesApi.deleteAttachment(attachmentId);
      setAttachments((current) => current.filter((a) => a.id !== attachmentId));
      addToast('success', 'Document deleted');
    } catch (error: any) {
      addToast('error', error.response?.data?.detail || 'Could not delete document');
    }
  };

  useEffect(() => {
    if (!id) return;

    const loadExpense = async () => {
      try {
        const response = await expensesApi.get(id);
        const expenseData = response.data;
        setExpense(expenseData);

        const [attachmentsResponse, lookups] = await Promise.all([
          expensesApi.listAttachments(id),
          Promise.all([
            api.get<{ items: Lookup[] }>('/common/projects', { params: { page_size: 200 } }),
            api.get<{ items: Lookup[] }>('/master/expense-categories', { params: { page_size: 200 } }),
            api.get<{ items: Lookup[] }>('/master/payment-modes', { params: { page_size: 200 } }),
            api.get<{ items: Lookup[] }>('/master/payment-statuses', { params: { page_size: 200 } }),
          ]),
        ]);

        setAttachments(
          (attachmentsResponse.data.items || []).map((attachment: any) => ({
            id: attachment.id,
            name: attachment.filename ?? attachment.file_name ?? attachment.attachment_id,
            url: resolveBackendUrl(attachment.url ?? `/api/v1/uploads/${attachment.attachment_id}/download`),
          })),
        );

        const lookupsData = await Promise.all([
          api.get<{ items: Lookup[] }>('/common/projects', { params: { page_size: 200 } }),
          api.get<{ items: Lookup[] }>('/master/expense-categories', { params: { page_size: 200 } }),
          api.get<{ items: Lookup[] }>('/master/payment-modes', { params: { page_size: 200 } }),
          api.get<{ items: Lookup[] }>('/master/payment-statuses', { params: { page_size: 200 } }),
        ]);

        setProjectName(
          resolveLookupLabel(lookupsData[0].data.items.find((item) => String(item.id) === expenseData.project_id)) ?? null,
        );
        setCategoryName(
          resolveLookupLabel(lookupsData[1].data.items.find((item) => String(item.id) === expenseData.expense_category_id)) ?? null,
        );
        setPaymentModeName(
          resolveLookupLabel(lookupsData[2].data.items.find((item) => String(item.id) === expenseData.payment_mode_id)) ?? null,
        );
        setPaymentStatusName(
          resolveLookupLabel(lookupsData[3].data.items.find((item) => String(item.id) === expenseData.payment_status_id)) ?? null,
        );
      } catch {
        addToast('error', 'Could not load expense.');
      } finally {
        setLoading(false);
      }
    };

    void loadExpense();
  }, [id, addToast]);

  if (loading) {
    return (
      <div className="page-loading">
        Loading expense details...
      </div>
    );
  }

  if (!expense) {
    return (
      <div className="page-error">
        Expense not found.
      </div>
    );
  }

  return (
    <div className="expense-details-page" style={{ display: 'grid', gap: '1.25rem' }}>
      <div className="page-header">
        <div>
          <button
            className="btn btn-secondary"
            onClick={() => navigate('/expenses')}
          >
            ← Back
          </button>

          <h1>{expense.expense_number ?? expense.expense_no ?? 'Expense'}</h1>

          <p className="page-subtitle">
            {projectName ?? expense.project_id}
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', alignItems: 'flex-end' }}>
          <span className="badge">
            {paymentStatusName ?? expense.payment_status_name ??
              expense.payment_status_id ??
              'Unknown'}
          </span>
          <div className="page-actions" style={{ justifyContent: 'flex-end', margin: 0 }}>
            <button
              className="btn btn-secondary"
              onClick={() => window.print()}
            >
              Print
            </button>
            <button
              className="btn btn-primary"
              onClick={() => navigate(`/expenses/${id}/edit`)}
            >
              Edit Expense
            </button>
          </div>
        </div>
      </div>

      <div className="details-grid" style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))' }}>
        <section className="card">
          <h3>Expense Information</h3>

          <DetailRow
            label="Expense Date"
            value={formatDate(expense.expense_date)}
          />

          <DetailRow
            label="Project"
            value={projectName ?? expense.project_id}
          />

          <DetailRow
            label="Category"
            value={categoryName ?? expense.expense_category_name ?? expense.expense_category_id}
          />

          <DetailRow
            label="Bill Reference"
            value={expense.bill_reference}
          />
        </section>

        <section className="card">
          <h3>Financial Details</h3>

          <DetailRow
            label="Amount"
            value={formatCurrency(expense.amount)}
          />

          <DetailRow
            label="Payment Mode"
            value={paymentModeName ?? expense.payment_mode_name ?? expense.payment_mode_id}
          />

          <DetailRow
            label="Payment Status"
            value={paymentStatusName ?? expense.payment_status_name ?? expense.payment_status_id}
          />
        </section>
      </div>

      <section className="card">
        <h3>Description</h3>
        <p>{expense.description || '-'}</p>
      </section>

      <section className="card">
        <h3>Remarks</h3>
        <p>{expense.remarks || '-'}</p>
      </section>

      <section className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <h3 style={{ margin: 0 }}>Related Documents</h3>
          <label className="btn btn-primary" style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center' }}>
            {uploading ? 'Uploading...' : 'Upload Document'}
            <input accept="application/pdf,image/*" type="file" onChange={handleUploadDocument} style={{ display: 'none' }} disabled={uploading} />
          </label>
        </div>

        {attachments.length ? (
          <ul style={{ marginTop: '1rem', paddingLeft: '1.1rem', display: 'grid', gap: '0.5rem' }}>
            {attachments.map((attachment) => (
              <li key={attachment.id} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button type="button" onClick={() => handleView(attachment)} style={{ background: 'none', border: 'none', padding: 0, color: 'var(--accent-primary)', cursor: 'pointer' }}>
                  {attachment.name}
                </button>
                {isAdmin() && (
                  <button type="button" className="btn btn-link" onClick={() => handleDeleteAttachment(attachment.id)} style={{ marginLeft: 'auto' }}>
                    Delete
                  </button>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>No documents attached yet.</p>
        )}
      </section>
      {viewerOpen && (
        <div className="modal-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }} onClick={handleCloseViewer}>
          <div className="modal-content" style={{ background: 'white', maxWidth: '90%', maxHeight: '90%', width: viewerIsImage ? 'auto' : '80%', height: viewerIsImage ? 'auto' : '90%', padding: '0.5rem', position: 'relative' }} onClick={(e) => e.stopPropagation()}>
            <button onClick={handleCloseViewer} style={{ position: 'absolute', right: 8, top: 8 }} className="btn btn-secondary">Close</button>
            <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {viewerLoading ? (
                <div>Loading document...</div>
              ) : viewerUrl ? (
                viewerIsImage ? (
                  // eslint-disable-next-line jsx-a11y/img-redundant-alt
                  <img src={viewerUrl} alt={viewerUrl ?? 'document'} style={{ maxWidth: '100%', maxHeight: '80vh' }} />
                ) : (
                  <iframe src={viewerUrl ?? ''} title="Document Viewer" style={{ width: '100%', height: '80vh', border: 'none' }} />
                )
              ) : (
                <div>Unable to load document</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpenseDetails;