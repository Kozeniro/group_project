import React from 'react';
import { useNavigate } from 'react-router-dom';

const YandexAuth = () => {
    const clientId = "60712c9fe7104b4aa8ee392ad5a96c02";
    const redirectUri = "http://localhost:3000/auth/yandex/callback";
    const navigate = useNavigate();

    const handleYandexAuth = () => {

        window.location.href = `https://oauth.yandex.ru/authorize?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}`;
    };

    // После получения данных пользователя (в вашем callback обработчике)
    const handleLoginSuccess = () => {
        navigate('/dashboard'); // Перенаправляем пользователя в личный кабинет
    };

    return (
        <button onClick={handleYandexAuth} className="social-button yandex">
            <i className="fab fa-yandex" style={{ marginRight: '8px' }}></i>
            Войти через Яндекс ID
        </button>
    );
};