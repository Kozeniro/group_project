// src/components/resources/Tests/TestAPI.js
import axios from 'axios';

// Получить список всех тестов
export const fetchTests = () => {
    return axios.get('/api/tests');
};

// Получить информацию о конкретном тесте
export const fetchTestDetails = (id) => {
    return axios.get(`/api/tests/${id}`);
};

// Создать новый тест
export const createTest = (data) => {
    return axios.post('/api/tests', data);
};

// Обновить информацию о тесте
export const updateTest = (id, data) => {
    return axios.put(`/api/tests/${id}`, data);
};

// Удалить тест
export const deleteTest = (id) => {
    return axios.delete(`/api/tests/${id}`);
};