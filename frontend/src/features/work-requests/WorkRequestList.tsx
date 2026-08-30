import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Search, AlertTriangle, CheckCircle, Clock, AlertCircle } from "lucide-react";

import { Input, Select, TextArea } from "../../components/FormControls";
import { Modal } from "../../components/Modal";
import { api } from "../../services/api";
import { useToast } from "../../contexts/ToastContext";
import { LocationSearchSelect } from "../assets/LocationSearchSelect";
import type { WorkRequest, Paginated, Lookup } from "./types";

type WorkRequestTarget = "asset" | "location";

const newForm = {
  project_id: "",
  work_type_id: "",
  incident_category_id: "",
  incident_priority_id: "",
  incident_status_id: "",
  asset_id: "",
  location_id: "",
  description: "",
  // Simple workflow additions
  requester_name: "",
  requester_email: "",
  acceptance_criteria: "",
  target_date: "",
  fast_track: false,
};

const priorityColor: Record<string, string> = {
  CRITICAL: "#dc2626",
  HIGH: "#ef4444",
  MEDIUM: "#f59e0b",
  LOW: "#22c55e",
};

const statusColor: Record<string, string> = {
  OPEN: "#3b82f6",
  IN_PROGRESS: "#f59e0b",
  RESOLVED: "#22c55e",
  CLOSED: "#6b7280",
  ON_HOLD: "#8b5cf6",
};

const Badge: React.FC<{ label: string; color?: string }> = ({ label, color = "#6b7280" }) => (
  <span style={{
    display: "inline-flex",
    alignItems: "center",
    padding: "0.15rem 0.6rem",
    borderRadius: "999px",
    background: `${color}22`,
    color,
    border: `1px solid ${color}44`,
    fontSize: "0.75rem",
    fontWeight: 600,
    whiteSpace: "nowrap",
  }}>{label}</span>
);

const PriorityIcon: React.FC<{ code?: string }> = ({ code }) => {
  if (code === "CRITICAL" || code === "HIGH") return <AlertTriangle size={14} style={{ color: priorityColor[code!] }} />;
  if (code === "LOW") return <CheckCircle size={14} style={{ color: "#22c55e" }} />;
  return <Clock size={14} style={{ color: "#f59e0b" }} />;
};

