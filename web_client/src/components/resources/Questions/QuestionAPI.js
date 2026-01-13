import axios from 'axios';

const API_URL = '/api/questions';

// Получить список всех вопросов
export const fetchQuestions = async () => {
    const response = await axios.get(API_URL);
    return response.data;
};

// Получить информацию о конкретном вопросе по его ID и версии
export const fetchQuestionByIdAndVersion = async (id, version) => {
    const response = await axios.get(`${API_URL}/${id}/${version}`);
    return response.data;
};

// Создать новый вопрос
export const createQuestion = async (newQuestion) => {
    const response = await axios.post(API_URL, newQuestion);
    return response.data;
};

// Обновить вопрос по его ID
export const updateQuestion = async (id, updatedQuestion) => {
    const response = await axios.put(`${API_URL}/${id}`, updatedQuestion);
    return response.data;
};

// Удалить вопрос по его ID
export const deleteQuestion = async (id) => {
    await axios.delete(`${API_URL}/${id}`);
};