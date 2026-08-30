import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, AlertTriangle, Clock, RefreshCw, Wrench, FileText, Package } from "lucide-react";

import { Input, Select } from "../../components/FormControls";
import { Tabs } from "../../components/Tabs";
import { Modal } from "../../components/Modal";
import { api } from "../../services/api";
import { useToast } from "../../contexts/ToastContext";
import { LocationSearchSelect } from "../assets/LocationSearchSelect";
import type { WorkRequest, WorkRequestUpdate, Paginated, Lookup } from "./types";

const fmt = (v?: string | null) => (v ? new Date(v).toLocaleString() : "—");
const fmtDate = (v?: string | null) => (v ? new Date(v).toLocaleDateString() : "—");

const Badge: React.FC<{ label: string; color?: string }> = ({ label, color = "var(--accent-color)" }) => (
  <span style={{
    display: "inline-block",
    padding: "0.2rem 0.7rem",
    borderRadius: "999px",
    background: `${color}22`,
    color,
    border: `1px solid ${color}55`,
    fontSize: "0.78rem",
    fontWeight: 600,
    letterSpacing: "0.03em",
  }}>{label}</span>
);

const Panel: React.FC<{ title: string; icon?: React.ReactNode; children: React.ReactNode }> = ({ title, icon, children }) => (
  <section className="glass-panel" style={{ padding: "1.4rem" }}>
    <h3 style={{ marginTop: 0, marginBottom: "1.1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
      {icon}{title}
    </h3>
    {children}
  </section>
);

const KV: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div>
    <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.2rem" }}>{label}</div>
    <div style={{ fontWeight: 600 }}>{value}</div>
  </div>
);

const Timeline: React.FC<{ updates: WorkRequestUpdate[]; statuses: Lookup[]; users: any[] }> = ({ updates, statuses, users }) => (
  <div style={{ display: "grid", gap: "0" }}>
    {updates.length === 0 && <div style={{ color: "var(--text-secondary)" }}>No work log entries recorded yet.</div>}
    {updates.map((item, i) => {
      const author = users.find(u => u.id === item.updated_by);
      const statusName = item.status_after_update_id
        ? statuses.find(s => Number(s.id) === item.status_after_update_id)?.name
        : null;
      return (
        <div key={item.id} style={{ display: "flex", gap: "1rem", paddingBottom: i < updates.length - 1 ? "1.2rem" : 0 }}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ width: "10px", height: "10px", borderRadius: "50%", background: "var(--accent-color)", flexShrink: 0, marginTop: "4px" }} />
            {i < updates.length - 1 && <div style={{ width: "2px", flex: 1, background: "var(--border-color)", margin: "4px 0" }} />}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", marginBottom: "0.25rem", flexWrap: "wrap" }}>
              <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{fmt(item.update_at || item.created_at)}</span>
              {author && <span style={{ fontSize: "0.82rem", fontWeight: 600 }}>{author.full_name || author.username}</span>}
              {statusName && <Badge label={statusName} />}
            </div>
            <div style={{ background: "var(--bg-secondary)", borderRadius: "var(--border-radius-md)", padding: "0.7rem 1rem", fontSize: "0.9rem" }}>{item.update_notes}</div>
          </div>
        </div>
      );
    })}
  </div>
);

type AffectedAsset = { id: string; asset_number: string; category: string; status: string; current_location?: string | null };
type AssetRecord = { basic_information: { asset_number: string; serial_number?: string | null; current_location?: string | null }; status: { name: string; code?: string }; category: { name: string }; model?: { name: string } | null };

