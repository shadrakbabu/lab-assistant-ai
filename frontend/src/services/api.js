import axios from 'axios';

const API_BASE = '/api';

export const api = {
  checkHealth: async () => {
    const res = await axios.get('/health');
    return res.data;
  },

  uploadManual: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await axios.post(`${API_BASE}/manuals/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  getManuals: async () => {
    const res = await axios.get(`${API_BASE}/manuals`);
    return res.data;
  },

  getManualDetails: async (manualId) => {
    const res = await axios.get(`${API_BASE}/manuals/${manualId}`);
    return res.data;
  },

  getExperiments: async (manualId) => {
    const res = await axios.get(`${API_BASE}/experiments/manual/${manualId}`);
    return res.data;
  },

  getExperimentDetails: async (experimentId) => {
    const res = await axios.get(`${API_BASE}/experiments/${experimentId}`);
    return res.data;
  },

  sendChatMessage: async ({ manualId, experimentId, query, mode = 'standard' }) => {
    const res = await axios.post(`${API_BASE}/chat`, {
      manual_id: manualId,
      experiment_id: experimentId || null,
      query,
      mode
    });
    return res.data;
  }
};
