import axios from 'axios';

// Update this to match your FastAPI server URL if different
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getMeets = async () => {
  const response = await api.get('/meets');
  return response.data;
};

export const generateHeatSheet = async (meetId) => {
  const formData = new FormData();
  formData.append('meet_id', meetId);

  const response = await api.post('/generate', formData, {
    responseType: 'blob', // Important to handle PDF binary data
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export default api;
