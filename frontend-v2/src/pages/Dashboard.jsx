// src/pages/Dashboard.jsx
// The main 3-panel desktop layout.

import { LeftPanel } from "@/components/layout/LeftPanel";
import { CenterPanel } from "@/components/layout/CenterPanel";
import { ChatPanel } from "@/components/chat/ChatPanel";

export default function Dashboard() {
  return (
    <div className="aura-app-bg h-screen w-screen overflow-hidden">
      <div className="h-full w-full px-4 py-4 md:px-6 md:py-6">
        <div className="h-full w-full grid grid-cols-12 gap-4 md:gap-6">
          <section className="col-span-12 md:col-span-4 h-full min-h-0">
            <LeftPanel />
          </section>
          <section className="col-span-12 md:col-span-5 h-full min-h-0">
            <CenterPanel />
          </section>
          <section className="col-span-12 md:col-span-3 h-full min-h-0">
            <ChatPanel />
          </section>
        </div>
      </div>
    </div>
  );
}
