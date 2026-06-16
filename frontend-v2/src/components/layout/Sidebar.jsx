// src/components/layout/Sidebar.jsx
// Vertical navigation rail inside the left panel.

import clsx from "clsx";
import { motion } from "framer-motion";
import {
  Home,
  ListChecks,
  Target,
  Sparkles,
  Calendar,
  Brain,
  LineChart,
  Link2,
  Settings,
  ChevronRight,
} from "lucide-react";
import { useUserStore } from "@/store/useUserStore";
import { useNavStore } from "@/store/useNavStore";
import { SymbiteLogo } from "@/components/aura/SymbiteLogo";

const NAV = [
  { key: "home", label: "Home", icon: Home },
  { key: "tasks", label: "Tasks", icon: ListChecks },
  { key: "goals", label: "Goals", icon: Target },
  { key: "skills", label: "Skills", icon: Sparkles },
  { key: "calendar", label: "Calendar", icon: Calendar },
  { key: "memory", label: "Memory", icon: Brain },
  { key: "insights", label: "Insights", icon: LineChart },
  { key: "connections", label: "Connections", icon: Link2 },
  { key: "settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const active = useNavStore((s) => s.active);
  const setActive = useNavStore((s) => s.setActive);
  const user = useUserStore((s) => s.user);

  return (
    <aside className="flex flex-col items-stretch gap-5 px-3 py-5 w-[108px]">
      {/* Symbiote Logo */}
      <div className="flex flex-col items-center gap-2 pt-1">
        <SymbiteLogo size={46} />
        <span className="text-[11px] tracking-[0.38em] font-display font-semibold text-aura-ink">
          AURA
        </span>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 mt-1">
        {NAV.map(({ key, label, icon: Icon }) => {
          const isActive = key === active;
          return (
            <motion.button
              key={key}
              whileHover={{ x: 1 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => setActive(key)}
              className={clsx(
                "group relative flex items-center gap-2.5 rounded-xl py-2 px-2.5 text-[11px] font-medium tracking-wide transition-all",
                isActive
                  ? "text-white bg-gradient-to-r from-aura-accent/25 to-aura-accent/5 ring-1 ring-aura-accent/40 shadow-[0_0_20px_rgba(46,168,255,0.2)]"
                  : "text-aura-soft hover:text-aura-ink hover:bg-white/5",
              )}
              title={label}
            >
              <Icon
                size={16}
                strokeWidth={1.8}
                className={isActive ? "text-aura-accentSoft" : ""}
              />
              <span>{label}</span>
              {isActive && (
                <motion.span
                  layoutId="nav-active-indicator"
                  className="absolute left-0 top-1.5 bottom-1.5 w-[2px] rounded-r-full bg-aura-accentSoft shadow-glow"
                />
              )}
            </motion.button>
          );
        })}
      </nav>

      {/* User chip at bottom */}
      <div className="mt-auto flex items-center gap-2 p-1.5 glass-inner">
        <div className="relative w-8 h-8 rounded-full bg-gradient-to-br from-aura-accentSoft to-aura-accentDeep grid place-items-center text-white font-semibold shadow-glow shrink-0">
          {user?.name?.[0]?.toUpperCase() ?? "B"}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-hand text-[16px] leading-tight text-aura-ink truncate">
            {user?.name ?? "Boss"}
          </div>
          <div className="text-[9px] text-aura-muted tracking-wider">
            Pro Plan
          </div>
        </div>
        <ChevronRight size={12} className="text-aura-muted" />
      </div>
    </aside>
  );
}

export default Sidebar;
