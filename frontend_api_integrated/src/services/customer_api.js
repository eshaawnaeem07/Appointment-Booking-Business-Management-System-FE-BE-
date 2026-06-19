import api from './api';

const BASE_URL = '/businesses';

export const customerApi = {
  getAllCustomers: (businessId) => {
    return api.get(`${BASE_URL}/${businessId}/customers`);
  },

  getCustomerById: (businessId, customerId) => {
    return api.get(`${BASE_URL}/${businessId}/customers/${customerId}`);
  },

  createCustomer: (businessId, customerData) => {
    return api.post(`${BASE_URL}/${businessId}/customers`, customerData);
  },

  updateCustomer: (businessId, customerId, customerData) => {
    return api.put(`${BASE_URL}/${businessId}/customers/${customerId}`, customerData);
  },

  deleteCustomer: (businessId, customerId) => {
    return api.delete(`${BASE_URL}/${businessId}/customers/${customerId}`);
  },
};
