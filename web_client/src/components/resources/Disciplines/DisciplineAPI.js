import axios from 'axios';

// Получить список всех дисциплин
export const fetchDisciplines = () => {
    return axios.get('/api/disciplines');
};

// Получить информацию о конкретной дисциплине по её ID
export const fetchDisciplineDetails = (id) => {
    return axios.get(`/api/disciplines/${id}`);
};

// Создать новую дисциплину
export const createDiscipline = (data) => {
    return axios.post('/api/disciplines', data);
};

// Обновить информацию о дисциплине по её ID
export const updateDiscipline = (id, data) => {
    return axios.put(`/api/disciplines/${id}`, data);
};

// Удалить дисциплину по её ID
export const deleteDiscipline = (id) => {
    return axios.delete(`/api/disciplines/${id}`);
};

// Получить тесты дисциплины
export const fetchDisciplineTests = (id) => {
    return axios.get(`/api/disciplines/${id}/tests`);
};

// Активировать тест
export const activateTest = (disciplineId, testId) => {
    return axios.put(`/api/disciplines/${disciplineId}/tests/${testId}/activate`);
};

// Деактивировать тест
export const deactivateTest = (disciplineId, testId) => {
    return axios.put(`/api/disciplines/${disciplineId}/tests/${testId}/deactivate`);
};

// Удалить тест из дисциплины
export const deleteTest = (disciplineId, testId) => {
    return axios.delete(`/api/disciplines/${disciplineId}/tests/${testId}`);
};

// Получить информацию о том, активен ли тест
export const checkTestActiveStatus = (disciplineId, testId) => {
    return axios.get(`/api/disciplines/${disciplineId}/tests/${testId}/active`);
};

// Получить список пользователей дисциплины
export const fetchDisciplineUsers = (id) => {
    return axios.get(`/api/disciplines/${id}/users`);
};

// Записать пользователя на дисциплину
export const enrollUser = (disciplineId, userId) => {
    return axios.put(`/api/disciplines/${disciplineId}/users/${userId}`);
};

// Отчислить пользователя с дисциплины
export const unenrollUser = (disciplineId, userId) => {
    return axios.delete(`/api/disciplines/${disciplineId}/users/${userId}`);
};

// Получить дисциплины, на которые записан пользователь
export const fetchUserDisciplines = async (userId) => {
    const response = await axios.get(`/api/user/${userId}/courses`); // Отправляем GET-запрос
    return response.data; // Возвращаем данные из ответа
};

// Обновить дисциплину
export const fetchUpdateDiscipline = (id, data) => {
    return axios.put(`/api/disciplines/${id}`, data);
};