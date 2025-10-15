import { FormEvent, useState } from "react";

interface UploadResult {
  status: string;
  data?: { records: { ioa: number; label: string; unit: string }[]; path: string };
  detail?: string;
}

export default function SignalListUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch("http://localhost:8000/api/signal-lists/upload", {
      method: "POST",
      body: formData,
    });
    setResult(await response.json());
  };

  return (
    <div className="p-6 space-y-4">
      <form className="flex items-center gap-4" onSubmit={handleSubmit}>
        <input type="file" accept=".xlsx" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        <button type="submit" className="bg-emerald-600 hover:bg-emerald-700 px-4 py-2 rounded">
          Hochladen
        </button>
      </form>
      {result?.data && (
        <div className="bg-slate-900 border border-slate-800 rounded p-4">
          <h3 className="font-semibold mb-2">Extrahierte Signale</h3>
          <ul className="space-y-1 text-sm">
            {result.data.records.map((row, index) => (
              <li key={index} className="text-slate-300">
                {row.ioa} – {row.label} ({row.unit})
              </li>
            ))}
          </ul>
        </div>
      )}
      {result?.detail && <div className="text-red-400 text-sm">{result.detail}</div>}
    </div>
  );
}
