import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Save, X, Package, Trash2, Plus } from 'lucide-react';
import { Input, Select, TextArea } from '../../components/FormControls';
import { useToast } from '../../contexts/ToastContext';
import { createDispatch, updateDispatch, getDispatchDetails } from './api';
import type { DispatchFormPayload, DispatchItemFormPayload } from './types';
import { api } from '../../services/api';

export const DispatchForm: React.FC<{ mode: 'create' | 'edit' }> = ({ mode }) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  const [loading, setLoading] = useState(mode === 'edit');
  const [submitting, setSubmitting] = useState(false);
  const [vendors, setVendors] = useState<{ label: string, value: string }[]>([]);
  const [assets, setAssets] = useState<{ label: string, value: string }[]>([]);
  
  const [formData, setFormData] = useState<DispatchFormPayload>({
    dispatch_date: new Date().toISOString().split('T')[0],
    vendor_id: null,
    purpose: 'Repair',
    courier_name: '',
    tracking_number: '',
    remarks: '',
    items: [],
  });

  useEffect(() => {
    const loadLookups = async () => {
      try {
        const [vendorsRes, assetsRes] = await Promise.all([
          api.get('/common/vendors'),
          api.get('/assets', { params: { page_size: 1000, location_type_code: 'STORE' } })
        ]);
        
        setVendors(vendorsRes.data.items.map((v: any) => ({ label: v.vendor_name, value: v.id })));
        setAssets(assetsRes.data.items.map((a: any) => ({
          label: `${a.asset_number} – ${a.category}${a.current_location ? ` (${a.current_location})` : ''}`,
          value: a.id
        })));
      } catch (err) {
        console.error("Lookup error:", err);
        addToast('error', 'Failed to load lookup data');
      }
    };
    
    loadLookups();
  }, [addToast]);

  useEffect(() => {
    if (mode === 'edit' && id) {
      const loadDispatch = async () => {
        try {
          const data = await getDispatchDetails(id);
          setFormData({
            dispatch_date: data.dispatch_date,
            vendor_id: data.vendor_id || null,
            purpose: data.purpose,
            courier_name: data.courier_name || '',
            tracking_number: data.tracking_number || '',
            remarks: data.remarks || '',
            items: data.items.map(item => ({
              asset_id: item.asset_id || null,
              dispatch_type: item.dispatch_type,
              component_name: item.component_name || '',
              quantity: item.quantity,
              condition: item.condition,
              remarks: item.remarks || '',
            })),
          });
        } catch {
          addToast('error', 'Failed to load dispatch details');
          navigate('/dispatches');
        } finally {
          setLoading(false);
        }
      };
      loadDispatch();
    }
  }, [mode, id, navigate, addToast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.items.length === 0) {
      addToast('error', 'Please add at least one item to dispatch');
      return;
    }
    
    setSubmitting(true);
    try {
      if (mode === 'create') {
        const res = await createDispatch(formData);
        addToast('success', 'Dispatch created successfully');
        navigate(`/dispatches/${res.id}`);
      } else if (id) {
        await updateDispatch(id, formData);
        addToast('success', 'Dispatch updated successfully');
        navigate(`/dispatches/${id}`);
      }
    } catch {
      addToast('error', `Failed to ${mode} dispatch`);
    } finally {
      setSubmitting(false);
    }
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, {
        dispatch_type: 'Asset',
        asset_id: null,
        component_name: '',
        quantity: 1,
        condition: 'Faulty',
        remarks: '',
      }]
    }));
  };

  const updateItem = (index: number, field: keyof DispatchItemFormPayload, value: any) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  const removeItem = (index: number) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Package size={28} color="var(--primary)" />
          {mode === 'create' ? 'New Dispatch' : 'Edit Dispatch'}
        </h1>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>
            <X size={18} />
            <span>Cancel</span>
          </button>
          <button type="button" className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
            <Save size={18} />
            <span>{submitting ? 'Saving...' : 'Save Dispatch'}</span>
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, margin: '0 0 1rem 0' }}>Dispatch Details</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            <Input
              label="Dispatch Date"
              type="date"
              required
              value={formData.dispatch_date}
              onChange={(e) => setFormData({ ...formData, dispatch_date: e.target.value })}
            />
            <Select
              label="Purpose"
              required
              options={[
                { label: 'Repair', value: 'Repair' },
                { label: 'Warranty', value: 'Warranty' },
                { label: 'Calibration', value: 'Calibration' },
                { label: 'Transfer', value: 'Transfer' },
                { label: 'Others', value: 'Others' }
              ]}
              value={formData.purpose}
              onChange={(e) => setFormData({ ...formData, purpose: e.target.value as any })}
            />
            <Select
              label="Vendor / Service Center"
              options={[{ label: 'Select Vendor...', value: '' }, ...vendors]}
              value={formData.vendor_id || ''}
              onChange={(e) => setFormData({ ...formData, vendor_id: e.target.value || null })}
            />
            <Input
              label="Courier Name"
              value={formData.courier_name || ''}
              onChange={(e) => setFormData({ ...formData, courier_name: e.target.value })}
            />
            <Input
              label="Tracking Number"
              value={formData.tracking_number || ''}
              onChange={(e) => setFormData({ ...formData, tracking_number: e.target.value })}
            />
          </div>
          <div style={{ marginTop: '1rem' }}>
            <TextArea
              label="Remarks"
              rows={3}
              value={formData.remarks || ''}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
            />
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, margin: 0 }}>Dispatch Items</h2>
            {mode === 'create' && (
              <button type="button" className="btn btn-secondary btn-sm" onClick={addItem}>
                <Plus size={16} /> Add Item
              </button>
            )}
          </div>
          
          {formData.items.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', border: '1px dashed var(--border-color)', borderRadius: 'var(--border-radius-sm)' }}>
              No items added yet. Click "Add Item" to include assets or components in this dispatch.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {formData.items.map((item, index) => (
                <div key={index} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--border-radius-sm)', padding: '1rem', position: 'relative' }}>
                  {mode === 'create' && (
                    <button 
                      type="button" 
                      onClick={() => removeItem(index)}
                      style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}
                    >
                      <Trash2 size={18} />
                    </button>
                  )}
                  
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', paddingRight: '2rem' }}>
                    <Select
                      label="Type"
                      options={[
                        { label: 'Asset', value: 'Asset' },
                        { label: 'Component', value: 'Component' }
                      ]}
                      value={item.dispatch_type}
                      onChange={(e) => updateItem(index, 'dispatch_type', e.target.value)}
                      disabled={mode === 'edit'}
                    />
                    
                    {item.dispatch_type === 'Asset' ? (
                      <>
                        <Select
                          label="Asset"
                          required
                          options={[{ label: 'Select Asset in Store...', value: '' }, ...assets]}
                          value={item.asset_id || ''}
                          onChange={(e) => updateItem(index, 'asset_id', e.target.value || null)}
                          disabled={mode === 'edit'}
                        />
                        {assets.length === 0 && mode === 'create' && (
                          <p style={{ fontSize: '0.78rem', color: 'var(--warning, #f59e0b)', margin: '-0.5rem 0 0', gridColumn: '1 / -1' }}>
                            ⚠ No assets currently in a Store location. Move the asset to a store before dispatching.
                          </p>
                        )}
                      </>
                    ) : (
                      <>
                        <Select
                          label="Parent Asset (Optional)"
                          options={[{ label: 'Select Parent Asset...', value: '' }, ...assets]}
                          value={item.asset_id || ''}
                          onChange={(e) => updateItem(index, 'asset_id', e.target.value || null)}
                          disabled={mode === 'edit'}
                        />
                        <Input
                          label="Component Name"
                          required
                          value={item.component_name || ''}
                          onChange={(e) => updateItem(index, 'component_name', e.target.value)}
                          disabled={mode === 'edit'}
                        />
                      </>
                    )}
                    
                    <Select
                      label="Condition"
                      options={[
                        { label: 'Faulty', value: 'Faulty' },
                        { label: 'Working', value: 'Working' },
                        { label: 'Damaged', value: 'Damaged' }
                      ]}
                      value={item.condition}
                      onChange={(e) => updateItem(index, 'condition', e.target.value)}
                      disabled={mode === 'edit'}
                    />
                    <Input
                      label="Quantity"
                      type="number"
                      min={1}
                      required
                      value={item.quantity}
                      onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                      disabled={mode === 'edit'}
                    />
                  </div>
                  <div style={{ marginTop: '1rem' }}>
                    <Input
                      label="Item Remarks"
                      value={item.remarks || ''}
                      onChange={(e) => updateItem(index, 'remarks', e.target.value)}
                      disabled={mode === 'edit'}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
