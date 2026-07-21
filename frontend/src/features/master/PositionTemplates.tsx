import React, { useEffect, useState, useCallback } from 'react';
import { api } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { Modal } from '../../components/Modal';
import { Input, Select } from '../../components/FormControls';
import {
  Plus, Edit2, Trash2, LayoutGrid, ChevronRight, ChevronDown,
  Layers, Settings, Package, AlertCircle,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// ─── Types ────────────────────────────────────────────────────────────────────

interface PositionType {
  id: number;
  code: string;
  name: string;
}

interface TemplateNode {
  id: number;
  position_template_id: number;
  position_type_id: number;
  position_type_name: string;
  position_number: string;
  maximum_capacity: number;
  node_order: number;
  remarks: string | null;
}

interface PositionTemplate {
  id: number;
  code: string;
  name: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
  node_count: number;
  nodes: TemplateNode[];
}

// ─── Node Row Component ────────────────────────────────────────────────────────

const NodeRow: React.FC<{
  node: TemplateNode;
  positionTypes: PositionType[];
  onEdit: (node: TemplateNode) => void;
  onDelete: (nodeId: number) => void;
}> = ({ node, positionTypes, onEdit, onDelete }) => {
  const ptName = node.position_type_name || positionTypes.find(p => p.id === node.position_type_id)?.name || '—';
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '0.75rem',
      padding: '0.55rem 0.9rem',
      borderRadius: 'var(--border-radius-sm)',
      border: '1px solid var(--border-color)',
      background: 'rgba(255,255,255,0.03)',
      transition: 'background 0.15s',
    }}>
      <LayoutGrid size={14} color="var(--accent-secondary)" style={{ flexShrink: 0 }} />

      <span style={{ fontWeight: 500, fontSize: '0.85rem', minWidth: 100 }}>{node.position_number}</span>

      <span style={{
        fontSize: '0.75rem', color: 'var(--text-muted)',
        background: 'var(--bg-primary)', padding: '2px 8px',
        borderRadius: 10, flexShrink: 0,
      }}>{ptName}</span>

      <span style={{
        fontSize: '0.75rem', color: 'var(--text-muted)',
        background: 'var(--bg-primary)', padding: '2px 8px',
        borderRadius: 10, flexShrink: 0,
      }}>Cap: {node.maximum_capacity}</span>

      {node.remarks && (
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {node.remarks}
        </span>
      )}

      <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.4rem' }}>
        <button
          onClick={() => onEdit(node)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-primary)', display: 'flex', padding: '0.2rem', borderRadius: '4px' }}
          title="Edit"
        >
          <Edit2 size={14} />
        </button>
        <button
          onClick={() => onDelete(node.id)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--danger)', display: 'flex', padding: '0.2rem', borderRadius: '4px' }}
          title="Delete"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
};

// ─── Template Card Component ───────────────────────────────────────────────────

