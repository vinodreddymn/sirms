import React, { useEffect, useState } from "react";
import { Input } from "../../components/FormControls";
import { DataTable } from "../../components/DataTable";
import { api } from "../../services/api";

interface Movement { id: string; asset_id: string; asset_number: string; movement_type?: string | null; from_location?: string | null; to_location?: string | null; vendor?: string | null; moved_at: string; remarks?: string | null }

export const AssetMovementsPage: React.FC = () => {
  const [search, setSearch] = useState("");
  const [items, setItems] = useState<Movement[]>([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => { const timer = window.setTimeout(async () => { setLoading(true); try { const response = await api.get("/assets/movements", { params: { search, page_size: 50 } }); setItems(response.data.items); } finally { setLoading(false); } }, 250); return () => window.clearTimeout(timer); }, [search]);
  return <div style={{ display: "grid", gap: "1.5rem" }}><div><h1>Asset Movement History</h1><p style={{ color: "var(--text-secondary)" }}>Search movement records across all enrolled assets.</p></div><Input label="Search movements" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Asset number, movement, location, vendor, or remarks" /><DataTable columns={[{ header: "Asset", accessor: (item) => item.asset_number }, { header: "Movement", accessor: (item) => item.movement_type || "-" }, { header: "From", accessor: (item) => item.from_location || "-" }, { header: "To", accessor: (item) => item.to_location || "-" }, { header: "Date", accessor: (item) => new Date(item.moved_at).toLocaleString() }, { header: "Remarks", accessor: (item) => item.remarks || "-" }]} data={items} loading={loading} emptyMessage="No movement history found." /></div>;
};
