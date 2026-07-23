import React, { useEffect, useMemo, useState } from "react";

import { Modal } from "../../components/Modal";
import { Input, Select } from "../../components/FormControls";
import { useToast } from "../../contexts/ToastContext";
import { api } from "../../services/api";
import { LocationSearchSelect } from "./LocationSearchSelect";
import { AssetSearchMultiSelect } from "./AssetSearchMultiSelect";
import type {
  AssetDetails,
  AssetFormPayload,
  AssetSpecificationDefinition,
  AssetSpecificationFormValue,
  LookupOption,
} from "./types";

interface AssetFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void | Promise<void>;
  assetToEdit?: AssetDetails;
}

interface ProjectApiRow {
  id: string;
  project_name: string;
  project_code: string;
}

interface PositionApiRow {
  id: string;
  position_number: string;
}

interface LookupApiRow {
  id: number | string;
  code?: string | null;
  name: string;
}

const getErrorMessage = (error: unknown, fallback: string) => {
  if (typeof error === "object" && error !== null && "response" in error) {
    const response = (error as { response?: { data?: unknown } }).response;
    const data = response?.data;
    if (typeof data === "object" && data !== null && "detail" in data) {
      const detail = (data as { detail?: unknown }).detail;
      if (typeof detail === "string" && detail.trim()) return detail;
      if (Array.isArray(detail)) {
        const messages = detail
          .map((item) => {
            if (typeof item === "string") return item;
            if (typeof item === "object" && item !== null && "msg" in item) {
              return String((item as { msg?: unknown }).msg ?? "");
            }
            return "";
          })
          .filter(Boolean);
        if (messages.length) return messages.join(" ");
      }
    }
    if (typeof data === "object" && data !== null && "message" in data) {
      const message = (data as { message?: unknown }).message;
      if (typeof message === "string" && message.trim()) return message;
    }
    if (typeof data === "object" && data !== null && "errors" in data) {
      const errors = (data as { errors?: unknown }).errors;
      if (Array.isArray(errors)) {
        const messages = errors
          .map((item) => {
            if (typeof item === "string") return item;
            if (typeof item === "object" && item !== null && "message" in item) {
              return String((item as { message?: unknown }).message ?? "");
            }
            return "";
          })
          .filter(Boolean);
        if (messages.length) return messages.join(" ");
      }
    }
  }
  return fallback;
};

const emptyPayload: AssetFormPayload = {
  project_id: "",
  asset_number: "",
  asset_category_id: 0,
  asset_subcategory_id: null,
  manufacturer_id: null,
  asset_model_id: null,
  asset_status_id: 0,
  asset_condition_id: null,
  asset_lifecycle_id: null,
  serial_number: "",
  barcode: "",
  qr_code: "",
  purchase_date: "",
  warranty_expiry: "",
  current_location_id: null,
  remarks: "",
  location_position_id: null,
  installation_date: "",
  specification_values: [],
  relationship_ids: { POWERED_BY: [], CONNECTED_TO: [], PARENT_OF: [], CHILD_OF: [] },
};

const LOOKUP_PAGE_SIZE = 100;

const toLookup = (rows: LookupApiRow[]): LookupOption[] =>
  rows.map((row) => ({ id: String(row.id), code: row.code, name: row.name }));

const toSelectOptions = (rows: LookupOption[], emptyLabel: string) => [
  { label: emptyLabel, value: "" },
  ...rows.map((row) => ({ label: row.name, value: row.id })),
];

const sanitizePayload = (payload: AssetFormPayload) => ({
  project_id: payload.project_id,
  asset_number: payload.asset_number,
  asset_category_id: payload.asset_category_id,
  asset_subcategory_id: payload.asset_subcategory_id || null,
  manufacturer_id: payload.manufacturer_id || null,
  asset_model_id: payload.asset_model_id || null,
  asset_status_id: payload.asset_status_id,
  asset_condition_id: payload.asset_condition_id || null,
  asset_lifecycle_id: payload.asset_lifecycle_id || null,
  serial_number: payload.serial_number || null,
  barcode: payload.barcode || null,
  qr_code: payload.qr_code || null,
  purchase_date: payload.purchase_date || null,
  warranty_expiry: payload.warranty_expiry || null,
  current_location_id: payload.current_location_id || null,
  remarks: payload.remarks || null,
  location_position_id: payload.location_position_id || null,
  installation_date: payload.installation_date || null,
  specification_values: payload.specification_values,
  relationship_ids: payload.relationship_ids,
});

