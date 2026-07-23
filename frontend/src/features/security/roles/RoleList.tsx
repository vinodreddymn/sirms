import React, { useEffect, useState } from "react";
import { DataTable } from "../../../components/DataTable";
import type { Column } from "../../../components/DataTable";
import { api } from "../../../services/api";
import { useToast } from "../../../contexts/ToastContext";
import { Modal } from "../../../components/Modal";
import { Input, Select } from "../../../components/FormControls";
import { Plus, Edit2, ShieldAlert, ShieldCheck } from "lucide-react";

interface Role {
  id: string;
  role_code: string;
  role_name: string;
  description?: string;
  is_system_role: boolean;
}

const defaultFormData = {
  role_code: "",
  role_name: "",
  description: "",
  is_system_role: false,
};

export const RoleList: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState(defaultFormData);
  const [saving, setSaving] = useState(false);

  const { addToast } = useToast();

  const fetchRoles = async () => {
    setLoading(true);
    try {
      const response = await api.get("/roles", { params: { page_size: 100 } });
      setRoles(response.data.items ?? []);
    } catch (error) {
      console.error(error);
      addToast("error", "Failed to load roles.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  const handleOpenModal = (role?: Role) => {
    if (role) {
      setEditingId(role.id);
      setFormData({
        role_code: role.role_code,
        role_name: role.role_name,
        description: role.description || "",
        is_system_role: role.is_system_role,
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
    if (!formData.role_code || !formData.role_name) {
      addToast("error", "Role Code and Role Name are required.");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        role_code: formData.role_code,
        role_name: formData.role_name,
        description: formData.description || null,
        is_system_role: formData.is_system_role,
      };

      if (editingId) {
        await api.put(`/roles/${editingId}`, payload);
        addToast("success", "Role successfully updated.");
      } else {
        await api.post("/roles", payload);
        addToast("success", "Role successfully created.");
      }
      handleCloseModal();
      fetchRoles();
    } catch (error: any) {
      console.error(error);
      addToast("error", error.response?.data?.detail || "Failed to save role.");
    } finally {
      setSaving(false);
    }
  };

  const columns: Column<Role>[] = [
    { header: "Role Code", accessor: "role_code", width: "150px" },
    { header: "Role Name", accessor: "role_name", width: "200px" },
    { header: "Description", accessor: "description" },
    { 
      header: "Type", 
      accessor: (row) => (
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.25rem",
            color: row.is_system_role ? "#0284c7" : "#4b5563",
            fontWeight: 500,
            padding: "0.25rem 0.5rem",
            borderRadius: "999px",
            backgroundColor: row.is_system_role ? "#e0f2fe" : "#f3f4f6"
          }}
        >
          {row.is_system_role ? <ShieldAlert size={14} /> : <ShieldCheck size={14} />}
          {row.is_system_role ? "System" : "Custom"}
        </span>
      ),
      width: "120px" 
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
            justifyContent: "center",
            opacity: row.is_system_role ? 0.5 : 1,
            pointerEvents: row.is_system_role ? "none" : "auto"
          }}
          title={row.is_system_role ? "System roles cannot be edited" : "Edit"}
          disabled={row.is_system_role}
        >
          <Edit2 size={18} />
        </button>
      ),
      width: "80px",
    },
  ];

  return (
    <div style={{ padding: '1.5rem' }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <div>
          <h1>Roles</h1>
          <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
            Manage user roles and permissions.
          </p>
        </div>

        <button 
          className="btn btn-primary"
          onClick={() => handleOpenModal()}
          style={{ display: "flex", alignItems: "center", gap: "0.5rem", height: "40px" }}
        >
          <Plus size={18} /> Add Role
        </button>
      </div>

      <DataTable
        columns={columns}
        data={roles}
        loading={loading}
      />

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingId ? "Edit Role" : "Add Role"}
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
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem", minWidth: "400px" }}>
          <Input
            label="Role Code"
            value={formData.role_code}
            onChange={(e) => setFormData({ ...formData, role_code: e.target.value })}
            placeholder="ADMIN"
            required
            disabled={!!editingId}
          />
          
          <Input
            label="Role Name"
            value={formData.role_name}
            onChange={(e) => setFormData({ ...formData, role_name: e.target.value })}
            placeholder="Administrator"
            required
          />

          <Input
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Full system access"
          />
        </div>
      </Modal>
    </div>
  );
};
