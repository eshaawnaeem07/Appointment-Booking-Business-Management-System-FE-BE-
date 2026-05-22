import { create } from "zustand";

const useBusinessStore = create(set => ({
  business: null,
  setBusiness: business => set({ business }),
}));

export default useBusinessStore;