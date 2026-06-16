// src/hooks/useAuraState.js
// Tiny convenience hook around useAuraStore for components that
// just want to read/drive the avatar state.

import { useAuraStore } from "@/store/useAuraStore";

export function useAuraState() {
  return {
    state: useAuraStore((s) => s.state),
    anchored: useAuraStore((s) => s.anchored),
    position: useAuraStore((s) => s.position),
    setState: useAuraStore((s) => s.setState),
    setPosition: useAuraStore((s) => s.setPosition),
    enterRoamingMode: useAuraStore((s) => s.enterRoamingMode),
    exitRoamingMode: useAuraStore((s) => s.exitRoamingMode),
  };
}

export default useAuraState;
