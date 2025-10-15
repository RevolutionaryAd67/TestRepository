import clsx from "clsx";
import { TabKey } from "../../router";
import { useTranslation } from "react-i18next";

interface TabsProps {
  active: TabKey;
  onChange: (tab: TabKey) => void;
}

export function Tabs({ active, onChange }: TabsProps) {
  const { t } = useTranslation();
  const tabs: { key: TabKey; label: string }[] = [
    { key: "start", label: t("nav.start") },
    { key: "tests", label: t("nav.tests") },
    { key: "signals", label: t("nav.signalLists") },
    { key: "admin", label: t("nav.admin") },
  ];
  return (
    <div className="flex gap-2 bg-slate-900 border-b border-slate-800 px-6 py-2">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={clsx(
            "px-3 py-1 rounded-md text-sm",
            active === tab.key ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white"
          )}
          onClick={() => onChange(tab.key)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
