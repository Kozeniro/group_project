import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css'; // Подключаем стили

const Login = () => {
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const type = params.get('type');

        if (type) {
            axios.post('/api/login', { type })
                .then(response => {
                    const { sessionToken } = response.data;
                    document.cookie = `session_token=${sessionToken}; path=/`;
                    navigate('/');
                })
                .catch(error => {
                    console.error('Ошибка при логине:', error);
                });
        }
    }, [location.search, navigate]);

    return (
        <div className="login-container">
            <h2>Авторизация</h2>
            <div className="social-login">
                <a href="/auth/github" className="social-button">Войти через GitHub</a>
                <a href="/auth/yandex" className="social-button">Войти через Яндекс</a>
            </div>
            <p>Или введите код для авторизации:</p>
            <input type="text" className="input-code" placeholder="Введите код" />
            <button>Авторизоваться</button>
            <p className="registration-message">
                Нет аккаунта? <a href="/register">Зарегистрируйтесь</a>
            </p>
        </div>
    );
};

export default Login;