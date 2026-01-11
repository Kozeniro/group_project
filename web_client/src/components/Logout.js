import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Logout = ({ all, setUserStatus }) => {
    const navigate = useNavigate();

    useEffect(() => {
        const sessionToken = document.cookie
            .split('; ')
            .find((row) => row.startsWith('session_token='))
            ?.split('=')[1];

        if (sessionToken) {
            axios
                .post('/api/logout', { all }, { headers: { Authorization: `Bearer ${sessionToken}` } })
                .then(() => {
                    document.cookie = 'session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                    setUserStatus('unknown');
                    navigate('/');
                })
                .catch(() => {
                    navigate('/error');
                });
        } else {
            setUserStatus('unknown');
            navigate('/');
        }
    }, [all, setUserStatus, navigate]);

    return <div>Выход из системы...</div>;
};