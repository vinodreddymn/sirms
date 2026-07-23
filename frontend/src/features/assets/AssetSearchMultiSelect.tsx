import React, { useEffect, useState } from "react";
import { Search, X, Check } from "lucide-react";
import { api } from "../../services/api";
import type { AssetListItem, PaginatedResponse } from "./types";

interface AssetSearchMultiSelectProps {
  label: string;
  value: string[];
  onChange: (value: string[]) => void;
  categoryId?: number;
  placeholder?: string;
}

export const AssetSearchMultiSelect: React.FC<AssetSearchMultiSelectProps> = ({
  label,
  value,
  onChange,
  categoryId,
  placeholder = "Search by asset no, serial, barcode...",
}) => {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState<AssetListItem[]>([]);
  const [isOpen, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedAssets, setSelectedAssets] = useState<Record<string, string>>({});

  useEffect(() => {
    // Attempt to load names for already selected values if we don't have them
    // For simplicity, we just show the UUID if not loaded.
    const newSelected = { ...selectedAssets };
    let changed = false;
    value.forEach((val) => {
      if (!newSelected[val]) {
        newSelected[val] = val; // fallback to UUID
        changed = true;
      }
    });
    if (changed) {
      setSelectedAssets(newSelected);
    }
  }, [value, selectedAssets]);

  useEffect(() => {
    const query = search.trim();
    if (query.length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }
    const timeout = window.setTimeout(async () => {
      setLoading(true);
      try {
        const response = await api.get<PaginatedResponse<AssetListItem>>("/assets", {
          params: { search: query, category_id: categoryId, page_size: 25 },
        });
        setResults(response.data.items);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => window.clearTimeout(timeout);
  }, [search, categoryId]);

  const toggleSelection = (item: AssetListItem) => {
    const newSelected = { ...selectedAssets, [item.id]: item.asset_number };
    setSelectedAssets(newSelected);

    if (value.includes(item.id)) {
      onChange(value.filter((v) => v !== item.id));
    } else {
      onChange([...value, item.id]);
    }
  };

  const removeValue = (idToRemove: string) => {
    onChange(value.filter((v) => v !== idToRemove));
  };

  return (
    <div style={{ position: "relative", marginBottom: "1rem" }}>
      <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 500, color: "var(--text-secondary)", marginBottom: "0.5rem" }}>
        {label}
      </label>
      
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "0.5rem" }}>
        {value.map((id) => (
          <div key={id} style={{ display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.2rem 0.5rem", background: "var(--accent-primary)", color: "white", borderRadius: "4px", fontSize: "0.8rem", fontWeight: 500 }}>
            <span>{selectedAssets[id] || id}</span>
            <button type="button" onClick={() => removeValue(id)} style={{ background: "transparent", border: "none", color: "white", cursor: "pointer", display: "flex", padding: 0 }} aria-label="Remove">
              <X size={14} />
            </button>
          </div>
        ))}
      </div>

      <div style={{ position: "relative" }}>
        <Search size={16} style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-secondary)" }} />
        <input
          className="form-input"
          value={search}
          onChange={(event) => { setSearch(event.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          placeholder={placeholder}
          style={{ width: "100%", padding: "0.625rem 1rem 0.625rem 2.65rem" }}
        />
      </div>
      
      {isOpen && (
        <>
          <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, zIndex: 15 }} onClick={() => setOpen(false)} />
          <div style={{ position: "absolute", zIndex: 20, width: "100%", marginTop: "0.4rem", maxHeight: "280px", overflowY: "auto", background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", boxShadow: "0 12px 24px rgba(0,0,0,0.25)" }}>
            {search.trim().length < 2 ? <div style={{ padding: "0.85rem 1rem", color: "var(--text-secondary)", fontSize: "0.875rem" }}>Type at least 2 characters to search.</div>
              : loading ? <div style={{ padding: "0.85rem 1rem", color: "var(--text-secondary)", fontSize: "0.875rem" }}>Searching assets...</div>
                : results.length === 0 ? <div style={{ padding: "0.85rem 1rem", color: "var(--text-secondary)", fontSize: "0.875rem" }}>No matching assets found.</div>
                  : results.map((item) => {
                    const isSelected = value.includes(item.id);
                    return (
                      <button key={item.id} type="button" onClick={() => { toggleSelection(item); }} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%", padding: "0.8rem 1rem", border: "none", borderBottom: "1px solid var(--border-color)", background: isSelected ? "rgba(59,130,246,0.1)" : "transparent", color: "var(--text-primary)", textAlign: "left", cursor: "pointer" }}>
                        <div>
                          <div style={{ fontWeight: 700 }}>{item.asset_number}</div>
                          <div style={{ marginTop: "0.2rem", color: "var(--text-secondary)", fontSize: "0.8rem" }}>
                            {item.category} {item.serial_number ? `· SN: ${item.serial_number}` : ""} {item.barcode ? `· BC: ${item.barcode}` : ""}
                          </div>
                        </div>
                        {isSelected && <Check size={16} color="var(--accent-primary)" />}
                      </button>
                    );
                  })}
          </div>
        </>
      )}
    </div>
  );
};
