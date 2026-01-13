import axios from 'axios';

// Получить список всех пользователей
export const fetchUsers = () => {
    return axios.get('/api/users');
};

// Получить информацию о конкретном пользователе по его ID
export const fetchUserDetails = (id) => {
    console.log(id);
    return axios.get(`/api/users/${id}/name`);
};

// Получить список курсов, на которые записан пользователь
export const fetchUserCourses = (id) => {
    return axios.get(`/api/users/${id}/courses`);
};

// Получить оценки пользователя по его ID
export const fetchUserGrades = (id) => {
    return axios.get(`/api/users/${id}/grades`);
};

// Получить список ролей пользователя
export const fetchUserRoles = (id) => {
    return axios.get(`/api/users/${id}/roles`);
};

// Изменить роли пользователя
export const saveUser = (id, data) => {
    return axios.put(`/api/users/${id}/name`, { fullName: data.fullName })
        .then(() => axios.put(`/api/users/${id}/roles`, { roles: data.roles }));
};

// Получить доступные роли
export const fetchAvailableRoles = () => {
    return axios.get('/api/roles');
};

// Заблокировать пользователя
export const blockUser = (id) => {
    return axios.put(`/api/users/${id}/block`);
};

// Разблокировать пользователя
export const unblockUser = (id) => {
    return axios.put(`/api/users/${id}/unblock`);
};