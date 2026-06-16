// src/components/layout/LeftPanel.jsx
// Sidebar + dynamic content panel. Nav state controls which view renders.
// Home loads live data: goals (/goals) + boss state (/state).

import { useEffect, useState } from "react";
import { Sidebar } from "./Sidebar";
import { TaskList } from "@/components/tasks/TaskList";
import { GoalList } from "@/components/goals/GoalList";
import { MemoryView } from "@/components/memory/MemoryView";
import { WeeklyProgress } from "@/components/dashboard/WeeklyProgress";
import { FocusScore } from "@/components/dashboard/FocusScore";
import { BossState } from "@/components/dashboard/BossState";
import { Recommendation } from "@/components/dashboard/Recommendation";
import { GlassCard } from "@/components/ui/GlassCard";
import { useNavStore } from "@/store/useNavStore";
import { useUserStore } from "@/store/useUserStore";
import { useGoalStore } from "@/store/useGoalStore";
import { useStateStore } from "@/store/useStateStore";
import { updateAiName as apiUpdateAiName } from "@/services/authService";
import { Link2, LineChart, Sparkles, Calendar, Check, Pencil } from "lucide-react";

function HomeView() {
  const userId = useUserStore((s) => s.user.id);
  const loadGoals = useGoalStore((s) => s.loadGoals);
  const loadState = useStateStore((s) => s.loadState);

  useEffect(() => {
    if (!userId) return;
    loadGoals(userId);
    loadState(userId);
  }, [userId, loadGoals, loadState]);

  return (
    <div className="flex-1 px-4 pb-4 space-y-3 overflow-y-auto aura-scroll">
      <TaskList />
      <WeeklyProgress />
      <div className="flex gap-3">
        <FocusScore />
        <BossState />
      </div>
      <Recommendation />
    </div>
  );
}

function TasksView() {
  return (
    <div className="flex-1 px-4 pb-4 overflow-y-auto aura-scroll">
      <TaskList />
    </div>
  );
}

function GoalsView() {
  return (
    <div className="flex-1 px-4 pb-4 overflow-y-auto aura-scroll">
      <GoalList />
    </div>
  );
}

function MemoryVaultView() {
  return (
    <div className="flex-1 px-4 pb-4 overflow-y-auto aura-scroll">
      <MemoryView />
    </div>
  );
}

function ComingSoonView({ icon: Icon, label, description }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-3 px-6 text-center">
      <div className="w-14 h-14 rounded-2xl glass-inner flex items-center justify-center">
        <Icon size={24} className="text-aura-accentSoft" strokeWidth={1.5} />
      </div>
      <h3 className="font-display font-semibold text-aura-ink text-base">{label}</h3>
      <p className="text-xs text-aura-muted leading-relaxed">{description}</p>
      <div className="mt-2 px-3 py-1 rounded-full glass-inner text-[10px] tracking-widest text-aura-accent uppercase">
        Coming Soon
      </div>
    </div>
  );
}

