import React from 'react';
import { useNavigate } from 'react-router-dom';

const ErrorPage = () => {
    const navigate = useNavigate();

    const handleGoHome = () => {
        navigate('/');
    };

    return (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
            <h1>Ошибка</h1>
            <p>Не удалось загрузить данные пользователя. Пожалуйста, попробуйте позже.</p>
            <button onClick={handleGoHome} style={{ padding: '10px 20px', fontSize: '16px' }}>
                Вернуться на главную
            </button>
        </div>
    );
};

export default ErrorPage;