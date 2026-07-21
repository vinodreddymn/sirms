import React, { useEffect, useState } from "react";
import { Edit2, Plus } from "lucide-react";

import { DataTable } from "../../components/DataTable";
import type { Column } from "../../components/DataTable";
import { Input, Select } from "../../components/FormControls";
import { Modal } from "../../components/Modal";
import { useToast } from "../../contexts/ToastContext";
import { api } from "../../services/api";

interface Lookup { id: number; name: string; }
interface Definition {
  id: number; code: string; name: string; data_type: string; unit_of_measure?: string | null;
  required_flag: boolean; display_order: number; asset_category_id?: number | null;
  asset_subcategory_id?: number | null; category_name?: string | null; subcategory_name?: string | null;
}
interface Page<T> { items: T[]; total: number; }

const emptyForm = {
  asset_category_id: "", asset_subcategory_id: "", code: "", name: "", data_type: "TEXT",
  unit_of_measure: "", required_flag: false, display_order: 0,
};
const options = (items: Lookup[], emptyLabel: string) => [{ label: emptyLabel, value: "" }, ...items.map((item) => ({ label: item.name, value: String(item.id) }))];

export const SpecificationDefinitions: React.FC = () => {
  const { addToast } = useToast();
  const [definitions, setDefinitions] = useState<Definition[]>([]);
  const [categories, setCategories] = useState<Lookup[]>([]);
  const [subcategories, setSubcategories] = useState<Lookup[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Definition | null>(null);
  const [form, setForm] = useState(emptyForm);

  const loadDefinitions = async () => {
    setLoading(true);
    try {
      const response = await api.get<Page<Definition>>("/master/specification-definitions", { params: { page_size: 100 } });
      setDefinitions(response.data.items);
    } catch { addToast("error", "Unable to load specification definitions."); }
    finally { setLoading(false); }
  };

  useEffect(() => { void loadDefinitions(); }, []);
  useEffect(() => {
    void api.get<Page<Lookup>>("/master/asset-categories", { params: { page_size: 100 } })
      .then((response) => setCategories(response.data.items))
      .catch(() => addToast("error", "Unable to load asset categories."));
  }, [addToast]);
  useEffect(() => {
    if (!form.asset_category_id) { setSubcategories([]); return; }
    void api.get<Page<Lookup>>("/master/asset-subcategories", { params: { page_size: 100, asset_category_id: form.asset_category_id } })
      .then((response) => setSubcategories(response.data.items))
      .catch(() => addToast("error", "Unable to load asset subcategories."));
  }, [addToast, form.asset_category_id]);

  const openModal = (definition?: Definition) => {
    setEditing(definition ?? null);
    setForm(definition ? {
      asset_category_id: definition.asset_category_id ? String(definition.asset_category_id) : "",
      asset_subcategory_id: definition.asset_subcategory_id ? String(definition.asset_subcategory_id) : "",
      code: definition.code, name: definition.name, data_type: definition.data_type,
      unit_of_measure: definition.unit_of_measure ?? "", required_flag: definition.required_flag,
      display_order: definition.display_order,
    } : emptyForm);
    setModalOpen(true);
  };

  const save = async () => {
    if (!form.code.trim() || !form.name.trim()) { addToast("error", "Code and name are required."); return; }
    setSaving(true);
    const payload = {
      ...form, code: form.code.trim().toUpperCase(), name: form.name.trim(),
      asset_category_id: form.asset_category_id ? Number(form.asset_category_id) : null,
      asset_subcategory_id: form.asset_subcategory_id ? Number(form.asset_subcategory_id) : null,
      unit_of_measure: form.unit_of_measure.trim() || null, display_order: Number(form.display_order),
    };
    try {
      if (editing) await api.put(`/master/specification-definitions/${editing.id}`, payload);
      else await api.post("/master/specification-definitions", payload);
      addToast("success", editing ? "Specification updated." : "Specification added.");
      setModalOpen(false); await loadDefinitions();
    } catch { addToast("error", "Unable to save the specification."); }
    finally { setSaving(false); }
  };

  const columns: Column<Definition>[] = [
    { header: "Code", accessor: "code" }, { header: "Specification", accessor: "name" },
    { header: "Applies To", accessor: (item) => item.subcategory_name || item.category_name || "All assets" },
    { header: "Type", accessor: "data_type", width: "100px" },
    { header: "Unit", accessor: (item) => item.unit_of_measure || "-", width: "100px" },
    { header: "Required", accessor: (item) => item.required_flag ? "Yes" : "No", width: "90px" },
    { header: "Edit", accessor: (item) => <button className="btn btn-secondary" type="button" onClick={() => openModal(item)} style={{ padding: "0.4rem" }}><Edit2 size={16} /></button>, width: "70px" },
  ];

  return <div style={{ display: "grid", gap: "1.5rem" }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", flexWrap: "wrap" }}>
      <div><h1 style={{ margin: 0 }}>Dynamic Specifications</h1><p style={{ margin: "0.35rem 0 0", color: "var(--text-secondary)" }}>Configure the field details operators capture for each asset category or subcategory.</p></div>
      <button className="btn btn-primary" type="button" onClick={() => openModal()}><Plus size={16} /> Add Specification</button>
    </div>
    <div className="glass-panel"><DataTable columns={columns} data={definitions} loading={loading} emptyMessage="No specification definitions configured." /></div>
    <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editing ? "Edit Specification" : "Add Specification"} maxWidth="720px" footer={<><button className="btn btn-secondary" type="button" onClick={() => setModalOpen(false)} disabled={saving}>Cancel</button><button className="btn btn-primary" type="button" onClick={() => void save()} disabled={saving}>{saving ? "Saving..." : "Save Specification"}</button></>}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
        <Select label="Category (optional)" value={form.asset_category_id} onChange={(event) => setForm((current) => ({ ...current, asset_category_id: event.target.value, asset_subcategory_id: "" }))} options={options(categories, "All Categories")} />
        <Select label="Subcategory (optional)" value={form.asset_subcategory_id} onChange={(event) => setForm((current) => ({ ...current, asset_subcategory_id: event.target.value }))} options={options(subcategories, form.asset_category_id ? "All Subcategories" : "Choose a category first")} disabled={!form.asset_category_id} />
        <Input label="Code" value={form.code} onChange={(event) => setForm((current) => ({ ...current, code: event.target.value }))} placeholder="e.g. INPUT_VOLTAGE" required />
        <Input label="Name" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} placeholder="e.g. Input Voltage" required />
        <Select label="Data Type" value={form.data_type} onChange={(event) => setForm((current) => ({ ...current, data_type: event.target.value }))} options={["TEXT", "NUMBER", "BOOLEAN", "DATE", "JSON"].map((value) => ({ label: value, value }))} />
        <Input label="Unit of Measure" value={form.unit_of_measure} onChange={(event) => setForm((current) => ({ ...current, unit_of_measure: event.target.value }))} placeholder="e.g. VOLT, METER, AH" />
        <Input label="Display Order" type="number" value={form.display_order} onChange={(event) => setForm((current) => ({ ...current, display_order: Number(event.target.value) || 0 }))} />
        <Select label="Required in Enrollment" value={form.required_flag ? "true" : "false"} onChange={(event) => setForm((current) => ({ ...current, required_flag: event.target.value === "true" }))} options={[{ label: "Optional", value: "false" }, { label: "Required", value: "true" }]} />
      </div>
    </Modal>
  </div>;
};
