import React, { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Edit2, RefreshCw } from "lucide-react";

import { useToast } from "../../contexts/ToastContext";
import { api } from "../../services/api";
import { AssetForm } from "./AssetForm";
import { Modal } from "../../components/Modal";
import { Input } from "../../components/FormControls";
import { Tabs } from "../../components/Tabs";
import type { AssetDetails } from "./types";
import { AssetMovementHistory } from "./AssetMovementHistory";

const formatDate = (value?: string | null) => (value ? new Date(value).toLocaleDateString() : "-");

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className="glass-panel" style={{ padding: "1.4rem" }}>
    <h3 style={{ marginTop: 0, marginBottom: "1rem" }}>{title}</h3>
    {children}
  </section>
);

const DetailGrid: React.FC<{ items: Array<{ label: string; value: React.ReactNode }> }> = ({ items }) => (
  <div
    style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
      gap: "1rem",
    }}
  >
    {items.map((item) => (
      <div key={item.label}>
        <div style={{ color: "var(--text-secondary)", fontSize: "0.82rem", marginBottom: "0.35rem" }}>{item.label}</div>
        <div style={{ fontWeight: 600 }}>{item.value}</div>
      </div>
    ))}
  </div>
);

const RelationshipSection: React.FC<{ title: string; items: AssetDetails["related_assets"] }> = ({ title, items }) => (
  <Section title={title}>
    {items.length === 0 ? (
      <div style={{ color: "var(--text-secondary)" }}>No linked assets.</div>
    ) : (
      <div style={{ display: "grid", gap: "0.8rem" }}>
        {items.map((item) => (
          <div
            key={item.id}
            style={{
              padding: "0.9rem 1rem",
              border: "1px solid var(--border-color)",
              borderRadius: "var(--border-radius-md)",
            }}
          >
            <div style={{ fontWeight: 700 }}>{item.related_asset_number}</div>
            <div style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              {item.related_asset_name} {item.relationship_type ? `- ${item.relationship_type}` : ""}
            </div>
          </div>
        ))}
      </div>
    )}
  </Section>
);

