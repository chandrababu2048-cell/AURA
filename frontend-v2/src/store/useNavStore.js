import { create } from "zustand";

export const useNavStore = create((set) => ({
  active: "home",
  setActive: (key) => set({ active: key }),
}));
