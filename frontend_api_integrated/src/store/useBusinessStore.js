import { create } from "zustand";

const useBusinessStore = create(set => ({
  business: null,
  businessId: null, // Add businessId to the state
  setBusiness: business => set({
    business,
    businessId: business ? business.id : null, // Extract and store businessId
  }),
}));

export default useBusinessStore;