import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, Plus, RefreshCw, Search } from 'lucide-react';

import { DataTable } from '../../components/DataTable';
import type { Column } from '../../components/DataTable';
import { Input, Select } from '../../components/FormControls';
import { useToast } from '../../contexts/ToastContext';
import { getDispatches } from './api';
import type { DispatchListItem, PaginatedResponse } from './types';

const formatDate = (value?: string | null) => {
  if (!value) return '-';
  return new Date(value).toLocaleDateString();
};

const formatBadge = (label: string) => {
  const normalized = label.toLowerCase();
  let palette = { bg: 'rgba(148,163,184,0.18)', color: '#cbd5e1' };
  
  if (normalized === 'draft') palette = { bg: 'rgba(148,163,184,0.18)', color: '#cbd5e1' };
  if (normalized === 'dispatched') palette = { bg: 'rgba(59,130,246,0.18)', color: '#93c5fd' };
  if (normalized === 'partially returned') palette = { bg: 'rgba(245,158,11,0.18)', color: '#fcd34d' };
  if (normalized === 'closed') palette = { bg: 'rgba(34,197,94,0.18)', color: '#86efac' };
  if (normalized === 'cancelled') palette = { bg: 'rgba(239,68,68,0.18)', color: '#fca5a5' };

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0.35rem 0.75rem',
        borderRadius: '999px',
        background: palette.bg,
        color: palette.color,
        fontWeight: 700,
        fontSize: '0.75rem',
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </span>
  );
};

export const DispatchList: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<PaginatedResponse<DispatchListItem> | null>(null);

  const loadList = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getDispatches({ page, page_size: pageSize, search: search || undefined });
      setData(response);
    } catch {
      addToast('error', 'Unable to load dispatches.');
    } finally {
      setLoading(false);
    }
  }, [addToast, page, pageSize, search]);

  useEffect(() => {
    loadList();
  }, [loadList]);

  const columns: Column<DispatchListItem>[] = [
    {
      header: 'Dispatch No',
      accessor: 'dispatch_no',
      cell: (value, row) => (
        <span
          style={{ color: 'var(--primary)', cursor: 'pointer', fontWeight: 600 }}
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/dispatches/${row.id}`);
          }}
        >
          {typeof value === 'string' ? value : ''}
        </span>
      ),
    },
    { header: 'Challan No', accessor: 'delivery_challan_no', cell: (value) => (value ? String(value) : '-') },
    { header: 'Date', accessor: 'dispatch_date', cell: (value) => formatDate(typeof value === 'string' ? value : undefined) },
    { header: 'Purpose', accessor: 'purpose' },
    { header: 'Vendor', accessor: 'vendor_name', cell: (value) => (value ? String(value) : '-') },
    { header: 'Status', accessor: 'status', cell: (value) => formatBadge(typeof value === 'string' ? value : String(value)) },
    { header: 'Courier', accessor: 'courier_name', cell: (value) => (value ? String(value) : '-') },
    { header: 'Tracking', accessor: 'tracking_number', cell: (value) => (value ? String(value) : '-') },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Package size={28} color="var(--primary)" />
            Dispatches & Challans
          </h1>
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>Manage material dispatches and delivery challans</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn btn-secondary" onClick={loadList} title="Refresh">
            <RefreshCw size={18} />
          </button>
          <button className="btn btn-primary" onClick={() => navigate('/dispatches/new')}>
            <Plus size={18} />
            <span>New Dispatch</span>
          </button>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
          <div style={{ minWidth: '300px' }}>
            <Input
              icon={<Search size={18} />}
              placeholder="Search by dispatch no..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') { setPage(1); loadList(); } }}
            />
          </div>
        </div>

        <DataTable
          columns={columns}
          data={data?.items || []}
          isLoading={loading}
          onRowClick={(row) => navigate(`/dispatches/${row.id}`)}
          pagination={data ? {
            page: data.page,
            pageSize: data.page_size,
            totalItems: data.total,
            totalPages: data.pages,
            onPageChange: setPage,
            onPageSizeChange: setPageSize,
          } : undefined}
          emptyMessage={
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <Package size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
              <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>No dispatches found</p>
              <p style={{ margin: 0, fontSize: '0.875rem' }}>Adjust your search or create a new dispatch</p>
            </div>
          }
        />
      </div>
    </div>
  );
};
