import { LiveEvent } from "./LiveLogView";

interface FrameInspectorProps {
  event: LiveEvent | null;
}

export function FrameInspector({ event }: FrameInspectorProps) {
  if (!event) {
    return <div className="text-xs text-slate-500 p-4">No frame selected.</div>;
  }
  return (
    <pre className="text-[10px] text-slate-200 bg-slate-800 rounded m-4 p-4 overflow-auto">
      {JSON.stringify(event, null, 2)}
    </pre>
  );
}
