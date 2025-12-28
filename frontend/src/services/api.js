import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Teams API
export const teamsAPI = {
  getAll: (params = {}) => api.get('/api/teams', { params }),
  getById: (id) => api.get(`/api/teams/${id}`),
  refresh: () => api.post('/api/teams/refresh'),
};

// Simulations API
export const simulationsAPI = {
  run: (data) => api.post('/api/simulate', data),
  getById: (id) => api.get(`/api/simulations/${id}`),
  getAll: (params = {}) => api.get('/api/simulations', { params }),
  delete: (id) => api.delete(`/api/simulations/${id}`),
};

// Statistics API
export const statsAPI = {
  getSummary: () => api.get('/api/stats/summary'),
};

export default api;
