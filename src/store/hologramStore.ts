import { create } from 'zustand';

type HologramStore = {
  /** Anzahl Partikel pro Burst, kann von außen überschrieben werden */
  defaultBurstCount: number;
  /** Signalisiert einen neuen Burst mit gewünschter Partikelzahl */
  pendingBursts: number[];
  triggerBurst: (count?: number) => void;
  consumeBurst: () => number | null;
  setDefaultBurstCount: (n: number) => void;
};

export const useHologramStore = create<HologramStore>((set, get) => ({
  defaultBurstCount: 80,
  pendingBursts: [],
  triggerBurst: (count) => set((s) => ({ pendingBursts: [...s.pendingBursts, count ?? s.defaultBurstCount] })),
  consumeBurst: () => {
    const { pendingBursts } = get();
    if (pendingBursts.length === 0) return null;
    const [head, ...tail] = pendingBursts;
    set({ pendingBursts: tail });
    return head;
  },
  setDefaultBurstCount: (n) => set({ defaultBurstCount: n }),
}));