const createInitialState = (asset?: AssetDetails): AssetFormPayload => {
  if (!asset) return emptyPayload;
  return {
    project_id: String(asset.project.id),
    asset_number: asset.basic_information.asset_number,
    asset_category_id: Number(asset.category.id),
    asset_subcategory_id: asset.subcategory ? Number(asset.subcategory.id) : null,
    manufacturer_id: asset.manufacturer ? Number(asset.manufacturer.id) : null,
    asset_model_id: asset.model ? Number(asset.model.id) : null,
    asset_status_id: Number(asset.status.id),
    asset_condition_id: asset.condition ? Number(asset.condition.id) : null,
    asset_lifecycle_id: asset.lifecycle ? Number(asset.lifecycle.id) : null,
    serial_number: asset.basic_information.serial_number || "",
    barcode: asset.basic_information.barcode || "",
    qr_code: asset.qr_code || "",
    purchase_date: asset.basic_information.purchase_date || "",
    warranty_expiry: asset.basic_information.warranty_expiry || "",
    current_location_id: asset.installation?.location_id || null,
    remarks: asset.basic_information.remarks || "",
    location_position_id: asset.installation?.position_id || null,
    installation_date: asset.installation?.installed_on || "",
    specification_values: asset.specifications.map<AssetSpecificationFormValue>((item) => ({
      specification_definition_id: item.specification_definition_id,
      value_text: item.data_type === "TEXT" ? String(item.value ?? "") : null,
      value_number: item.data_type === "NUMBER" && typeof item.value === "number" ? item.value : null,
      value_boolean: item.data_type === "BOOLEAN" && typeof item.value === "boolean" ? item.value : null,
      value_date: item.data_type === "DATE" && typeof item.value === "string" ? item.value : null,
      value_json: item.data_type === "JSON" && typeof item.value === "object" && item.value !== null
        ? item.value
        : null,
    })),
    relationship_ids: { POWERED_BY: [], CONNECTED_TO: [], PARENT_OF: [], CHILD_OF: [] },
  };
};

