import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

type Movement = {
  id: string;
  asset_number?: string;
  movement_type?: string;
  from_location?: string | null;
  to_location?: string | null;
  moved_at?: string;
  remarks?: string | null;
  details_title?: string | null;
};

type AssetListItem = { id: string; asset_number: string };

export const DailyWorkLog: React.FC = () => {
  const { addToast } = useToast();

  const [loading, setLoading] = useState(false);
  const [movements, setMovements] = useState<Movement[]>([]);
  const [assets, setAssets] = useState<AssetListItem[]>([]);

  // Form state for adding custom work
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [noteText, setNoteText] = useState('');
  const [observedAt, setObservedAt] = useState<string>(new Date().toISOString().slice(0, 16));
  const [saving, setSaving] = useState(false);
  const [localLogs, setLocalLogs] = useState<Array<{ id: string; notes: string; observed_at: string; asset?: string | null }>>([]);
  const [filters, setFilters] = useState<{ module?: string; user_id?: string; project_id?: string }>({});

  const load = async () => {
    setLoading(true);
    try {
      const [actsRes, assetsRes] = await Promise.all([
        api.get('/common/activities', { params: { page_size: 50, module: filters.module, project_id: filters.project_id, user_id: filters.user_id } }),
        api.get('/assets', { params: { page_size: 200 } }),
      ]);
      const items = actsRes.data.items || [];
      // Normalize activities into movements-like items
      const ops = items.map((a: any) => ({ id: a.id, asset_number: a.asset_id || null, movement_type: a.module, moved_at: a.activity_time, remarks: a.description, to_location: a.location_id, details_title: a.title }));
      setMovements(ops);
      setAssets(assetsRes.data.items.map((a: any) => ({ id: a.id, asset_number: a.asset_number })) || []);
    } catch (err) {
      addToast('error', 'Failed to load activities or assets.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const submitNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteText.trim()) return;
    setSaving(true);
    try {
      // Create manual Activity via central API
      const payload: any = {
        activity_time: new Date(observedAt).toISOString(),
        source: 'MANUAL',
        module: 'MANUAL',
        action: 'CREATE',
        title: noteText.split('\n')[0].slice(0, 120),
        description: noteText,
        asset_id: selectedAsset || undefined,
      };
      try {
        await api.post('/common/activities', payload);
        addToast('success', 'Activity recorded.');
        await load();
      } catch (err: any) {
        // fallback to local log if API fails
        const entry = { id: `local-${Date.now()}`, notes: noteText, observed_at: new Date(observedAt).toISOString(), asset: selectedAsset };
        setLocalLogs((s) => [entry, ...s]);
        addToast('warning', 'Saved locally; server save failed.');
      }
      setNoteText('');
    } catch (err: any) {
      addToast('error', err?.response?.data?.detail || 'Could not save work log entry.');
    } finally {
      setSaving(false);
    }
  };

  const combinedItems = [
    // Map movements into a common shape
    ...movements.map((m) => ({ id: m.id, title: m.details_title || m.movement_type || 'Activity', at: m.moved_at || '', details: `${m.asset_number || ''} → ${m.to_location || '-'} ${m.remarks ? `(${m.remarks})` : ''}` })),
    ...localLogs.map((l) => ({ id: l.id, title: 'Manual Log', at: l.observed_at, details: l.notes })),
  ];

  return (
    <div style={{ padding: '1.5rem', display: 'grid', gap: '1rem' }}>
      <div>
        <h2>Activities</h2>
        <p style={{ color: 'var(--text-muted)' }}>A chronological timeline of automatic and manual activities.</p>
      </div>

      <form onSubmit={submitNote} style={{ display: 'grid', gap: '0.5rem', maxWidth: 800 }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <label style={{ minWidth: 110, color: 'var(--text-secondary)' }}>Asset (optional)</label>
          <select value={selectedAsset ?? ''} onChange={(e) => setSelectedAsset(e.target.value || null)} style={{ flex: 1 }}>
            <option value="">-- General / Site-level --</option>
            {assets.map((a) => <option key={a.id} value={a.id}>{a.asset_number}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <label style={{ minWidth: 110, color: 'var(--text-secondary)' }}>When</label>
          <input type="datetime-local" value={observedAt} onChange={(e) => setObservedAt(e.target.value)} />
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
          <label style={{ minWidth: 110, color: 'var(--text-secondary)', marginTop: '6px' }}>Description</label>
          <textarea value={noteText} onChange={(e) => setNoteText(e.target.value)} rows={4} style={{ flex: 1 }} />
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div />
          <button type="submit" disabled={saving} style={{ padding: '0.5rem 0.8rem' }}>{saving ? 'Saving…' : 'Add work log'}</button>
        </div>
      </form>

      <div style={{ maxWidth: 1000 }}>
        <h3>Recent Site Operations</h3>
        {loading ? (
          <div style={{ color: 'var(--text-secondary)' }}>Loading operations…</div>
        ) : combinedItems.length === 0 ? (
          <div style={{ color: 'var(--text-secondary)' }}>No operations recorded yet.</div>
        ) : (
          <div style={{ display: 'grid', gap: '0.6rem' }}>
            {combinedItems.map((it) => (
              <div key={it.id} style={{ borderLeft: '3px solid var(--accent-primary)', paddingLeft: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <strong>{it.title}</strong>
                  <small style={{ color: 'var(--text-secondary)' }}>{it.at ? new Date(it.at).toLocaleString() : ''}</small>
                </div>
                <div style={{ color: 'var(--text-secondary)' }}>{it.details}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
