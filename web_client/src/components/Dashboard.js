import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ErrorPage from './ErrorPage'; // Импортируем компонент страницы ошибки
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const [userData, setUserData] = useState(null);
    const [error, setError] = useState(false); // Состояние для отслеживания ошибки
    const [loading, setLoading] = useState(true); // Состояние загрузки
    const navigate = useNavigate(); // Хук для навигации

    useEffect(() => {
        const getSessionToken = () => {
            const sessionTokenRow = document.cookie.split('; ').find(row => row.startsWith('session_token='));
            return sessionTokenRow ? sessionTokenRow.split('=')[1] : null;
        };

        const sessionToken = getSessionToken();

        if (!sessionToken) {
            console.error('Токен не найден');
            navigate('/login'); // Перенаправляем на страницу логина, если токен не найден
            return;
        }

        setLoading(true); // Начинаем загрузку
        axios.get('/api/user-data', { headers: { Authorization: `Bearer ${sessionToken}` } })
            .then(response => {
                if (response.status === 200) {
                    setUserData(response.data);
                } else {
                    throw new Error('Не удалось получить данные пользователя');
                }
            })
            .catch(err => {
                console.error('Ошибка при получении данных пользователя:', err);
                if (err.response && err.response.status === 401) {
                    navigate('/login');
                } else {
                    setError(true); // Устанавливаем ошибку при получении данных
                }
            })
            .finally(() => {
                setLoading(false); // Завершаем загрузку
            });
    }, [navigate]); // Добавляем navigate в зависимости

    if (loading) return <div>Загрузка...</div>; // Показываем индикатор загрузки
    if (error) return <ErrorPage />; // Если ошибка, отображаем ErrorPage

    return (
        <div>
            <h2>Личный кабинет</h2>
            <p>Имя: {userData.name}</p>
            {/* Отображение других данных пользователя */}
        </div>
    );
};

export default Dashboard;