import React, { useEffect, useState } from "react";
import { DataTable } from "../../../components/DataTable";
import type { Column } from "../../../components/DataTable";
import { api } from "../../../services/api";
import { useToast } from "../../../contexts/ToastContext";

interface LoginHistory {
  id: string;
  user_id: string;
  username: string;
  login_at: string;
  logout_at?: string;
  login_status: string;
  ip_address?: string;
  device_info?: string;
  remarks?: string;
}

export const AuditList: React.FC = () => {
  const [history, setHistory] = useState<LoginHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const { addToast } = useToast();

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await api.get("/audit/login-history", { params: { page_size: 100 } });
      setHistory(response.data.items ?? []);
    } catch (error) {
      console.error(error);
      addToast("error", "Failed to load login history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const formatDateToLocal = (dateString?: string) => {
    if (!dateString) return "-";
    // Using Date object will automatically parse UTC (if provided by backend) 
    // and convert to the user's local timezone for display.
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const columns: Column<LoginHistory>[] = [
    { header: "Username", accessor: "username", width: "150px" },
    { 
      header: "Login Time (Local)", 
      accessor: (row) => formatDateToLocal(row.login_at),
      width: "200px" 
    },
    { 
      header: "Logout Time (Local)", 
      accessor: (row) => formatDateToLocal(row.logout_at),
      width: "200px" 
    },
    { 
      header: "Status", 
      accessor: (row) => (
        <span style={{ 
          color: row.login_status === 'SUCCESS' ? '#16a34a' : '#dc2626',
          fontWeight: 500 
        }}>
          {row.login_status}
        </span>
      ),
      width: "120px" 
    },
    { header: "IP Address", accessor: "ip_address", width: "140px" },
    { header: "Device", accessor: "device_info", width: "200px" },
    { header: "Remarks", accessor: "remarks" },
  ];

  return (
    <div style={{ padding: '1.5rem' }}>
      <div style={{ marginBottom: '20px' }}>
        <h1>Login History</h1>
        <p style={{ color: 'var(--text-muted)' }}>View system login activity and audit logs.</p>
      </div>
      
      <DataTable
        columns={columns}
        data={history}
        loading={loading}
      />
    </div>
  );
};
