import React, { useState } from 'react';
import './styles/Login.css';
import GitHubAuth from './auth/GitHubAuth';
import YandexAuth from './auth/YandexAuth'; 
import CodeAuth from './auth/CodeAuth'; 
import { useNavigate } from 'react-router-dom';

const Login = ({ userStatus, setUserStatus }) => {
    const navigate = useNavigate();

    const handleLogoutClick = () => {
        navigate('/logout');
    };

    const handleDashboardClick = () => {
        navigate('/dashboard');
    };

    const handleEnterCodeClick = () => {
        navigate('/enter-code');
    };

    return (
        <div className="container">
            <h1>Добро пожаловать!</h1>
            {userStatus === 'unknown' && (
                <>
                    <p>Вы не авторизованы. Выберите способ входа:</p>
                    <GitHubAuth setUserStatus={setUserStatus} />
                    <YandexAuth setUserStatus={setUserStatus} />
                    <CodeAuth setUserStatus={setUserStatus} />
                </>
            )}
            {userStatus === 'authorized' && (
                <>
                    <p>Вы авторизованы!</p>
                    <button className="social-button" onClick={handleEnterCodeClick}>
                        Авторизоваться с другого устройства
                    </button>
                    <button className="social-button" onClick={handleDashboardClick}>Перейти в личный кабинет</button>
                    <button className="social-button" onClick={handleLogoutClick}>Выйти</button>
                </>
            )}
        </div>
    );
};

export default Login;