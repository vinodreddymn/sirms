import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  CheckCircle,
  Download,
  Eye,
  LayoutGrid,
  List,
  MapPin,
  Package,
  Plus,
  RefreshCw,
  Search,
  Wrench,
  XCircle,
} from "lucide-react";

import { DataTable } from "../../components/DataTable";
import type { Column } from "../../components/DataTable";
import { Input, Select } from "../../components/FormControls";
import { useToast } from "../../contexts/ToastContext";
import { api } from "../../services/api";
import { AssetForm } from "./AssetForm";
import { LocationSearchSelect } from "./LocationSearchSelect";
import type {
  AssetListItem,
  AssetSummary,
  LookupOption,
  PaginatedResponse,
} from "./types";

interface LookupApiRow {
  id: number | string;
  code?: string | null;
  name: string;
}

interface QueryState {
  page: number;
  page_size: number;
  search: string;
  sort: string;
  order: "asc" | "desc";
  project_id: string;
  category_id: string;
  subcategory_id: string;
  manufacturer_id: string;
  model_id: string;
  status_id: string;
  condition_id: string;
  lifecycle_id: string;
  location_id: string;
  warranty_status: string;
}

const initialQuery: QueryState = {
  page: 1,
  page_size: 10,
  search: "",
  sort: "created_at",
  order: "desc",
  project_id: "",
  category_id: "",
  subcategory_id: "",
  manufacturer_id: "",
  model_id: "",
  status_id: "",
  condition_id: "",
  lifecycle_id: "",
  location_id: "",
  warranty_status: "",
};

const LOOKUP_PAGE_SIZE = 100;

const formatDate = (value?: string | null) => {
  if (!value) return "-";
  return new Date(value).toLocaleDateString();
};

const formatBadge = (label?: string | null, tone: "status" | "condition" = "status") => {
  if (!label) return "-";
  const normalized = label.toLowerCase();
  const palette =
    tone === "condition"
      ? normalized.includes("excellent")
        ? { bg: "rgba(34,197,94,0.18)", color: "#86efac" }
        : normalized.includes("fair")
          ? { bg: "rgba(245,158,11,0.18)", color: "#fcd34d" }
          : normalized.includes("poor")
            ? { bg: "rgba(239,68,68,0.18)", color: "#fca5a5" }
            : { bg: "rgba(148,163,184,0.18)", color: "#cbd5e1" }
      : normalized.includes("active")
        ? { bg: "rgba(34,197,94,0.18)", color: "#86efac" }
        : normalized.includes("repair")
          ? { bg: "rgba(245,158,11,0.18)", color: "#fcd34d" }
          : normalized.includes("retired")
            ? { bg: "rgba(239,68,68,0.18)", color: "#fca5a5" }
            : { bg: "rgba(148,163,184,0.18)", color: "#cbd5e1" };

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0.35rem 0.75rem",
        borderRadius: "999px",
        background: palette.bg,
        color: palette.color,
        fontWeight: 700,
        fontSize: "0.75rem",
        whiteSpace: "nowrap",
      }}
    >
      {label}
    </span>
  );
};

