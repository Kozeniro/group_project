import React, { useState } from 'react';
import axios from 'axios';
import '../styles/Login.css';

const CodeAuth = ({ setUserStatus }) => {
    const [authCode, setAuthCode] = useState(''); // Код авторизации от сервера
    const [error, setError] = useState('');

    // Функция для получения кода авторизации
    const handleRequestCode = async () => {
        try {
            console.log('Отправляем запрос на генерацию кода...');
            const responseCode = await axios.post('/api/auth/code'); 
            console.log('Ответ от сервера при получении кода:', responseCode.data);
            
            if (responseCode.data && responseCode.data.code) {
                setAuthCode(responseCode.data.code); // Сохраняем код авторизации
                console.log('Сохранен код авторизации:', responseCode.data.code);
            } else {
                throw new Error('Ответ не содержит правильные данные');
            }
        } catch (err) {
            console.error("Ошибка при получении кода:", err);
            setError('Не удалось получить код. Попробуйте еще раз.');
        }
    };

    return (
        <div className="code-auth-container">
            <button onClick={handleRequestCode} className="social-button">
                Получить код авторизации
            </button>
            {authCode && <p>Ваш код авторизации: {authCode}</p>} {/* Отображаем код авторизации */}
            {error && <p className="error-message">{error}</p>}
        </div>
    );
};

export default CodeAuth;