import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AuthCallback = ({ setUserStatus }) => {
    const navigate = useNavigate();

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');

        axios
            .post('/api/auth/callback', { code, state })
            .then((response) => {
                document.cookie = `session_token=${response.data.sessionToken}; path=/`;
                setUserStatus(response.data.status); // 'anonymous' или 'authorized'
                navigate('/dashboard');
            })
            .catch(() => {
                navigate('/error');
            });
    }, [setUserStatus, navigate]);

    return <div>Загрузка...</div>;
};

export default AuthCallback;