import React, { useState } from 'react';
import axios from 'axios';

const CodeAuth = () => {
    const [code, setCode] = useState('');

    const handleCodeAuth = () => {
        const sessionTokenRow = document.cookie.split('; ').find(row => row.startsWith('session_token='));
        const sessionToken = sessionTokenRow ? sessionTokenRow.split('=')[1] : null;

        axios.post('http://localhost:3000/api/code-auth', { code, sessionToken })
            .then(response => {
                // Обработка успешной авторизации
                console.log('Авторизация прошла успешно:', response.data);
            })
            .catch(error => {
                console.error('Ошибка авторизации:', error);
            });
    };

    return (
        <div>
            <input
                type="text"
                className="input-code"  // Используем класс input-code
                placeholder="Введите код"
                value={code}
                onChange={(e) => setCode(e.target.value)}
            />
            <button onClick={handleCodeAuth} className="social-button">Авторизоваться</button>
        </div>
    );
};

export default CodeAuth;