import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  de: {
    translation: {
      "nav.start": "Start",
      "nav.tests": "Prüfung",
      "nav.signalLists": "Signallisten",
      "nav.admin": "Administration",
      "live.title": "Live-Kommunikation",
      "tests.singleCommand": "Einzelkommando",
      "tests.protocols": "Prüfprotokolle",
      "signal.upload": "Signalliste hochladen",
      "admin.partners": "Kommunikationspartner",
      "admin.testConfig": "Prüfungskonfiguration",
      "admin.language": "Sprache",
    },
  },
  en: {
    translation: {
      "nav.start": "Start",
      "nav.tests": "Testing",
      "nav.signalLists": "Signal Lists",
      "nav.admin": "Administration",
      "live.title": "Live Communication",
      "tests.singleCommand": "Single Command",
      "tests.protocols": "Test Protocols",
      "signal.upload": "Upload Signal List",
      "admin.partners": "Partners",
      "admin.testConfig": "Test Configuration",
      "admin.language": "Language",
    },
  },
} as const;

i18n.use(initReactI18next).init({
  resources,
  lng: "de",
  fallbackLng: "de",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
