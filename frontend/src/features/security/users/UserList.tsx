import React, { useEffect, useState } from "react";
import { DataTable } from "../../../components/DataTable";
import type { Column } from "../../../components/DataTable";
import { api } from "../../../services/api";
import { useToast } from "../../../contexts/ToastContext";
import { Modal } from "../../../components/Modal";
import { Input, Select } from "../../../components/FormControls";
import { Plus, Edit2, Lock, Unlock } from "lucide-react";

interface User {
  id: string;
  username: string;
  full_name: string;
  email: string;
  mobile_number?: string;
  is_locked: boolean;
  created_at: string;
  last_login_at?: string;
}

const defaultFormData = {
  username: "",
  full_name: "",
  email: "",
  password: "",
  mobile_number: "",
  is_locked: false,
};

export const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState(defaultFormData);
  const [saving, setSaving] = useState(false);
  const [roles, setRoles] = useState<Array<{ id: string; role_code: string; role_name: string }>>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string | null>(null);

  const { addToast } = useToast();

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get("/users", { params: { page_size: 100 } });
      setUsers(response.data.items ?? []);
    } catch (error) {
      console.error(error);
      addToast("error", "Failed to load users.");
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const res = await api.get('/roles', { params: { page_size: 200 } });
      setRoles(res.data.items ?? []);
    } catch (err) {
      // ignore
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, []);

  const handleOpenModal = (user?: User) => {
    if (user) {
      setEditingId(user.id);
      setFormData({
        username: user.username,
        full_name: user.full_name,
        email: user.email,
        password: "", // do not populate password on edit
        mobile_number: user.mobile_number || "",
        is_locked: user.is_locked,
      });
        // set selected role if present on user (take first)
        setSelectedRoleId((user as any).role_ids && (user as any).role_ids.length ? String((user as any).role_ids[0]) : null);
    } else {
      setEditingId(null);
      setFormData(defaultFormData);
        setSelectedRoleId(null);
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    setFormData(defaultFormData);
  };

  const handleSave = async () => {
    if (!formData.username || !formData.email || !formData.full_name) {
      addToast("error", "Username, Email, and Full Name are required.");
      return;
    }
    if (!editingId && !formData.password) {
      addToast("error", "Password is required for new users.");
      return;
    }

    setSaving(true);
    try {
      const payload: Record<string, any> = {
        full_name: formData.full_name,
        email: formData.email,
        mobile_number: formData.mobile_number || null,
        is_locked: formData.is_locked,
      };

      if (editingId) {
        const res = await api.put(`/users/${editingId}`, payload);
        addToast("success", "User successfully updated.");
        // handle role change
        const existingRoleIds: string[] = (res.data.role_ids ?? []).map(String);
        const newRoleId = selectedRoleId;
        const prevRoleId = existingRoleIds.length ? String(existingRoleIds[0]) : null;
        if (prevRoleId && prevRoleId !== newRoleId) {
          // remove old
          await api.delete(`/users/${editingId}/roles/${prevRoleId}`);
        }
        if (newRoleId && newRoleId !== prevRoleId) {
          await api.post(`/users/${editingId}/roles`, { role_id: newRoleId });
        }
      } else {
        payload.username = formData.username;
        payload.password = formData.password;
        const res = await api.post("/users", payload);
        const newUserId = res.data.id;
        if (selectedRoleId) {
          await api.post(`/users/${newUserId}/roles`, { role_id: selectedRoleId });
        }
        addToast("success", "User successfully created.");
      }
      handleCloseModal();
      fetchUsers();
    } catch (error: any) {
      console.error(error);
      addToast("error", error.response?.data?.detail || "Failed to save user.");
    } finally {
      setSaving(false);
    }
  };

  const columns: Column<User>[] = [
    { header: "Username", accessor: "username" },
    { header: "Full Name", accessor: "full_name" },
    { header: "Role", accessor: (row) => ((row as any).role_codes && (row as any).role_codes.length ? (row as any).role_codes[0] : '—'), width: '150px' },
    { header: "Email", accessor: "email" },
    { 
      header: "Status", 
      accessor: (row) => (
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.25rem",
            color: row.is_locked ? "#dc2626" : "#16a34a",
            fontWeight: 500,
            padding: "0.25rem 0.5rem",
            borderRadius: "999px",
            backgroundColor: row.is_locked ? "#fee2e2" : "#dcfce7"
          }}
        >
          {row.is_locked ? <Lock size={14} /> : <Unlock size={14} />}
          {row.is_locked ? "Locked" : "Active"}
        </span>
      ),
      width: "120px" 
    },
    { 
      header: "Last Login", 
      accessor: (row) => row.last_login_at ? new Date(row.last_login_at).toLocaleString() : "Never",
      width: "180px"
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
          <h1>Users</h1>
          <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
            Manage system users and access.
          </p>
        </div>

        <button 
          className="btn btn-primary"
          onClick={() => handleOpenModal()}
          style={{ display: "flex", alignItems: "center", gap: "0.5rem", height: "40px" }}
        >
          <Plus size={18} /> Add User
        </button>
      </div>

      <DataTable
        columns={columns}
        data={users}
        loading={loading}
      />

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingId ? "Edit User" : "Add User"}
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
          {!editingId && (
            <Input
              label="Username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              placeholder="jdoe"
              required
            />
          )}
          
          <Input
            label="Full Name"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            placeholder="John Doe"
            required
          />

          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="jdoe@example.com"
            required
          />

          {!editingId && (
            <Input
              label="Password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="••••••••"
              required
            />
          )}

          <Input
            label="Mobile Number"
            value={formData.mobile_number}
            onChange={(e) => setFormData({ ...formData, mobile_number: e.target.value })}
            placeholder="+1 234 567 8900"
          />

          <Select
            label="Role"
            value={selectedRoleId ?? ""}
            onChange={(e) => setSelectedRoleId(e.target.value || null)}
            options={[{ label: "(none)", value: "" }, ...(roles.map(r => ({ label: `${r.role_name} (${r.role_code})`, value: r.id })))]}
          />

          {editingId && (
            <Select
              label="Account Status"
              value={formData.is_locked ? "locked" : "active"}
              onChange={(e) => setFormData({ ...formData, is_locked: e.target.value === "locked" })}
              options={[
                { label: "Active", value: "active" },
                { label: "Locked", value: "locked" }
              ]}
            />
          )}
        </div>
      </Modal>
    </div>
  );
};
