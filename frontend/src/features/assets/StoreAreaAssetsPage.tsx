import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, RefreshCw, Search } from 'lucide-react';

import { DataTable } from '../../components/DataTable';
import type { Column } from '../../components/DataTable';
import { Input } from '../../components/FormControls';
import { useToast } from '../../contexts/ToastContext';
import { api } from '../../services/api';
import type { AssetListItem, PaginatedResponse } from './types';

const formatBadge = (label?: string | null) => {
  if (!label) return '-';
  const normalized = label.toLowerCase();
  const palette = normalized.includes('repair')
    ? { bg: 'rgba(245,158,11,0.18)', color: '#fcd34d' }
    : normalized.includes('retired')
      ? { bg: 'rgba(239,68,68,0.18)', color: '#fca5a5' }
      : { bg: 'rgba(34,197,94,0.18)', color: '#86efac' };

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

export const StoreAreaAssetsPage: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [assets, setAssets] = useState<AssetListItem[]>([]);

  const loadAssets = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get<PaginatedResponse<AssetListItem>>('/assets', {
        params: {
          page_size: 200,
          search: search || undefined,
          location_type_code: 'STORE',
        },
      });
      setAssets(response.data.items || []);
    } catch {
      addToast('error', 'Unable to load store-area assets.');
    } finally {
      setLoading(false);
    }
  }, [addToast, search]);

  useEffect(() => {
    void loadAssets();
  }, [loadAssets]);

  const columns: Column<AssetListItem>[] = [
    {
      header: 'Asset No',
      accessor: 'asset_number',
      width: '140px',
    },
    {
      header: 'Category',
      accessor: 'category',
      width: '180px',
    },
    {
      header: 'Current Location',
      accessor: (row) => row.current_location || '-',
      width: '220px',
    },
    {
      header: 'Status',
      accessor: (row) => formatBadge(row.status),
      width: '140px',
    },
    {
      header: 'Condition',
      accessor: (row) => row.condition || '-',
      width: '140px',
    },
    {
      header: 'Serial No',
      accessor: (row) => row.serial_number || '-',
      width: '180px',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Package size={28} color="var(--primary)" />
            Store Area Assets
          </h1>
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>Assets currently assigned to store-area locations.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={() => void loadAssets()} title="Refresh">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <div style={{ marginBottom: '1rem', maxWidth: '360px' }}>
          <Input
            icon={<Search size={18} />}
            placeholder="Search by asset no or location"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                void loadAssets();
              }
            }}
          />
        </div>

        <DataTable
          columns={columns}
          data={assets}
          loading={loading}
          onRowClick={(row) => navigate(`/assets/${row.id}`)}
          emptyMessage="No assets found in store areas."
        />
      </div>
    </div>
  );
};
