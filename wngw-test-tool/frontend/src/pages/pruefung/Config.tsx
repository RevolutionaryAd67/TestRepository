import { FormEvent, useState } from "react";
import { apiRequest } from "../../lib/apiClient";
import { FormField } from "../../components/ui/FormField";
import { Toast } from "../../components/ui/Toast";

export default function TestConfigPage() {
  const [form, setForm] = useState({ host: "127.0.0.1", port: 2404, ca: 1, ioa: 1, value: true });
  const [toast, setToast] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await apiRequest("/api/tests/single-command", { method: "POST", body: form });
      setToast("Single command sent successfully");
    } catch (error) {
      setToast(`Error: ${(error as Error).message}`);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <form className="grid grid-cols-2 gap-4" onSubmit={handleSubmit}>
        <FormField label="Host">
          <input
            className="bg-slate-800 rounded px-2 py-1"
            value={form.host}
            onChange={(event) => setForm((prev) => ({ ...prev, host: event.target.value }))}
          />
        </FormField>
        <FormField label="Port">
          <input
            type="number"
            className="bg-slate-800 rounded px-2 py-1"
            value={form.port}
            onChange={(event) => setForm((prev) => ({ ...prev, port: Number(event.target.value) }))}
          />
        </FormField>
        <FormField label="Common Address (CA)">
          <input
            type="number"
            className="bg-slate-800 rounded px-2 py-1"
            value={form.ca}
            onChange={(event) => setForm((prev) => ({ ...prev, ca: Number(event.target.value) }))}
          />
        </FormField>
        <FormField label="IOA">
          <input
            type="number"
            className="bg-slate-800 rounded px-2 py-1"
            value={form.ioa}
            onChange={(event) => setForm((prev) => ({ ...prev, ioa: Number(event.target.value) }))}
          />
        </FormField>
        <FormField label="Value">
          <select
            className="bg-slate-800 rounded px-2 py-1"
            value={form.value ? "true" : "false"}
            onChange={(event) => setForm((prev) => ({ ...prev, value: event.target.value === "true" }))}
          >
            <option value="true">True</option>
            <option value="false">False</option>
          </select>
        </FormField>
        <div className="flex items-end">
          <button type="submit" className="bg-emerald-600 hover:bg-emerald-700 px-4 py-2 rounded">
            Senden
          </button>
        </div>
      </form>
      {toast && <Toast message={toast} />}
    </div>
  );
}
