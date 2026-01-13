import React from 'react';
import { useLocation } from 'react-router-dom';

const AuthErrorPage = () => {
    const location = useLocation();
    const message = location.state?.message || 'Произошла ошибка. Повторите попытку позже.';

    return (
        <div className="error-container">
            <h1>Ошибка авторизации</h1>
            <p>{message}</p>
            <a href="/">Вернуться на главную страницу</a>
        </div>
    );
};

export default AuthErrorPage;