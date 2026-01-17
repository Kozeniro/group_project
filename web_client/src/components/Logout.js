import React, { useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Logout = ({ setUserStatus }) => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            // Запрос на выход
            await axios.post('/api/logout', {}, { withCredentials: true });
            setUserStatus('unknown'); // Обновляем статус пользователя на 'unknown'
            navigate('/'); 
        } catch (error) {
            console.error('Ошибка выхода:', error);
        }
    };

    // Вызов функции handleLogout сразу при загрузке компонента
    useEffect(() => {
        handleLogout();
    }, []);

    return <div>Выход из системы...</div>;
};

export default Logout;