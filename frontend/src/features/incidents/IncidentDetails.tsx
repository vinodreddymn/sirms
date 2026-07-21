import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Input, Select } from "../../components/FormControls";
import { Tabs } from "../../components/Tabs";
import { api } from "../../services/api";
import { useToast } from "../../contexts/ToastContext";
import { LocationSearchSelect } from "../assets/LocationSearchSelect";
import type { Incident, IncidentUpdate, Paginated, WorkOrder } from "./types";

interface Lookup { id: number; name: string; }

export const LegacyIncidentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [updates, setUpdates] = useState<IncidentUpdate[]>([]);
  const [orders, setOrders] = useState<WorkOrder[]>([]);
  const [statuses, setStatuses] = useState<Lookup[]>([]);
  const [assetStatuses, setAssetStatuses] = useState<Lookup[]>([]);
  const [workOrderStatuses, setWorkOrderStatuses] = useState<Lookup[]>([]);
  const [note, setNote] = useState("");
  const [status, setStatus] = useState("");
  const [action, setAction] = useState("CHANGE_STATUS");
  const [actionStatus, setActionStatus] = useState("");
  const [actionLocation, setActionLocation] = useState("");
  const [actionReason, setActionReason] = useState("");
  const [savingAction, setSavingAction] = useState(false);
  const [users, setUsers] = useState<any[]>([]);
  const [assignee, setAssignee] = useState("");
  const [workOrderDesc, setWorkOrderDesc] = useState("");
  const [workOrderPlannedStart, setWorkOrderPlannedStart] = useState("");

  const load = async () => {
    if (!id) return;
    const [incidentResponse, updateResponse, orderResponse, statusResponse, assetStatusResponse, workOrderStatusResponse, usersResponse] = await Promise.all([
      api.get<Incident>(`/incidents/${id}`),
      api.get<Paginated<IncidentUpdate>>(`/incidents/${id}/updates`, { params: { page_size: 100 } }),
      api.get<Paginated<WorkOrder>>("/incidents/work-orders", { params: { page_size: 100 } }),
      api.get("/master/incident-status", { params: { page_size: 100 } }),
      api.get("/master/asset-status", { params: { page_size: 100 } }),
      api.get("/master/work-order-status", { params: { page_size: 100 } }),
      api.get("/users", { params: { page_size: 100 } }),
    ]);
    setIncident(incidentResponse.data);
    setUpdates(updateResponse.data.items);
    setOrders(orderResponse.data.items.filter((item) => item.incident_id === id));
    setStatuses(statusResponse.data.items);
    setAssetStatuses(assetStatusResponse.data.items);
    setWorkOrderStatuses(workOrderStatusResponse.data.items);
    setStatus(String(incidentResponse.data.incident_status_id));
    setAssignee(incidentResponse.data.assigned_to || "");
    setUsers(usersResponse.data.items);
  };

  useEffect(() => { void load(); }, [id]);

  if (!incident) return <div>Loading incident...</div>;

  const addUpdate = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await api.post(`/incidents/${id}/updates`, { status_after_update_id: status ? Number(status) : null, update_notes: note });
      setNote("");
      await load();
      addToast("success", "Incident update recorded.");
    } catch { addToast("error", "Could not save incident update."); }
  };

  const applyAssetAction = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!incident.asset_id) return;
    setSavingAction(true);
    try {
      await api.post(`/incidents/${id}/asset-actions`, {
        asset_id: incident.asset_id,
        action,
        reason: actionReason,
        status_id: action === "CHANGE_STATUS" ? Number(actionStatus) : undefined,
        location_id: action === "MOVE" ? actionLocation || undefined : undefined,
      });
      setActionReason("");
      setActionLocation("");
      await load();
      addToast("success", "Controlled asset action recorded against this incident.");
    } catch (error: any) { addToast("error", error.response?.data?.detail || "Asset action could not be completed."); }
    finally { setSavingAction(false); }
  };

  const assignIncident = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await api.put(`/incidents/${id}`, { assigned_to: assignee || null });
      await load();
      addToast("success", "Incident assigned successfully.");
    } catch { addToast("error", "Could not assign incident."); }
  };

  const createWorkOrder = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await api.post("/incidents/work-orders", {
        incident_id: id,
        remarks: workOrderDesc,
        planned_start_date: workOrderPlannedStart || undefined,
      });
      setWorkOrderDesc("");
      setWorkOrderPlannedStart("");
      await load();
      addToast("success", "Work order created.");
    } catch { addToast("error", "Could not create work order."); }
  };

  const statusOptions = statuses.map((item) => ({ value: item.id, label: item.name }));
  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <button className="btn btn-secondary" onClick={() => navigate("/incidents")}>Back to incidents</button>
      <div><h1>{incident.incident_number}</h1><p>{incident.description}</p></div>
      {incident.asset_id && <button className="btn btn-secondary" onClick={() => navigate(`/assets/${incident.asset_id}?incident=${id}`)}>Open affected asset</button>}

      <section className="glass-panel" style={{ padding: "1.4rem" }}>
        <h3>Assignment</h3>
        <form onSubmit={assignIncident} style={{ display: "flex", gap: "1rem", alignItems: "flex-end" }}>
          <div style={{ flex: 1 }}>
            <Select label="Assigned to" value={assignee} onChange={(event) => setAssignee(event.target.value)} options={[{ value: "", label: "Unassigned" }, ...users.map(u => ({ value: u.id, label: u.full_name || u.username }))]} />
          </div>
          <button className="btn btn-primary" type="submit">Assign</button>
        </form>
      </section>

      <section className="glass-panel" style={{ padding: "1.4rem" }}>
        <h3>Investigation update</h3>
        <form onSubmit={addUpdate}>
          <Select label="Incident status" value={status} onChange={(event) => setStatus(event.target.value)} options={statusOptions} />
          <Input label="Update notes" value={note} onChange={(event) => setNote(event.target.value)} required />
          <button className="btn btn-primary">Save update</button>
        </form>
      </section>

      {incident.asset_id && <section className="glass-panel" style={{ padding: "1.4rem" }}>
        <h3>Controlled Asset Action</h3>
        <p style={{ color: "var(--text-secondary)" }}>Every action is logged against this incident; direct asset editing remains unavailable in this context.</p>
        <form onSubmit={applyAssetAction}>
          <Select label="Action" value={action} onChange={(event) => setAction(event.target.value)} options={[{ value: "CHANGE_STATUS", label: "Change asset status" }, { value: "MOVE", label: "Move asset" }, { value: "SEND_FOR_REPAIR", label: "Send for repair" }]} />
          {action === "CHANGE_STATUS" && <Select label="New asset status" value={actionStatus} onChange={(event) => setActionStatus(event.target.value)} options={[{ value: "", label: "Select status" }, ...assetStatuses.map((item) => ({ value: item.id, label: item.name }))]} required />}
          {action === "MOVE" && <LocationSearchSelect label="Destination location" value={actionLocation || null} projectId={incident.project_id} onChange={(locationId) => setActionLocation(locationId || "")} />}
          <Input label="Reason" value={actionReason} onChange={(event) => setActionReason(event.target.value)} placeholder="Describe the operational action" required />
          <button className="btn btn-primary" disabled={savingAction}>{savingAction ? "Recording..." : "Record asset action"}</button>
        </form>
      </section>}

      <section className="glass-panel" style={{ padding: "1.4rem" }}>
        <h3>History</h3>
        {updates.length ? updates.map((item) => <div key={item.id} style={{ padding: "0.8rem 0", borderBottom: "1px solid var(--border-color)" }}><strong>{new Date(item.update_at || item.created_at).toLocaleString()}</strong><div>{item.update_notes}</div></div>) : <span>No updates recorded.</span>}
      </section>

      <section className="glass-panel" style={{ padding: "1.4rem" }}>
        <h3>Work orders</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginBottom: "1.5rem" }}>
          {orders.length ? orders.map((item) => (
            <div key={item.id} style={{ padding: "1rem", background: "var(--bg-primary)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)" }}>
              <strong>{item.work_order_number}</strong>
              {item.remarks && <p style={{ margin: "0.5rem 0" }}>{item.remarks}</p>}
              <div style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>
                {item.assigned_to && <span>Assigned to: {users.find(u => u.id === item.assigned_to)?.full_name || "User"} • </span>}
                <span>Status: {workOrderStatuses.find((statusItem) => statusItem.id === item.status_id)?.name || item.status_id} • </span>
                {item.planned_start_date && <span>Planned Start: {new Date(item.planned_start_date).toLocaleDateString()}</span>}
              </div>
            </div>
          )) : <span>No work order linked yet.</span>}
        </div>
        
        <h4>Create Work Order</h4>
        <form onSubmit={createWorkOrder}>
          <Input label="Description / Remarks" value={workOrderDesc} onChange={(event) => setWorkOrderDesc(event.target.value)} required />
          <Input label="Planned Start Date" type="date" value={workOrderPlannedStart} onChange={(event) => setWorkOrderPlannedStart(event.target.value)} />
          <button className="btn btn-primary" type="submit">Create Work Order</button>
        </form>
      </section>
    </div>
  );
};

