import React from 'react';

const YandexAuth = () => {
    const clientId = "60712c9fe7104b4aa8ee392ad5a96c02";
    const redirectUri = "http://localhost:3000/auth/yandex/callback";

    const handleYandexAuth = () => {
        // Перенаправляем пользователя на страницу авторизации Яндекса
        window.location.href = `https://oauth.yandex.ru/authorize?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}`;
    };

    return (
        <button onClick={handleYandexAuth} className="social-button yandex">
            <i className="fab fa-yandex" style={{ marginRight: '8px' }}></i> {/* Иконка Яндекса */}
            Войти через Яндекс ID
        </button>
    );
};

export default YandexAuth;