import { useTranslation } from "react-i18next";

export default function LanguagePage() {
  const { i18n } = useTranslation();
  return (
    <div className="p-6 space-y-4">
      <div className="flex gap-4">
        <button
          onClick={() => i18n.changeLanguage("de")}
          className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded"
        >
          Deutsch
        </button>
        <button
          onClick={() => i18n.changeLanguage("en")}
          className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded"
        >
          English
        </button>
      </div>
      <p className="text-slate-400 text-sm">Spracheinstellungen gelten sofort.</p>
    </div>
  );
}
