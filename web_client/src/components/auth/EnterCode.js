import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import '../styles/Login.css';

const EnterCode = ({ setUserStatus }) => {
    const [code, setCode] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const getSessionToken = async () => {
        try {
            const response = await axios.get('/api/auth/get-session-token', { withCredentials: true });
            return response.data.sessionToken;
        } catch (err) {
            console.error('Ошибка при получении sessionToken:', err);
            return null;
        }
    };

    // Обработка отправки кода
    const submitCode = async (e) => {
        e.preventDefault(); // Предотвращаем перезагрузку страницы
        console.log('Функция submitCode вызвана с кодом:', code);

        try {
            const sessionToken = await getSessionToken(); // Получаем токен через новый эндпоинт
            console.log('Полученный sessionToken:', sessionToken);

            if (!sessionToken) {
                setError('Сессионный токен отсутствует. Пожалуйста, получите код авторизации сначала.');
                return;
            }

            console.log('Отправляем код на сервер:', { code, sessionToken });

            const response = await fetch('/api/auth/verify-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code, sessionToken }),
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Перенаправление на личный кабинет
                    navigate('/dashboard'); // Замените на ваш путь к ЛК
                }
            } else {
                const errorData = await response.json();
                console.error('Ошибка:', errorData.error);
                setError('Ошибка при вводе кода: ' + errorData.error);
            }
        } catch (err) {
            console.error("Ошибка при отправке кода:", err);
            setError('Неверный код или произошла ошибка. Попробуйте снова.');
        }
    };

    return (
        <div className="code-auth-container">
            <form onSubmit={submitCode}>
                <input
                    type="text"
                    className="input-code"
                    placeholder="Введите код"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                />
                <button type="submit" className="social-button">Авторизоваться</button>
            </form>
            {error && <p className="error-message">{error}</p>}
        </div>
    );
};

export default EnterCode;