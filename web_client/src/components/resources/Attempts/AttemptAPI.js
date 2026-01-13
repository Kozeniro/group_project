import axios from 'axios';

export const fetchAttempts = async () => {
    const response = await axios.get('/api/attempts');
    return response.data;
};

export const fetchAttemptById = async (id) => {
    const response = await axios.get(`/api/attempts/${id}`);
    return response.data;
};

export const createAttempt = async (newAttempt) => {
    const response = await axios.post('/api/attempts', newAttempt);
    return response.data;
};

export const updateAttempt = async (id, updatedAttempt) => {
    const response = await axios.put(`/api/attempts/${id}`, updatedAttempt);
    return response.data;
};

export const deleteAttempt = async (id) => {
    await axios.delete(`/api/attempts/${id}`);
};