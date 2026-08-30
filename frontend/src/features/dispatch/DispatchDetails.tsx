import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Edit2, FileText, Package, Send, CheckCircle } from 'lucide-react';

import { useToast } from '../../contexts/ToastContext';
import { getDispatchDetails, submitDispatch, receiveDispatchItem } from './api';
import { api } from '../../services/api';
import type { DispatchDetails as DispatchDetailsType, DispatchItemListItem, ReceiveItemPayload } from './types';
import { ReceiveItemDialog } from './ReceiveItemDialog';
import { Panel } from '../../components/Panel';
import { generateDispatchChallanPdf } from './challanPdf';

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

export const DispatchDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DispatchDetailsType | null>(null);
  
  const [receivingItem, setReceivingItem] = useState<DispatchItemListItem | null>(null);

  const loadData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const response = await getDispatchDetails(id);
      setData(response);
    } catch {
      addToast('error', 'Failed to load dispatch details');
      navigate('/dispatches');
    } finally {
      setLoading(false);
    }
  }, [id, addToast, navigate]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSubmit = async () => {
    if (!id || !window.confirm('Are you sure you want to submit this dispatch? This will generate a Delivery Challan and change asset statuses.')) return;
    
    try {
      await submitDispatch(id);
      addToast('success', 'Dispatch submitted successfully');
      loadData();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      addToast('error', detail || 'Failed to submit dispatch');
    }
  };

  const handlePrintChallan = () => {
    if (!data) return;

    generateDispatchChallanPdf(data);
    addToast('success', 'Challan PDF generated');
  };

  const handleReceiveItem = async (payload: ReceiveItemPayload) => {
    if (!id || !receivingItem) return;
    
    try {
      const sanitizedPayload = {
        ...payload,
        to_location_id: payload.to_location_id || null,
        repair_cost: payload.repair_cost || null,
        remarks: payload.remarks || null,
      };
      const item = await receiveDispatchItem(id, receivingItem.id, sanitizedPayload);
      // If this receive updated an asset, fetch the updated asset and broadcast an event
      // Always emit an asset-updated event with the affected asset id when present
      if (item) {
        const affectedAssetId = item.asset_id || null;
        try {
          if (affectedAssetId) {
            const resp = await api.get(`/assets/${affectedAssetId}`);
            if (resp && resp.data) {
              window.dispatchEvent(new CustomEvent('asset-updated', { detail: { id: resp.data.id } }));
            } else {
              window.dispatchEvent(new CustomEvent('asset-updated', { detail: { id: affectedAssetId } }));
            }
          } else {
            window.dispatchEvent(new CustomEvent('asset-updated', { detail: {} }));
          }
        } catch (err) {
          // non-fatal; still notify with id when possible
          window.dispatchEvent(new CustomEvent('asset-updated', { detail: { id: affectedAssetId } }));
        }
      }
      addToast('success', 'Item received successfully');
      loadData();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      addToast('error', detail || 'Failed to receive item');
    }
  };

  if (loading || !data) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <button className="btn btn-secondary" onClick={() => navigate('/dispatches')} style={{ padding: '0.5rem' }}>
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Package size={28} color="var(--primary)" />
            Dispatch: {data.dispatch_no}
            {formatBadge(data.status)}
          </h1>
          {data.delivery_challan_no && (
            <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-muted)' }}>Challan: {data.delivery_challan_no}</p>
          )}
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '1rem' }}>
          {data.status === 'Draft' && (
            <>
              <button className="btn btn-secondary" onClick={() => navigate(`/dispatches/${id}/edit`)}>
                <Edit2 size={18} /> Edit
              </button>
              <button className="btn btn-primary" onClick={handleSubmit}>
                <Send size={18} /> Submit
              </button>
            </>
          )}
          {['Dispatched', 'Partially Returned', 'Closed'].includes(data.status) && (
            <button className="btn btn-secondary" onClick={handlePrintChallan}>
              <FileText size={18} /> Print Challan
            </button>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <Panel title="Information">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Date</p>
              <p style={{ margin: 0, fontWeight: 500 }}>{formatDate(data.dispatch_date)}</p>
            </div>
            <div>
              <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Purpose</p>
              <p style={{ margin: 0, fontWeight: 500 }}>{data.purpose}</p>
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Vendor / Service Center</p>
              <p style={{ margin: 0, fontWeight: 500 }}>{data.vendor_name || '-'}</p>
            </div>
          </div>
        </Panel>

        <Panel title="Shipping Details">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Courier Name</p>
              <p style={{ margin: 0, fontWeight: 500 }}>{data.courier_name || '-'}</p>
            </div>
            <div>
              <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Tracking Number</p>
              <p style={{ margin: 0, fontWeight: 500 }}>{data.tracking_number || '-'}</p>
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Remarks</p>
              <p style={{ margin: 0, fontWeight: 500 }}>{data.remarks || '-'}</p>
            </div>
          </div>
        </Panel>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, margin: '0 0 1rem 0' }}>Dispatch Items</h2>
        
        {data.items.length === 0 ? (
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>No items found.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.75rem', fontWeight: 500 }}>Type</th>
                <th style={{ padding: '0.75rem', fontWeight: 500 }}>Asset / Component</th>
                <th style={{ padding: '0.75rem', fontWeight: 500 }}>Category</th>
                <th style={{ padding: '0.75rem', fontWeight: 500 }}>Subcategory</th>
                <th style={{ padding: '0.75rem', fontWeight: 500 }}>Serial</th>
                <th style={{ padding: '0.75rem', fontWeight: 500 }}>Qty</th>
                <th style={{ padding: '0.75rem', fontWeight: 500 }}>Status</th>
                <th style={{ padding: '0.75rem', fontWeight: 500 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem' }}>{item.dispatch_type}</td>
                  <td style={{ padding: '0.75rem' }}>
                    {item.dispatch_type === 'Asset' 
                      ? <span style={{ fontWeight: 500 }}>{item.asset_number || '-'}</span>
                      : <span style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                          <span style={{ fontWeight: 500 }}>{item.component_name}</span>
                          <small style={{ color: 'var(--text-muted)' }}>Parent asset: {item.asset_number || '-'}</small>
                        </span>
                    }
                  </td>
                  <td style={{ padding: '0.75rem' }}>{item.asset_category || '-'}</td>
                  <td style={{ padding: '0.75rem' }}>{item.asset_subcategory || '-'}</td>
                  <td style={{ padding: '0.75rem' }}>{item.asset_serial_number || '-'}</td>
                  <td style={{ padding: '0.75rem' }}>{item.quantity}</td>
                  <td style={{ padding: '0.75rem' }}>
                    <span style={{ 
                      display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                      color: item.status === 'Returned' ? 'var(--success)' : 'var(--warning)',
                      fontWeight: 600, fontSize: '0.875rem'
                    }}>
                      {item.status === 'Returned' ? <CheckCircle size={14} /> : null}
                      {item.status}
                    </span>
                    {item.status === 'Returned' && item.result && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                        {item.result} on {formatDate(item.return_date)}
                      </div>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {['Dispatched', 'Partially Returned'].includes(data.status) && item.status === 'Out' && (
                      <button 
                        className="btn btn-secondary btn-sm"
                        onClick={() => setReceivingItem(item)}
                      >
                        Receive
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {receivingItem && (
        <ReceiveItemDialog
          isOpen={true}
          onClose={() => setReceivingItem(null)}
          onSubmit={handleReceiveItem}
          itemName={receivingItem.dispatch_type === 'Asset' ? (receivingItem.asset_number || 'Asset') : (receivingItem.component_name || 'Component')}
        />
      )}
    </div>
  );
};
