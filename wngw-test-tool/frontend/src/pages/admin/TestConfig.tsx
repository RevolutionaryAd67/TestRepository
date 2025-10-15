import { useState } from "react";

const placeholderLists = [
  { id: "list-1", name: "Liste 1" },
  { id: "list-2", name: "Liste 2" },
];

export default function TestConfigurationPage() {
  const [selected, setSelected] = useState<string>(placeholderLists[0].id);
  return (
    <div className="p-6 space-y-4">
      <div className="bg-slate-900 border border-slate-800 rounded p-4">
        <label className="text-sm text-slate-300">Signalliste</label>
        <select
          className="bg-slate-800 rounded px-2 py-1 mt-2"
          value={selected}
          onChange={(event) => setSelected(event.target.value)}
        >
          {placeholderLists.map((list) => (
            <option key={list.id} value={list.id}>
              {list.name}
            </option>
          ))}
        </select>
      </div>
      <p className="text-slate-400 text-sm">TODO: Signallisten mit Backend verknüpfen.</p>
    </div>
  );
}