function SettingsView() {
  const user = useUserStore((s) => s.user);
  const updateAiName = useUserStore((s) => s.updateAiName);
  const logout = useUserStore((s) => s.logout);

  const [editing, setEditing] = useState(false);
  const [aiDraft, setAiDraft] = useState(user?.ai_name ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const saveAiName = async () => {
    const name = aiDraft.trim();
    if (!name || name === user.ai_name) {
      setEditing(false);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await apiUpdateAiName(user.id, name);
      updateAiName(name);
      setEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex-1 px-4 pb-4 overflow-y-auto aura-scroll space-y-3">
      <GlassCard inner className="p-5 space-y-4">
        <h3 className="font-display font-semibold text-aura-ink text-sm">Account</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-aura-muted">Your Name</span>
            <span className="text-xs text-aura-ink font-medium">{user?.name ?? "—"}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-aura-muted">Email</span>
            <span className="text-xs text-aura-ink font-medium">{user?.email ?? "—"}</span>
          </div>
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs text-aura-muted shrink-0">AI Name</span>
            {editing ? (
              <span className="flex items-center gap-1.5">
                <input
                  value={aiDraft}
                  onChange={(e) => setAiDraft(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && saveAiName()}
                  className="w-28 bg-white/5 border border-aura-accent/40 rounded-lg px-2 py-1 text-xs text-aura-ink outline-none"
                  autoFocus
                />
                <button
                  onClick={saveAiName}
                  disabled={saving}
                  aria-label="Save AI name"
                  className="text-aura-mint hover:scale-110 transition-transform"
                >
                  <Check size={13} />
                </button>
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <span className="text-xs text-aura-ink font-medium">{user?.ai_name ?? "—"}</span>
                <button
                  onClick={() => {
                    setAiDraft(user?.ai_name ?? "");
                    setEditing(true);
                  }}
                  aria-label="Edit AI name"
                  className="text-aura-muted hover:text-aura-ink transition-colors"
                >
                  <Pencil size={11} />
                </button>
              </span>
            )}
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-aura-muted">Wake Time</span>
            <span className="text-xs text-aura-ink font-medium">{user?.wake_time ?? "—"}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-aura-muted">Sleep Time</span>
            <span className="text-xs text-aura-ink font-medium">{user?.sleep_time ?? "—"}</span>
          </div>
        </div>
        {error && <p className="text-[11px] text-red-400/80">{error}</p>}
      </GlassCard>

      <GlassCard inner className="p-5 space-y-3">
        <h3 className="font-display font-semibold text-aura-ink text-sm">Connectors</h3>
        {[
          { name: "Calendar", status: "Connected", ok: true },
          { name: "Gmail", status: "Phase 3", ok: false },
          { name: "Apple Health", status: "Phase 4", ok: false },
          { name: "Spotify", status: "Phase 4", ok: false },
        ].map(({ name, status, ok }) => (
          <div key={name} className="flex items-center justify-between">
            <span className="text-xs text-aura-soft">{name}</span>
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${ok ? "bg-aura-mint/20 text-aura-mint" : "bg-white/5 text-aura-muted"}`}>
              {status}
            </span>
          </div>
        ))}
      </GlassCard>

      <button
        onClick={logout}
        className="w-full py-2 rounded-xl border border-white/10 text-xs text-aura-muted hover:text-aura-ink hover:border-white/20 transition-colors"
      >
        Sign out
      </button>
    </div>
  );
}

const VIEWS = {
  home: <HomeView />,
  tasks: <TasksView />,
  goals: <GoalsView />,
  memory: <MemoryVaultView />,
  skills: <ComingSoonView icon={Sparkles} label="Skills" description="Skill tracking and growth metrics coming in Phase 4." />,
  calendar: <ComingSoonView icon={Calendar} label="Calendar" description="Calendar connector is live. Full UI view coming soon." />,
  insights: <ComingSoonView icon={LineChart} label="Insights" description="Cognitive drag, bond analytics, and pattern insights. Phase 4." />,
  connections: <ComingSoonView icon={Link2} label="Connections" description="Connect Calendar, Gmail, Apple Health, Spotify and more." />,
  settings: <SettingsView />,
};

export function LeftPanel() {
  const active = useNavStore((s) => s.active);

  const titles = {
    home: "Today Overview",
    tasks: "Daily Tasks",
    goals: "Your Goals",
    skills: "Skills",
    calendar: "Calendar",
    memory: "Memory Vault",
    insights: "Insights",
    connections: "Connections",
    settings: "Settings",
  };

  return (
    <GlassCard grid className="h-full overflow-hidden flex">
      <Sidebar />
      <div className="flex-1 border-l border-white/10 flex flex-col min-w-0">
        <header className="px-5 pt-5 pb-3 shrink-0">
          <p className="text-[10px] tracking-[0.28em] font-semibold text-aura-muted uppercase">
            {titles[active] ?? "Overview"}
          </p>
        </header>
        {VIEWS[active] ?? VIEWS.home}
      </div>
    </GlassCard>
  );
}

export default LeftPanel;
