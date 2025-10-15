import { useEffect, useState } from "react";
import { apiRequest } from "../../lib/apiClient";
import { DataTable } from "../../components/ui/DataTable";

interface ProtocolEntry {
  path: string;
  created_at: string;
  description?: string | null;
}

export default function ProtocolsPage() {
  const [entries, setEntries] = useState<ProtocolEntry[]>([]);

  useEffect(() => {
    apiRequest<ProtocolEntry[]>("/api/tests/protocols").then(setEntries).catch(console.error);
  }, []);

  return (
    <div className="p-6">
      <DataTable
        data={entries}
        columns={[
          { header: "Datei", accessor: (row) => row.path },
          { header: "Erstellt", accessor: (row) => new Date(row.created_at).toLocaleString() },
        ]}
      />
    </div>
  );
}
