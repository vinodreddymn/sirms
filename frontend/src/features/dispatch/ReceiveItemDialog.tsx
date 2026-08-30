import React, { useEffect, useState } from 'react';
import { Modal } from '../../components/Modal';
import { Input, Select, TextArea } from '../../components/FormControls';
import type { ReceiveItemPayload } from './types';
import { api } from '../../services/api';

interface ReceiveItemDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: ReceiveItemPayload) => Promise<void>;
  itemName: string;
}

export const ReceiveItemDialog: React.FC<ReceiveItemDialogProps> = ({
  isOpen, onClose, onSubmit, itemName
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [locations, setLocations] = useState<Array<{ id: string; name: string }>>([]);
  const [formData, setFormData] = useState<ReceiveItemPayload>({
    return_date: new Date().toISOString().split('T')[0],
    result: 'Repaired',
    repair_cost: null,
    remarks: '',
    to_location_id: '',
  });

  useEffect(() => {
    if (!isOpen) return;
    api.get('/common/locations', { params: { type: 'STORE' } })
      .then((res) => setLocations(res.data.items || []))
      .catch(() => setLocations([]));
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!formData.to_location_id) {
      alert('Please select a store location to receive the item.');
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Receive Item: ${itemName}`}
      maxWidth="500px"
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose} disabled={submitting}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Processing...' : 'Receive Item'}
          </button>
        </>
      }
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <Input
          label="Return Date"
          type="date"
          required
          value={formData.return_date}
          onChange={(e) => setFormData({ ...formData, return_date: e.target.value })}
        />
        <Select
          label="Store Location"
          required
          options={[{ label: 'Select Store Location', value: '' }, ...locations.map((loc) => ({ label: loc.name, value: loc.id }))]}
          value={formData.to_location_id ?? ''}
          onChange={(e) => setFormData({ ...formData, to_location_id: e.target.value })}
        />
        <Select
          label="Result"
          required
          options={[
            { label: 'Repaired', value: 'Repaired' },
            { label: 'Replaced', value: 'Replaced' },
            { label: 'Beyond Repair', value: 'Beyond Repair' },
            { label: 'Returned Without Repair', value: 'Returned Without Repair' }
          ]}
          value={formData.result}
          onChange={(e) => setFormData({ ...formData, result: e.target.value as any })}
        />
        <Input
          label="Repair Cost"
          type="number"
          step="0.01"
          min="0"
          value={formData.repair_cost || ''}
          onChange={(e) => setFormData({ ...formData, repair_cost: parseFloat(e.target.value) || null })}
        />
        <TextArea
          label="Remarks"
          rows={3}
          value={formData.remarks || ''}
          onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
        />
      </div>
    </Modal>
  );
};