type AffectedAsset = { id: string; asset_number: string; category: string; status: string; current_location?: string | null; serial_number?: string | null };
type AssetRecord = { basic_information: { asset_number: string; serial_number?: string | null; current_location?: string | null }; status: { name: string }; condition?: { name: string } | null; category: { name: string }; model?: { name: string } | null };

const Panel: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => <section className="glass-panel" style={{ padding: "1.4rem" }}><h3 style={{ marginTop: 0 }}>{title}</h3>{children}</section>;

export const IncidentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>(); const navigate = useNavigate(); const { addToast } = useToast();
  const [incident, setIncident] = useState<Incident | null>(null); const [updates, setUpdates] = useState<IncidentUpdate[]>([]); const [orders, setOrders] = useState<WorkOrder[]>([]); const [statuses, setStatuses] = useState<Lookup[]>([]); const [users, setUsers] = useState<any[]>([]); const [affectedAsset, setAffectedAsset] = useState<AssetRecord | null>(null); const [affectedAssets, setAffectedAssets] = useState<AffectedAsset[]>([]); const [note, setNote] = useState(""); const [status, setStatus] = useState(""); const [assignee, setAssignee] = useState(""); const [workOrderDesc, setWorkOrderDesc] = useState(""); const [workOrderPlannedStart, setWorkOrderPlannedStart] = useState("");
  const load = async () => { if (!id) return; try { const [incidentResponse, updateResponse, orderResponse, statusResponse, usersResponse] = await Promise.all([api.get<Incident>(`/incidents/${id}`), api.get<Paginated<IncidentUpdate>>(`/incidents/${id}/updates`, { params: { page_size: 100 } }), api.get<Paginated<WorkOrder>>("/incidents/work-orders", { params: { page_size: 100 } }), api.get("/master/incident-status", { params: { page_size: 100 } }), api.get("/users", { params: { page_size: 100 } })]); const currentIncident = incidentResponse.data; setIncident(currentIncident); setUpdates(updateResponse.data.items); setOrders(orderResponse.data.items.filter((order) => order.incident_id === id)); setStatuses(statusResponse.data.items); setUsers(usersResponse.data.items); setStatus(String(currentIncident.incident_status_id)); setAssignee(currentIncident.assigned_to || ""); if (currentIncident.asset_id) { const assetResponse = await api.get<AssetRecord>(`/assets/${currentIncident.asset_id}`); setAffectedAsset(assetResponse.data); setAffectedAssets([]); } else if (currentIncident.location_id) { const assetsResponse = await api.get<Paginated<AffectedAsset>>("/assets", { params: { page_size: 100, project_id: currentIncident.project_id, location_id: currentIncident.location_id } }); setAffectedAssets(assetsResponse.data.items); setAffectedAsset(null); } } catch (error: any) { addToast("error", error.response?.data?.detail || "Could not load incident details."); navigate("/incidents"); } };
  useEffect(() => { void load(); }, [id]);
  const saveUpdate = async (event: React.FormEvent) => { event.preventDefault(); try { await api.post(`/incidents/${id}/updates`, { status_after_update_id: Number(status), update_notes: note }); setNote(""); await load(); addToast("success", "Investigation update recorded."); } catch (error: any) { addToast("error", error.response?.data?.detail || "Could not save incident update."); } };
  const saveAssignment = async (event: React.FormEvent) => { event.preventDefault(); try { await api.put(`/incidents/${id}`, { assigned_to: assignee || null }); await load(); addToast("success", "Incident assignment updated."); } catch { addToast("error", "Could not update assignment."); } };
  const createWorkOrder = async (event: React.FormEvent) => { event.preventDefault(); try { await api.post("/incidents/work-orders", { incident_id: id, remarks: workOrderDesc, planned_start_date: workOrderPlannedStart || undefined }); setWorkOrderDesc(""); setWorkOrderPlannedStart(""); await load(); addToast("success", "Work order created."); } catch { addToast("error", "Could not create work order."); } };
  if (!incident) return <div className="glass-panel" style={{ padding: "2rem" }}>Loading incident details...</div>;
  const statusName = statuses.find((item) => item.id === incident.incident_status_id)?.name || incident.incident_status_id;
  const assignedName = users.find((user) => user.id === incident.assigned_to)?.full_name || "Unassigned";
  const tabs = [{ id: "overview", label: "Overview", content: <div style={{ display: "grid", gap: "1.25rem" }}><Panel title="Incident Summary"><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}><div><small>Status</small><strong style={{ display: "block" }}>{statusName}</strong></div><div><small>Assigned to</small><strong style={{ display: "block" }}>{assignedName}</strong></div><div><small>Reported</small><strong style={{ display: "block" }}>{new Date(incident.reported_at).toLocaleString()}</strong></div><div><small>Target</small><strong style={{ display: "block" }}>{incident.asset_id ? "Asset" : "Location / region"}</strong></div></div><p style={{ marginBottom: 0 }}>{incident.description}</p></Panel><Panel title="Assignment"><form onSubmit={saveAssignment} style={{ display: "flex", gap: "1rem", alignItems: "flex-end", flexWrap: "wrap" }}><div style={{ flex: 1, minWidth: "220px" }}><Select label="Assigned to" value={assignee} onChange={(event) => setAssignee(event.target.value)} options={[{ value: "", label: "Unassigned" }, ...users.map((user) => ({ value: user.id, label: user.full_name || user.username }))]} /></div><button className="btn btn-primary">Save assignment</button></form></Panel></div> }, { id: "affected", label: incident.asset_id ? "Affected Asset" : "Affected Region", content: incident.asset_id ? <Panel title="Affected Asset Details">{affectedAsset ? <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem" }}><div><small>Asset number</small><strong style={{ display: "block" }}>{affectedAsset.basic_information.asset_number}</strong></div><div><small>Category</small><strong style={{ display: "block" }}>{affectedAsset.category.name}</strong></div><div><small>Model</small><strong style={{ display: "block" }}>{affectedAsset.model?.name || "-"}</strong></div><div><small>Operational status</small><strong style={{ display: "block" }}>{affectedAsset.status.name}</strong></div><div><small>Location</small><strong style={{ display: "block" }}>{affectedAsset.basic_information.current_location || "-"}</strong></div></div> : <span>Loading affected asset...</span>}<button className="btn btn-secondary" style={{ marginTop: "1rem" }} onClick={() => navigate(`/assets/${incident.asset_id}?incident=${id}`)}>Open full asset record</button></Panel> : <Panel title="Assets in the Affected Region">{affectedAssets.length ? <div style={{ display: "grid", gap: "0.75rem" }}>{affectedAssets.map((asset) => <button key={asset.id} className="glass-panel" type="button" onClick={() => navigate(`/assets/${asset.id}?incident=${id}`)} style={{ textAlign: "left", padding: "0.9rem", border: "1px solid var(--border-color)", color: "inherit", cursor: "pointer" }}><strong>{asset.asset_number}</strong><div style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>{asset.category} · {asset.status} · {asset.current_location || "Location not recorded"}</div></button>)}</div> : <span>No assets are currently registered at this location.</span>}</Panel> }, { id: "investigation", label: "Investigation", content: <div style={{ display: "grid", gap: "1.25rem" }}><Panel title="Record Investigation Update"><form onSubmit={saveUpdate}><Select label="Incident status" value={status} onChange={(event) => setStatus(event.target.value)} options={statuses.map((item) => ({ value: item.id, label: item.name }))} /><Input label="Update notes" value={note} onChange={(event) => setNote(event.target.value)} placeholder="Findings, immediate controls, and next action" required /><button className="btn btn-primary">Save update</button></form></Panel><Panel title="Investigation History">{updates.length ? updates.map((update) => <div key={update.id} style={{ padding: "0.8rem 0", borderBottom: "1px solid var(--border-color)" }}><strong>{new Date(update.update_at || update.created_at).toLocaleString()}</strong><div>{update.update_notes}</div></div>) : <span>No updates recorded.</span>}</Panel></div> }, { id: "work-orders", label: "Work Orders", content: <div style={{ display: "grid", gap: "1.25rem" }}><Panel title="Linked Work Orders">{orders.length ? orders.map((order) => <div key={order.id} style={{ padding: "0.85rem 0", borderBottom: "1px solid var(--border-color)" }}><strong>{order.work_order_number}</strong><div>{order.remarks || "No remarks"}</div></div>) : <span>No work orders linked yet.</span>}</Panel><Panel title="Create Work Order"><form onSubmit={createWorkOrder}><Input label="Description / remarks" value={workOrderDesc} onChange={(event) => setWorkOrderDesc(event.target.value)} required /><Input label="Planned start date" type="date" value={workOrderPlannedStart} onChange={(event) => setWorkOrderPlannedStart(event.target.value)} /><button className="btn btn-primary">Create work order</button></form></Panel></div> }];
  return <div style={{ display: "grid", gap: "1.5rem" }}><button className="btn btn-secondary" style={{ justifySelf: "start" }} onClick={() => navigate("/incidents")}>Back to incidents</button><div><h1 style={{ marginBottom: "0.35rem" }}>{incident.incident_number}</h1><p style={{ margin: 0, color: "var(--text-secondary)" }}>{incident.description}</p></div><Tabs tabs={tabs} /></div>;
};
