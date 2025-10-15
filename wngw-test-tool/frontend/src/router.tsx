export type TabKey = "start" | "tests" | "signals" | "admin";

export interface SubRoute {
  key: string;
  titleKey: string;
  tab: TabKey;
}

export const routes: Record<TabKey, SubRoute[]> = {
  start: [{ key: "start", titleKey: "nav.start", tab: "start" }],
  tests: [
    { key: "tests-config", titleKey: "tests.singleCommand", tab: "tests" },
    { key: "tests-protocols", titleKey: "tests.protocols", tab: "tests" },
  ],
  signals: [{ key: "signal-upload", titleKey: "signal.upload", tab: "signals" }],
  admin: [
    { key: "admin-partners", titleKey: "admin.partners", tab: "admin" },
    { key: "admin-test-config", titleKey: "admin.testConfig", tab: "admin" },
    { key: "admin-language", titleKey: "admin.language", tab: "admin" },
  ],
};
