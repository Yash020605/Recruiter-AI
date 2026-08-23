import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://recruiter-ai-backend-production-1c27.up.railway.app';

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

// --- Added Collaboration & Verification API Helpers ---
export const addCandidateComment = (candidateId: number, content: string) =>
  api.post(`/candidates/${candidateId}/comments`, { text: content });

export const getCandidateComments = (candidateId: number) => 
  api.get(`/candidates/${candidateId}/comments`);

export const triggerReferenceCheck = (candidateId: number, refereeEmail: string) =>
  api.post(`/candidates/${candidateId}/reference-check`, { referee_email: refereeEmail });

// --- Export helpers ---
const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`,
});

const downloadCsv = async (url: string, filename: string) => {
  const API_URL = import.meta.env.VITE_API_URL || 'https://recruiter-ai-backend-production-1c27.up.railway.app';
  const res = await fetch(`${API_URL}/api/v1${url}`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error('Export failed');
  const blob = await res.blob();
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
};

export const exportCandidatesCsv = () => downloadCsv('/export/candidates/csv', 'candidates_export.csv');
export const exportAnalyticsCsv = () => downloadCsv('/export/analytics/csv', 'hiring_analytics.csv');
export const exportCandidateReport = (id: number) => downloadCsv(`/export/candidate/${id}/report`, `candidate_${id}_report.csv`);