const TemplateCard: React.FC<{
  template: PositionTemplate;
  isExpanded: boolean;
  positionTypes: PositionType[];
  onToggle: () => void;
  onEditTemplate: (t: PositionTemplate) => void;
  onAddNode: (templateId: number) => void;
  onEditNode: (node: TemplateNode) => void;
  onDeleteNode: (nodeId: number) => void;
  onRefresh: () => void;
}> = ({ template, isExpanded, positionTypes, onToggle, onEditTemplate, onAddNode, onEditNode, onDeleteNode }) => {
  return (
    <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex', alignItems: 'center', gap: '0.75rem',
          padding: '1rem 1.25rem', cursor: 'pointer',
          borderBottom: isExpanded ? '1px solid var(--border-color)' : 'none',
        }}
        onClick={onToggle}
      >
        <div style={{
          width: 36, height: 36, borderRadius: 8,
          background: template.is_active
            ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))'
            : 'var(--bg-primary)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>
          <Layers size={16} color="white" />
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{template.name}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{template.code}</div>
        </div>

        <span style={{
          fontSize: '0.72rem', color: 'var(--text-muted)',
          background: 'var(--bg-primary)', padding: '2px 8px', borderRadius: 10, flexShrink: 0,
        }}>
          {template.node_count} position{template.node_count !== 1 ? 's' : ''}
        </span>

        <span style={{
          fontSize: '0.72rem', fontWeight: 600, flexShrink: 0,
          color: template.is_active ? 'var(--success)' : 'var(--text-muted)',
        }}>
          {template.is_active ? 'Active' : 'Inactive'}
        </span>

        <button
          onClick={e => { e.stopPropagation(); onEditTemplate(template); }}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-primary)', display: 'flex', padding: '0.3rem', borderRadius: '4px', flexShrink: 0 }}
          title="Edit template"
        >
          <Settings size={15} />
        </button>

        <span style={{ color: 'var(--text-muted)', display: 'flex', flexShrink: 0 }}>
          {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </span>
      </div>

      {/* Expanded nodes */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.18 }}
          >
            <div style={{ padding: '1rem 1.25rem' }}>
              {template.description && (
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '0 0 1rem' }}>{template.description}</p>
              )}

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Installation Positions</span>
                <button
                  className="btn btn-primary"
                  onClick={() => onAddNode(template.id)}
                  style={{ padding: '0.25rem 0.7rem', fontSize: '0.75rem', gap: '0.3rem' }}
                >
                  <Plus size={13} /> Add Position
                </button>
              </div>

              {template.nodes.length === 0 ? (
                <div style={{
                  textAlign: 'center', padding: '1.5rem',
                  border: '1px dashed var(--border-color)', borderRadius: 'var(--border-radius-md)',
                  color: 'var(--text-muted)', fontSize: '0.82rem',
                }}>
                  <AlertCircle size={22} style={{ marginBottom: '0.4rem', opacity: 0.4, display: 'block', margin: '0 auto 0.4rem' }} />
                  No positions defined yet. Add one above.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {template.nodes.map(node => (
                    <NodeRow
                      key={node.id}
                      node={node}
                      positionTypes={positionTypes}
                      onEdit={onEditNode}
                      onDelete={id => onDeleteNode(id)}
                    />
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ─── Main Page ────────────────────────────────────────────────────────────────

const defaultTemplateForm = { code: '', name: '', description: '', display_order: 0, is_active: true };
const defaultNodeForm = { position_type_id: 0, position_number: '', maximum_capacity: 1, node_order: 0, remarks: '' };

export const PositionTemplates: React.FC = () => {
  const [templates, setTemplates] = useState<PositionTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [positionTypes, setPositionTypes] = useState<PositionType[]>([]);
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());
  const { addToast } = useToast();

  // Template modal
  const [templateModalOpen, setTemplateModalOpen] = useState(false);
  const [editingTemplateId, setEditingTemplateId] = useState<number | null>(null);
  const [templateForm, setTemplateForm] = useState(defaultTemplateForm);
  const [templateSaving, setTemplateSaving] = useState(false);

  // Node modal
  const [nodeModalOpen, setNodeModalOpen] = useState(false);
  const [editingNodeId, setEditingNodeId] = useState<number | null>(null);
  const [activeTemplateId, setActiveTemplateId] = useState<number | null>(null);
  const [nodeForm, setNodeForm] = useState(defaultNodeForm);
  const [nodeSaving, setNodeSaving] = useState(false);

  // ─── Data fetching ──────────────────────────────────────────────────────────

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/master/position-templates?page_size=100');
      const items: PositionTemplate[] = res.data.items ?? [];
      // Fetch nodes for expanded templates
      const enriched = await Promise.all(
        items.map(async (t) => {
          const detail = await api.get(`/master/position-templates/${t.id}`);
          return { ...t, nodes: detail.data.nodes ?? [], node_count: detail.data.node_count ?? 0 };
        }),
      );
      setTemplates(enriched);
    } catch {
      addToast('error', 'Failed to load position templates.');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    fetchTemplates();
    api.get('/master/position-types?page_size=100').then(res => {
      setPositionTypes(res.data.items ?? []);
    }).catch(() => addToast('error', 'Failed to load position types.'));
  }, []);

  // ─── Template CRUD ──────────────────────────────────────────────────────────

  const openAddTemplate = () => {
    setEditingTemplateId(null);
    setTemplateForm(defaultTemplateForm);
    setTemplateModalOpen(true);
  };

  const openEditTemplate = (t: PositionTemplate) => {
    setEditingTemplateId(t.id);
    setTemplateForm({
      code: t.code,
      name: t.name,
      description: t.description ?? '',
      display_order: t.display_order,
      is_active: t.is_active,
    });
    setTemplateModalOpen(true);
  };

  const saveTemplate = async () => {
    if (!templateForm.code) { addToast('error', 'Code is required.'); return; }
    if (!templateForm.name) { addToast('error', 'Name is required.'); return; }
    setTemplateSaving(true);
    try {
      const payload = { ...templateForm, display_order: Number(templateForm.display_order) };
      if (editingTemplateId) {
        await api.put(`/master/position-templates/${editingTemplateId}`, payload);
        addToast('success', 'Template updated.');
      } else {
        const res = await api.post('/master/position-templates', payload);
        // Auto-expand new template
        setExpandedIds(prev => new Set([...prev, res.data.id]));
        addToast('success', 'Template created.');
      }
      setTemplateModalOpen(false);
      fetchTemplates();
    } catch {
      addToast('error', 'Failed to save template.');
    } finally {
      setTemplateSaving(false);
    }
  };

  // ─── Node CRUD ──────────────────────────────────────────────────────────────

  const openAddNode = (templateId: number) => {
    setEditingNodeId(null);
    setActiveTemplateId(templateId);
    setNodeForm({
      ...defaultNodeForm,
      position_type_id: positionTypes[0]?.id ?? 0,
      // Suggest next order
      node_order: (templates.find(t => t.id === templateId)?.nodes.length ?? 0) + 1,
    });
    setNodeModalOpen(true);
  };

  const openEditNode = (node: TemplateNode) => {
    setEditingNodeId(node.id);
    setActiveTemplateId(node.position_template_id);
    setNodeForm({
      position_type_id: node.position_type_id,
      position_number: node.position_number,
      maximum_capacity: node.maximum_capacity,
      node_order: node.node_order,
      remarks: node.remarks ?? '',
    });
    setNodeModalOpen(true);
  };

  const saveNode = async () => {
    if (!nodeForm.position_number) { addToast('error', 'Position number is required.'); return; }
    if (!nodeForm.position_type_id) { addToast('error', 'Position type is required.'); return; }
    setNodeSaving(true);
    try {
      const payload = {
        ...nodeForm,
        position_type_id: Number(nodeForm.position_type_id),
        maximum_capacity: Number(nodeForm.maximum_capacity),
        node_order: Number(nodeForm.node_order),
      };
      if (editingNodeId) {
        await api.put(`/master/position-template-nodes/${editingNodeId}`, payload);
        addToast('success', 'Position updated.');
      } else {
        await api.post(`/master/position-templates/${activeTemplateId}/nodes`, payload);
        addToast('success', 'Position added.');
      }
      setNodeModalOpen(false);
      fetchTemplates();
    } catch {
      addToast('error', 'Failed to save position.');
    } finally {
      setNodeSaving(false);
    }
  };

  const deleteNode = async (nodeId: number) => {
    if (!window.confirm('Delete this position from the template?')) return;
    try {
      await api.delete(`/master/position-template-nodes/${nodeId}`);
      addToast('success', 'Position deleted.');
      fetchTemplates();
    } catch {
      addToast('error', 'Failed to delete position.');
    }
  };

  // ─── Toggle expand ──────────────────────────────────────────────────────────

  const toggleExpand = (id: number) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const totalPositions = templates.reduce((sum, t) => sum + t.node_count, 0);

  // ─── Render ─────────────────────────────────────────────────────────────────

  return (
    <div>
      {/* Page header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ marginBottom: '0.25rem' }}>Position Templates</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
            Define reusable installation position samples for location types
          </p>
        </div>
        <button className="btn btn-primary" onClick={openAddTemplate} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Plus size={18} /> New Template
        </button>
      </div>

      {/* Stats bar */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Total Templates', value: templates.length, icon: <Package size={18} color="var(--accent-primary)" /> },
          { label: 'Active Templates', value: templates.filter(t => t.is_active).length, icon: <Layers size={18} color="var(--success)" /> },
          { label: 'Total Positions', value: totalPositions, icon: <LayoutGrid size={18} color="var(--accent-secondary)" /> },
        ].map(stat => (
          <div key={stat.label} className="glass-panel" style={{ flex: 1, padding: '0.85rem 1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {stat.icon}
            <div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>{stat.value}</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Template list */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[...Array(3)].map((_, i) => (
            <div key={i} style={{ height: 64, borderRadius: 'var(--border-radius-md)', background: 'rgba(255,255,255,0.04)', animation: 'pulse 1.5s infinite' }} />
          ))}
        </div>
      ) : templates.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          <Layers size={40} style={{ marginBottom: '0.75rem', opacity: 0.4, display: 'block', margin: '0 auto 0.75rem' }} />
          <p style={{ margin: 0 }}>No position templates yet. Create one to get started.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {templates.map(t => (
            <TemplateCard
              key={t.id}
              template={t}
              isExpanded={expandedIds.has(t.id)}
              positionTypes={positionTypes}
              onToggle={() => toggleExpand(t.id)}
              onEditTemplate={openEditTemplate}
              onAddNode={openAddNode}
              onEditNode={openEditNode}
              onDeleteNode={deleteNode}
              onRefresh={fetchTemplates}
            />
          ))}
        </div>
      )}

      {/* ── Template Modal ── */}
      <Modal
        isOpen={templateModalOpen}
        onClose={() => setTemplateModalOpen(false)}
        title={editingTemplateId ? 'Edit Template' : 'New Position Template'}
        maxWidth="480px"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setTemplateModalOpen(false)} disabled={templateSaving}>Cancel</button>
            <button className="btn btn-primary" onClick={saveTemplate} disabled={templateSaving}>{templateSaving ? 'Saving...' : 'Save'}</button>
          </>
        }
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <Input label="Code *" value={templateForm.code} onChange={e => setTemplateForm({ ...templateForm, code: e.target.value })} placeholder="e.g. POLE_STD" />
          <Input label="Display Order" type="number" value={templateForm.display_order} onChange={e => setTemplateForm({ ...templateForm, display_order: parseInt(e.target.value) || 0 })} />
        </div>
        <Input label="Name *" value={templateForm.name} onChange={e => setTemplateForm({ ...templateForm, name: e.target.value })} placeholder="e.g. Standard Pole Template" />
        <Input label="Description" value={templateForm.description} onChange={e => setTemplateForm({ ...templateForm, description: e.target.value })} placeholder="Optional description..." />
        <Select
          label="Status"
          value={templateForm.is_active ? 'active' : 'inactive'}
          onChange={e => setTemplateForm({ ...templateForm, is_active: e.target.value === 'active' })}
          options={[{ value: 'active', label: 'Active' }, { value: 'inactive', label: 'Inactive' }]}
        />
      </Modal>

      {/* ── Node Modal ── */}
      <Modal
        isOpen={nodeModalOpen}
        onClose={() => setNodeModalOpen(false)}
        title={editingNodeId ? 'Edit Position' : 'Add Position to Template'}
        maxWidth="460px"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setNodeModalOpen(false)} disabled={nodeSaving}>Cancel</button>
            <button className="btn btn-primary" onClick={saveNode} disabled={nodeSaving}>{nodeSaving ? 'Saving...' : 'Save'}</button>
          </>
        }
      >
        <Select
          label="Position Type *"
          value={nodeForm.position_type_id}
          onChange={e => setNodeForm({ ...nodeForm, position_type_id: Number(e.target.value) })}
          options={positionTypes.map(pt => ({ value: pt.id, label: pt.name }))}
        />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <Input label="Position Number *" value={nodeForm.position_number} onChange={e => setNodeForm({ ...nodeForm, position_number: e.target.value })} placeholder="e.g. PTZ-01" />
          <Input label="Max Capacity" type="number" value={nodeForm.maximum_capacity} onChange={e => setNodeForm({ ...nodeForm, maximum_capacity: parseInt(e.target.value) || 1 })} />
        </div>
        <Input label="Order" type="number" value={nodeForm.node_order} onChange={e => setNodeForm({ ...nodeForm, node_order: parseInt(e.target.value) || 0 })} />
        <Input label="Remarks" value={nodeForm.remarks} onChange={e => setNodeForm({ ...nodeForm, remarks: e.target.value })} placeholder="Optional notes..." />
      </Modal>
    </div>
  );
};
