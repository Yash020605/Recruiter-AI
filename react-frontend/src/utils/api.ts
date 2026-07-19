import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://recruiter-ai-production-9983.up.railway.app';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
