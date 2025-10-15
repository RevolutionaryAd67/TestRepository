import { useMemo, useState } from "react";
import StartPage from "./pages/start/Start";
import TestConfigPage from "./pages/pruefung/Config";
import ProtocolsPage from "./pages/pruefung/Protocols";
import SignalListUploadPage from "./pages/signallisten/Upload";
import PartnerSettingsPage from "./pages/admin/Partners";
import TestConfigurationPage from "./pages/admin/TestConfig";
import LanguagePage from "./pages/admin/Language";
import { Header } from "./components/layout/Header";
import { Footer } from "./components/layout/Footer";
import { LeftSidebar } from "./components/layout/LeftSidebar";
import { RightSidebar } from "./components/layout/RightSidebar";
import { Tabs } from "./components/layout/Tabs";
import { routes, TabKey } from "./router";
import { LiveSocket } from "./lib/apiClient";
import { LiveLogView } from "./components/live/LiveLogView";

const socket = new LiveSocket();

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("start");
  const [activeRoute, setActiveRoute] = useState<string>(routes.start[0].key);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);

  const Content = useMemo(() => {
    switch (activeRoute) {
      case "start":
        return <StartPage />;
      case "tests-config":
        return <TestConfigPage />;
      case "tests-protocols":
        return <ProtocolsPage />;
      case "signal-upload":
        return <SignalListUploadPage />;
      case "admin-partners":
        return <PartnerSettingsPage />;
      case "admin-test-config":
        return <TestConfigurationPage />;
      case "admin-language":
        return <LanguagePage />;
      default:
        return <StartPage />;
    }
  }, [activeRoute]);

  const subRoutes = routes[activeTab];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <Tabs
        active={activeTab}
        onChange={(tab) => {
          setActiveTab(tab);
          const next = routes[tab][0];
          setActiveRoute(next.key);
        }}
      />
      <div className="flex flex-1">
        <LeftSidebar
          routes={subRoutes}
          active={activeRoute}
          onSelect={setActiveRoute}
          collapsed={leftCollapsed}
          onToggle={() => setLeftCollapsed((prev) => !prev)}
        />
        <main className="flex-1 overflow-y-auto bg-slate-950">{Content}</main>
        <RightSidebar collapsed={rightCollapsed} onToggle={() => setRightCollapsed((prev) => !prev)}>
          <LiveLogView socket={socket} />
        </RightSidebar>
      </div>
      <Footer />
    </div>
  );
}