export const WorkRequestDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [workRequest, setWorkRequest] = useState<WorkRequest | null>(null);
  const [updates, setUpdates] = useState<WorkRequestUpdate[]>([]);
  const [statuses, setStatuses] = useState<Lookup[]>([]);
  const [assetStatuses, setAssetStatuses] = useState<Lookup[]>([]);
  const [workTypes, setWorkTypes] = useState<Lookup[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [affectedAsset, setAffectedAsset] = useState<AssetRecord | null>(null);
  const [affectedAssets, setAffectedAssets] = useState<AffectedAsset[]>([]);
  const [loading, setLoading] = useState(true);

  // Work log form
  const [noteText, setNoteText] = useState("");
  const [noteStatus, setNoteStatus] = useState("");
  const [savingNote, setSavingNote] = useState(false);

  // Asset action
  const [actionOpen, setActionOpen] = useState(false);
  const [action, setAction] = useState("CHANGE_STATUS");
  const [actionStatus, setActionStatus] = useState("");
  const [actionLocation, setActionLocation] = useState<string | null>(null);
  const [actionReason, setActionReason] = useState("");
  const [savingAction, setSavingAction] = useState(false);
  const [actionPosition, setActionPosition] = useState("");
  const [installPositions, setInstallPositions] = useState<Array<{ id: string; position_number: string }>>([]);

  useEffect(() => {
    if (action === "INSTALL" && actionLocation) {
      api.get(`/infrastructure/locations/${actionLocation}/positions`)
        .then(res => setInstallPositions(res.data.items || []))
        .catch(() => setInstallPositions([]));
    } else {
      setInstallPositions([]);
      setActionPosition("");
    }
  }, [action, actionLocation]);

  const load = async () => {
    if (!id) return;
    try {
      const [wrRes, updRes, statusRes, assetStatusRes, workTypeRes, userRes] = await Promise.all([
        api.get<WorkRequest>(`/work-requests/${id}`),
        api.get<Paginated<WorkRequestUpdate>>(`/work-requests/${id}/updates`, { params: { page_size: 200 } }),
        api.get("/master/incident-status", { params: { page_size: 100 } }),
        api.get("/master/asset-status", { params: { page_size: 100 } }),
        api.get("/master/work-types", { params: { page_size: 100 } }),
        api.get("/users", { params: { page_size: 100 } }),
      ]);
      const wr = wrRes.data;
      setWorkRequest(wr);
      setUpdates(updRes.data.items);
      setStatuses(statusRes.data.items);
      setAssetStatuses(assetStatusRes.data.items);
      setWorkTypes(workTypeRes.data.items);
      setUsers(userRes.data.items);
      setNoteStatus(String(wr.incident_status_id));

      // Load affected asset / region assets
      if (wr.asset_id) {
        const assetRes = await api.get<AssetRecord>(`/assets/${wr.asset_id}`);
        setAffectedAsset(assetRes.data);
        setAffectedAssets([]);
      } else if (wr.location_id) {
        const assetsRes = await api.get<Paginated<AffectedAsset>>("/assets", { params: { page_size: 100, project_id: wr.project_id } });
        setAffectedAssets(assetsRes.data.items);
        setAffectedAsset(null);
      }
    } catch {
      addToast("error", "Could not load work request details.");
      navigate("/work-requests");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, [id]);

  const saveNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteText.trim()) return;
    const selectedStatusCode = statuses.find(s => String(s.id) === noteStatus)?.code;
    const isClosing = selectedStatusCode === "CLOSED" || selectedStatusCode === "RESOLVED";
    setSavingNote(true);
    try {
      await api.post(`/work-requests/${id}/updates`, {
        status_after_update_id: noteStatus ? Number(noteStatus) : null,
        update_notes: noteText,
      });
      setNoteText("");
      await load();
      addToast("success", isClosing ? "Work Request resolved/closed." : "Work log entry recorded.");
    } catch { addToast("error", "Could not save update."); }
    finally { setSavingNote(false); }
  };

  const applyAction = async () => {
    if (!workRequest?.asset_id) return;
    if (action === "INSTALL" && !actionPosition) {
      addToast("error", "Please select a position before recording an Install action.");
      return;
    }
    if ((action === "MOVE" || action === "UNINSTALL" || action === "RETURN_FROM_REPAIR") && !actionLocation) {
      addToast("error", "Please select a destination location.");
      return;
    }
    setSavingAction(true);
    try {
      await api.post(`/work-requests/${id}/asset-actions`, {
        asset_id: workRequest.asset_id,
        action,
        reason: actionReason,
        status_id: action === "CHANGE_STATUS" ? Number(actionStatus) : undefined,
        location_id: (action === "MOVE" || action === "UNINSTALL" || action === "RETURN_FROM_REPAIR") ? actionLocation || undefined : undefined,
        location_position_id: action === "INSTALL" ? actionPosition || undefined : undefined,
      });
      setActionOpen(false);
      setActionReason("");
      await load();
      addToast("success", "Asset action recorded against this work request.");
    } catch (err: any) {
      addToast("error", err.response?.data?.detail || "Action failed.");
    } finally { setSavingAction(false); }
  };

  if (loading) return <div className="glass-panel" style={{ padding: "2rem", textAlign: "center" }}>Loading work request details...</div>;
  if (!workRequest) return null;

  const statusName = statuses.find(s => Number(s.id) === workRequest.incident_status_id)?.name || "Unknown";
  const statusCode = (statuses.find(s => Number(s.id) === workRequest.incident_status_id) as any)?.code || "";
  const isClosed = statusCode === "CLOSED" || statusCode === "RESOLVED";

  const tabs = [
    {
      id: "overview",
      label: "Overview",
      content: (
        <div style={{ display: "grid", gap: "1.25rem" }}>
          <Panel title="Work Request Summary" icon={<AlertTriangle size={16} />}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1.1rem", marginBottom: "1rem" }}>
              <KV label="Status" value={<Badge label={statusName} color={isClosed ? "#22c55e" : "var(--accent-color)"} />} />              <KV label="Work Request Type" value={workTypes.find(wt => String(wt.id) === workRequest.work_type_id)?.name || "General"} />              <KV label="Requested" value={fmt(workRequest.reported_at)} />
              {isClosed && <KV label="Resolved" value={fmtDate(workRequest.closed_date)} />}
              <KV label="Target" value={workRequest.asset_id ? "Asset" : workRequest.location_id ? "Location / Region" : "General"} />
            </div>
            <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "1rem", color: "var(--text-secondary)" }}>
              {workRequest.description}
            </div>
            {isClosed && workRequest.resolution_remarks && (
              <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "1rem", marginTop: "1rem", color: "var(--text-secondary)" }}>
                <strong style={{ color: "var(--text-primary)" }}>Resolution Remarks:</strong>
                <p style={{ marginTop: "0.5rem", marginBottom: 0 }}>{workRequest.resolution_remarks}</p>
              </div>
            )}
          </Panel>
        </div>
      ),
    },
    {
      id: "affected",
      label: workRequest.asset_id ? "Affected Asset" : "Affected Region",
      content: (
        <div style={{ display: "grid", gap: "1.25rem" }}>
          {workRequest.asset_id ? (
            <Panel title="Affected Asset" icon={<Package size={16} />}>
              {affectedAsset ? (
                <>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1rem", marginBottom: "1rem" }}>
                    <KV label="Asset Number" value={affectedAsset.basic_information.asset_number} />
                    <KV label="Category" value={affectedAsset.category.name} />
                    <KV label="Model" value={affectedAsset.model?.name || "—"} />
                    <KV label="Status" value={<Badge label={affectedAsset.status.name} color={affectedAsset.status.code === "UNDER_REPAIR" ? "#f59e0b" : undefined} />} />
                    <KV label="Serial No." value={affectedAsset.basic_information.serial_number || "—"} />
                    <KV label="Location" value={affectedAsset.basic_information.current_location || "—"} />
                  </div>
                  <button className="btn btn-secondary" onClick={() => navigate(`/assets/${workRequest.asset_id}?work-request=${id}`)}>
                    Open Full Asset Record
                  </button>
                </>
              ) : <div style={{ color: "var(--text-secondary)" }}>Loading asset...</div>}
            </Panel>
          ) : (
            <Panel title="Assets in Affected Region" icon={<Package size={16} />}>
              {affectedAssets.length > 0 ? (
                <div style={{ display: "grid", gap: "0.75rem" }}>
                  {affectedAssets.map(asset => (
                    <button key={asset.id} type="button" className="glass-panel"
                      onClick={() => navigate(`/assets/${asset.id}?work-request=${id}`)}
                      style={{ textAlign: "left", padding: "0.9rem", border: "1px solid var(--border-color)", color: "inherit", cursor: "pointer" }}>
                      <strong>{asset.asset_number}</strong>
                      <div style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginTop: "0.2rem" }}>
                        {asset.category} · {asset.status} · {asset.current_location || "Location not recorded"}
                      </div>
                    </button>
                  ))}
                </div>
              ) : <div style={{ color: "var(--text-secondary)" }}>No assets registered at this location.</div>}
            </Panel>
          )}

          {workRequest.asset_id && (
            <Panel title="Controlled Asset Actions" icon={<Wrench size={16} />}>
              <p style={{ margin: "0 0 1rem", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                All asset changes during a work request are logged against this Work Request number. Direct asset editing is disabled in this context.
              </p>
              <button className="btn btn-primary" onClick={() => setActionOpen(true)} disabled={isClosed}>
                Record Asset Action
              </button>
              {isClosed && <p style={{ margin: "0.5rem 0 0", fontSize: "0.85rem", color: "var(--text-secondary)" }}>Work Request is closed. Asset actions are locked.</p>}
            </Panel>
          )}
        </div>
      ),
    },
    {
      id: "work-log",
      label: "Work Log",
      content: (
        <div style={{ display: "grid", gap: "1.25rem" }}>
          <Panel title={isClosed ? "Add Final Note" : "Add Work Log Entry"} icon={<FileText size={16} />}>
            <form onSubmit={saveNote} style={{ display: "grid", gap: "1rem" }}>
              <Select label="Update work request status to"
                value={noteStatus}
                onChange={e => setNoteStatus(e.target.value)}
                options={statuses.map(s => ({ value: String(s.id), label: s.name }))}
                disabled={isClosed} />
              <Input
                label={statuses.find(s => String(s.id) === noteStatus)?.code === "CLOSED" ? "Resolution Remarks *" : "Work log notes *"}
                value={noteText}
                onChange={e => setNoteText(e.target.value)}
                placeholder={statuses.find(s => String(s.id) === noteStatus)?.code === "CLOSED" ? "Detailed resolution reasoning..." : "Findings, root cause, corrective actions, next steps..."}
                required />
              <div>
                <button className="btn btn-primary" disabled={savingNote}>{savingNote ? "Saving..." : "Add Entry"}</button>
              </div>
            </form>
          </Panel>

          <Panel title="Work Log Timeline" icon={<Clock size={16} />}>
            <Timeline updates={[...updates].reverse()} statuses={statuses} users={users} />
          </Panel>
        </div>
      ),
    },
  ];

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", flexWrap: "wrap" }}>
        <div style={{ display: "flex", gap: "0.9rem", alignItems: "flex-start" }}>
          <button className="btn btn-secondary" style={{ padding: "0.65rem" }} onClick={() => navigate("/work-requests")}>
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 style={{ marginBottom: "0.25rem" }}>{workRequest.incident_number}</h1>
            <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
              <Badge label={statusName} color={isClosed ? "#22c55e" : "var(--accent-color)"} />
              <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                Requested {fmt(workRequest.reported_at)}
              </span>
            </div>
          </div>
        </div>
        <button className="btn btn-secondary" onClick={() => { setLoading(true); void load(); }}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="glass-panel" style={{ padding: "1.2rem" }}>
        <Tabs tabs={tabs} defaultTab="overview" />
      </div>

      {/* Asset Action Modal */}
      <Modal
        isOpen={actionOpen}
        onClose={() => setActionOpen(false)}
        title="Record Controlled Asset Action"
        footer={<>
          <button className="btn btn-secondary" onClick={() => setActionOpen(false)} disabled={savingAction}>Cancel</button>
          <button className="btn btn-primary" onClick={() => void applyAction()} disabled={savingAction || !actionReason.trim() || (action === "INSTALL" && !actionPosition) || (action === "MOVE" && !actionLocation) || (action === "UNINSTALL" && !actionLocation) || (action === "RETURN_FROM_REPAIR" && !actionLocation)}>
            {savingAction ? "Recording..." : "Record Action"}
          </button>
        </>}
      >
        <p style={{ margin: "0 0 1rem", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
          This action is logged against work request <strong>{workRequest.incident_number}</strong>.
        </p>
        <Select label="Action Type" value={action} onChange={e => { setAction(e.target.value); setActionLocation(null); setActionPosition(""); }}
          options={[
            { value: "CHANGE_STATUS", label: "Change Asset Status" },
            { value: "MOVE", label: "Move Asset to Location" },
            { value: "INSTALL", label: "Install Asset at Position" },
            { value: "UNINSTALL", label: "Uninstall Asset from Position" },
            { value: "SEND_FOR_REPAIR", label: "Send for Repair (OEM/Vendor)" },
            { value: "RETURN_FROM_REPAIR", label: "Return from Repair" },
          ]} />
        {action === "CHANGE_STATUS" && (
          <Select label="New Asset Status" value={actionStatus} onChange={e => setActionStatus(e.target.value)}
            options={[{ value: "", label: "Select status" }, ...assetStatuses.map(s => ({ value: String(s.id), label: s.name }))]}
            required />
        )}
        {action === "MOVE" && (
          <LocationSearchSelect label="Destination Location" value={actionLocation} projectId={workRequest.project_id}
            onChange={locId => setActionLocation(locId)} />
        )}
        {action === "INSTALL" && (
          <>
            <LocationSearchSelect label="Select Location" value={actionLocation} projectId={workRequest.project_id}
              onChange={locId => setActionLocation(locId)} />
            {actionLocation && (
              <Select label="Select Position" value={actionPosition} onChange={e => setActionPosition(e.target.value)}
                options={[{ value: "", label: "Select position" }, ...installPositions.map(p => ({ value: p.id, label: p.position_number }))]}
                required />
            )}
          </>
        )}
        {(action === "UNINSTALL" || action === "RETURN_FROM_REPAIR") && (
          <LocationSearchSelect label="Destination Store Location" value={actionLocation} projectId={workRequest.project_id}
            onChange={locId => setActionLocation(locId)} />
        )}
        <Input label="Reason / Notes" value={actionReason} onChange={e => setActionReason(e.target.value)}
          placeholder="Describe why this action is being taken" required />
      </Modal>
    </div>
  );
};
