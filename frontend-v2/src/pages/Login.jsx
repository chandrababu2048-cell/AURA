// src/pages/Login.jsx
// Glass login / register screen. Talks to /auth/login and
// /auth/register via authService, stores the user in useUserStore.

import { useState } from "react";
import { motion } from "framer-motion";
import { LogIn, UserPlus, Loader2 } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { SymbiteLogo } from "@/components/aura/SymbiteLogo";
import { login, register } from "@/services/authService";
import { useUserStore } from "@/store/useUserStore";

const inputCls =
  "w-full bg-white/5 border border-white/10 rounded-xl px-3.5 py-2.5 text-sm " +
  "text-aura-ink placeholder:text-aura-muted outline-none " +
  "focus:border-aura-accent/60 focus:shadow-[0_0_16px_rgba(46,168,255,0.15)] transition-all";

export default function Login() {
  const setUser = useUserStore((s) => s.setUser);

  const [mode, setMode] = useState("login"); // "login" | "register"
  const [form, setForm] = useState({ name: "", email: "", password: "", ai_name: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e?.preventDefault();
    setError(null);

    if (!form.email.trim() || !form.password) {
      setError("Email and password are required.");
      return;
    }
    if (mode === "register" && !form.name.trim()) {
      setError("Tell Symbite your name.");
      return;
    }

    setBusy(true);
    try {
      if (mode === "register") {
        const reg = await register({
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password,
          ai_name: form.ai_name.trim() || undefined,
        });
        if (!reg.success) {
          setError(reg.message || "Registration failed.");
          return;
        }
      }
      const res = await login(form.email.trim(), form.password);
      if (res.success && res.user) {
        setUser(res.user); // App.jsx flips to Dashboard
      } else {
        setError(res.message || "Login failed.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="aura-app-bg h-screen w-screen overflow-hidden grid place-items-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-sm"
      >
        <GlassCard strong grid className="p-8">
          {/* Identity */}
          <div className="flex flex-col items-center gap-3 mb-7">
            <SymbiteLogo size={56} />
            <div className="text-center">
              <h1 className="font-display text-3xl tracking-[0.42em] font-semibold bg-gradient-to-b from-white via-aura-accentSoft to-aura-accent bg-clip-text text-transparent">
                AURA
              </h1>
              <p className="mt-1 text-[10px] tracking-[0.34em] text-aura-soft uppercase">
                Symbiote Intelligence
              </p>
            </div>
          </div>

          <form onSubmit={submit} className="space-y-3">
            {mode === "register" && (
              <>
                <input
                  value={form.name}
                  onChange={set("name")}
                  placeholder="Your name"
                  autoComplete="name"
                  className={inputCls}
                />
                <input
                  value={form.ai_name}
                  onChange={set("ai_name")}
                  placeholder="Name your Symbite (optional)"
                  className={inputCls}
                />
              </>
            )}
            <input
              value={form.email}
              onChange={set("email")}
              placeholder="Email"
              type="email"
              autoComplete="email"
              className={inputCls}
            />
            <input
              value={form.password}
              onChange={set("password")}
              placeholder="Password"
              type="password"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              className={inputCls}
            />

            {error && (
              <p className="text-[11px] text-red-400/90 leading-snug px-1">{error}</p>
            )}

            <button
              type="submit"
              disabled={busy}
              className="w-full flex items-center justify-center gap-2 rounded-xl py-2.5 text-sm font-medium text-white
                         bg-gradient-to-r from-aura-accentDeep to-aura-accent
                         shadow-[0_0_24px_rgba(46,168,255,0.35)] hover:shadow-[0_0_32px_rgba(46,168,255,0.5)]
                         disabled:opacity-60 transition-all"
            >
              {busy ? (
                <Loader2 size={16} className="animate-spin" />
              ) : mode === "login" ? (
                <LogIn size={15} />
              ) : (
                <UserPlus size={15} />
              )}
              {mode === "login" ? "Enter" : "Begin the Bond"}
            </button>
          </form>

          <button
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError(null);
            }}
            className="mt-5 w-full text-center text-[11px] text-aura-muted hover:text-aura-ink transition-colors"
          >
            {mode === "login"
              ? "First time? Create your Symbite →"
              : "Already bonded? Sign in →"}
          </button>
        </GlassCard>
      </motion.div>
    </div>
  );
}
