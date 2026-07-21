import React, { useMemo, useState } from "react";

import { DataTable } from "../../components/DataTable";
import { Modal } from "../../components/Modal";
import { Input } from "../../components/FormControls";
import type { AssetMovementHistory as AssetMovementHistoryItem } from "./types";

interface AssetMovementHistoryProps {
  items: AssetMovementHistoryItem[];
}

const formatDate = (value: string) => new Date(value).toLocaleString();

export const AssetMovementHistory: React.FC<AssetMovementHistoryProps> = ({ items }) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const normalizedSearch = search.trim().toLowerCase();
  const filteredItems = useMemo(
    () => items.filter((item) => !normalizedSearch || [item.movement_type, item.from_location, item.to_location, item.vendor, item.remarks].some((value) => value?.toLowerCase().includes(normalizedSearch))),
    [items, normalizedSearch],
  );

  return (
    <>
      <section className="glass-panel" style={{ padding: "1.4rem", display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h3 style={{ margin: 0 }}>Movement History</h3>
          <div style={{ color: "var(--text-secondary)", marginTop: "0.35rem" }}>{items.length} recorded movement{items.length === 1 ? "" : "s"}</div>
        </div>
        <button type="button" className="btn btn-secondary" onClick={() => setOpen(true)} disabled={!items.length}>Open Movement History</button>
      </section>
      <Modal isOpen={open} onClose={() => setOpen(false)} title="Asset Movement History" maxWidth="1100px">
        <Input label="Search history" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Movement type, location, vendor, or remarks" />
        <div style={{ marginTop: "1rem" }}>
          <DataTable
            columns={[
              { header: "Date", accessor: (item) => formatDate(item.moved_at), width: "18%" },
              { header: "Movement", accessor: (item) => item.movement_type || "-", width: "16%" },
              { header: "From", accessor: (item) => item.from_location || "-" },
              { header: "To", accessor: (item) => item.to_location || "-" },
              { header: "Vendor", accessor: (item) => item.vendor || "-" },
              { header: "Remarks", accessor: (item) => item.remarks || "-" },
            ]}
            data={filteredItems}
            emptyMessage="No movement records match the search."
          />
        </div>
      </Modal>
    </>
  );
};
