import React, { useEffect, useState } from "react";
import { DataTable } from "../../components/DataTable";
import type { Column } from "../../components/DataTable";
import { api } from "../../services/api";
import { useToast } from "../../contexts/ToastContext";
import { Modal } from "../../components/Modal";
import { Input, Select } from "../../components/FormControls";
import { Plus, Edit2 } from "lucide-react";

interface Lookup {
  id: number;
  code: string;
  name: string;
  display_order: number;
  is_active: boolean;
}

const lookupOptions = [
  { label: "Location Types", value: "location-types" },
  { label: "Position Types", value: "position-types" },
  { label: "Asset Categories", value: "asset-categories" },
  { label: "Asset Subcategories", value: "asset-subcategories" },
  { label: "Manufacturers", value: "manufacturers" },
  { label: "Asset Models", value: "asset-models" },
  { label: "Asset Status", value: "asset-status" },
  { label: "Asset Condition", value: "asset-condition" },
  { label: "Asset Lifecycle", value: "asset-lifecycle" },
  { label: "Maintenance Types", value: "maintenance-types" },
  { label: "Failure Categories", value: "failure-categories" },
  { label: "Root Cause Categories", value: "root-cause-categories" },
  { label: "Incident Status", value: "incident-status" },
  { label: "Incident Priority", value: "incident-priority" },
  { label: "Incident Categories", value: "incident-categories" },
  { label: "Work Order Status", value: "work-order-status" },
  { label: "Relationship Types", value: "relationship-types" },
  { label: "Document Types", value: "document-types" },
  { label: "Photo Types", value: "photo-types" },
  { label: "Project Types", value: "project-types" },
  { label: "Movement Types", value: "movement-types" },
  { label: "Stock Transaction Types", value: "stock-transaction-types" },
];

const defaultFormData = {
  code: "",
  name: "",
  display_order: 0,
  is_active: true,
};

export const LookupsList: React.FC = () => {
  const [tableName, setTableName] = useState("location-types");
  const [lookups, setLookups] = useState<Lookup[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState(defaultFormData);
  const [saving, setSaving] = useState(false);

  const { addToast } = useToast();

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/master/${tableName}`, { params: { page_size: 1000 } });
      setLookups(response.data.items ?? []);
    } catch (error) {
      console.error(error);
      addToast("error", "Failed to load lookup data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [tableName]);

  const handleOpenModal = (lookup?: Lookup) => {
    if (lookup) {
      setEditingId(lookup.id);
      setFormData({
        code: lookup.code || "",
        name: lookup.name || "",
        display_order: lookup.display_order || 0,
        is_active: lookup.is_active ?? true,
      });
    } else {
      setEditingId(null);
      setFormData(defaultFormData);
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    setFormData(defaultFormData);
  };

  const handleSave = async () => {
    if (!formData.name) {
      addToast("error", "Name is required.");
      return;
    }
    setSaving(true);
    try {
      const payload = {
        ...formData,
        display_order: Number(formData.display_order)
      };

      if (editingId) {
        await api.put(`/master/${tableName}/${editingId}`, payload);
        addToast("success", "Successfully updated.");
      } else {
        await api.post(`/master/${tableName}`, payload);
        addToast("success", "Successfully added.");
      }
      handleCloseModal();
      fetchData();
    } catch (error) {
      console.error(error);
      addToast("error", "Failed to save data.");
    } finally {
      setSaving(false);
    }
  };

  const columns: Column<Lookup>[] = [
    { header: "ID", accessor: "id", width: "80px" },
    { header: "Code", accessor: "code" },
    { header: "Name", accessor: "name" },
    { header: "Display Order", accessor: "display_order", width: "140px" },
    {
      header: "Status",
      accessor: (row) => (
        <span
          style={{
            color: row.is_active ? "#16a34a" : "#dc2626",
            fontWeight: 600,
          }}
        >
          {row.is_active ? "Active" : "Inactive"}
        </span>
      ),
      width: "120px",
    },
    {
      header: "Actions",
      accessor: (row) => (
        <button
          onClick={() => handleOpenModal(row)}
          style={{
            background: "none",
            border: "none",
            color: "var(--primary-color)",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
          title="Edit"
        >
          <Edit2 size={18} />
        </button>
      ),
      width: "80px",
    },
  ];

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <h1>Master Data</h1>

        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <select
            value={tableName}
            onChange={(e) => setTableName(e.target.value)}
            className="input"
            style={{ width: 280, height: "40px", padding: "0 10px", borderRadius: "var(--border-radius-md)", border: "1px solid var(--border-color)", background: "var(--bg-tertiary)", color: "var(--text-primary)" }}
          >
            {lookupOptions.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>

          <button 
            className="btn btn-primary"
            onClick={() => handleOpenModal()}
            style={{ display: "flex", alignItems: "center", gap: "0.5rem", height: "40px" }}
          >
            <Plus size={18} /> Add New
          </button>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={lookups}
        loading={loading}
      />

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingId ? "Edit Record" : "Add Record"}
        footer={
          <>
            <button className="btn btn-secondary" onClick={handleCloseModal} disabled={saving}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : "Save"}
            </button>
          </>
        }
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Input
            label="Code"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            placeholder="Enter code"
          />
          <Input
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Enter name"
            required
          />
          <Input
            label="Display Order"
            type="number"
            value={formData.display_order}
            onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) || 0 })}
          />
          <Select
            label="Status"
            value={formData.is_active ? "active" : "inactive"}
            onChange={(e) => setFormData({ ...formData, is_active: e.target.value === "active" })}
            options={[
              { label: "Active", value: "active" },
              { label: "Inactive", value: "inactive" }
            ]}
          />
        </div>
      </Modal>
    </div>
  );
};