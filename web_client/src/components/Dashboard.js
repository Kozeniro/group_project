import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ErrorPage from './errors/ErrorPage';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const [userData, setUserData] = useState(null);
    const [error, setError] = useState(false);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const getSessionToken = () => {
            const sessionTokenRow = document.cookie.split('; ').find(row => row.startsWith('session_token='));
            return sessionTokenRow ? sessionTokenRow.split('=')[1] : null;
        };

        const sessionToken = getSessionToken();

        if (!sessionToken) {
            console.error('Токен не найден');
            navigate('/unauthorized');
            return;
        }

        setLoading(true);
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
                if (err.response) {
                    if (err.response.status === 401) {
                        // Токен истёк или недействителен
                        navigate('/unauthorized');
                    } else if (err.response.status === 403) {
                        // Доступ запрещён
                        navigate('/forbidden');
                    } else {
                        setError(true);
                    }
                } else {
                    setError(true);
                }
            })
            .finally(() => {
                setLoading(false);
            });
    }, [navigate]);

    if (loading) return <div>Загрузка...</div>;
    if (error) return <ErrorPage />;

    const handleLogout = () => {
        navigate('/logout'); // Переход на страницу выхода
    };

    return (
        <div>
            <h2>Личный кабинет</h2>
            <p>Имя: {userData.name}</p>
            <button onClick={handleLogout}>Выйти</button>
            {/* Отображение других данных пользователя */}
        </div>
    );
};