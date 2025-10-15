import { FormEvent, useEffect, useState } from "react";
import { apiRequest } from "../../lib/apiClient";
import { FormField } from "../../components/ui/FormField";

interface PartnerSettings {
  client_ip: string;
  client_port: number;
  server_bind_ip: string;
  server_port: number;
  common_address: number;
  language: string;
}

export default function PartnerSettingsPage() {
  const [settings, setSettings] = useState<PartnerSettings | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<PartnerSettings>("/api/admin/partners").then(setSettings).catch(console.error);
  }, []);

  if (!settings) {
    return <div className="p-6 text-slate-400">Lade Einstellungen...</div>;
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const updated = await apiRequest<PartnerSettings>("/api/admin/partners", {
      method: "PUT",
      body: settings,
    });
    setSettings(updated);
    setMessage("Gespeichert");
    setTimeout(() => setMessage(null), 3000);
  };

  return (
    <div className="p-6 space-y-4">
      <form className="grid grid-cols-2 gap-4" onSubmit={handleSubmit}>
        <FormField label="Client IP">
          <input
            className="bg-slate-800 rounded px-2 py-1"
            value={settings.client_ip}
            onChange={(event) => setSettings({ ...settings, client_ip: event.target.value })}
          />
        </FormField>
        <FormField label="Client Port">
          <input
            type="number"
            className="bg-slate-800 rounded px-2 py-1"
            value={settings.client_port}
            onChange={(event) => setSettings({ ...settings, client_port: Number(event.target.value) })}
          />
        </FormField>
        <FormField label="Server Bind IP">
          <input
            className="bg-slate-800 rounded px-2 py-1"
            value={settings.server_bind_ip}
            onChange={(event) => setSettings({ ...settings, server_bind_ip: event.target.value })}
          />
        </FormField>
        <FormField label="Server Port">
          <input
            type="number"
            className="bg-slate-800 rounded px-2 py-1"
            value={settings.server_port}
            onChange={(event) => setSettings({ ...settings, server_port: Number(event.target.value) })}
          />
        </FormField>
        <FormField label="Common Address">
          <input
            type="number"
            className="bg-slate-800 rounded px-2 py-1"
            value={settings.common_address}
            onChange={(event) => setSettings({ ...settings, common_address: Number(event.target.value) })}
          />
        </FormField>
        <div className="col-span-2 flex items-center justify-between">
          <FormField label="Sprache">
            <select
              className="bg-slate-800 rounded px-2 py-1"
              value={settings.language}
              onChange={(event) => setSettings({ ...settings, language: event.target.value })}
            >
              <option value="de">Deutsch</option>
              <option value="en">English</option>
            </select>
          </FormField>
          <button type="submit" className="bg-emerald-600 hover:bg-emerald-700 px-4 py-2 rounded">
            Speichern
          </button>
        </div>
      </form>
      {message && <div className="text-emerald-400 text-sm">{message}</div>}
    </div>
  );
}
