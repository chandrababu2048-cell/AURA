// src/components/memory/MemoryView.jsx
// Memory Vault view — LIVE. Shows what Symbite currently holds in
// working memory: the morning context block (/memory/context) and
// the weekly analytics report (/memory/report).

import { useEffect, useState } from "react";
import { Brain, BarChart3, RefreshCw } from "lucide-react";
import { fetchContext, fetchWeeklyReport } from "@/services/memoryService";
import { useUserStore } from "@/store/useUserStore";

function MemoryCard({ icon: Icon, title, body, loading }) {
  return (
    <div
      className="rounded-2xl p-5"
      style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}
    >
      <div className="flex items-center gap-2 mb-3">
        <div
          className="w-7 h-7 rounded-xl grid place-items-center"
          style={{ background: "rgba(46,168,255,0.15)" }}
        >
          <Icon size={14} className="text-aura-accent" strokeWidth={2} />
        </div>
        <p className="text-[10px] tracking-[0.22em] text-aura-muted uppercase font-semibold">
          {title}
        </p>
      </div>
      {loading ? (
        <p className="text-xs text-aura-muted">Reading memory…</p>
      ) : (
        <pre className="text-xs text-aura-soft leading-relaxed whitespace-pre-wrap font-sans">
          {body || "Nothing here yet."}
        </pre>
      )}
    </div>
  );
}

export function MemoryView() {
  const userId = useUserStore((s) => s.user.id);
  const [context, setContext] = useState("");
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const [ctx, rep] = await Promise.all([
        fetchContext(userId),
        fetchWeeklyReport(userId),
      ]);
      setContext(ctx);
      setReport(rep);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <button
          onClick={load}
          className="flex items-center gap-1.5 text-[10px] tracking-widest uppercase text-aura-muted hover:text-aura-ink transition-colors"
        >
          <RefreshCw size={11} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>
      {error && (
        <p className="text-xs text-red-400/80 px-1">
          Couldn't reach the vault: {error}
        </p>
      )}
      <MemoryCard
        icon={Brain}
        title="What Symbite knows right now"
        body={context}
        loading={loading}
      />
      <MemoryCard
        icon={BarChart3}
        title="Weekly Report"
        body={report}
        loading={loading}
      />
    </div>
  );
}

export default MemoryView;
