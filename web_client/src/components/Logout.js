import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Logout = ({ all }) => {
    const navigate = useNavigate();

    useEffect(() => {
        const sessionToken = document.cookie.split('; ').find(row => row.startsWith('session_token=')).split('=')[1];

        axios.post('/api/logout', { all }, { headers: { Authorization: `Bearer ${sessionToken}` } })
            .then(() => {
                // Удалить куки и редирект на главную
                document.cookie = "session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                navigate('/');
            })
            .catch(error => {
                console.error('Ошибка при выходе:', error);
            });
    }, [all, navigate]);

    return <div>Выход из системы...</div>;
};

export default Logout;