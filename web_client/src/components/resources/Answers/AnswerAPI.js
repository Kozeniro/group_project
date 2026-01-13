import axios from 'axios';

export const fetchAnswers = async () => {
    const response = await axios.get('/api/answers');
    return response.data;
};

export const fetchAnswerById = async (id) => {
    const response = await axios.get(`/api/answers/${id}`);
    return response.data;
};

export const createAnswer = async (newAnswer) => {
    const response = await axios.post('/api/answers', newAnswer);
    return response.data;
};

export const updateAnswer = async (id, updatedAnswer) => {
    const response = await axios.put(`/api/answers/${id}`, updatedAnswer);
    return response.data;
};

export const deleteAnswer = async (id) => {
    await axios.delete(`/api/answers/${id}`);
};