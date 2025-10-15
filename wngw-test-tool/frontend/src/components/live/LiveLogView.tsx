import { useEffect, useMemo, useState } from "react";
import { LiveSocket } from "../../lib/apiClient";

export interface LiveEvent {
  kind: string;
  role: "client" | "server";
  dir: "tx" | "rx";
  ts: string;
  apci: { type: string; vs: number; vr: number };
  asdu: { typeId: number; cause: number; ca: number; ioa: number | null; payload: Record<string, unknown> };
  raw: string | null;
}

interface Filters {
  role: "all" | "client" | "server";
  dir: "all" | "tx" | "rx";
  typeId: string;
  search: string;
  freeze: boolean;
}

const defaultFilters: Filters = {
  role: "all",
  dir: "all",
  typeId: "",
  search: "",
  freeze: false,
};

interface LiveLogViewProps {
  socket: LiveSocket;
}

export function LiveLogView({ socket }: LiveLogViewProps) {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [filters, setFilters] = useState<Filters>(defaultFilters);

  useEffect(() => {
    return socket.subscribe((data) => {
      if (!data || typeof data !== "object") {
        return;
      }
      const event = data as LiveEvent;
      setEvents((prev) => {
        const next = filters.freeze ? prev : [...prev, event];
        return next.slice(-200);
      });
    });
  }, [socket, filters.freeze]);

  const filtered = useMemo(() => {
    return events.filter((event) => {
      if (filters.role !== "all" && event.role !== filters.role) return false;
      if (filters.dir !== "all" && event.dir !== filters.dir) return false;
      if (filters.typeId && event.asdu.typeId !== Number(filters.typeId)) return false;
      if (filters.search) {
        const target = JSON.stringify(event).toLowerCase();
        if (!target.includes(filters.search.toLowerCase())) return false;
      }
      return true;
    });
  }, [events, filters]);

  return (
    <div className="p-4 space-y-4">
      <div className="grid grid-cols-2 gap-2 text-xs">
        <select
          value={filters.role}
          onChange={(event) => setFilters((prev) => ({ ...prev, role: event.target.value as Filters["role"] }))}
          className="bg-slate-800 rounded px-2 py-1"
        >
          <option value="all">All roles</option>
          <option value="client">Client</option>
          <option value="server">Server</option>
        </select>
        <select
          value={filters.dir}
          onChange={(event) => setFilters((prev) => ({ ...prev, dir: event.target.value as Filters["dir"] }))}
          className="bg-slate-800 rounded px-2 py-1"
        >
          <option value="all">All directions</option>
          <option value="tx">TX</option>
          <option value="rx">RX</option>
        </select>
        <input
          placeholder="Type ID"
          value={filters.typeId}
          onChange={(event) => setFilters((prev) => ({ ...prev, typeId: event.target.value }))}
          className="bg-slate-800 rounded px-2 py-1 col-span-2"
        />
        <input
          placeholder="Search"
          value={filters.search}
          onChange={(event) => setFilters((prev) => ({ ...prev, search: event.target.value }))}
          className="bg-slate-800 rounded px-2 py-1 col-span-2"
        />
        <label className="flex items-center gap-2 col-span-2">
          <input
            type="checkbox"
            checked={filters.freeze}
            onChange={(event) => setFilters((prev) => ({ ...prev, freeze: event.target.checked }))}
          />
          Freeze
        </label>
      </div>
      <div className="space-y-2 text-xs">
        {filtered.map((event, index) => (
          <div key={index} className="bg-slate-800 rounded px-2 py-2">
            <div className="flex justify-between text-slate-400">
              <span>
                {event.role.toUpperCase()} {event.dir.toUpperCase()} Type {event.asdu.typeId}
              </span>
              <span>{new Date(event.ts).toLocaleTimeString()}</span>
            </div>
            <pre className="text-slate-200 whitespace-pre-wrap text-[10px]">
              {JSON.stringify(event.asdu.payload, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