export const AssetDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { addToast } = useToast();

  const [asset, setAsset] = useState<AssetDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEditModalOpen, setEditModalOpen] = useState(false);
  const [replacementOpen, setReplacementOpen] = useState(false);
  const [spareAssetId, setSpareAssetId] = useState("");
  const [spareSearch, setSpareSearch] = useState("");
  const [spareCandidates, setSpareCandidates] = useState<Array<{ id: string; asset_number: string; serial_number?: string | null; barcode?: string | null; qr_code?: string | null; status: string; current_location?: string | null }>>([]);
  const [replacementReason, setReplacementReason] = useState("");
  const [replacing, setReplacing] = useState(false);
  const [timeline, setTimeline] = useState<Array<{ id: string; event_type: string; event_at: string; description: string }>>([]);

  const loadAsset = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const response = await api.get<AssetDetails>(`/assets/${id}`);
      setAsset(response.data);
      const timelineResponse = await api.get<Array<{ id: string; event_type: string; event_at: string; description: string }>>(`/assets/${id}/timeline`);
      setTimeline(timelineResponse.data);
    } catch {
      addToast("error", "Failed to load asset details.");
      navigate("/assets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadAsset();
  }, [id]);

  useEffect(() => {
    if (!replacementOpen || !id) return;
    const timer = window.setTimeout(async () => {
      try {
        const response = await api.get(`/assets/${id}/replacement-candidates`, { params: { search: spareSearch } });
        setSpareCandidates(response.data);
      } catch {
        setSpareCandidates([]);
      }
    }, 250);
    return () => window.clearTimeout(timer);
  }, [replacementOpen, spareSearch, id]);

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: "2rem", textAlign: "center", color: "var(--text-secondary)" }}>
        Loading asset details...
      </div>
    );
  }

  if (!asset) return null;

  const basic = asset.basic_information;
  const incidentContext = new URLSearchParams(location.search).has("incident");
  const tabContentStyle: React.CSSProperties = { display: "grid", gap: "1.5rem" };
  const twoColumnStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "1.5rem",
  };

  const submitReplacement = async () => {
    if (!spareAssetId || !replacementReason.trim()) {
      addToast("error", "Select a spare asset ID and provide a replacement reason.");
      return;
    }
    setReplacing(true);
    try {
      await api.post(`/assets/${id}/replacement`, { spare_asset_id: spareAssetId, reason: replacementReason.trim() });
      addToast("success", "Replacement recorded and installation transferred.");
      setReplacementOpen(false);
      setSpareAssetId("");
      setReplacementReason("");
      await loadAsset();
    } catch (error: any) {
      addToast("error", error.response?.data?.detail || "Replacement could not be completed.");
    } finally {
      setReplacing(false);
    }
  };

  const tabs = [
    {
      id: "overview",
      label: "Overview",
      content: (
        <div style={tabContentStyle}>
          <Section title="Basic Information">
            {incidentContext && <p style={{ marginTop: 0, color: "var(--text-secondary)" }}>This asset was opened from an incident. Direct editing is disabled; use a controlled operational action and record the result in the incident.</p>}
            <DetailGrid
              items={[
                { label: "Project", value: asset.project.name },
                { label: "Asset Number", value: basic.asset_number },
                { label: "Category", value: asset.category.name },
                { label: "Subcategory", value: asset.subcategory?.name ?? "-" },
                { label: "Manufacturer", value: asset.manufacturer?.name ?? "-" },
                { label: "Model", value: asset.model?.name ?? "-" },
                { label: "Serial Number", value: basic.serial_number || "-" },
                { label: "Barcode", value: basic.barcode || "-" },
                { label: "QR Code", value: asset.qr_code || "-" },
              ]}
            />
          </Section>

          <Section title="Operational State & Lifecycle">
            <p style={{ margin: "0 0 1rem", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              Operational status shows whether the asset can be used now. Lifecycle stage shows its long-term stage of ownership and service.
            </p>
            <DetailGrid
              items={[
                { label: "Operational Status", value: asset.status.name },
                { label: "Condition", value: asset.condition?.name ?? "-" },
                { label: "Lifecycle Stage", value: asset.lifecycle?.name ?? "-" },
                { label: "Created", value: formatDate(basic.created_at) },
                { label: "Last Updated", value: formatDate(basic.updated_at) },
              ]}
            />
          </Section>

          <Section title="Installation Information">
            <DetailGrid
              items={[
                { label: "Current Location", value: basic.current_location || "-" },
                { label: "Installation Position", value: asset.installation?.position_name ?? "-" },
                { label: "Installation Status", value: asset.installation?.installation_status ?? "-" },
                { label: "Installation Date", value: formatDate(asset.installation?.installed_on) },
                { label: "Removed On", value: formatDate(asset.installation?.removed_on) },
                { label: "Installation Remarks", value: asset.installation?.remarks ?? "-" },
              ]}
            />
            {(asset.installation?.power_source || asset.installation?.electrical_panel || asset.installation?.network_switch || asset.installation?.switch_port || asset.installation?.patch_panel || asset.installation?.junction_box || asset.installation?.mounting_details) && (
              <>
                <p style={{ margin: "1rem 0 0.5rem", fontWeight: 600, fontSize: "0.875rem", color: "var(--text-secondary)", borderTop: "1px solid var(--border-color)", paddingTop: "0.75rem" }}>
                  Fixed Infrastructure (Position)
                </p>
                <DetailGrid
                  items={[
                    { label: "Power Source / UPS", value: asset.installation?.power_source ?? "-" },
                    { label: "Electrical Panel / Circuit", value: asset.installation?.electrical_panel ?? "-" },
                    { label: "Network Switch", value: asset.installation?.network_switch ?? "-" },
                    { label: "Switch Port", value: asset.installation?.switch_port ?? "-" },
                    { label: "Patch Panel", value: asset.installation?.patch_panel ?? "-" },
                    { label: "Junction Box", value: asset.installation?.junction_box ?? "-" },
                    { label: "Mounting Details", value: asset.installation?.mounting_details ?? "-" },
                  ].filter((item) => item.value !== "-")}
                />
              </>
            )}
          </Section>


          <Section title="Operational Notes">
            <DetailGrid items={[{ label: "Remarks", value: basic.remarks || "-" }]} />
          </Section>
        </div>
      ),
    },
    {
      id: "specifications",
      label: "Specifications",
      content: (
        <Section title="Dynamic Specifications">
          {asset.specifications.length === 0 ? (
            <div style={{ color: "var(--text-secondary)" }}>No specification values captured yet.</div>
          ) : (
            <div style={{ display: "grid", gap: "0.85rem" }}>
              {asset.specifications.map((item) => (
                <div
                  key={item.id}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "1rem",
                    padding: "0.9rem 1rem",
                    border: "1px solid var(--border-color)",
                    borderRadius: "var(--border-radius-md)",
                    flexWrap: "wrap",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 700 }}>{item.specification_name}</div>
                    <div style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                      {item.data_type} {item.unit ? `- ${item.unit}` : ""}
                    </div>
                  </div>
                  <div style={{ fontWeight: 600, maxWidth: "50%", wordBreak: "break-word" }}>
                    {typeof item.value === "object" && item.value !== null ? JSON.stringify(item.value) : String(item.value ?? "-")}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Section>
      ),
    },
    {
      id: "relationships",
      label: "Relationships",
      content: (
        <div style={tabContentStyle}>
          <div style={twoColumnStyle}>
            <RelationshipSection title="Power Sources" items={asset.power_sources} />
            <RelationshipSection title="Network Connections" items={asset.network_connections} />
            <RelationshipSection title="Parent Assets" items={asset.parent_assets} />
            <RelationshipSection title="Child Assets" items={asset.child_assets} />
          </div>
          <RelationshipSection title="Related Assets" items={asset.related_assets} />
        </div>
      ),
    },
    {
      id: "movement",
      label: "Movement",
      content: (
        <div style={tabContentStyle}>
          <Section title="Asset Timeline">
            {timeline.length === 0 ? (
              <div style={{ color: "var(--text-secondary)" }}>No recorded operational events yet.</div>
            ) : (
              <div style={{ display: "grid", gap: "0.75rem" }}>
                {timeline.map((event) => (
                  <div key={event.id} style={{ borderLeft: "3px solid var(--accent-primary)", paddingLeft: "0.8rem" }}>
                    <strong>{event.event_type.replaceAll("_", " ")}</strong>
                    <div>{event.description}</div>
                    <small style={{ color: "var(--text-secondary)" }}>{formatDate(event.event_at)}</small>
                  </div>
                ))}
              </div>
            )}
          </Section>
          <AssetMovementHistory items={asset.movement_history} />
        </div>
      ),
    },
    {
      id: "maintenance",
      label: "Maintenance",
      content: (
        <div style={twoColumnStyle}>
          <Section title="Maintenance Schedule">
            {asset.maintenance_schedules.length === 0 ? (
              <div style={{ color: "var(--text-secondary)" }}>No maintenance schedule configured.</div>
            ) : (
              <div style={{ display: "grid", gap: "0.8rem" }}>
                {asset.maintenance_schedules.map((item) => (
                  <div key={item.id} style={{ border: "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", padding: "1rem" }}>
                    <div style={{ fontWeight: 700 }}>{item.checklist_name}</div>
                    <div style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginTop: "0.3rem" }}>
                      Next due: {formatDate(item.next_due_date)} - Last maintenance: {formatDate(item.last_maintenance)}
                    </div>
                    <div style={{ marginTop: "0.4rem" }}>Frequency: {item.frequency_days ? `${item.frequency_days} days` : "-"}</div>
                    <div style={{ marginTop: "0.6rem", display: "grid", gap: "0.35rem" }}>
                      {item.tasks.map((task) => (
                        <div key={task.id} style={{ color: "var(--text-secondary)" }}>
                          {task.sequence_order}. {task.task_description} {task.is_required ? "(Required)" : ""}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Section>

          <Section title="Maintenance History">
            {asset.maintenance_history.length === 0 ? (
              <div style={{ color: "var(--text-secondary)" }}>No maintenance history recorded.</div>
            ) : (
              <div style={{ display: "grid", gap: "0.8rem" }}>
                {asset.maintenance_history.map((item) => (
                  <div key={item.id} style={{ border: "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", padding: "1rem" }}>
                    <div style={{ fontWeight: 700 }}>{item.checklist_name}</div>
                    <div style={{ color: "var(--text-secondary)", marginTop: "0.3rem" }}>
                      {formatDate(item.performed_on)} - {item.completed ? "Completed" : "Open"}
                    </div>
                    <div style={{ marginTop: "0.35rem" }}>{item.remarks || "No remarks"}</div>
                  </div>
                ))}
              </div>
            )}
          </Section>
        </div>
      ),
    },
    {
      id: "files",
      label: "Files",
      content: (
        <div style={twoColumnStyle}>
          <Section title="Documents">
            {asset.documents.length === 0 ? (
              <div style={{ color: "var(--text-secondary)" }}>No asset documents uploaded.</div>
            ) : (
              <div style={{ display: "grid", gap: "0.8rem" }}>
                {asset.documents.map((item) => (
                  <div key={item.id} style={{ border: "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", padding: "1rem" }}>
                    <div style={{ fontWeight: 700 }}>{item.file_name}</div>
                    <div style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginTop: "0.25rem" }}>
                      {item.document_type || "Document"} - {item.mime_type || "Unknown type"}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Section>

          <Section title="Photos">
            {asset.photos.length === 0 ? (
              <div style={{ color: "var(--text-secondary)" }}>No asset photos uploaded.</div>
            ) : (
              <div style={{ display: "grid", gap: "0.8rem" }}>
                {asset.photos.map((item) => (
                  <div key={item.id} style={{ border: "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", padding: "1rem" }}>
                    <div style={{ fontWeight: 700 }}>{item.file_name}</div>
                    <div style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginTop: "0.25rem" }}>{item.mime_type || "Photo"}</div>
                  </div>
                ))}
              </div>
            )}
          </Section>
        </div>
      ),
    },
  ];

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "1rem",
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", gap: "0.9rem", alignItems: "flex-start" }}>
          <button className="btn btn-secondary" onClick={() => navigate("/assets")} style={{ padding: "0.65rem" }}>
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 style={{ marginBottom: "0.35rem" }}>{basic.asset_number}</h1>
            <p style={{ margin: 0, color: "var(--text-secondary)" }}>
              {basic.category}
              {basic.subcategory ? ` - ${basic.subcategory}` : ""}
              {basic.model ? ` - ${basic.model}` : ""}
            </p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <button className="btn btn-secondary" onClick={() => void loadAsset()}>
            <RefreshCw size={16} />
            Refresh
          </button>
          {!incidentContext && (
            <button className="btn btn-primary" onClick={() => setEditModalOpen(true)}>
              <Edit2 size={16} />
              Edit Asset
            </button>
          )}
          <button className="btn btn-secondary" onClick={() => setReplacementOpen(true)}>Replace Asset</button>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: "1.2rem" }}>
        <Tabs tabs={tabs} defaultTab="overview" />
      </div>

      <AssetForm
        isOpen={isEditModalOpen}
        onClose={() => setEditModalOpen(false)}
        onSuccess={loadAsset}
        assetToEdit={asset}
      />
      <Modal isOpen={replacementOpen} onClose={() => setReplacementOpen(false)} title="Replace Faulty Asset" footer={<><button className="btn btn-secondary" onClick={() => setReplacementOpen(false)} disabled={replacing}>Cancel</button><button className="btn btn-primary" onClick={() => void submitReplacement()} disabled={replacing}>{replacing ? "Replacing..." : "Complete Replacement"}</button></>}>
        <p style={{ marginTop: 0, color: "var(--text-secondary)" }}>The selected spare inherits this asset's installation position. The faulty asset moves to Under Repair and both histories are recorded.</p>
        <Input label="Search Spare Asset" value={spareSearch} onChange={(event) => setSpareSearch(event.target.value)} placeholder="Asset no, serial, barcode, QR, or MAC address" />
        <div style={{ display: "grid", gap: "0.5rem", maxHeight: "220px", overflowY: "auto", marginBottom: "1rem" }}>
          {spareCandidates.map((candidate) => (
            <button key={candidate.id} type="button" onClick={() => setSpareAssetId(candidate.id)} style={{ textAlign: "left", padding: "0.7rem", border: candidate.id === spareAssetId ? "2px solid var(--accent-color)" : "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", background: "transparent", color: "inherit", cursor: "pointer" }}>
              <strong>{candidate.asset_number}</strong> - {candidate.serial_number || candidate.barcode || candidate.qr_code || "No identifier"}<br />
              <small style={{ color: "var(--text-secondary)" }}>{candidate.status} - {candidate.current_location || "Unassigned"}</small>
            </button>
          ))}
          {!spareCandidates.length && <span style={{ color: "var(--text-secondary)" }}>No spare assets found.</span>}
        </div>
        <Input label="Replacement Reason" value={replacementReason} onChange={(event) => setReplacementReason(event.target.value)} placeholder="e.g. Camera failed to power on" required />
      </Modal>
    </div>
  );
};