export const AssetForm: React.FC<AssetFormProps> = ({ isOpen, onClose, onSuccess, assetToEdit }) => {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [lookupsLoading, setLookupsLoading] = useState(false);
  const [formData, setFormData] = useState<AssetFormPayload>(createInitialState(assetToEdit));
  const [specDefinitions, setSpecDefinitions] = useState<AssetSpecificationDefinition[]>([]);
  const [positions, setPositions] = useState<LookupOption[]>([]);
  const [jsonDrafts, setJsonDrafts] = useState<Record<number, string>>({});
  const [saveError, setSaveError] = useState<string | null>(null);

  const [projects, setProjects] = useState<LookupOption[]>([]);
  const [categories, setCategories] = useState<LookupOption[]>([]);
  const [subcategories, setSubcategories] = useState<LookupOption[]>([]);
  const [manufacturers, setManufacturers] = useState<LookupOption[]>([]);
  const [models, setModels] = useState<LookupOption[]>([]);
  const [statuses, setStatuses] = useState<LookupOption[]>([]);
  const [conditions, setConditions] = useState<LookupOption[]>([]);
  const [lifecycles, setLifecycles] = useState<LookupOption[]>([]);

  useEffect(() => {
    setFormData(createInitialState(assetToEdit));
    setJsonDrafts({});
    setSaveError(null);
  }, [assetToEdit, isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const loadLookups = async () => {
      setLookupsLoading(true);
      try {
        const [
          projectResponse,
          categoryResponse,
          statusResponse,
          conditionResponse,
          lifecycleResponse,
        ] = await Promise.all([
          api.get("/common/projects", { params: { page_size: LOOKUP_PAGE_SIZE } }),
          api.get("/master/asset-categories", { params: { page_size: LOOKUP_PAGE_SIZE } }),
          api.get("/master/asset-status", { params: { page_size: LOOKUP_PAGE_SIZE } }),
          api.get("/master/asset-condition", { params: { page_size: LOOKUP_PAGE_SIZE } }),
          api.get("/master/asset-lifecycle", { params: { page_size: LOOKUP_PAGE_SIZE } }),
        ]);

        setProjects(
          projectResponse.data.items.map((item: ProjectApiRow) => ({
            id: item.id,
            code: item.project_code,
            name: item.project_name,
          })),
        );
        setCategories(toLookup(categoryResponse.data.items as LookupApiRow[]));
        setStatuses(toLookup(statusResponse.data.items as LookupApiRow[]));
        setConditions(toLookup(conditionResponse.data.items as LookupApiRow[]));
        setLifecycles(toLookup(lifecycleResponse.data.items as LookupApiRow[]));
      } catch {
        addToast("error", "Unable to load asset form lookups.");
      } finally {
        setLookupsLoading(false);
      }
    };

    void loadLookups();
  }, [addToast, isOpen]);

  useEffect(() => {
    if (!isOpen || !formData.asset_category_id) {
      setSubcategories([]);
      return;
    }
    const loadSubcategories = async () => {
      try {
        const response = await api.get("/master/asset-subcategories", {
          params: { page_size: LOOKUP_PAGE_SIZE, asset_category_id: formData.asset_category_id },
        });
        setSubcategories(toLookup(response.data.items as LookupApiRow[]));
      } catch {
        addToast("error", "Unable to load subcategories for the selected category.");
      }
    };
    void loadSubcategories();
  }, [addToast, formData.asset_category_id, isOpen]);

  useEffect(() => {
    if (!isOpen || !formData.asset_category_id) { setManufacturers([]); return; }
    void api.get("/master/manufacturers", { params: {
      page_size: LOOKUP_PAGE_SIZE, asset_category_id: formData.asset_category_id,
      asset_subcategory_id: formData.asset_subcategory_id || undefined,
    } }).then((response) => setManufacturers(toLookup(response.data.items as LookupApiRow[])))
      .catch(() => addToast("error", "Unable to load manufacturers."));
  }, [addToast, formData.asset_category_id, formData.asset_subcategory_id, isOpen]);

  useEffect(() => {
    if (!isOpen || !formData.manufacturer_id) {
      setModels([]);
      return;
    }
    const loadModels = async () => {
      try {
        const response = await api.get("/master/asset-models", {
          params: { page_size: LOOKUP_PAGE_SIZE, manufacturer_id: formData.manufacturer_id, asset_subcategory_id: formData.asset_subcategory_id || undefined },
        });
        setModels(toLookup(response.data.items as LookupApiRow[]));
      } catch {
        addToast("error", "Unable to load models for the selected manufacturer.");
      }
    };
    void loadModels();
  }, [addToast, formData.asset_subcategory_id, formData.manufacturer_id, isOpen]);

  useEffect(() => {
    if (!isOpen || !formData.asset_category_id) {
      setSpecDefinitions([]);
      return;
    }
    const loadDefinitions = async () => {
      try {
        const response = await api.get<AssetSpecificationDefinition[]>("/assets/specification-definitions", {
          params: {
            category_id: formData.asset_category_id,
            subcategory_id: formData.asset_subcategory_id || undefined,
          },
        });
        const definitions = response.data;
        setSpecDefinitions(definitions);
        setFormData((current) => {
          const existingMap = new Map(
            current.specification_values.map((item) => [item.specification_definition_id, item]),
          );
          return {
            ...current,
            specification_values: definitions.map((definition) => existingMap.get(definition.id) ?? {
              specification_definition_id: definition.id,
              value_text: null,
              value_number: null,
              value_boolean: null,
              value_date: null,
              value_json: null,
            }),
          };
        });
      } catch {
        addToast("error", "Unable to load dynamic specifications.");
      }
    };
    void loadDefinitions();
  }, [addToast, formData.asset_category_id, formData.asset_subcategory_id, isOpen]);

  useEffect(() => {
    if (!isOpen || !formData.current_location_id) {
      setPositions([]);
      return;
    }
    const loadPositions = async () => {
      try {
        const response = await api.get(`/infrastructure/locations/${formData.current_location_id}/positions`, {
          params: { page_size: LOOKUP_PAGE_SIZE },
        });
        setPositions(
          response.data.items.map((item: PositionApiRow) => ({
            id: item.id,
            name: item.position_number,
          })),
        );
      } catch {
        addToast("error", "Unable to load installation positions.");
      }
    };
    void loadPositions();
  }, [addToast, formData.current_location_id, isOpen]);

  const setField = <K extends keyof AssetFormPayload>(key: K, value: AssetFormPayload[K]) => {
    setSaveError(null);
    setFormData((current) => ({ ...current, [key]: value }));
  };

  const specValuesByDefinition = useMemo(
    () => new Map(formData.specification_values.map((item) => [item.specification_definition_id, item])),
    [formData.specification_values],
  );

  const handleSpecChange = (definitionId: number, nextValue: Partial<AssetSpecificationFormValue>) => {
    setFormData((current) => ({
      ...current,
        specification_values: current.specification_values.map((item) =>
          item.specification_definition_id === definitionId
            ? {
                ...item,
                value_text: null,
                value_number: null,
                value_boolean: null,
                value_date: null,
                value_json: null,
                ...nextValue,
              }
            : item,
        ),
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaveError(null);
    if (!formData.project_id || !formData.asset_category_id || !formData.asset_status_id || !formData.asset_number) {
      addToast("error", "Project, asset number, category, and status are required.");
      return;
    }
    setLoading(true);
    try {
      const payload = sanitizePayload(formData);
      if (assetToEdit) {
        await api.put(`/assets/${assetToEdit.id}`, { ...payload, relationship_ids: undefined });
        addToast("success", "Asset updated successfully.");
      } else {
        await api.post("/assets", payload);
        addToast("success", "Asset created successfully.");
      }
      await onSuccess();
      onClose();
    } catch (error) {
      const message = getErrorMessage(error, "Failed to save asset.");
      setSaveError(message);
      addToast("error", message);
    } finally {
      setLoading(false);
    }
  };

  const renderSpecificationField = (definition: AssetSpecificationDefinition) => {
    const value = specValuesByDefinition.get(definition.id);
    switch (definition.data_type) {
      case "NUMBER":
        return (
          <Input
            label={definition.name}
            type="number"
            value={value?.value_number ?? ""}
            onChange={(event) =>
              handleSpecChange(definition.id, {
                value_number: event.target.value ? Number(event.target.value) : null,
              })
            }
          />
        );
      case "BOOLEAN":
        return (
          <Select
            label={definition.name}
            value={value?.value_boolean === null || value?.value_boolean === undefined ? "" : String(value.value_boolean)}
            onChange={(event) =>
              handleSpecChange(definition.id, {
                value_boolean: event.target.value === "" ? null : event.target.value === "true",
              })
            }
            options={[
              { label: "Select value", value: "" },
              { label: "True", value: "true" },
              { label: "False", value: "false" },
            ]}
          />
        );
      case "DATE":
        return (
          <Input
            label={definition.name}
            type="date"
            value={value?.value_date ?? ""}
            onChange={(event) => handleSpecChange(definition.id, { value_date: event.target.value || null })}
          />
        );
      case "JSON":
        return (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "1rem" }}>
            <label style={{ fontSize: "0.875rem", fontWeight: 500, color: "var(--text-secondary)" }}>
              {definition.name}
            </label>
            <textarea
              value={
                jsonDrafts[definition.id] ??
                (value?.value_json ? JSON.stringify(value.value_json, null, 2) : "")
              }
              onChange={(event) =>
                setJsonDrafts((current) => ({
                  ...current,
                  [definition.id]: event.target.value,
                }))
              }
              onBlur={() => {
                const next = (jsonDrafts[definition.id] ?? "").trim();
                if (!next) {
                  handleSpecChange(definition.id, { value_json: null });
                  return;
                }
                try {
                  handleSpecChange(definition.id, {
                    value_json: JSON.parse(next) as Record<string, unknown>,
                  });
                } catch {
                  addToast("error", `${definition.name} must contain valid JSON.`);
                }
              }}
              rows={5}
              style={{
                width: "100%",
                background: "var(--bg-tertiary)",
                border: "1px solid var(--border-color)",
                color: "var(--text-primary)",
                padding: "0.8rem 1rem",
                borderRadius: "var(--border-radius-md)",
                resize: "vertical",
              }}
            />
          </div>
        );
      default:
        return (
          <Input
            label={definition.name}
            value={value?.value_text ?? ""}
            onChange={(event) => handleSpecChange(definition.id, { value_text: event.target.value || null })}
          />
        );
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={assetToEdit ? "Update Asset Record" : "Enrol Asset"}
      maxWidth="1000px"
      footer={
        <>
          <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button type="submit" form="asset-form" className="btn btn-primary" disabled={loading || lookupsLoading}>
            {loading ? "Saving..." : assetToEdit ? "Update Asset" : "Enrol Asset"}
          </button>
        </>
      }
    >
      <form id="asset-form" onSubmit={handleSubmit} style={{ display: "grid", gap: "1.25rem" }}>
        {saveError && (
          <div
            role="alert"
            style={{
              padding: "0.85rem 1rem",
              border: "1px solid rgba(239,68,68,0.35)",
              borderRadius: "var(--border-radius-md)",
              background: "rgba(239,68,68,0.1)",
              color: "var(--danger, #f87171)",
              fontSize: "0.9rem",
            }}
          >
            {saveError}
          </div>
        )}
        {!assetToEdit && (
          <div style={{ padding: "0.85rem 1rem", borderRadius: "var(--border-radius-md)", background: "rgba(59,130,246,0.1)", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Start with the asset tag, category, status, and site. Add the remaining identification and technical details when available.
          </div>
        )}
        <section>
          <h3 style={{ marginTop: 0 }}>Basic Information</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
            <Select
              label="Project"
              value={formData.project_id}
              onChange={(event) => setField("project_id", event.target.value)}
              options={toSelectOptions(projects, "Select Project")}
              required
            />
            <Input
              label="Asset Number"
              value={formData.asset_number}
              onChange={(event) => setField("asset_number", event.target.value)}
              required
            />
            <Select
              label="Category"
              value={formData.asset_category_id ? String(formData.asset_category_id) : ""}
              onChange={(event) => {
                setFormData((current) => ({
                  ...current,
                  asset_category_id: Number(event.target.value),
                  asset_subcategory_id: null,
                  manufacturer_id: null,
                  asset_model_id: null,
                }));
              }}
              options={toSelectOptions(categories, "Select Category")}
              required
            />
            <Select
              label="Subcategory"
              value={formData.asset_subcategory_id ? String(formData.asset_subcategory_id) : ""}
              onChange={(event) => setField("asset_subcategory_id", event.target.value ? Number(event.target.value) : null)}
              options={toSelectOptions(subcategories, formData.asset_category_id ? "Select Subcategory" : "Select a category first")}
              disabled={!formData.asset_category_id}
            />
            <Select
              label="Manufacturer"
              value={formData.manufacturer_id ? String(formData.manufacturer_id) : ""}
              onChange={(event) => {
                setFormData((current) => ({
                  ...current,
                  manufacturer_id: event.target.value ? Number(event.target.value) : null,
                  asset_model_id: null,
                }));
              }}
              options={toSelectOptions(manufacturers, formData.asset_category_id ? "Select Manufacturer" : "Select a category first")}
              disabled={!formData.asset_category_id}
            />
            <Select
              label="Model"
              value={formData.asset_model_id ? String(formData.asset_model_id) : ""}
              onChange={(event) => setField("asset_model_id", event.target.value ? Number(event.target.value) : null)}
              options={toSelectOptions(models, formData.manufacturer_id ? "Select Model" : "Select a manufacturer first")}
              disabled={!formData.manufacturer_id}
            />
          </div>
        </section>

        <section>
          <h3 style={{ marginTop: 0 }}>Identification</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
            <Input label="Serial Number" value={formData.serial_number ?? ""} onChange={(event) => setField("serial_number", event.target.value)} />
            <Input label="Barcode" value={formData.barcode ?? ""} onChange={(event) => setField("barcode", event.target.value)} />
            <Input label="QR Code" value={formData.qr_code ?? ""} onChange={(event) => setField("qr_code", event.target.value)} />
          </div>
        </section>

        <section>
          <h3 style={{ marginTop: 0 }}>Asset Relationships</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>Search and select related assets. These relationships are saved during enrollment.</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem" }}>
            <AssetSearchMultiSelect
              label="Power Sources"
              value={formData.relationship_ids.POWERED_BY}
              onChange={(val) => setFormData((current) => ({ ...current, relationship_ids: { ...current.relationship_ids, POWERED_BY: val } }))}
              categoryId={3}
              placeholder="Search Power assets..."
            />
            <AssetSearchMultiSelect
              label="Network Connections"
              value={formData.relationship_ids.CONNECTED_TO}
              onChange={(val) => setFormData((current) => ({ ...current, relationship_ids: { ...current.relationship_ids, CONNECTED_TO: val } }))}
              categoryId={2}
              placeholder="Search Network assets..."
            />
            <AssetSearchMultiSelect
              label="Parent Assets"
              value={formData.relationship_ids.PARENT_OF}
              onChange={(val) => setFormData((current) => ({ ...current, relationship_ids: { ...current.relationship_ids, PARENT_OF: val } }))}
              placeholder="Search parent assets..."
            />
            <AssetSearchMultiSelect
              label="Child Assets"
              value={formData.relationship_ids.CHILD_OF}
              onChange={(val) => setFormData((current) => ({ ...current, relationship_ids: { ...current.relationship_ids, CHILD_OF: val } }))}
              placeholder="Search child assets..."
            />
          </div>
        </section>

        <section>
          <h3 style={{ marginTop: 0 }}>Operational State & Lifecycle</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "0.75rem", marginBottom: "1rem" }}>
            <div style={{ padding: "0.75rem 0.9rem", borderLeft: "3px solid var(--accent-primary)", background: "rgba(59,130,246,0.08)", borderRadius: "var(--border-radius-sm)" }}>
              <strong style={{ display: "block", marginBottom: "0.2rem" }}>Operational status</strong>
              <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>What is the asset’s current operating state?</span>
            </div>
            <div style={{ padding: "0.75rem 0.9rem", borderLeft: "3px solid #a78bfa", background: "rgba(167,139,250,0.08)", borderRadius: "var(--border-radius-sm)" }}>
              <strong style={{ display: "block", marginBottom: "0.2rem" }}>Lifecycle stage</strong>
              <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>Where is it in its long-term ownership and service journey?</span>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
            <Select
              label="Operational Status"
              value={formData.asset_status_id ? String(formData.asset_status_id) : ""}
              onChange={(event) => setField("asset_status_id", Number(event.target.value))}
              options={toSelectOptions(statuses, "Select Status")}
              required
            />
            <Select
              label="Condition"
              value={formData.asset_condition_id ? String(formData.asset_condition_id) : ""}
              onChange={(event) => setField("asset_condition_id", event.target.value ? Number(event.target.value) : null)}
              options={toSelectOptions(conditions, "Select Condition")}
            />
            <Select
              label="Lifecycle Stage"
              value={formData.asset_lifecycle_id ? String(formData.asset_lifecycle_id) : ""}
              onChange={(event) => setField("asset_lifecycle_id", event.target.value ? Number(event.target.value) : null)}
              options={toSelectOptions(lifecycles, "Select Lifecycle")}
            />
          </div>
        </section>

        <section>
          <h3 style={{ marginTop: 0 }}>Installation</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
            <LocationSearchSelect
              value={formData.current_location_id ?? null}
              selectedLabel={assetToEdit?.installation?.location_name}
              projectId={formData.project_id}
              onChange={(locationId) => {
                setFormData((current) => ({
                  ...current,
                  current_location_id: locationId,
                  location_position_id: null,
                }));
              }}
            />
            <Select
              label="Position"
              value={formData.location_position_id ?? ""}
              onChange={(event) => setField("location_position_id", event.target.value || null)}
              options={toSelectOptions(positions, "Select Position")}
            />
            <Input
              label="Installation Date"
              type="date"
              value={formData.installation_date ?? ""}
              onChange={(event) => setField("installation_date", event.target.value)}
            />
          </div>
        </section>

        <section>
          <h3 style={{ marginTop: 0 }}>Purchase</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
            <Input
              label="Purchase Date"
              type="date"
              value={formData.purchase_date ?? ""}
              onChange={(event) => setField("purchase_date", event.target.value)}
            />
            <Input
              label="Warranty Expiry"
              type="date"
              value={formData.warranty_expiry ?? ""}
              onChange={(event) => setField("warranty_expiry", event.target.value)}
            />
          </div>
        </section>

        <section>
          <h3 style={{ marginTop: 0 }}>Dynamic Specifications</h3>
          {specDefinitions.length === 0 ? (
            <div style={{ color: "var(--text-secondary)" }}>Select a category to load specification fields.</div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
              {specDefinitions.map((definition) => (
                <div key={definition.id}>
                  {renderSpecificationField(definition)}
                </div>
              ))}
            </div>
          )}
        </section>

        <section>
          <h3 style={{ marginTop: 0 }}>Remarks</h3>
          <textarea
            value={formData.remarks ?? ""}
            onChange={(event) => setField("remarks", event.target.value)}
            rows={4}
            style={{
              width: "100%",
              background: "var(--bg-tertiary)",
              border: "1px solid var(--border-color)",
              color: "var(--text-primary)",
              padding: "0.8rem 1rem",
              borderRadius: "var(--border-radius-md)",
              resize: "vertical",
            }}
          />
        </section>
      </form>
    </Modal>
  );
};
