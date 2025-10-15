import { ReactNode } from "react";

interface DialogProps {
  title: string;
  children: ReactNode;
}

export function Dialog({ title, children }: DialogProps) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 shadow-xl">
      <h2 className="text-lg font-semibold mb-3">{title}</h2>
      <div>{children}</div>
    </div>
  );
}
