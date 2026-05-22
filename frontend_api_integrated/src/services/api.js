import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('Missing refresh token');

        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh-token`, {
          refresh_token: refreshToken,
        });

        localStorage.setItem('access_token', data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authApi = {
  login: (payload) => api.post('/auth/login', payload),
  register: (payload) => api.post('/auth/register', payload),
  forgotPassword: (payload) => api.post('/auth/forgot-password', payload),
  resetPassword: (payload) => api.post('/auth/reset-password', payload),
};

export const businessesApi = {
  list: () => api.get('/businesses/'),
  get: (id) => api.get(`/businesses/${id}`),
  create: (payload) => api.post('/businesses/', payload),
  update: (id, payload) => api.put(`/businesses/${id}`, payload),
  remove: (id) => api.delete(`/businesses/${id}`),
  hours: (id) => api.get(`/businesses/${id}/hours`),
  saveHours: (id, payload) => api.post(`/businesses/${id}/hours`, payload),
  updateHour: (id, hourId, payload) => api.put(`/businesses/${id}/hours/${hourId}`, payload),
  appointments: (id) => api.get(`/businesses/${id}/appointments`),
  customers: (id) => api.get(`/businesses/${id}/customers`),
  getCustomer: (id, customerId) => api.get(`/businesses/${id}/customers/${customerId}`),
  createCustomer: (id, payload) => api.post(`/businesses/${id}/customers`, payload),
  updateCustomer: (id, customerId, payload) => api.put(`/businesses/${id}/customers/${customerId}`, payload),
  deleteCustomer: (id, customerId) => api.delete(`/businesses/${id}/customers/${customerId}`),
};

export const servicesApi = {
  listByBusiness: (businessId) => api.get(`/services/businesses/${businessId}/services`),
  get: (serviceId) => api.get(`/services/services/${serviceId}`),
  availableSlots: (serviceId, selectedDate) => api.get(`/services/${serviceId}/available-slots`, { params: selectedDate ? { selected_date: selectedDate } : {} }),
  create: (businessId, payload) => api.post(`/services/businesses/${businessId}/services`, payload),
  update: (serviceId, payload) => api.put(`/services/services/${serviceId}`, payload),
  remove: (serviceId) => api.delete(`/services/services/${serviceId}`),
};

export const appointmentsApi = {
  mine: () => api.get('/appointments'),
  get: (id) => api.get(`/appointments/${id}`),
  create: (payload) => api.post('/appointments', payload),
  reschedule: (id, payload) => api.patch(`/appointments/${id}`, payload),
  confirm: (id) => api.patch(`/appointments/${id}/confirm`),
  complete: (id) => api.patch(`/appointments/${id}/complete`),
  noShow: (id) => api.patch(`/appointments/${id}/no-show`),
};

export const paymentsApi = {
  checkout: (payload) => api.post('/payments/checkout-session', payload),
  status: (appointmentId) => api.get(`/payments/appointments/${appointmentId}/status`),
};

export default api;
