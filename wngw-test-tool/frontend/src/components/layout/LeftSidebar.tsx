import { SubRoute } from "../../router";
import { useTranslation } from "react-i18next";
import clsx from "clsx";

interface LeftSidebarProps {
  routes: SubRoute[];
  active: string;
  onSelect: (key: string) => void;
  collapsed: boolean;
  onToggle: () => void;
}

export function LeftSidebar({ routes, active, onSelect, collapsed, onToggle }: LeftSidebarProps) {
  const { t } = useTranslation();
  return (
    <aside className={clsx("bg-slate-900 border-r border-slate-800 transition-all", collapsed ? "w-16" : "w-56")}
    >
      <button
        className="w-full text-left px-4 py-2 text-xs text-slate-400 hover:text-slate-200"
        onClick={onToggle}
      >
        {collapsed ? ">" : "<"}
      </button>
      <nav className="flex flex-col gap-1 px-2">
        {routes.map((route) => (
          <button
            key={route.key}
            className={clsx(
              "text-left px-3 py-2 rounded-md text-sm",
              active === route.key
                ? "bg-slate-800 text-white"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            )}
            onClick={() => onSelect(route.key)}
          >
            {t(route.titleKey)}
          </button>
        ))}
      </nav>
    </aside>
  );
}