const formatWarranty = (value?: string | null) => {
  if (!value) return "-";
  const dateValue = new Date(value);
  const daysRemaining = Math.ceil((dateValue.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
  const color =
    daysRemaining < 0 ? "#fca5a5" : daysRemaining <= 90 ? "#fcd34d" : "#bfdbfe";
  return <span style={{ color, fontWeight: 700 }}>{dateValue.toLocaleDateString()}</span>;
};

const toLookupOptions = (rows: LookupApiRow[]): LookupOption[] =>
  rows.map((row) => ({
    id: String(row.id),
    code: row.code,
    name: row.name,
  }));

const toSelectOptions = (rows: LookupOption[], emptyLabel: string) => [
  { label: emptyLabel, value: "" },
  ...rows.map((row) => ({ label: row.name, value: row.id })),
];

export const AssetList: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [query, setQuery] = useState<QueryState>(initialQuery);
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [assets, setAssets] = useState<PaginatedResponse<AssetListItem> | null>(null);
  const [summary, setSummary] = useState<AssetSummary | null>(null);
  const [isModalOpen, setModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState<"field" | "register">("field");

  const [projects, setProjects] = useState<LookupOption[]>([]);
  const [categories, setCategories] = useState<LookupOption[]>([]);
  const [subcategories, setSubcategories] = useState<LookupOption[]>([]);
  const [manufacturers, setManufacturers] = useState<LookupOption[]>([]);
  const [models, setModels] = useState<LookupOption[]>([]);
  const [statuses, setStatuses] = useState<LookupOption[]>([]);
  const [conditions, setConditions] = useState<LookupOption[]>([]);
  const [lifecycles, setLifecycles] = useState<LookupOption[]>([]);

  const requestParams = useMemo(
    () => ({
      ...query,
      search: query.search || undefined,
      project_id: query.project_id || undefined,
      category_id: query.category_id || undefined,
      subcategory_id: query.subcategory_id || undefined,
      manufacturer_id: query.manufacturer_id || undefined,
      model_id: query.model_id || undefined,
      status_id: query.status_id || undefined,
      condition_id: query.condition_id || undefined,
      lifecycle_id: query.lifecycle_id || undefined,
      location_id: query.location_id || undefined,
      warranty_status: query.warranty_status || undefined,
    }),
    [query],
  );

  const loadList = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get<PaginatedResponse<AssetListItem>>("/assets", { params: requestParams });
      setAssets(response.data);
    } catch {
      addToast("error", "Unable to load assets.");
    } finally {
      setLoading(false);
    }
  }, [addToast, requestParams]);

  const loadSummary = useCallback(async () => {
    setSummaryLoading(true);
    try {
      const response = await api.get<AssetSummary>("/assets/summary", { params: requestParams });
      setSummary(response.data);
    } catch {
      addToast("error", "Unable to load asset summary.");
    } finally {
      setSummaryLoading(false);
    }
  }, [addToast, requestParams]);

  const loadLookups = useCallback(async () => {
    try {
      const [
        projectResponse,
        categoryResponse,
        manufacturerResponse,
        statusResponse,
        conditionResponse,
        lifecycleResponse,
      ] = await Promise.all([
        api.get("/common/projects", { params: { page_size: LOOKUP_PAGE_SIZE } }),
        api.get("/master/asset-categories", { params: { page_size: LOOKUP_PAGE_SIZE } }),
        api.get("/master/manufacturers", { params: { page_size: LOOKUP_PAGE_SIZE } }),
        api.get("/master/asset-status", { params: { page_size: LOOKUP_PAGE_SIZE } }),
        api.get("/master/asset-condition", { params: { page_size: LOOKUP_PAGE_SIZE } }),
        api.get("/master/asset-lifecycle", { params: { page_size: LOOKUP_PAGE_SIZE } }),
      ]);

      const projectRows = projectResponse.data.items.map((item: { id: string; project_name: string; project_code: string }) => ({
        id: item.id,
        code: item.project_code,
        name: item.project_name,
      }));
      setProjects(toLookupOptions(projectRows));
      setCategories(toLookupOptions(categoryResponse.data.items as LookupApiRow[]));
      setManufacturers(toLookupOptions(manufacturerResponse.data.items as LookupApiRow[]));
      setStatuses(toLookupOptions(statusResponse.data.items as LookupApiRow[]));
      setConditions(toLookupOptions(conditionResponse.data.items as LookupApiRow[]));
      setLifecycles(toLookupOptions(lifecycleResponse.data.items as LookupApiRow[]));
    } catch {
      addToast("error", "Unable to load asset filters.");
    }
  }, [addToast]);

  useEffect(() => {
    void loadLookups();
  }, [loadLookups]);

  useEffect(() => {
    if (!query.category_id) {
      setSubcategories([]);
      return;
    }
    void api.get("/master/asset-subcategories", {
      params: { page_size: LOOKUP_PAGE_SIZE, asset_category_id: query.category_id },
    }).then((response) => setSubcategories(toLookupOptions(response.data.items as LookupApiRow[])))
      .catch(() => addToast("error", "Unable to load subcategories for the selected category."));
  }, [addToast, query.category_id]);

  useEffect(() => {
    if (!query.manufacturer_id) {
      setModels([]);
      return;
    }
    void api.get("/master/asset-models", {
      params: { page_size: LOOKUP_PAGE_SIZE, manufacturer_id: query.manufacturer_id },
    }).then((response) => setModels(toLookupOptions(response.data.items as LookupApiRow[])))
      .catch(() => addToast("error", "Unable to load models for the selected manufacturer."));
  }, [addToast, query.manufacturer_id]);

  useEffect(() => {
    void loadList();
    void loadSummary();
  }, [loadList, loadSummary]);

  const updateQuery = <K extends keyof QueryState>(key: K, value: QueryState[K]) => {
    setQuery((current) => ({ ...current, [key]: value, page: key === "page" ? Number(value) : 1 }));
  };

  const handleSortChange = (sortKey: string) => {
    setQuery((current) => ({
      ...current,
      page: 1,
      sort: sortKey,
      order: current.sort === sortKey && current.order === "asc" ? "desc" : "asc",
    }));
  };

  const handleExport = async () => {
    try {
      const response = await api.get<Blob>("/assets/export", {
        params: requestParams,
        responseType: "blob",
      });
      const blobUrl = window.URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = "assets.csv";
      link.click();
      window.URL.revokeObjectURL(blobUrl);
    } catch {
      addToast("error", "Asset export failed.");
    }
  };

  const clearFilters = () => setQuery(initialQuery);

  const columns: Column<AssetListItem>[] = [
    { header: "Asset Number", accessor: "asset_number", width: "180px", sortKey: "asset_number" },
    { header: "Category", accessor: "category", sortKey: "category" },
    { header: "Subcategory", accessor: (row) => row.subcategory || "-", width: "150px" },
    { header: "Manufacturer", accessor: (row) => row.manufacturer || "-", sortKey: "manufacturer" },
    { header: "Model", accessor: (row) => row.model || "-", width: "160px" },
    { header: "Serial Number", accessor: (row) => row.serial_number || "-", width: "170px" },
    { header: "Operational Status", accessor: (row) => formatBadge(row.status), width: "160px", sortKey: "status" },
    { header: "Condition", accessor: (row) => formatBadge(row.condition, "condition"), width: "130px" },
    { header: "Location", accessor: (row) => row.current_location || "-", width: "180px" },
    { header: "Purchase Date", accessor: (row) => formatDate(row.purchase_date), width: "140px", sortKey: "purchase_date" },
    { header: "Warranty", accessor: (row) => formatWarranty(row.warranty_expiry), width: "150px", sortKey: "warranty_expiry" },
    {
      header: "Actions",
      accessor: (row) => (
        <button
          className="btn btn-secondary"
          style={{ display: "inline-flex", alignItems: "center", gap: "0.45rem", padding: "0.5rem 0.9rem" }}
          onClick={(event) => {
            event.stopPropagation();
            navigate(`/assets/${row.id}`);
          }}
        >
          <Eye size={15} />
          View
        </button>
      ),
      width: "110px",
    },
  ];

  const cards = [
    {
      title: "Total Assets",
      value: summary?.total_assets ?? 0,
      icon: <Package size={24} />,
      color: "#bfdbfe",
    },
    {
      title: "Active Assets",
      value: summary?.active_assets ?? 0,
      icon: <CheckCircle size={24} />,
      color: "#86efac",
    },
    {
      title: "Assets in Repair",
      value: summary?.assets_in_repair ?? 0,
      icon: <Wrench size={24} />,
      color: "#fcd34d",
    },
    {
      title: "Retired Assets",
      value: summary?.retired_assets ?? 0,
      icon: <XCircle size={24} />,
      color: "#fca5a5",
    },
    {
      title: "Warranty Expiring Soon",
      value: summary?.warranty_expiring_soon ?? 0,
      icon: <AlertTriangle size={24} />,
      color: "#fdba74",
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
        <div>
          <h1 style={{ marginBottom: "0.35rem" }}>Asset Register</h1>
          <p style={{ margin: 0, color: "var(--text-secondary)" }}>
            Enrol, locate, and verify equipment while working in the field.
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <button className="btn btn-secondary" onClick={() => { void loadList(); void loadSummary(); }}>
            <RefreshCw size={16} />
            Refresh
          </button>
          <button className="btn btn-secondary" onClick={handleExport}>
            <Download size={16} />
            Export
          </button>
          <button className="btn btn-primary" onClick={() => setModalOpen(true)}>
            <Plus size={16} />
            Enrol Asset
          </button>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "1rem",
        }}
      >
        {cards.map((card) => (
          <div key={card.title} className="glass-panel" style={{ padding: "1.15rem 1.25rem" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem" }}>
              <div>
                <div style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "0.4rem" }}>
                  {card.title}
                </div>
                <div style={{ fontSize: "1.9rem", fontWeight: 800 }}>
                  {summaryLoading ? "..." : card.value}
                </div>
              </div>
              <div style={{ color: card.color }}>{card.icon}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="glass-panel" style={{ padding: "1.4rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.05rem" }}>Find an asset</h2>
            <p style={{ margin: "0.3rem 0 0", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              Search a tag, serial number, model, or site before enrolling a duplicate.
            </p>
          </div>
          <button className="btn btn-secondary" type="button" onClick={clearFilters}>
            Clear filters
          </button>
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "1rem",
          }}
        >
          <Input
            label="Search"
            value={query.search}
            onChange={(event) => updateQuery("search", event.target.value)}
            placeholder="Asset number, serial, barcode, manufacturer, model..."
            icon={<Search size={16} />}
          />
          <Select
            label="Project"
            value={query.project_id}
            onChange={(event) => updateQuery("project_id", event.target.value)}
            options={toSelectOptions(projects, "All Projects")}
          />
          <Select
            label="Category"
            value={query.category_id}
            onChange={(event) => setQuery((current) => ({ ...current, category_id: event.target.value, subcategory_id: "", page: 1 }))}
            options={toSelectOptions(categories, "All Categories")}
          />
          <Select
            label="Subcategory"
            value={query.subcategory_id}
            onChange={(event) => updateQuery("subcategory_id", event.target.value)}
            options={toSelectOptions(subcategories, query.category_id ? "All Subcategories" : "Select a category first")}
            disabled={!query.category_id}
          />
          <Select
            label="Manufacturer"
            value={query.manufacturer_id}
            onChange={(event) => setQuery((current) => ({ ...current, manufacturer_id: event.target.value, model_id: "", page: 1 }))}
            options={toSelectOptions(manufacturers, "All Manufacturers")}
          />
          <Select
            label="Model"
            value={query.model_id}
            onChange={(event) => updateQuery("model_id", event.target.value)}
            options={toSelectOptions(models, query.manufacturer_id ? "All Models" : "Select a manufacturer first")}
            disabled={!query.manufacturer_id}
          />
          <Select
            label="Operational Status"
            value={query.status_id}
            onChange={(event) => updateQuery("status_id", event.target.value)}
            options={toSelectOptions(statuses, "All Operational States")}
          />
          <Select
            label="Condition"
            value={query.condition_id}
            onChange={(event) => updateQuery("condition_id", event.target.value)}
            options={toSelectOptions(conditions, "All Conditions")}
          />
          <Select
            label="Lifecycle Stage"
            value={query.lifecycle_id}
            onChange={(event) => updateQuery("lifecycle_id", event.target.value)}
            options={toSelectOptions(lifecycles, "All Lifecycle Stages")}
          />
          <LocationSearchSelect
            label="Location"
            value={query.location_id || null}
            projectId={query.project_id}
            onChange={(locationId) => updateQuery("location_id", locationId || "")}
          />
          <Select
            label="Warranty"
            value={query.warranty_status}
            onChange={(event) => updateQuery("warranty_status", event.target.value)}
            options={[
              { label: "All Warranty States", value: "" },
              { label: "Active", value: "active" },
              { label: "Expired", value: "expired" },
              { label: "Expiring Soon", value: "expiring_soon" },
            ]}
          />
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: "1.15rem" }}>Assets in scope</h2>
          <p style={{ margin: "0.25rem 0 0", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            {assets ? `${assets.total} asset${assets.total === 1 ? "" : "s"} found` : "Loading assets..."}
          </p>
        </div>
        <div style={{ display: "inline-flex", padding: "0.25rem", border: "1px solid var(--border-color)", borderRadius: "var(--border-radius-md)", gap: "0.25rem" }}>
          <button className={viewMode === "field" ? "btn btn-primary" : "btn btn-secondary"} type="button" onClick={() => setViewMode("field")} style={{ padding: "0.45rem 0.7rem" }}>
            <LayoutGrid size={16} /> Field view
          </button>
          <button className={viewMode === "register" ? "btn btn-primary" : "btn btn-secondary"} type="button" onClick={() => setViewMode("register")} style={{ padding: "0.45rem 0.7rem" }}>
            <List size={16} /> Register
          </button>
        </div>
      </div>

      {viewMode === "field" ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem" }}>
          {loading ? (
            <div className="glass-panel" style={{ padding: "2rem", color: "var(--text-secondary)" }}>Loading assets...</div>
          ) : assets?.items.length ? (
            assets.items.map((asset) => (
              <button key={asset.id} type="button" className="glass-panel" onClick={() => navigate(`/assets/${asset.id}`)} style={{ border: "1px solid var(--border-color)", padding: "1.2rem", color: "inherit", textAlign: "left", cursor: "pointer", display: "grid", gap: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.75rem" }}>
                  <div>
                    <div style={{ fontWeight: 800, fontSize: "1.1rem" }}>{asset.asset_number}</div>
                    <div style={{ color: "var(--text-secondary)", marginTop: "0.25rem" }}>{asset.category}{asset.model ? ` · ${asset.model}` : ""}</div>
                  </div>
                  {formatBadge(asset.status)}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                  <MapPin size={16} color="var(--accent-primary)" />
                  {asset.current_location || "Location not recorded"}
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", fontSize: "0.85rem" }}>
                  <div><span style={{ color: "var(--text-secondary)" }}>Serial</span><br />{asset.serial_number || "Not recorded"}</div>
                  <div><span style={{ color: "var(--text-secondary)" }}>Condition</span><br />{asset.condition || "Not assessed"}</div>
                </div>
                <span style={{ color: "var(--accent-primary)", fontWeight: 700, fontSize: "0.9rem" }}>Open field record →</span>
              </button>
            ))
          ) : (
            <div className="glass-panel" style={{ padding: "2rem", color: "var(--text-secondary)" }}>No assets match the current search and filters.</div>
          )}
          {(assets?.pages ?? 1) > 1 && (
            <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end", alignItems: "center", gap: "0.75rem" }}>
              <span style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>Page {assets?.page} of {assets?.pages}</span>
              <button className="btn btn-secondary" type="button" disabled={(assets?.page ?? 1) <= 1} onClick={() => updateQuery("page", (assets?.page ?? 1) - 1)}>Previous</button>
              <button className="btn btn-secondary" type="button" disabled={(assets?.page ?? 1) >= (assets?.pages ?? 1)} onClick={() => updateQuery("page", (assets?.page ?? 1) + 1)}>Next</button>
            </div>
          )}
        </div>
      ) : (
        <div className="glass-panel">
          <DataTable
            columns={columns}
            data={assets?.items ?? []}
            loading={loading}
            page={assets?.page}
            totalPages={assets?.pages}
            onPageChange={(page) => updateQuery("page", page)}
            onRowClick={(row) => navigate(`/assets/${row.id}`)}
            emptyMessage="No assets match the current search and filters."
            sort={query.sort}
            order={query.order}
            onSortChange={handleSortChange}
          />
        </div>
      )}

      <AssetForm
        isOpen={isModalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={async () => {
          await loadList();
          await loadSummary();
        }}
      />
    </div>
  );
};
