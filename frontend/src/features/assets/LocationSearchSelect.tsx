import React, { useEffect, useState } from "react";
import { MapPin, Search, X } from "lucide-react";

import { api } from "../../services/api";

interface LocationSearchResult {
  id: string;
  code: string;
  name: string;
  location_type_name: string;
  hierarchy_path: string;
}

interface LocationSearchSelectProps {
  value: string | null;
  label?: string;
  selectedLabel?: string | null;
  projectId?: string;
  onChange: (locationId: string | null) => void;
}

export const LocationSearchSelect: React.FC<LocationSearchSelectProps> = ({
  value,
  label = "Current Location",
  selectedLabel,
  projectId,
  onChange,
}) => {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState<LocationSearchResult[]>([]);
  const [isOpen, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

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
        const response = await api.get<LocationSearchResult[]>("/infrastructure/locations/search", {
          params: { search: query, project_id: projectId || undefined, limit: 25 },
        });
        setResults(response.data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => window.clearTimeout(timeout);
  }, [projectId, search]);

  const selectedResult = results.find((item) => item.id === value);
  const displayLabel = selectedResult ? `${selectedResult.code} · ${selectedResult.name}` : selectedLabel;

  return (
    <div style={{ position: "relative", marginBottom: "1rem" }}>
      <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 500, color: "var(--text-secondary)", marginBottom: "0.5rem" }}>
        {label}
      </label>
      {value ? (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.75rem", padding: "0.7rem 0.85rem", border: "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", background: "var(--bg-tertiary)" }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.45rem", fontWeight: 700 }}><MapPin size={16} color="var(--accent-primary)" />{displayLabel || "Selected location"}</div>
            {selectedResult?.hierarchy_path && <div style={{ marginTop: "0.25rem", color: "var(--text-secondary)", fontSize: "0.8rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{selectedResult.hierarchy_path}</div>}
          </div>
          <button type="button" className="btn btn-secondary" onClick={() => { onChange(null); setSearch(""); }} style={{ padding: "0.4rem" }} aria-label="Clear location"><X size={16} /></button>
        </div>
      ) : (
        <>
          <div style={{ position: "relative" }}>
            <Search size={16} style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-secondary)" }} />
            <input
              className="form-input"
              value={search}
              onChange={(event) => { setSearch(event.target.value); setOpen(true); }}
              onFocus={() => setOpen(true)}
              placeholder="Search code or location name (min. 2 characters)"
              style={{ width: "100%", padding: "0.625rem 1rem 0.625rem 2.65rem" }}
            />
          </div>
          {isOpen && (
            <div style={{ position: "absolute", zIndex: 20, width: "100%", marginTop: "0.4rem", maxHeight: "280px", overflowY: "auto", background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", boxShadow: "0 12px 24px rgba(0,0,0,0.25)" }}>
              {search.trim().length < 2 ? <div style={{ padding: "0.85rem 1rem", color: "var(--text-secondary)", fontSize: "0.875rem" }}>Type at least 2 characters to search locations.</div>
                : loading ? <div style={{ padding: "0.85rem 1rem", color: "var(--text-secondary)", fontSize: "0.875rem" }}>Searching locations...</div>
                  : results.length === 0 ? <div style={{ padding: "0.85rem 1rem", color: "var(--text-secondary)", fontSize: "0.875rem" }}>No matching locations found.</div>
                    : results.map((item) => (
                      <button key={item.id} type="button" onClick={() => { onChange(item.id); setOpen(false); setSearch(""); }} style={{ display: "block", width: "100%", padding: "0.8rem 1rem", border: "none", borderBottom: "1px solid var(--border-color)", background: "transparent", color: "var(--text-primary)", textAlign: "left", cursor: "pointer" }}>
                        <div style={{ fontWeight: 700 }}>{item.code} · {item.name}</div>
                        <div style={{ marginTop: "0.2rem", color: "var(--text-secondary)", fontSize: "0.8rem" }}>{item.location_type_name} · {item.hierarchy_path}</div>
                      </button>
                    ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};
