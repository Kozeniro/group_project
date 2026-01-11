import React from 'react';
import './Home.css';
import GitHubAuth from './GitHubAuth';
import YandexAuth from './YandexAuth';

const Home = () => {
    return (
        <div className="container">
            <h1>Добро пожаловать!</h1>
            <p>Пожалуйста, выберите способ авторизации:</p>
            <div>
                <h2>Авторизация через:</h2>
                <GitHubAuth />
                <YandexAuth />
                <p>Или введите код для авторизации:</p>
                <input type="text" className="auth-input" placeholder="Введите код" />
                <button className="auth-button">Авторизоваться</button>
            </div>
        </div>
    );
};

export default Home;