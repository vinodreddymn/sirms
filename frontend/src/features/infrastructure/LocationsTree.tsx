import React, { useEffect, useState, useCallback } from 'react';
import { api } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { Modal } from '../../components/Modal';
import { Input, Select } from '../../components/FormControls';
import {
  ChevronRight, ChevronDown, MapPin, FolderOpen, Folder,
  Plus, Edit2, Layers, Map, Building2, LayoutGrid, Trash2, AlertCircle,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// ─── Types ────────────────────────────────────────────────────────────────────

interface LocationNode {
  id: string;
  code: string;
  name: string;
  location_type_id: number;
  location_type_name: string;
  parent_location_id: string | null;
  latitude: number | null;
  longitude: number | null;
  remarks: string | null;
  children: LocationNode[];
}

interface LocationPosition {
  id: string;
  location_id: string;
  position_type_id: number;
  position_number: string;
  maximum_capacity: number;
  remarks: string | null;
}

interface LookupOption { id: number; code: string; name: string; }

interface PositionTemplate { id: number; code: string; name: string; node_count: number; }

interface PositionPreview {
  position_type_id: number;
  position_type_name: string;
  position_number: string;
  maximum_capacity: number;
  node_order: number;
  remarks: string | null;
  // For override tracking
  _edited?: boolean;
}



// ─── Icon helper ──────────────────────────────────────────────────────────────

const LocationIcon: React.FC<{ typeName: string; size?: number; color?: string }> = ({ typeName, size = 16, color }) => {
  const t = typeName.toUpperCase();
  const c = color || 'var(--accent-primary)';
  if (t.includes('BUILDING')) return <Building2 size={size} color={c} />;
  if (t.includes('FLOOR') || t.includes('ROOM')) return <LayoutGrid size={size} color={c} />;
  if (t.includes('POWER') || t.includes('POLE') || t.includes('TOWER')) return <Layers size={size} color={c} />;
  return <MapPin size={size} color={c} />;
};

const countNodes = (nodes: LocationNode[]): number =>
  nodes.reduce((sum, n) => sum + 1 + countNodes(n.children), 0);

// ─── Position Sub-panel ───────────────────────────────────────────────────────

const PositionPanel: React.FC<{
  locationId: string;
  locationName: string;
  positionTypes: LookupOption[];
  positionTemplates: PositionTemplate[];
}> = ({ locationId, locationName, positionTypes, positionTemplates }) => {
  const [positions, setPositions] = useState<LocationPosition[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({ position_type_id: 0, position_number: '', maximum_capacity: 1, remarks: '' });
  const { addToast } = useToast();

  // Template apply state
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | ''>('');
  const [previewPositions, setPreviewPositions] = useState<PositionPreview[]>([]);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [templateSaving, setTemplateSaving] = useState(false);

  const fetchPositions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/infrastructure/locations/${locationId}/positions`);
      setPositions(res.data.items ?? []);
    } catch {
      addToast('error', 'Failed to load positions');
    } finally {
      setLoading(false);
    }
  }, [locationId, addToast]);

  useEffect(() => { fetchPositions(); }, [fetchPositions]);

  const openAdd = () => {
    setEditingId(null);
    setFormData({ position_type_id: positionTypes[0]?.id ?? 0, position_number: '', maximum_capacity: 1, remarks: '' });
    setIsModalOpen(true);
  };

  const openEdit = (pos: LocationPosition) => {
    setEditingId(pos.id);
    setFormData({ position_type_id: pos.position_type_id, position_number: pos.position_number, maximum_capacity: pos.maximum_capacity, remarks: pos.remarks ?? '' });
    setIsModalOpen(true);
  };

  const openApplyTemplate = () => {
    setSelectedTemplateId('');
    setPreviewPositions([]);
    setIsTemplateModalOpen(true);
  };

  const handleTemplateChange = async (templateId: number | '') => {
    setSelectedTemplateId(templateId);
    setPreviewPositions([]);
    if (!templateId) return;
    setPreviewLoading(true);
    try {
      const res = await api.get(`/infrastructure/position-templates/${templateId}/preview`);
      setPreviewPositions((res.data as PositionPreview[]).map(p => ({ ...p, _edited: false })));
    } catch {
      addToast('error', 'Failed to load template preview.');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleApplyTemplate = async () => {
    if (previewPositions.length === 0) {
      addToast('error', 'No positions to apply.');
      return;
    }
    setTemplateSaving(true);
    try {
      await Promise.all(
        previewPositions.map(pos =>
          api.post(`/infrastructure/locations/${locationId}/positions`, {
            location_id: locationId,
            position_type_id: Number(pos.position_type_id),
            position_number: pos.position_number,
            maximum_capacity: Number(pos.maximum_capacity),
            remarks: pos.remarks || null,
          }),
        ),
      );
      addToast('success', `Successfully applied template with ${previewPositions.length} positions.`);
      setIsTemplateModalOpen(false);
      fetchPositions();
    } catch {
      addToast('error', 'Failed to apply template positions.');
    } finally {
      setTemplateSaving(false);
    }
  };

  const handleSave = async () => {
    if (!formData.position_number) { addToast('error', 'Position number is required.'); return; }
    if (!formData.position_type_id) { addToast('error', 'Position type is required.'); return; }
    setSaving(true);
    try {
      const payload = { ...formData, location_id: locationId, position_type_id: Number(formData.position_type_id), maximum_capacity: Number(formData.maximum_capacity) };
      if (editingId) {
        await api.put(`/infrastructure/positions/${editingId}`, payload);
        addToast('success', 'Position updated.');
      } else {
        await api.post(`/infrastructure/locations/${locationId}/positions`, payload);
        addToast('success', 'Position added.');
      }
      setIsModalOpen(false);
      fetchPositions();
    } catch {
      addToast('error', 'Failed to save position.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ marginTop: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
          Positions — {locationName}
        </span>
        <div style={{ display: 'flex', gap: '0.4rem' }}>
          <button className="btn btn-secondary" onClick={openApplyTemplate} style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem', gap: '0.3rem' }}>
            <Layers size={14} /> Apply Template
          </button>
          <button className="btn btn-primary" onClick={openAdd} style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem', gap: '0.3rem' }}>
            <Plus size={14} /> Add Position
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Loading positions...</div>
      ) : positions.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', padding: '1rem', border: '1px dashed var(--border-color)', borderRadius: 'var(--border-radius-md)' }}>
          No positions defined for this location.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {positions.map(pos => (
            <div key={pos.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(255,255,255,0.04)', borderRadius: 'var(--border-radius-sm)', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <LayoutGrid size={14} color="var(--accent-secondary)" />
                <span style={{ fontWeight: 500, fontSize: '0.85rem' }}>{pos.position_number}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'var(--bg-primary)', padding: '0 6px', borderRadius: '10px' }}>
                  Capacity: {pos.maximum_capacity}
                </span>
              </div>
              <button onClick={() => openEdit(pos)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-primary)', display: 'flex', padding: '0.2rem' }}>
                <Edit2 size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? 'Edit Position' : 'Add Position'}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsModalOpen(false)} disabled={saving}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
          </>
        }
      >
        <Select
          label="Position Type"
          value={formData.position_type_id}
          onChange={e => setFormData({ ...formData, position_type_id: Number(e.target.value) })}
          options={positionTypes.map(pt => ({ value: pt.id, label: pt.name }))}
        />
        <Input label="Position Number" value={formData.position_number} onChange={e => setFormData({ ...formData, position_number: e.target.value })} placeholder="e.g. CAM-01" />
        <Input label="Maximum Capacity" type="number" value={formData.maximum_capacity} onChange={e => setFormData({ ...formData, maximum_capacity: parseInt(e.target.value) || 1 })} />
        <Input label="Remarks" value={formData.remarks} onChange={e => setFormData({ ...formData, remarks: e.target.value })} placeholder="Optional notes..." />
      </Modal>

      {/* ── Apply Template Modal ── */}
      <Modal
        isOpen={isTemplateModalOpen}
        onClose={() => setIsTemplateModalOpen(false)}
        title={`Apply Template to ${locationName}`}
        maxWidth="600px"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsTemplateModalOpen(false)} disabled={templateSaving}>Cancel</button>
            <button className="btn btn-primary" onClick={handleApplyTemplate} disabled={templateSaving}>
              {templateSaving ? 'Applying...' : `Apply ${previewPositions.length > 0 ? `${previewPositions.length} positions` : ''}`}
            </button>
          </>
        }
      >
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem' }}>
            Select Position Template
          </label>
          <select
            value={selectedTemplateId}
            onChange={e => handleTemplateChange(e.target.value ? Number(e.target.value) : '')}
            style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '0.625rem 1rem', borderRadius: 'var(--border-radius-md)', outline: 'none', width: '100%', cursor: 'pointer', marginBottom: '0.75rem' }}
          >
            <option value="">— Select a template —</option>
            {positionTemplates.map(t => (
              <option key={t.id} value={t.id}>{t.name} ({t.node_count} positions)</option>
            ))}
          </select>
        </div>

        {selectedTemplateId !== '' && (
          <div>
            {previewLoading ? (
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', padding: '0.5rem 0' }}>Loading positions...</div>
            ) : (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Positions to be added ({previewPositions.length})
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      const newPos: PositionPreview = {
                        position_type_id: positionTypes[0]?.id ?? 0,
                        position_type_name: positionTypes[0]?.name ?? '',
                        position_number: '',
                        maximum_capacity: 1,
                        node_order: previewPositions.length + 1,
                        remarks: null,
                        _edited: true,
                      };
                      setPreviewPositions([...previewPositions, newPos]);
                    }}
                    style={{ background: 'none', border: '1px solid var(--border-color)', color: 'var(--accent-primary)', padding: '0.2rem 0.6rem', borderRadius: 'var(--border-radius-sm)', cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  >
                    <Plus size={12} /> Add Row
                  </button>
                </div>
                <PositionPreviewTable
                  positions={previewPositions}
                  positionTypes={positionTypes}
                  onChange={setPreviewPositions}
                />
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

// ─── Detail Panel ──────────────────────────────────────────────────────────────

const DetailPanel: React.FC<{
  node: LocationNode;
  positionTypes: LookupOption[];
  positionTemplates: PositionTemplate[];
  onEdit: (node: LocationNode) => void;
}> = ({ node, positionTypes, positionTemplates, onEdit }) => {
  return (
    <motion.div
      key={node.id}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.2 }}
      className="glass-panel"
      style={{ padding: '1.5rem', height: 'fit-content', position: 'sticky', top: '1rem' }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 40, height: 40, borderRadius: '10px', background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <LocationIcon typeName={node.location_type_name} size={20} color="white" />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{node.name}</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{node.code}</span>
          </div>
        </div>
        <button onClick={() => onEdit(node)} className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', gap: '0.3rem' }}>
          <Edit2 size={14} /> Edit
        </button>
      </div>

      {/* Info Fields */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <InfoRow label="Type" value={node.location_type_name} />
        <InfoRow label="Children" value={String(node.children.length)} />
        {node.latitude != null && <InfoRow label="Latitude" value={String(node.latitude)} />}
        {node.longitude != null && <InfoRow label="Longitude" value={String(node.longitude)} />}
        {node.remarks && <InfoRow label="Remarks" value={node.remarks} />}
      </div>

      <div style={{ height: '1px', background: 'var(--border-color)', margin: '1.25rem 0' }} />

      {/* Positions */}
      <PositionPanel
        locationId={node.id}
        locationName={node.name}
        positionTypes={positionTypes}
        positionTemplates={positionTemplates}
      />
    </motion.div>
  );
};

const InfoRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', minWidth: 90 }}>{label}</span>
    <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)', textAlign: 'right', wordBreak: 'break-word' }}>{value}</span>
  </div>
);

// ─── Tree Node ─────────────────────────────────────────────────────────────────

const TreeNode: React.FC<{
  node: LocationNode;
  level: number;
  selectedId: string | null;
  onSelect: (node: LocationNode) => void;
  onAddChild: (parent: LocationNode) => void;
}> = ({ node, level, selectedId, onSelect, onAddChild }) => {
  const [expanded, setExpanded] = useState(level === 0);
  const isSelected = selectedId === node.id;
  const hasChildren = node.children.length > 0;

  return (
    <div>
      <div
        style={{
          display: 'flex', alignItems: 'center', gap: '0.4rem',
          padding: '0.45rem 0.6rem',
          marginLeft: `${level * 18}px`,
          borderRadius: 'var(--border-radius-sm)',
          cursor: 'pointer',
          background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
          border: isSelected ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
          transition: 'all 0.15s',
        }}
        onMouseEnter={e => { if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.04)'; }}
        onMouseLeave={e => { if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = 'transparent'; }}
        onClick={() => onSelect(node)}
      >
        {/* Expand toggle */}
        <span onClick={e => { e.stopPropagation(); setExpanded(v => !v); }} style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)', flexShrink: 0 }}>
          {hasChildren ? (expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />) : <span style={{ width: 14 }} />}
        </span>

        {/* Icon */}
        <span style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
          {hasChildren && expanded ? <FolderOpen size={15} color="var(--accent-primary)" /> : hasChildren ? <Folder size={15} color="var(--accent-primary)" /> : <LocationIcon typeName={node.location_type_name} size={15} />}
        </span>

        {/* Name & code */}
        <span style={{ fontWeight: isSelected ? 600 : 400, fontSize: '0.875rem', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{node.name}</span>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', background: 'var(--bg-primary)', padding: '0 5px', borderRadius: '8px', flexShrink: 0 }}>{node.code}</span>

        {/* Add child button */}
        <button
          onClick={e => { e.stopPropagation(); onAddChild(node); }}
          title="Add child location"
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', padding: '2px', borderRadius: '4px', flexShrink: 0, opacity: 0.6 }}
          onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.opacity = '1'; (e.currentTarget as HTMLButtonElement).style.color = 'var(--accent-primary)'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.opacity = '0.6'; (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)'; }}
        >
          <Plus size={12} />
        </button>
      </div>

      <AnimatePresence>
        {expanded && hasChildren && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.15 }}>
            {node.children.map(child => (
              <TreeNode key={child.id} node={child} level={level + 1} selectedId={selectedId} onSelect={onSelect} onAddChild={onAddChild} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ─── Position Preview/Override Table ─────────────────────────────────────────

const PositionPreviewTable: React.FC<{
  positions: PositionPreview[];
  positionTypes: LookupOption[];
  onChange: (positions: PositionPreview[]) => void;
}> = ({ positions, positionTypes, onChange }) => {
  const update = (idx: number, field: keyof PositionPreview, value: string | number | null) => {
    const next = positions.map((p, i) => i === idx ? { ...p, [field]: value, _edited: true } : p);
    onChange(next);
  };
  const remove = (idx: number) => onChange(positions.filter((_, i) => i !== idx));

  if (positions.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '0.75rem', border: '1px dashed var(--border-color)', borderRadius: 'var(--border-radius-md)', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
        <AlertCircle size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: 'middle' }} />
        No positions in this template.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
      {/* Column headers */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 130px 80px 1fr 28px', gap: '0.4rem', padding: '0 0.1rem' }}>
        {['Position Type', 'Number', 'Capacity', 'Remarks', ''].map(h => (
          <span key={h} style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>{h}</span>
        ))}
      </div>

      {positions.map((pos, idx) => (
        <div key={idx} style={{
          display: 'grid', gridTemplateColumns: '1fr 130px 80px 1fr 28px',
          gap: '0.4rem', alignItems: 'center',
          padding: '0.4rem 0.5rem',
          borderRadius: 'var(--border-radius-sm)',
          border: `1px solid ${pos._edited ? 'var(--accent-primary)' : 'var(--border-color)'}`,
          background: pos._edited ? 'rgba(99,102,241,0.05)' : 'rgba(255,255,255,0.03)',
        }}>
          <select
            value={pos.position_type_id}
            onChange={e => update(idx, 'position_type_id', Number(e.target.value))}
            style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '0.3rem 0.5rem', borderRadius: 'var(--border-radius-sm)', fontSize: '0.78rem', width: '100%' }}
          >
            {positionTypes.map(pt => <option key={pt.id} value={pt.id}>{pt.name}</option>)}
          </select>
          <input
            value={pos.position_number}
            onChange={e => update(idx, 'position_number', e.target.value)}
            style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '0.3rem 0.5rem', borderRadius: 'var(--border-radius-sm)', fontSize: '0.78rem', width: '100%' }}
          />
          <input
            type="number"
            value={pos.maximum_capacity}
            onChange={e => update(idx, 'maximum_capacity', parseInt(e.target.value) || 1)}
            style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '0.3rem 0.5rem', borderRadius: 'var(--border-radius-sm)', fontSize: '0.78rem', width: '100%' }}
          />
          <input
            value={pos.remarks ?? ''}
            onChange={e => update(idx, 'remarks', e.target.value || null)}
            placeholder="Remarks"
            style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '0.3rem 0.5rem', borderRadius: 'var(--border-radius-sm)', fontSize: '0.78rem', width: '100%' }}
          />
          <button
            onClick={() => remove(idx)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--danger)', display: 'flex', padding: 0, justifyContent: 'center' }}
            title="Remove this position"
          >
            <Trash2 size={14} />
          </button>
        </div>
      ))}

      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: '0.25rem 0 0', fontStyle: 'italic' }}>
        You can edit or remove individual positions before saving.
      </p>
    </div>
  );
};

// ─── Main Component ────────────────────────────────────────────────────────────

const defaultFormData = {
  project_id: '', code: '', name: '', location_type_id: 1,
  parent_location_id: '' as string | null,
  latitude: '' as string, longitude: '' as string, remarks: '',
};

export const LocationsTree: React.FC = () => {
  const [treeData, setTreeData] = useState<LocationNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<LocationNode | null>(null);
  const [locationTypes, setLocationTypes] = useState<LookupOption[]>([]);
  const [positionTypes, setPositionTypes] = useState<LookupOption[]>([]);
  const [positionTemplates, setPositionTemplates] = useState<PositionTemplate[]>([]);
  const [projects, setProjects] = useState<{ id: string; name: string; }[]>([]);

  // Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState(defaultFormData);
  const [saving, setSaving] = useState(false);

  // Template selection & preview
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | ''>('');
  const [previewPositions, setPreviewPositions] = useState<PositionPreview[]>([]);
  const [previewLoading, setPreviewLoading] = useState(false);

  const { addToast } = useToast();

  const flattenTree = (nodes: LocationNode[]): LocationNode[] =>
    nodes.flatMap(n => [n, ...flattenTree(n.children)]);

  const fetchTree = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/infrastructure/locations/tree');
      setTreeData(res.data);
    } catch {
      addToast('error', 'Failed to load locations.');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    fetchTree();
    Promise.all([
      api.get('/master/location-types?page_size=100'),
      api.get('/master/position-types?page_size=100'),
      api.get('/master/position-templates?page_size=100'),
      api.get('/common/projects?page_size=100'),
    ]).then(([lt, pt, tmpl, proj]) => {
      setLocationTypes(lt.data.items ?? []);
      setPositionTypes(pt.data.items ?? []);
      setPositionTemplates(tmpl.data.items ?? []);
      setProjects(proj.data.items.map((p: any) => ({ id: p.id, name: p.project_name })));
    }).catch(() => addToast('error', 'Failed to load lookup data.'));
  }, []);

  // Load preview when template selection changes
  const handleTemplateChange = async (templateId: number | '') => {
    setSelectedTemplateId(templateId);
    setPreviewPositions([]);
    if (!templateId) return;
    setPreviewLoading(true);
    try {
      const res = await api.get(`/infrastructure/position-templates/${templateId}/preview`);
      setPreviewPositions((res.data as PositionPreview[]).map(p => ({ ...p, _edited: false })));
    } catch {
      addToast('error', 'Failed to load template preview.');
    } finally {
      setPreviewLoading(false);
    }
  };

  const openAddModal = (parent?: LocationNode) => {
    setEditingId(null);
    setFormData({ ...defaultFormData, parent_location_id: parent ? parent.id : '', location_type_id: locationTypes[0]?.id ?? 1 });
    setSelectedTemplateId('');
    setPreviewPositions([]);
    setIsModalOpen(true);
  };

  const openEditModal = (node: LocationNode) => {
    setEditingId(node.id);
    setFormData({
      project_id: (node as any).project_id ?? '',
      code: node.code, name: node.name,
      location_type_id: node.location_type_id,
      parent_location_id: node.parent_location_id ?? '',
      latitude: node.latitude != null ? String(node.latitude) : '',
      longitude: node.longitude != null ? String(node.longitude) : '',
      remarks: node.remarks ?? '',
    });
    setSelectedTemplateId('');
    setPreviewPositions([]);
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!editingId && !formData.project_id) { addToast('error', 'Project is required.'); return; }
    if (!formData.code) { addToast('error', 'Code is required.'); return; }
    if (!formData.name) { addToast('error', 'Name is required.'); return; }
    if (!formData.location_type_id) { addToast('error', 'Location type is required.'); return; }
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {
        code: formData.code,
        name: formData.name,
        location_type_id: Number(formData.location_type_id),
        parent_location_id: formData.parent_location_id || null,
        latitude: formData.latitude ? parseFloat(formData.latitude) : null,
        longitude: formData.longitude ? parseFloat(formData.longitude) : null,
        remarks: formData.remarks || null,
      };
      if (!editingId) {
        payload.project_id = formData.project_id;
      }

      if (editingId) {
        // Editing: no template apply
        await api.put(`/infrastructure/locations/${editingId}`, payload);
        addToast('success', 'Location updated.');
      } else {
        // Creating: if a template is selected, create location normally, then batch-create positions
        let locationId: string | null = null;

        if (selectedTemplateId && previewPositions.length > 0) {
          // Create location without auto-template (we'll apply manually to support overrides)
          const locRes = await api.post('/infrastructure/locations', payload);
          locationId = locRes.data.id;

          // Create overridden positions one-by-one
          await Promise.all(
            previewPositions.map(pos =>
              api.post(`/infrastructure/locations/${locationId}/positions`, {
                location_id: locationId,
                position_type_id: Number(pos.position_type_id),
                position_number: pos.position_number,
                maximum_capacity: Number(pos.maximum_capacity),
                remarks: pos.remarks || null,
              }),
            ),
          );
          addToast('success', `Location created with ${previewPositions.length} positions.`);
        } else {
          // No template: plain create
          await api.post('/infrastructure/locations', payload);
          addToast('success', 'Location created.');
        }
      }

      setIsModalOpen(false);
      await fetchTree();
      if (editingId) {
        const flat = flattenTree(treeData);
        const updated = flat.find(n => n.id === editingId);
        if (updated) setSelectedNode(updated);
      }
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      addToast('error', e?.response?.data?.detail ?? 'Failed to save location.');
    } finally {
      setSaving(false);
    }
  };

  const totalLocations = countNodes(treeData);
  const allNodes = flattenTree(treeData);
  const isEditing = !!editingId;

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ marginBottom: '0.25rem' }}>Infrastructure</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
            Manage locations and positions across the project
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => openAddModal()} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Plus size={18} /> Add Location
        </button>
      </div>

      {/* Stats bar */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Total Locations', value: totalLocations, icon: <Map size={18} color="var(--accent-primary)" /> },
          { label: 'Root Nodes', value: treeData.length, icon: <Folder size={18} color="var(--accent-secondary)" /> },
          { label: 'Selected', value: selectedNode ? selectedNode.name : '—', icon: <MapPin size={18} color="var(--success)" /> },
        ].map(stat => (
          <div key={stat.label} className="glass-panel" style={{ flex: 1, padding: '0.85rem 1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {stat.icon}
            <div>
              <div style={{ fontSize: '1rem', fontWeight: 600 }}>{stat.value}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Main layout */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedNode ? '1fr 360px' : '1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* Tree panel */}
        <div className="glass-panel" style={{ padding: '1.25rem', minHeight: 400 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
            <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              <Folder size={15} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Location Hierarchy
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'var(--bg-primary)', padding: '2px 8px', borderRadius: '10px' }}>
              {totalLocations} locations
            </span>
          </div>

          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {[...Array(5)].map((_, i) => (
                <div key={i} style={{ height: 36, borderRadius: 'var(--border-radius-sm)', background: 'rgba(255,255,255,0.04)', marginLeft: `${(i % 3) * 18}px`, animation: 'pulse 1.5s infinite' }} />
              ))}
            </div>
          ) : treeData.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem 1rem' }}>
              <Map size={40} style={{ marginBottom: '0.75rem', opacity: 0.4 }} />
              <p>No locations found. Add one to get started.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
              {treeData.map(node => (
                <TreeNode
                  key={node.id}
                  node={node}
                  level={0}
                  selectedId={selectedNode?.id ?? null}
                  onSelect={setSelectedNode}
                  onAddChild={openAddModal}
                />
              ))}
            </div>
          )}
        </div>

        {/* Detail panel */}
        <AnimatePresence>
          {selectedNode && (
            <DetailPanel
              node={selectedNode}
              positionTypes={positionTypes}
              positionTemplates={positionTemplates}
              onEdit={openEditModal}
            />
          )}
        </AnimatePresence>
      </div>

      {/* ── Add / Edit Modal ── */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isEditing ? 'Edit Location' : 'Add Location'}
        maxWidth="600px"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsModalOpen(false)} disabled={saving}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : (isEditing ? 'Save' : `Create${previewPositions.length > 0 ? ` + ${previewPositions.length} positions` : ''}`)}
            </button>
          </>
        }
      >
        <Select
          label="Project *"
          value={formData.project_id}
          onChange={e => setFormData({ ...formData, project_id: e.target.value })}
          options={[{ value: '', label: '— Select Project —' }, ...projects.map(p => ({ value: p.id, label: p.name }))]}
          disabled={isEditing}
        />
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <Input label="Code *" value={formData.code} onChange={e => setFormData({ ...formData, code: e.target.value })} placeholder="e.g. BLD-A" />
          <Input label="Name *" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} placeholder="e.g. Building A" />
        </div>

        <Select
          label="Location Type *"
          value={formData.location_type_id}
          onChange={e => setFormData({ ...formData, location_type_id: Number(e.target.value) })}
          options={locationTypes.map(lt => ({ value: lt.id, label: lt.name }))}
        />

        <Select
          label="Parent Location"
          value={formData.parent_location_id ?? ''}
          onChange={e => setFormData({ ...formData, parent_location_id: e.target.value || null })}
          options={[{ value: '', label: '— None (Root) —' }, ...allNodes.filter(n => n.id !== editingId).map(n => ({ value: n.id, label: `${n.name} (${n.code})` }))]}
        />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <Input label="Latitude" type="number" value={formData.latitude} onChange={e => setFormData({ ...formData, latitude: e.target.value })} placeholder="e.g. 25.0657" />
          <Input label="Longitude" type="number" value={formData.longitude} onChange={e => setFormData({ ...formData, longitude: e.target.value })} placeholder="e.g. 55.1713" />
        </div>

        <Input label="Remarks" value={formData.remarks} onChange={e => setFormData({ ...formData, remarks: e.target.value })} placeholder="Optional notes..." />

        {/* ── Template Section (only when adding) ── */}
        {!isEditing && (
          <>
            <div style={{ height: '1px', background: 'var(--border-color)', margin: '0.5rem 0 1rem' }} />
            <div style={{ marginBottom: '0.5rem' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem' }}>
                Position Template <span style={{ fontSize: '0.75rem', fontWeight: 400, color: 'var(--text-muted)' }}>(optional — auto-creates installation positions)</span>
              </label>
              <select
                value={selectedTemplateId}
                onChange={e => handleTemplateChange(e.target.value ? Number(e.target.value) : '')}
                style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '0.625rem 1rem', borderRadius: 'var(--border-radius-md)', outline: 'none', width: '100%', cursor: 'pointer', marginBottom: '0.75rem' }}
              >
                <option value="">— No template (add positions manually) —</option>
                {positionTemplates.map(t => (
                  <option key={t.id} value={t.id}>{t.name} ({t.node_count} positions)</option>
                ))}
              </select>
            </div>

            {/* Preview / Override Table */}
            {selectedTemplateId !== '' && (
              <div>
                {previewLoading ? (
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', padding: '0.5rem 0' }}>Loading positions...</div>
                ) : (
                  <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                        <Layers size={13} style={{ verticalAlign: 'middle', marginRight: 5 }} />
                        Positions to be created ({previewPositions.length})
                      </span>
                      <button
                        type="button"
                        onClick={() => {
                          const newPos: PositionPreview = {
                            position_type_id: positionTypes[0]?.id ?? 0,
                            position_type_name: positionTypes[0]?.name ?? '',
                            position_number: '',
                            maximum_capacity: 1,
                            node_order: previewPositions.length + 1,
                            remarks: null,
                            _edited: true,
                          };
                          setPreviewPositions([...previewPositions, newPos]);
                        }}
                        style={{ background: 'none', border: '1px solid var(--border-color)', color: 'var(--accent-primary)', padding: '0.2rem 0.6rem', borderRadius: 'var(--border-radius-sm)', cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                      >
                        <Plus size={12} /> Add Row
                      </button>
                    </div>
                    <PositionPreviewTable
                      positions={previewPositions}
                      positionTypes={positionTypes}
                      onChange={setPreviewPositions}
                    />
                  </>
                )}
              </div>
            )}
          </>
        )}
      </Modal>
    </div>
  );
};
