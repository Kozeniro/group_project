import React from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const YandexAuth = () => {
    const navigate = useNavigate();

    const handleYandexAuth = async () => {
        try {
            // Запрос на получение URL авторизации от вашего сервера
            const response = await axios.get('/api/auth/login?type=yandex');
            const authUrl = response.data.authUrl;
            // Перенаправляем пользователя на страницу авторизации через Яндекс
            window.location.href = authUrl;
        } catch (err) {
            console.error("Ошибка при получении URL авторизации:", err);
            // Перенаправляем на страницу ошибки с сообщением
            navigate('/auth-error', { state: { message: 'Не удалось получить ссылку для авторизации через Яндекс. Попробуйте еще раз.' } });
        }
    };

    return (
        <button onClick={handleYandexAuth} className="social-button yandex">
            <i className="fab fa-yandex" style={{ marginRight: '8px' }}></i>
            Войти через Яндекс ID
        </button>
    );
};

export default YandexAuth;