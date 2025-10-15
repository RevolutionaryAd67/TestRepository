import { ReactNode } from "react";
import clsx from "clsx";

interface RightSidebarProps {
  children: ReactNode;
  collapsed: boolean;
  onToggle: () => void;
}

export function RightSidebar({ children, collapsed, onToggle }: RightSidebarProps) {
  return (
    <aside
      className={clsx(
        "bg-slate-900 border-l border-slate-800 transition-all flex flex-col",
        collapsed ? "w-14" : "w-80"
      )}
    >
      <button
        className="px-4 py-2 text-xs text-slate-400 hover:text-slate-200"
        onClick={onToggle}
      >
        {collapsed ? "<" : ">"}
      </button>
      {!collapsed && <div className="flex-1 overflow-y-auto">{children}</div>}
    </aside>
  );
}