export const WorkRequestList: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [data, setData] = useState<Paginated<WorkRequest> | null>(null);
  const [search, setSearch] = useState("");
  const [isOpen, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [target, setTarget] = useState<WorkRequestTarget>("asset");

  const [projects, setProjects] = useState<Lookup[]>([]);
  const [workTypes, setWorkTypes] = useState<Lookup[]>([]);
  const [assets, setAssets] = useState<{ id: string; asset_number: string }[]>([]);
  const [categories, setCategories] = useState<Lookup[]>([]);
  const [priorities, setPriorities] = useState<Lookup[]>([]);
  const [statuses, setStatuses] = useState<Lookup[]>([]);
  const [form, setForm] = useState(newForm);

  const displayLabel = (r: any) => r?.name ?? r?.description ?? r?.project_name ?? r?.asset_number ?? String(r?.id ?? "");

  const lkOpts = (rows: Lookup[], placeholder: string) =>
    [{ value: "", label: placeholder }, ...rows.map(r => ({ value: String(r.id), label: displayLabel(r) }))];

  const defaultId = (rows: Lookup[], code: string) =>
    String(rows.find(r => r.code === code)?.id || "");

  const load = async () => {
    try {
      const res = await api.get<Paginated<WorkRequest>>("/work-requests", {
        params: { page_size: 100, search: search || undefined },
      });
      setData(res.data);
    } catch { addToast("error", "Could not load work requests."); }
  };

  useEffect(() => { void load(); }, [search]);

  useEffect(() => {
    void Promise.all([
      api.get("/common/projects", { params: { page_size: 100 } }),
      api.get("/master/work-types", { params: { page_size: 100 } }),
      api.get("/master/incident-categories", { params: { page_size: 100 } }),
      api.get("/master/incident-priority", { params: { page_size: 100 } }),
      api.get("/master/incident-status", { params: { page_size: 100 } }),
      api.get("/users", { params: { page_size: 100 } }),
    ]).then(([p, w, c, pr, s, _]) => {
      const wts = w.data.items as Lookup[];
      const cats = c.data.items as Lookup[];
      const pris = pr.data.items as Lookup[];
      const sts = s.data.items as Lookup[];
      setProjects(p.data.items.map((pj: any) => ({ id: pj.id, name: pj.project_code ? `${pj.project_code} · ${pj.project_name}` : pj.project_name })));
      setWorkTypes(wts);
      setCategories(cats);
      setPriorities(pris);
      setStatuses(sts);
      setForm(f => ({
        ...f,
        work_type_id: f.work_type_id || defaultId(wts, "INCIDENT"),
        incident_category_id: f.incident_category_id || defaultId(cats, "ASSET_FAILURE"),
        incident_priority_id: f.incident_priority_id || defaultId(pris, "MEDIUM"),
        incident_status_id: f.incident_status_id || defaultId(sts, "OPEN"),
      }));
    }).catch(() => addToast("error", "Could not load form options."));
  }, []);

  useEffect(() => {
    if (!form.project_id || target !== "asset") { setAssets([]); return; }
    void api.get<Paginated<{ id: string; asset_number: string }>>("/assets", { params: { page_size: 200, project_id: form.project_id } })
      .then(r => setAssets(r.data.items))
      .catch(() => setAssets([]));
  }, [form.project_id, target]);

  const openForm = () => {
    setTarget("asset");
    setForm({
      ...newForm,
      work_type_id: defaultId(workTypes, "INCIDENT"),
      incident_category_id: defaultId(categories, "ASSET_FAILURE"),
      incident_priority_id: defaultId(priorities, "MEDIUM"),
      incident_status_id: defaultId(statuses, "OPEN"),
    });
    // Auto-populate requester details from the currently authenticated user, if available
    api.get('/users/me').then(res => {
      const u = res.data;
      setForm(f => ({ ...f, requester_name: u.full_name || u.username || '', requester_email: u.email || '' }));
    }).catch(() => {
      // If user profile not available (not authenticated or endpoint missing), leave fields editable
    });
    setOpen(true);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
      // Minimal required validations for the simple workflow
      if (!form.acceptance_criteria) { addToast("error", "Please provide acceptance criteria."); return; }
      if (target === "asset" && !form.asset_id) { addToast("error", "Select the affected asset."); return; }
      if (target === "location" && !form.location_id) { addToast("error", "Select the affected location."); return; }
      setSaving(true);
      try {
        // Attempt to read the signed-in user's profile and include name/email in the payload.
        let requester_name_payload: string | null = form.requester_name || null;
        let requester_email_payload: string | null = form.requester_email || null;
        try {
          const ures = await api.get('/users/me');
          const u = ures.data || {};
          requester_name_payload = (u.full_name || u.username || requester_name_payload) ?? null;
          requester_email_payload = (u.email || requester_email_payload) ?? null;
        } catch {
          // ignore - fall back to any values present on the form
        }

        await api.post("/work-requests", {
          ...form,
          work_type_id: form.work_type_id || null,
          incident_category_id: Number(form.incident_category_id),
          incident_priority_id: Number(form.incident_priority_id),
          incident_status_id: Number(form.incident_status_id),
          asset_id: form.asset_id || null,
          location_id: form.location_id || null,
          // Simple workflow fields
          requester_name: requester_name_payload || null,
          requester_email: requester_email_payload || null,
          acceptance_criteria: form.acceptance_criteria || null,
          target_date: form.target_date || null,
          fast_track: !!form.fast_track,
        });
        setOpen(false);
        await load();
        addToast("success", "Work request registered.");
      } catch (err: any) {
        addToast("error", err.response?.data?.detail || "Could not register work request.");
      } finally { setSaving(false); }
    };

  const openCount = data?.items.filter(i => {
    const code = statuses.find(s => Number(s.id) === i.incident_status_id)?.code;
    return code !== "CLOSED" && code !== "RESOLVED";
  }).length || 0;

  const criticalCount = data?.items.filter(i => {
    const code = priorities.find(p => Number(p.id) === i.incident_priority_id)?.code;
    return code === "CRITICAL" || code === "HIGH";
  }).length || 0;

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h1>Work Requests</h1>
          <p style={{ color: "var(--text-secondary)", margin: 0 }}>
            Capture, track, and resolve operational work requests, service requests, and maintenance actions across all sites.
          </p>
        </div>
        <button className="btn btn-primary" onClick={openForm}>
          <Plus size={16} /> Register Work Request
        </button>
      </div>

      {/* Summary Badges */}
      {data && (
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <div className="glass-panel" style={{ padding: "1rem 1.4rem", display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <AlertCircle size={18} style={{ color: "#3b82f6" }} />
            <div>
              <div style={{ fontSize: "1.4rem", fontWeight: 700 }}>{openCount}</div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>Open</div>
            </div>
          </div>
          <div className="glass-panel" style={{ padding: "1rem 1.4rem", display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <AlertTriangle size={18} style={{ color: "#ef4444" }} />
            <div>
              <div style={{ fontSize: "1.4rem", fontWeight: 700 }}>{criticalCount}</div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>High / Critical</div>
            </div>
          </div>
          <div className="glass-panel" style={{ padding: "1rem 1.4rem", display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <CheckCircle size={18} style={{ color: "#22c55e" }} />
            <div>
              <div style={{ fontSize: "1.4rem", fontWeight: 700 }}>{data.total - openCount}</div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>Closed / Resolved</div>
            </div>
          </div>
        </div>
      )}

      {/* Search */}
      <div style={{ position: "relative" }}>
        <Search size={16} style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-secondary)", pointerEvents: "none" }} />
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by request number, description, asset, or location..."
          style={{
            width: "100%",
            padding: "0.65rem 1rem 0.65rem 2.4rem",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-color)",
            borderRadius: "var(--border-radius-md)",
            color: "inherit",
            fontSize: "0.9rem",
            boxSizing: "border-box",
          }}
        />
      </div>

      {/* WorkRequest Table */}
      <div className="glass-panel" style={{ padding: 0, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
              {['Work Request #', 'Type', 'Target', 'Status', 'Priority', 'Requested', 'Description'].map(h => (
                <th key={h} style={{ padding: "0.9rem 1rem", textAlign: "left", fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-secondary)", fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(data?.items || []).length === 0 && (
              <tr>
                <td colSpan={7} style={{ padding: "2rem", textAlign: "center", color: "var(--text-secondary)" }}>No work requests found.</td>
              </tr>
            )}
            {(data?.items || []).map(row => {
              const status = statuses.find(s => Number(s.id) === row.incident_status_id);
              const priority = priorities.find(p => Number(p.id) === row.incident_priority_id);
              const sColor = statusColor[status?.code || ""] || "#6b7280";
              const pColor = priorityColor[priority?.code || ""] || "#6b7280";
              const targetLabel = row.asset_id ? "Asset" : row.location_id ? "Location" : "General";
              const wtFound = workTypes.find(wt => String(wt.id) === row.work_type_id);
              const typeName = wtFound ? (wtFound.name || (wtFound as any).description || String(wtFound.id)) : (row.work_type_id || "General");
              return (
                <tr key={row.id} onClick={() => navigate(`/work-requests/${row.id}`)}
                  style={{ borderBottom: "1px solid var(--border-color)", cursor: "pointer", transition: "background 0.15s" }}
                  onMouseEnter={e => (e.currentTarget.style.background = "var(--bg-secondary)")}
                  onMouseLeave={e => (e.currentTarget.style.background = "transparent")}>
                  <td style={{ padding: "0.85rem 1rem", fontWeight: 700, fontSize: "0.9rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                      <PriorityIcon code={priority?.code} />
                      {row.incident_number}
                    </div>
                  </td>
                  <td style={{ padding: "0.85rem 1rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                    {typeName}
                  </td>
                  <td style={{ padding: "0.85rem 1rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                    {targetLabel}
                  </td>
                  <td style={{ padding: "0.85rem 1rem" }}>
                    <Badge label={status?.name || String(row.incident_status_id)} color={sColor} />
                  </td>
                  <td style={{ padding: "0.85rem 1rem" }}>
                    <Badge label={priority?.name || String(row.incident_priority_id)} color={pColor} />
                  </td>
                  <td style={{ padding: "0.85rem 1rem", fontSize: "0.85rem", color: "var(--text-secondary)", whiteSpace: "nowrap" }}>
                    {new Date(row.reported_at).toLocaleString()}
                  </td>
                  <td style={{ padding: "0.85rem 1rem", fontSize: "0.85rem", color: "var(--text-secondary)", maxWidth: "300px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {row.description}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Register Work Request Modal */}
      <Modal isOpen={isOpen} onClose={() => setOpen(false)} title="Register Work Request">
        <form onSubmit={submit} style={{ display: "grid", gap: "1.25rem" }}>
          <Select label="Project *" value={form.project_id}
            onChange={e => setForm({ ...form, project_id: e.target.value, asset_id: "", location_id: "" })}
            options={lkOpts(projects, "Select project")} required />

          <Select label="Work Request Type *" value={form.work_type_id}
            onChange={e => setForm({ ...form, work_type_id: e.target.value })}
            options={lkOpts(workTypes, "Select work request type")} required />

          <div className="glass-panel" style={{ padding: "1rem" }}>
            <strong>Affected Record</strong>
            <p style={{ margin: "0.4rem 0 0.85rem", color: "var(--text-secondary)", fontSize: "0.85rem" }}>
              Link this work request to an asset, a site location, or a broader operational request.
            </p>
            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button type="button" className={target === "asset" ? "btn btn-primary" : "btn btn-secondary"}
                onClick={() => { setTarget("asset"); setForm(f => ({ ...f, asset_id: "", location_id: "" })); }}>
                Affected Asset
              </button>
              <button type="button" className={target === "location" ? "btn btn-primary" : "btn btn-secondary"}
                onClick={() => { setTarget("location"); setForm(f => ({ ...f, asset_id: "", location_id: "" })); }}>
                Location / Position
              </button>
            </div>
          </div>

          {target === "asset" ? (
            <Select label="Affected Asset *" value={form.asset_id}
              onChange={e => setForm({ ...form, asset_id: e.target.value })}
              options={[{ value: "", label: form.project_id ? "Select affected asset" : "Select a project first" }, ...assets.map(a => ({ value: a.id, label: a.asset_number }))]}
              disabled={!form.project_id} required />
          ) : (
            <LocationSearchSelect label="Affected Location *" value={form.location_id} projectId={form.project_id}
              onChange={locId => setForm({ ...form, location_id: locId || "" })} />
          )}

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1rem" }}>
            <Select label="Category *" value={form.incident_category_id}
              onChange={e => setForm({ ...form, incident_category_id: e.target.value })}
              options={lkOpts(categories, "Select category")} required />
            <Select label="Priority *" value={form.incident_priority_id}
              onChange={e => setForm({ ...form, incident_priority_id: e.target.value })}
              options={lkOpts(priorities, "Select priority")} required />
            <Select label="Status *" value={form.incident_status_id}
              onChange={e => setForm({ ...form, incident_status_id: e.target.value })}
              options={lkOpts(statuses, "Select status")} required />
          </div>

          <Input label="Describe request *" value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })}
            placeholder="Describe the request, expected outcome, and any relevant details" required />


          <TextArea label="Acceptance Criteria *" value={form.acceptance_criteria}
            onChange={e => setForm({ ...form, acceptance_criteria: e.target.value })}
            placeholder="What needs to be achieved for this request to be accepted" required />

          <button className="btn btn-primary" disabled={saving}>
            {saving ? "Registering..." : "Register Work Request"}
          </button>
        </form>
      </Modal>
    </div>
  );
};
