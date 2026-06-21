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
export const getCurrentUser = async (email) => {
  const response = await api.get(`/auth/me?email=${encodeURIComponent(email)}`);
  return response.data;
};

export const getActiveMeet = async () => {
  const response = await api.get('/active-meet');
  return response.data;
};

export const getTeams = async () => {
  const response = await api.get('/teams');
  return response.data;
};

export const createCoach = async (data) => {
  const response = await api.post('/admin/coaches', data);
  return response.data;
};

export const uploadRoster = async (teamId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/teams/${teamId}/upload-roster`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const createTeam = async (data) => {
  const response = await api.post('/admin/teams', data);
  return response.data;
};

export const updateTeam = async (teamId, data) => {
  const response = await api.put(`/admin/teams/${teamId}`, data);
  return response.data;
};

export const deleteTeam = async (teamId) => {
  const response = await api.delete(`/admin/teams/${teamId}`);
  return response.data;
};

export const getTeamSwimmers = async (teamId, meetId) => {
  const params = meetId ? `?meet_id=${meetId}` : '';
  const response = await api.get(`/teams/${teamId}/swimmers${params}`);
  return response.data;
};

export const updateSwimmerEntries = async (swimmerId, events, meetId) => {
  const response = await api.post(`/swimmers/${swimmerId}/entries`, { events, meet_id: meetId });
  return response.data;
};

export const createMeet = async (data) => {
  const response = await api.post('/admin/meets', data);
  return response.data;
};

export const updateMeet = async (meetId, data) => {
  const response = await api.put(`/admin/meets/${meetId}`, data);
  return response.data;
};

export const deleteMeet = async (meetId) => {
  const response = await api.delete(`/admin/meets/${meetId}`);
  return response.data;
};

export const getMeetEntryStatus = async (meetId) => {
  const response = await api.get(`/meets/${meetId}/entry-status`);
  return response.data;
};

export const addSwimmer = async (teamId, data) => {
  const response = await api.post(`/teams/${teamId}/swimmers`, data);
  return response.data;
};

export const toggleSwimmerStatus = async (swimmerId) => {
  const response = await api.patch(`/swimmers/${swimmerId}/status`);
  return response.data;
};

export const getMeetRelays = async (meetId, teamId) => {
  const response = await api.get(`/meets/${meetId}/relays?team_id=${teamId}`);
  return response.data;
};

export const createOrUpdateRelay = async (meetId, data) => {
  const response = await api.post(`/meets/${meetId}/relays`, data);
  return response.data;
};

export const deleteRelay = async (relayId) => {
  const response = await api.delete(`/relays/${relayId}`);
  return response.data;
};

export default api;
