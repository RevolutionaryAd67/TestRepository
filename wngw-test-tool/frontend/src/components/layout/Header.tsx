import { useTranslation } from "react-i18next";

export function Header() {
  const { t } = useTranslation();
  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
      <h1 className="text-xl font-semibold">WNGW Test Tool</h1>
      <span className="text-sm text-slate-400">IEC 60870-5-104</span>
    </header>
  );
}
