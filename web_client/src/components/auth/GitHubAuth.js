import React from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const GitHubAuth = ({ setUserStatus }) => {
    const navigate = useNavigate();

    const handleGitHubAuth = async () => {
        try {
            const response = await axios.get('/api/auth/login?type=github');
            const authUrl = response.data.authUrl;
            // Перенаправляем пользователя на страницу авторизации через GitHub
            window.location.href = authUrl;
        } catch (err) {
            console.error("Ошибка при получении URL авторизации:", err);
            // Перенаправляем на страницу ошибки с сообщением
            navigate('/auth-error', { state: { message: 'Не удалось получить ссылку для авторизации через GitHub. Попробуйте еще раз.' } });
        }
    };

    return (
        <button onClick={handleGitHubAuth} className="social-button github">
            <i className="fab fa-github" style={{ marginRight: '8px' }}></i>
            Войти через GitHub
        </button>
    );
};

export default GitHubAuth;